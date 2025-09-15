from pipeline.dedupe_embeddings import _mock_embedding, dedupe_by_embedding
def test_mock_embedding():
    a = _mock_embedding('hello world')
    b = _mock_embedding('hello world')
    assert a.shape == b.shape
def test_dedupe_simple():
    items = [
        {'domain':'example.com','title':'Oracle testing'},
        {'domain':'example.com','title':'Oracle testing duplicate'},
        {'domain':'other.com','title':'unrelated'}
    ]
    unique = dedupe_by_embedding(items, threshold=0.5)
    assert len(unique) >= 1
