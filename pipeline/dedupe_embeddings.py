import os, hashlib, numpy as np
try:
    import openai
    openai.api_key = os.environ.get('OPENAI_API_KEY')
except Exception:
    openai = None

def _mock_embedding(text):
    # simple deterministic mock embedding
    h = hashlib.sha256(text.encode('utf-8')).digest()
    arr = np.frombuffer(h, dtype=np.uint8).astype(float)
    return arr / (arr.sum()+1)

def get_embedding(text):
    if openai and openai.api_key:
        # use OpenAI embeddings API
        resp = openai.Embedding.create(input=text, model='text-embedding-3-small')
        return np.array(resp['data'][0]['embedding'], dtype=float)
    else:
        return _mock_embedding(text)

def dedupe_by_embedding(items, threshold=0.85):
    # items: list of dicts with 'domain' and 'title' etc.
    embs = []
    for it in items:
        txt = (it.get('domain') or '') + ' ' + (it.get('title') or '')
        embs.append(get_embedding(txt))
    clusters = []
    used = set()
    for i,e in enumerate(embs):
        if i in used:
            continue
        cluster = [i]
        for j in range(i+1, len(embs)):
            if j in used:
                continue
            # cosine similarity
            sim = float(np.dot(e, embs[j]) / (np.linalg.norm(e)*np.linalg.norm(embs[j]) + 1e-12))
            if sim >= threshold:
                cluster.append(j)
                used.add(j)
        clusters.append(cluster)
    # pick first member of each cluster
    unique = [items[c[0]] for c in clusters]
    return unique
