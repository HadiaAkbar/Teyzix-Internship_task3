from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default='user') # 'admin' or 'user'
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(Text, nullable=False)
    
    # Analysis Results
    contract_type = Column(String(100))
    parties_involved = Column(Text)
    effective_date = Column(String(50))
    expiry_date = Column(String(50))
    payment_terms = Column(Text)
    renewal_clauses = Column(Text)
    confidentiality_clauses = Column(Text)
    termination_clauses = Column(Text)
    responsibilities = Column(Text)
    
    # Risk Assessment
    risk_score = Column(Float, default=0.0)
    missing_clauses = Column(Text)
    high_risk_conditions = Column(Text)
    ambiguous_statements = Column(Text)
    unusual_payment_terms = Column(Text)
    legal_red_flags = Column(Text)
    
    # Summary
    executive_summary = Column(Text)
    key_obligations = Column(Text)
    important_dates = Column(Text)
    important_clauses = Column(Text)
    recommended_actions = Column(Text)
    
    user = relationship("User", back_populates="documents")

engine = create_engine('sqlite:///contracts.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
