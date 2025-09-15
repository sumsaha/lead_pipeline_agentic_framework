import os
from serpapi import GoogleSearch

def discover_sources_serp(keywords, limit=5):
    api_key = os.environ.get('SERPAPI_API_KEY')
    if not api_key:
        # fallback to demo sample pages
        return [
            'https://example.com/oracle-testing-announcement',
            'https://example.org/blog/oracle-cloud-qa'
        ]
    results = []
    for q in keywords:
        params = {
            'engine': 'google',
            'q': q,
            'api_key': api_key,
            'num': limit
        }
        search = GoogleSearch(params)
        data = search.get_dict()
        for item in data.get('organic_results', [])[:limit]:
            link = item.get('link')
            if link:
                results.append(link)
    # dedupe while preserving order
    seen = set()
    unique = []
    for r in results:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique
