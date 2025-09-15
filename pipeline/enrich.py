import tldextract
def enrich_contact(extracted):
    url = extracted.get('source_url') or ''
    t = tldextract.extract(url)
    domain = '.'.join([p for p in (t.domain, t.suffix) if p])
    out = dict(extracted)
    out['domain'] = domain
    out['has_email'] = len(out.get('emails') or []) > 0
    out['score'] = (50 if out['has_email'] else 10) + (20 if 'oracle' in (out.get('raw') or '').lower() else 0)
    return out
