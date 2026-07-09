from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Document, Analysis, RiskFinding, DocumentStatus
from app.schemas import DashboardStats
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc_query = db.query(Document)
    if current_user.role != "admin":
        doc_query = doc_query.filter(Document.owner_id == current_user.id)
    documents = doc_query.all()
    doc_ids = [d.id for d in documents]

    analyses = db.query(Analysis).filter(Analysis.document_id.in_(doc_ids)).all() if doc_ids else []
    avg_risk = round(sum(a.risk_score for a in analyses) / len(analyses), 1) if analyses else 0.0
    high_risk_count = sum(1 for a in analyses if a.risk_score >= 60)

    risks = db.query(RiskFinding).filter(RiskFinding.document_id.in_(doc_ids)).all() if doc_ids else []
    risk_titles = Counter(r.title for r in risks)
    frequent = [{"title": t, "count": c} for t, c in risk_titles.most_common(5)]

    # NEW: Get recent analyzed documents
    recent_docs = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id if current_user.role != "admin" else True)
        .filter(Document.status == DocumentStatus.ANALYZED)
        .order_by(Document.processed_at.desc())
        .limit(5)
        .all()
    )
    
    recent_documents = [
        {
            "id": d.id,
            "filename": d.filename,
            "risk_level": d.risk_level,
            "summary": d.summary,
            "processed_at": d.processed_at.isoformat() if d.processed_at else None,
        }
        for d in recent_docs
    ]
    
    return DashboardStats(
        total_documents=len(documents),
        average_risk_score=avg_risk,
        high_risk_documents=high_risk_count,
        frequently_detected_risks=frequent,
        recent_documents=recent_documents,  # NEW
    )
