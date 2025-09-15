from fastapi import FastAPI
from pipeline.persistence_pg import init_db, get_session
from pipeline.models_pg import Lead
app = FastAPI(title='Lead Pipeline MVP v2')

@app.on_event('startup')
def startup():
    init_db()

@app.get('/leads')
def list_leads():
    session = get_session()
    rows = session.query(Lead).order_by(Lead.created_at.desc()).limit(100).all()
    return [r.as_dict() for r in rows]
