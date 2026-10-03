def compress_text(text: str, limit: int = 240) -> str:
    return " ".join(text.split())[:limit]
