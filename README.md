# AI-Powered Contract & Legal Document Risk Analyzer

Teyzix Core Internship — Task AI-3

An AI-powered system that ingests contracts (PDF/DOCX/TXT), extracts key clauses,
detects risks with confidence scores and explanations, generates executive summaries,
supports natural-language search over documents, and produces downloadable PDF/DOCX
risk reports.

> **Note on status:** This repo is a working foundation covering every mandatory
> feature end-to-end (tested locally — see "Verified Workflow" below). Before
> submission you should: add your own test documents, tune/extend the risk rules or
> prompts, write your own commit history as you build on it, and take the required
> screenshots. Treat this as a strong starting point, not a copy-paste final deliverable.

## Architecture

```
contract-analyzer/
├── app/
│   ├── main.py               # FastAPI app entrypoint, router registration
│   ├── config.py             # Settings loaded from .env
│   ├── database.py           # SQLAlchemy engine/session
│   ├── models.py             # ORM models (User, Document, Analysis, RiskFinding, ...)
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── auth.py                # JWT auth, password hashing, role guards
│   ├── document_processor.py # PDF/DOCX/TXT text extraction + chunking
│   ├── ai_engine.py          # LLM analysis (Anthropic) + rule-based fallback engine
│   ├── semantic_search.py    # TF-IDF cosine-similarity search over chunks
│   ├── report_generator.py   # PDF (reportlab) and DOCX (python-docx) report builders
│   └── routers/
│       ├── auth_router.py        # /auth  register, login, me
│       ├── documents_router.py   # /documents  upload, analyze, list, delete
│       ├── search_router.py      # /search  semantic search + optional LLM Q&A
│       ├── reports_router.py     # /reports  PDF/DOCX download
│       ├── dashboard_router.py   # /dashboard  insights/stats
│       └── admin_router.py       # /admin  user mgmt, system stats, audit logs
├── frontend/
│   └── streamlit_app.py      # Full UI: login, upload, dashboard, search
├── sample_docs/              # Sample contracts for testing (incl. a high-risk one)
├── requirements.txt
├── Dockerfile / docker-compose.yml
├── .env.example
└── README.md
```

### Why a dual AI engine?
`ai_engine.py` tries an LLM (Anthropic Claude) first for extraction, risk detection, and
summarization via a strict JSON schema prompt. If no `ANTHROPIC_API_KEY` is configured
(or the call fails), it transparently falls back to a **rule-based/regex + keyword
engine** so the whole system is still fully functional, testable, and demoable offline.
Every risk finding — from either engine — carries a `category`, `severity`,
`confidence` score, and `explanation`, satisfying the explainability requirement.

### Data flow
1. User uploads a file → validated (type/size) → stored on disk, row created in `documents`.
2. `/documents/{id}/analyze` extracts text, chunks it (for search), runs the AI engine,
   persists structured `Analysis` + `RiskFinding` rows, computes a weighted risk score.
3. `/search` runs TF-IDF similarity search across stored chunks for natural-language
   queries like "show payment terms". `/search/ask` (bonus) does LLM-based RAG Q&A.
4. `/reports/{id}/pdf` and `/docx` render the stored analysis into downloadable reports.
5. `/dashboard` aggregates stats (avg risk score, high-risk doc count, top risk types).
6. `/admin/*` (admin role only) manages users and views audit logs.

## Setup

### 1. Clone & install
```bash
git clone <your-repo-url>
cd contract-analyzer
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```
Edit `.env`:
- `JWT_SECRET_KEY` — set to a long random string.
- `ANTHROPIC_API_KEY` — optional. Leave blank to run entirely on the rule-based engine.

### 3. Run the backend
```bash
uvicorn app.main:app --reload --port 8000
```
API docs (Swagger UI) at `http://localhost:8000/docs`.

### 4. Run the frontend
```bash
streamlit run frontend/streamlit_app.py
```
Opens at `http://localhost:8501`. The first registered user automatically becomes admin.

### 5. Docker (optional / bonus)
```bash
docker compose up --build
```

## Verified Workflow

The following flow was tested end-to-end against `sample_docs/sample_high_risk_vendor.txt`:

1. `POST /auth/register` → `POST /auth/login` → JWT issued.
2. `POST /documents/upload` → document stored, status `uploaded`.
3. `POST /documents/{id}/analyze` → correctly identified contract type, parties, dates,
   and flagged 5 real risks (sole-discretion clause, unlimited liability, vague
   "reasonable" language, non-refundable payments, rights waiver) with severities and
   confidence scores — risk score computed at 50.7/100.
4. `GET /dashboard` → aggregate stats reflected the new document/risk.
5. `POST /search` → natural-language query "payment terms" returned the relevant chunk.
6. `GET /reports/{id}/pdf` and `/docx` → both downloaded as valid, well-formed files.
7. `GET /admin/stats` → correct user/document/audit counts (admin-only).

## Sample Documents
- `sample_docs/sample_nda.txt` — a clean, low-risk mutual NDA.
- `sample_docs/sample_high_risk_vendor.txt` — deliberately contains multiple red flags
  (unlimited liability, non-refundable payments, sole-discretion clauses, rights waiver)
  to demonstrate the risk detector.

## Extending This Project
Ideas to push this toward "production-ready" and pick up bonus points:
- **RAG-based Q&A**: `search_router.ask_document` already stubs this out (LLM required) —
  swap the naive context window for a proper vector store (ChromaDB/FAISS) over chunks.
- **OCR**: add `pytesseract` + `pdf2image` in `document_processor.py` for scanned PDFs.
- **Multi-language**: prompt the LLM to detect/translate, or add `langdetect`.
- **Clause comparison / version diffing**: diff two `Analysis` rows for the same document.
- **Email delivery**: send generated reports via SMTP from `reports_router.py`.
- **Better semantic search**: swap TF-IDF for real embeddings if you enable an LLM provider.

## Tech Stack
Python, FastAPI, SQLAlchemy + SQLite, JWT auth (python-jose + passlib), pypdf,
python-docx, Anthropic Claude API (optional), scikit-learn (TF-IDF search), reportlab,
Streamlit, Docker.

## Disclaimer
This tool assists with contract review but does not constitute legal advice. All
AI-generated output should be reviewed by a qualified attorney before being relied upon.
