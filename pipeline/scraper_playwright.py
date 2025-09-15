import asyncio, os, hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import requests

async def _fetch_with_playwright(url):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        content = await page.content()
        await browser.close()
        return content

def fetch_and_snapshot(url, use_playwright=False):
    try:
        if use_playwright:
            html = asyncio.run(_fetch_with_playwright(url))
        else:
            r = requests.get(url, timeout=15, headers={'User-Agent':'lead-pipeline-mvp/2.0'})
            r.raise_for_status()
            html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
        text = ' '.join(paragraphs) if paragraphs else ''
        snapshot_hash = hashlib.sha256(html.encode('utf-8')).hexdigest()
        os.makedirs('data/snapshots', exist_ok=True)
        path = f"data/snapshots/{snapshot_hash[:12]}.html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return {
            'url': url,
            'html': html,
            'text': text,
            'snapshot': path,
            'fetched_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        print('fetch error', e)
        return None
