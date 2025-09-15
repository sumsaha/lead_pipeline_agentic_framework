from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime
Base = declarative_base()
class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    title = Column(String(512))
    source_url = Column(String(1024), unique=True)
    domain = Column(String(256))
    emails = Column(String(1024))
    phones = Column(String(512))
    score = Column(Integer, default=0)
    raw_snippet = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'source_url': self.source_url,
            'domain': self.domain,
            'emails': self.emails.split(',') if self.emails else [],
            'phones': self.phones.split(',') if self.phones else [],
            'score': self.score,
            'created_at': self.created_at.isoformat()
        }
