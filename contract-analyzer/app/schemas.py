from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import datetime as dt


# ---------- Auth ----------
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Documents ----------
class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    uploaded_at: dt.datetime
    processed_at: Optional[dt.datetime] = None
    risk_level: Optional[str] = "N/A"
    summary: Optional[str] = "No summary available"

    class Config:
        from_attributes = True


# ---------- Analysis ----------
class RiskFindingOut(BaseModel):
    category: str
    title: str
    explanation: str
    severity: str
    confidence: float
    evidence_snippet: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    contract_type: Optional[str]
    parties: Optional[List[str]]
    effective_date: Optional[str]
    expiry_date: Optional[str]
    payment_terms: Optional[str]
    renewal_clause: Optional[str]
    confidentiality_clause: Optional[str]
    termination_clause: Optional[str]
    responsibilities: Optional[str]
    executive_summary: Optional[str]
    key_obligations: Optional[List[str]]
    important_dates: Optional[List[str]]
    important_clauses: Optional[List[str]]
    recommended_actions: Optional[List[str]]
    risk_score: float
    engine_used: str
    risks: List[RiskFindingOut] = []

    class Config:
        from_attributes = True


# ---------- Search ----------
class SearchQuery(BaseModel):
    document_id: int
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    chunk_index: int
    text: str
    score: float


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_documents: int
    average_risk_score: float
    high_risk_documents: int
    frequently_detected_risks: List[Dict[str, Any]]
