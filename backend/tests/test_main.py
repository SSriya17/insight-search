from app.main import cosine_similarity

def test_cosine_similarity():
    assert round(cosine_similarity([1, 0], [1, 0]), 5) == 1.0
    assert round(cosine_similarity([1, 0], [0, 1]), 5) == 0.0
