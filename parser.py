import re
import os


def extract_text_from_upload(filepath: str, ext: str) -> str:
    """
    Extract plain text from an uploaded resume file.
    Supports .txt and .pdf formats.
    """
    if ext == '.txt':
        return _read_txt(filepath)
    elif ext == '.pdf':
        return _read_pdf(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _read_txt(filepath: str) -> str:
    """Read and clean a plain-text resume."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return _clean_text(text)


def _read_pdf(filepath: str) -> str:
    """Extract text from a PDF resume using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        pages = [page.get_text() for page in doc]
        doc.close()
        return _clean_text('\n'.join(pages))
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF parsing. "
            "Install it with: pip install PyMuPDF"
        )


def _clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    """
    Lowercase, strip punctuation, split into word tokens,
    and remove common stopwords.
    """
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that',
        'as', 'if', 'not', 'no', 'so', 'up', 'out', 'about',
    }
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if t not in stopwords and len(t) > 1]
