Lead Pipeline MVP v2
====================
Upgraded demo with:
- Playwright for JS rendering (python-playwright based)
- Lightweight LangGraph-style DAG runner with retries
- PostgreSQL + pgvector in docker-compose
- OpenAI embeddings-based dedupe (uses OPENAI_API_KEY; mocks if not set)
- OpenAI LLM-based extractor (uses OPENAI_API_KEY)
- SerpAPI discovery (uses SERPAPI_API_KEY)
- Vault secret loader (optional; uses VAULT_ADDR & VAULT_TOKEN)
- Unit tests (pytest) and GitHub Actions CI
- Dockerfile to build the app image

Quickstart (locally):
1. Install Python 3.11+ and Node.js (for playwright browsers).
2. Create venv and activate.
   python3 -m venv .venv && source .venv/bin/activate
3. Install Python deps:
   pip install -r requirements.txt
4. Install Playwright browsers:
   playwright install
5. Start services:
   docker-compose up -d
   (this will start postgres with pgvector)
6. Run the demo:
   python run_demo.py

Environment variables:
- OPENAI_API_KEY (optional, for embeddings & LLM)
- SERPAPI_API_KEY (optional, for discovery)
- VAULT_ADDR & VAULT_TOKEN (optional, for secrets)

Notes:
- This repo is an MVP scaffold. For production, replace mocks with your infra and secure secrets via Vault/KMS.


## Playwright toggle
Set the environment variable `PLAYWRIGHT_ENABLED` to `0` or `false` to disable Playwright fetches in the DAG. Default is enabled.

## Kubernetes
Manifests for Deployment/Service/Ingress are in `k8s/`. Replace image names and secret handling as appropriate.

## Traefik and Nginx
A Traefik service is included in `docker-compose.yml` for local reverse proxying. Nginx is added as a placeholder frontend.


## v4 LangGraph upgrade
This version replaces the lightweight mock DAG runner with the real `langgraph` library. Install dependencies and run `python pipeline/workflow.py` to execute the LangGraph workflow.
