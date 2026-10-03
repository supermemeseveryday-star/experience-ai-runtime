"""Local embeddings; uses sentence-transformers when installed, deterministic fallback otherwise."""

import hashlib
import re
from pathlib import Path
import numpy as np


class LocalEmbedder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimensions: int = 384,
    ):
        self.model_name, self.dimensions, self._model, self.load_error = (
            model_name,
            dimensions,
            None,
            None,
        )
        try:
            from sentence_transformers import SentenceTransformer

            model_path = Path(model_name)
            if not model_path.is_dir():
                from huggingface_hub import try_to_load_from_cache

                cached = try_to_load_from_cache(model_name, "modules.json")
                if not isinstance(cached, str):
                    raise FileNotFoundError(
                        f"Embedding model '{model_name}' is not fully cached locally."
                    )
                model_path = Path(cached).parent
            required = [
                model_path / "modules.json",
                model_path / "config.json",
                model_path / "model.safetensors",
                model_path / "1_Pooling" / "config.json",
            ]
            tokenizers = [
                model_path / name
                for name in ("tokenizer.json", "vocab.txt", "spiece.model")
            ]
            if not all(p.is_file() for p in required) or not any(
                p.is_file() for p in tokenizers
            ):
                raise FileNotFoundError(
                    f"Embedding model '{model_name}' has an incomplete local cache."
                )
            self._model = SentenceTransformer(str(model_path), local_files_only=True)
        except Exception as exc:
            self._model = None
            self.load_error = str(exc)
        self.backend = (
            "sentence-transformers"
            if self._model is not None
            else "hashed-token-char-ngram"
        )

    def embed(self, text: str) -> list[float]:
        if self._model is not None:
            return (
                self._model.encode(text, normalize_embeddings=True)
                .astype(float)
                .tolist()
            )
        # Hashed token and character n-gram vectors keep offline installs functional,
        # including Chinese text where whitespace tokenization is unavailable.
        vec = np.zeros(self.dimensions, dtype=np.float32)
        tokens = re.findall(r"[\w+#.-]+", text.lower())
        features = [(token, 1.0) for token in tokens]
        features += [(f"{a}_{b}", 1.25) for a, b in zip(tokens, tokens[1:])]
        for chunk in re.findall(r"[\u3400-\u9fff]+", text.lower()):
            if len(chunk) == 1:
                features.append((chunk, 1.0))
            for n in (2, 3):
                features.extend(
                    (chunk[i : i + n], 0.55 if n == 2 else 0.35)
                    for i in range(len(chunk) - n + 1)
                )
        for feature, weight in features:
            index = (
                int(hashlib.blake2b(feature.encode(), digest_size=8).hexdigest(), 16)
                % self.dimensions
            )
            vec[index] += weight
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist() if norm else vec.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    av, bv = np.asarray(a), np.asarray(b)
    denom = np.linalg.norm(av) * np.linalg.norm(bv)
    return float(np.dot(av, bv) / denom) if denom else 0.0
