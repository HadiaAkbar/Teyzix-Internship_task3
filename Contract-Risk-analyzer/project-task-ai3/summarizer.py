# VERSION: 1.0.2 - HARD RESET CACHE - 2026-07-08
# REMOVED ALL REFERENCES TO PYPDF2 - USING PYPDF ONLY
import io
import os
import pypdf
from docx import Document as DocxDocument
from typing import List, Tuple, Any

# This file will now primarily handle document reading and utility functions.
# AI summarization and analysis logic will be in ai_analyzer.py

def read_file(path: str) -> str:
    ext: str = os.path.splitext(path)[1].lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            text: str = ""
            with open(path, "rb") as f:
                reader: pypdf.PdfReader = pypdf.PdfReader(f)
                for page in reader.pages:
                    extracted: str = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if not text.strip():
                raise ValueError("Could not extract text from PDF.")
            return text
        elif ext == ".docx":
            doc = DocxDocument(path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        else:
            raise ValueError(f"Unsupported file type: '{ext}'. I can only read .txt, .pdf, and .docx! 🚫")
    except FileNotFoundError:
        raise RuntimeError(f"File not found: '{path}'. Please check the path! 🧐")
    except Exception as e:
        raise RuntimeError(f"Could not read file '{path}': {e} 💔")

def generate_txt_bytes(text: str) -> bytes:
    return text.encode("utf-8")

def generate_combined_txt_bytes(sections: List[Tuple[str, str]]) -> bytes:
    parts: List[str] = []
    for title, text in sections:
        parts.append(f"{'=' * 10} {title} {'=' * 10}\n{text}\n")
    return "\n".join(parts).encode("utf-8")

def _draw_wrapped_text(c: Any, text: str, y: float, width: float, height: float, margin: float, font_name: str = "Helvetica", font_size: int = 11, line_height: int = 16) -> float:
    c.setFont(font_name, font_size)
    def new_page() -> float:
        c.showPage()
        c.setFont(font_name, font_size)
        return height - 50 
    sentences: List[str] = [s.strip() for s in text.split(".") if s.strip()]
    if not sentences:
        sentences = [text] if text.strip() else []
    for sentence in sentences:
        line: str = sentence + "."
        words: List[str] = line.split(" ")
        current: str = ""
        for word in words:
            candidate: str = (current + " " + word).strip()
            if c.stringWidth(candidate, font_name, font_size) < width - 2 * margin:
                current = candidate
            else:
                c.drawString(margin, y, current)
                y -= line_height
                if y < 50:
                    y = new_page()
                current = word
        if current:
            c.drawString(margin, y, current)
            y -= line_height
            if y < 50:
                y = new_page()
    return y

def generate_pdf_bytes(text: str) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    buffer: io.BytesIO = io.BytesIO()
    c: canvas.Canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin: int = 40
    y: float = height - 50
    y = _draw_wrapped_text(c, text, y, width, height, margin)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def generate_pdf_bytes_multi(sections: List[Tuple[str, str]]) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    buffer: io.BytesIO = io.BytesIO()
    c: canvas.Canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin: int = 40
    y: float = height - 50
    for i, (title, text) in enumerate(sections):
        if i > 0:
            c.showPage() 
            y = height - 50
        c.setFont("Helvetica-Bold", 13) 
        c.drawString(margin, y, title)
        y -= 24 
        y = _draw_wrapped_text(c, text, y, width, height, margin)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
