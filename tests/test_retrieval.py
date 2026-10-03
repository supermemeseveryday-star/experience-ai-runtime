from experience_ai.embeddings.local import LocalEmbedder, cosine_similarity
from experience_ai.models.schemas import Experience
from experience_ai.models.enums import ExperienceStatus


def test_cosine_and_retrieval(runtime):
    emb = LocalEmbedder()
    assert (
        cosine_similarity(emb.embed("python package"), emb.embed("python package"))
        > 0.99
    )
    runtime.store.add(
        Experience(
            experience_id="exp_1",
            problem_pattern="python package",
            problem_summary="Install package",
            conditions=["python"],
            strategy=["Use pip"],
            status=ExperienceStatus.VERIFIED,
        )
    )
    assert (
        runtime.search.search("python package", 5)[0].experience.experience_id
        == "exp_1"
    )


def test_applicability_normalized(runtime):

    c = runtime.search.search("nothing", 1)
    if not c:
        runtime.store.add(
            Experience(
                experience_id="e",
                problem_pattern="",
                problem_summary="",
                status=ExperienceStatus.VERIFIED,
            )
        )
        c = runtime.search.search("x", 1)
    assert 0 <= runtime.checker.score("query", c[0]) <= 1


def test_chinese_fallback_matches_related_phrasing():
    emb = LocalEmbedder()
    assert emb.backend == "hashed-token-char-ngram"
    a = emb.embed("如何修复 Python 依赖安装失败")
    b = emb.embed("Python 安装依赖出错如何解决")
    assert cosine_similarity(a, b) > 0.05
