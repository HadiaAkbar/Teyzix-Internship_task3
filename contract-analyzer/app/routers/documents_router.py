import os
import uuid
import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import User, Document, DocumentStatus, Analysis, RiskFinding, DocumentChunk, AuditLog
from app.schemas import DocumentOut, AnalysisOut
from app.auth import get_current_user
from app.document_processor import extract_text, chunk_text, validate_file, UnsupportedFileType
from app.ai_engine import run_analysis

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contents = await file.read()
    
    # 1. Improved Validation
    ok, msg = validate_file(file.filename, contents, settings.MAX_UPLOAD_MB,
                             settings.ALLOWED_EXTENSIONS)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    # 2. Duplicate Check (Basic: same filename and size for same user today)
    # This is a simple heuristic to prevent accidental double uploads
    existing = db.query(Document).filter(
        Document.owner_id == current_user.id,
        Document.filename == file.filename,
        Document.status != DocumentStatus.FAILED
    ).first()
    
    if existing:
        # Check if the file on disk is the same size to be sure
        if os.path.exists(existing.stored_path) and os.path.getsize(existing.stored_path) == len(contents):
             # Return existing if it's already analyzed, or allow re-upload if it failed
             return existing

    # 3. Secure Storage
    ext = os.path.splitext(file.filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    
    try:
        with open(stored_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 4. Persistence
    document = Document(
        owner_id=current_user.id,
        filename=file.filename,
        stored_path=stored_path,
        file_type=ext,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    db.add(AuditLog(user_id=current_user.id, action="upload",
                     detail=f"Uploaded {file.filename} (ID: {document.id})"))
    db.commit()
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Document)
    if current_user.role != "admin":
        q = q.filter(Document.owner_id == current_user.id)
    return q.order_by(Document.uploaded_at.desc()).all()


def _get_owned_document(document_id: int, db: Session, current_user: User) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    return doc


@router.post("/{document_id}/analyze", response_model=AnalysisOut)
def analyze_document(document_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    doc = _get_owned_document(document_id, db, current_user)

    try:
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        # 1. Robust Extraction
        if not doc.raw_text:
            try:
                extracted = extract_text(doc.stored_path, doc.file_type)
                if not extracted or not extracted.strip():
                    raise ValueError("Document appears to be empty or contains no extractable text")
                doc.raw_text = extracted
                db.commit()
            except Exception as e:
                doc.status = DocumentStatus.FAILED
                db.commit()
                raise HTTPException(status_code=422, detail=f"Text extraction failed: {str(e)}")

        # 2. Chunking for Search
        if not doc.chunks:
            chunks = chunk_text(doc.raw_text)
            for i, chunk in enumerate(chunks):
                db.add(DocumentChunk(document_id=doc.id, chunk_index=i, text=chunk))
            db.commit()

        # 3. Analysis Execution
        try:
            result = run_analysis(doc.raw_text)
        except Exception as e:
            doc.status = DocumentStatus.FAILED
            db.commit()
            raise HTTPException(status_code=502, detail=f"AI Analysis engine error: {str(e)}")

        # upsert analysis
        existing = db.query(Analysis).filter(Analysis.document_id == doc.id).first()
        if existing:
            db.query(RiskFinding).filter(RiskFinding.document_id == doc.id).delete()
            db.delete(existing)
            db.commit()

        analysis = Analysis(
            document_id=doc.id,
            contract_type=result.get("contract_type"),
            parties=result.get("parties"),
            effective_date=result.get("effective_date"),
            expiry_date=result.get("expiry_date"),
            payment_terms=result.get("payment_terms"),
            renewal_clause=result.get("renewal_clause"),
            confidentiality_clause=result.get("confidentiality_clause"),
            termination_clause=result.get("termination_clause"),
            responsibilities=result.get("responsibilities"),
            executive_summary=result.get("executive_summary"),
            key_obligations=result.get("key_obligations"),
            important_dates=result.get("important_dates"),
            important_clauses=result.get("important_clauses"),
            recommended_actions=result.get("recommended_actions"),
            risk_score=result.get("risk_score", 0.0),
            engine_used=result.get("_engine", "rule_based"),
        )
        db.add(analysis)

        for r in result.get("risks", []):
            db.add(RiskFinding(
                document_id=doc.id,
                category=r.get("category", "Uncategorized"),
                title=r.get("title", ""),
                explanation=r.get("explanation", ""),
                severity=r.get("severity", "low"),
                confidence=r.get("confidence", 0.5),
                evidence_snippet=r.get("evidence_snippet"),
            ))

        doc.status = DocumentStatus.ANALYZED
        doc.processed_at = dt.datetime.utcnow()
        db.commit()
        db.refresh(analysis)

        db.add(AuditLog(user_id=current_user.id, action="analyze",
                         detail=f"Analyzed document {doc.id} ({doc.filename})"))
        db.commit()

        analysis.risks = db.query(RiskFinding).filter(RiskFinding.document_id == doc.id).all()
        return analysis

    except UnsupportedFileType as e:
        doc.status = DocumentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        doc.status = DocumentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.get("/{document_id}/analysis", response_model=AnalysisOut)
def get_analysis(document_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    doc = _get_owned_document(document_id, db, current_user)
    if not doc.analysis:
        raise HTTPException(status_code=404, detail="Document has not been analyzed yet")
    doc.analysis.risks = db.query(RiskFinding).filter(RiskFinding.document_id == doc.id).all()
    return doc.analysis


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    doc = _get_owned_document(document_id, db, current_user)
    if os.path.exists(doc.stored_path):
        os.remove(doc.stored_path)
    db.delete(doc)
    db.commit()
    return None
