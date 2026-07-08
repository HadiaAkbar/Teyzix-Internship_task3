import enum
import datetime as dt
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum, Boolean, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=dt.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="documents")
    analysis = relationship("Analysis", back_populates="document", uselist=False,
                             cascade="all, delete-orphan")
    risks = relationship("RiskFinding", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    @property
    def risk_level(self):
        if not self.analysis:
            return "N/A"
        score = self.analysis.risk_score
        if score >= 7.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        return "Low"

    @property
    def summary(self):
        if not self.analysis or not self.analysis.executive_summary:
            return "No summary available"
        return self.analysis.executive_summary[:150] + "..." if len(self.analysis.executive_summary) > 150 else self.analysis.executive_summary


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)

    contract_type = Column(String, nullable=True)
    parties = Column(JSON, nullable=True)
    effective_date = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    payment_terms = Column(Text, nullable=True)
    renewal_clause = Column(Text, nullable=True)
    confidentiality_clause = Column(Text, nullable=True)
    termination_clause = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)

    executive_summary = Column(Text, nullable=True)
    key_obligations = Column(JSON, nullable=True)
    important_dates = Column(JSON, nullable=True)
    important_clauses = Column(JSON, nullable=True)
    recommended_actions = Column(JSON, nullable=True)

    risk_score = Column(Float, default=0.0)
    engine_used = Column(String, default="rule_based")  # "llm" or "rule_based"
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    document = relationship("Document", back_populates="analysis")


class RiskFinding(Base):
    __tablename__ = "risk_findings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    category = Column(String, nullable=False)   # e.g. Missing Clause, High-Risk Condition
    title = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    severity = Column(String, nullable=False)    # low / medium / high
    confidence = Column(Float, nullable=False)   # 0-1
    evidence_snippet = Column(Text, nullable=True)

    document = relationship("Document", back_populates="risks")


class DocumentChunk(Base):
    """Chunks of document text used for semantic / keyword search."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    document = relationship("Document", back_populates="chunks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
