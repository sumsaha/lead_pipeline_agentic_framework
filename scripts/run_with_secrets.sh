#!/bin/bash
# Example: load secrets using hvac or env and run pipeline
export OPENAI_API_KEY=${OPENAI_API_KEY:-$(python -c "import os; print(os.getenv('OPENAI_API_KEY') or '')")}
python run_demo.py
