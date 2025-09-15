import os
import json
from langgraph.graph import StateGraph  # langgraph StateGraph
# from langgraph.nodes import FunctionNode
# Note: exact langgraph API may vary; this file provides a LangGraph-based example.
# If langgraph's API differs in your installed version, adjust imports accordingly.

from pipeline.discovery_serp import discover_sources_serp
from pipeline.scraper_playwright import fetch_and_snapshot
from pipeline.llm_extractor import extract_with_llm
from pipeline.enrich import enrich_contact
from pipeline.dedupe_embeddings import dedupe_by_embedding
from pipeline.persistence_pg import init_db, get_session
from pipeline.models_pg import Lead
from langgraph.types import Command

# wrapper nodes

def discover_node(state):
    keywords = state.get('keywords') or [
        'oracle test automation tool',
        'oracle cloud testing',
        'oracle fusion testing'
    ]
    urls = discover_sources_serp(keywords, limit=5)
    return Command(update={'urls': urls})


def fetch_node(state):
    urls = state.get('urls') or []
    use_pw = os.environ.get('PLAYWRIGHT_ENABLED', '1') in ('1', 'true', 'yes')
    fetched = []
    for u in urls:
        r = fetch_and_snapshot(u, use_playwright=use_pw)
        if r:
            fetched.append(r)
    return Command(update={'fetched': fetched})


def extract_node(state):
    fetched = state.get('fetched') or []
    extracted = []
    for f in fetched:
        text = f.get('text') or f.get('html', '')
        try:
            data = extract_with_llm(text, f.get('url'))
        except Exception:
            data = {'title': None, 'emails': [], 'phones': [], 'people': [], 'company': None, 'intent': 'unknown',
                    'topics': []}
        data['source_url'] = f.get('url')
        data['raw'] = text[:2000]
        extracted.append(data)
    return Command(update={'extracted': extracted})


def enrich_node(state):
    items = state.get('extracted') or []
    enriched = [enrich_contact(i) for i in items]
    return Command(update={'enriched': enriched})


def dedupe_node(state):
    items = state.get('enriched') or []
    unique = dedupe_by_embedding(items, threshold=0.90)
    return Command(update={'unique': unique})


def persist_node(state):
    init_db()
    items = state.get('unique') or []
    session = get_session()
    persisted_ids = []
    for it in items:
        lead = Lead(
            title=it.get('title'),
            source_url=it.get('source_url'),
            domain=it.get('domain'),
            emails=','.join(it.get('emails') or []),
            phones=','.join(it.get('phones') or []),
            score=int(it.get('score') or 0),
            raw_snippet=it.get('raw')[:2000]
        )
        session.merge(lead)
        session.commit()
        persisted_ids.append(lead.id)
    return Command(update={'persisted_ids': persisted_ids})


# --- summarizer node ---
def summarizer_node(state):
    persisted_ids = state.get("persisted_ids", [])
    enriched = state.get("unique", [])
    count = len(enriched)

    # Build summary string
    summary_lines = [f"✅ Workflow complete: {count} leads processed\n"]
    for i, lead in enumerate(enriched, 1):
        summary_lines.append(
            f"Lead {i}:\n"
            f"• Company: {lead.get('company')}\n"
            f"• Domain: {lead.get('domain')}\n"
            f"• Emails: {', '.join(lead.get('emails') or [])}\n"
            f"• Phones: {', '.join(lead.get('phones') or [])}\n"
            f"• URL: {lead.get('source_url')}\n"
            f"• Score: {lead.get('score', 0)}\n"
        )

    summary = "\n".join(summary_lines)

    # Print locally
    print("\n=== Lead Summary ===\n")
    print(summary)

    # Optional: push to Slack if webhook exists
    slack_url = os.environ.get("SLACK_WEBHOOK")
    if slack_url:
        try:
            from slack_sdk.webhook import WebhookClient
            wh = WebhookClient(slack_url)
            wh.send(text=summary[:3000])  # Slack has length limits
        except Exception as e:
            print("⚠️ Slack notify failed:", e)

    return Command(update={"summary": summary, "final_count": count})


def build_and_run(initial_keywords=None):
    # Build a StateGraph with FunctionNodes for each step
    graph = StateGraph(state_schema=dict)

    # graph.add_node(FunctionNode('discover', discover_node, max_retries=1))
    # graph.add_node(FunctionNode('fetch', fetch_node, max_retries=1))
    # graph.add_node(FunctionNode('extract', extract_node, max_retries=2))
    # graph.add_node(FunctionNode('enrich', enrich_node, max_retries=1))
    # graph.add_node(FunctionNode('dedupe', dedupe_node, max_retries=1))
    # graph.add_node(FunctionNode('persist', persist_node, max_retries=1))

    # Register nodes as plain functions
    graph.add_node("discover", discover_node)
    graph.add_node("fetch", fetch_node)
    graph.add_node("extract", extract_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("dedupe", dedupe_node)
    graph.add_node("persist", persist_node)
    graph.add_node("summarizer", summarizer_node)

    # Connect nodes (linear DAG)
    graph.add_edge('discover', 'fetch')
    graph.add_edge('fetch', 'extract')
    graph.add_edge('extract', 'enrich')
    graph.add_edge('enrich', 'dedupe')
    graph.add_edge('dedupe', 'persist')
    graph.add_edge("persist", "summarizer")

    graph.set_entry_point('discover')

    state = {}
    if initial_keywords:
        state['keywords'] = initial_keywords
    print('Invoking LangGraph workflow...')
    result = graph.compile().invoke(state)
    print('Workflow result:', json.dumps(result, default=str))
    return result


if __name__ == '__main__':
    build_and_run()
