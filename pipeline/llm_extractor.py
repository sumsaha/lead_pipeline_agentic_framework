import os, json, re, time
import openai
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Safer structured extraction prompt. Includes schema and an example output.
PROMPT_HEADER = '''You are a strict JSON extractor. Given page text and a URL, extract the following fields and return only JSON (no prose):
Schema:
{
  "title": string or null,
  "emails": [strings],
  "phones": [strings],
  "people": [strings],
  "company": string or null,
  "intent": string,    # one of "ad","need","hiring","interest","unknown"
  "topics": [strings]
}

Rules:
- Output must be valid JSON parsable by standard JSON libraries.
- If a field is not present, output null or an empty list as appropriate.

Example output:
{
  "title": "Hiring QA Automation Engineer for Oracle Cloud Testing",
  "emails": ["recruiter@example.com"],
  "phones": ["+1-555-0100"],
  "people": ["Jane Doe"],
  "company": "Example Corp",
  "intent": "hiring",
  "topics": ["oracle cloud", "automation", "cypress"]
}

Now extract from the provided PAGE_TEXT and URL below.
'''.strip()

JSON_BLOCK_RE = re.compile(r'(\{.*\})', re.DOTALL)

def _extract_json_from_text(text):
    # Try to find the first top-level JSON object in text
    m = JSON_BLOCK_RE.search(text)
    if not m:
        return None
    s = m.group(1)
    # Attempt to balance braces if truncated
    stack = []
    for i,c in enumerate(s):
        if c=='{':
            stack.append('{')
        elif c=='}':
            if stack:
                stack.pop()
            if not stack:
                return s[:i+1]
    return s

def extract_with_llm(text, url, max_retries=2):
    if not openai.api_key:
        # mock extraction
        return {
            'title': None,
            'emails': [],
            'phones': [],
            'people': [],
            'company': None,
            'intent': 'unknown',
            'topics': []
        }
    prompt = PROMPT_HEADER + "\n\nPAGE_TEXT:\n" + (text[:4000]) + "\n\nURL:\n" + url
    for attempt in range(max_retries+1):
        try:
            resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=[
                {'role':'system','content':'You are a JSON extraction assistant.'},
                {'role':'user','content':prompt}
            ], max_tokens=800, temperature=0)
            out = resp.choices[0].message['content'].strip()
            # Extract first JSON block
            jb = _extract_json_from_text(out)
            if not jb:
                # sometimes model returns only JSON-like text; attempt to parse whole output
                jb = out
            data = json.loads(jb)
            # normalize fields
            data.setdefault('title', None)
            data.setdefault('emails', [])
            data.setdefault('phones', [])
            data.setdefault('people', [])
            data.setdefault('company', None)
            data.setdefault('intent', 'unknown')
            data.setdefault('topics', [])
            return data
        except Exception as e:
            # retry on parse error or rate-limit
            if attempt < max_retries:
                time.sleep(1 + attempt*2)
                continue
            # fallback
            return {
                'title': None,
                'emails': [],
                'phones': [],
                'people': [],
                'company': None,
                'intent': 'unknown',
                'topics': []
            }
