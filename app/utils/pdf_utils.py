from io import BytesIO
from pypdf import PdfReader

from app.exceptions import ValidationException


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text_parts = []

        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(text)

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            raise ValidationException("No extractable text found in PDF")

        return full_text
    except ValidationException:
        raise
    except Exception as exc:
        raise ValidationException(f"Failed to parse PDF: {str(exc)}") from exc


def chunk_text(text: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> list[str]:
    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += max(1, chunk_size - chunk_overlap)

    return chunks