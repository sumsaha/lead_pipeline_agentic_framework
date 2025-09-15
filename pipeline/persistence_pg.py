import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DB_URL = os.environ.get('DATABASE_URL') or 'postgresql://demo:demo@localhost:5432/leads'
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
def init_db():
    # create tables via models import
    from .models_pg import Base
    Base.metadata.create_all(engine)
def get_session():
    return Session()
