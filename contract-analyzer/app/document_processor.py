import os
from pypdf import PdfReader
import docx
import warnings

warnings.filterwarnings('ignore')

# Try to import pytesseract for OCR support
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class UnsupportedFileType(Exception):
    pass


def extract_text(file_path: str, file_type: str) -> str:
    file_type = file_type.lower()
    try:
        if file_type == ".pdf":
            return _extract_pdf(file_path)
        elif file_type == ".docx":
            return _extract_docx(file_path)
        elif file_type == ".txt":
            return _extract_txt(file_path)
        else:
            raise UnsupportedFileType(f"Unsupported file type: {file_type}")
    except Exception as e:
        if isinstance(e, UnsupportedFileType):
            raise e
        raise Exception(f"Failed to extract text from {file_type} file: {str(e)}")


def _extract_pdf(path: str) -> str:
    """Extract text from PDF. NEW: Falls back to OCR if text extraction yields minimal content."""
    try:
        reader = PdfReader(path)
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        extracted_text = "\n".join(text_parts).strip()
        
        # NEW: If very little text extracted, attempt OCR
        if len(extracted_text) < 100 and HAS_OCR:
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(path)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img) + "\n"
                
                if len(ocr_text) > len(extracted_text):
                    extracted_text = ocr_text.strip()
            except Exception:
                pass  # OCR failed, use extracted text
        
        return extracted_text
    except Exception as e:
        raise Exception(f"PDF extraction error: {str(e)}")


def _extract_docx(path: str) -> str:
    try:
        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs).strip()
    except Exception as e:
        raise Exception(f"DOCX extraction error: {str(e)}")


def _extract_txt(path: str) -> str:
    try:
        # Try common encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read().strip()
            except UnicodeDecodeError:
                continue
        # Fallback to ignore errors if all encodings fail
        with open(path, "r", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        raise Exception(f"TXT extraction error: {str(e)}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Split text into overlapping chunks for semantic search / long-doc handling."""
    if not text or not text.strip():
        return []
    
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            break
        if end >= len(words):
            break
    return chunks if chunks else [text]


def validate_file(filename: str, contents: bytes, max_mb: int, allowed_ext: set) -> tuple:
    # 1. Check Extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_ext:
        return False, f"File type '{ext}' not supported. Allowed: {', '.join(allowed_ext)}"
    
    # 2. Check Size
    size_bytes = len(contents)
    if size_bytes > max_mb * 1024 * 1024:
        return False, f"File exceeds max size of {max_mb}MB"
    if size_bytes == 0:
        return False, "File is empty"

    return True, ""
