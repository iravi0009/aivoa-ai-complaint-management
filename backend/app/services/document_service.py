from email import policy
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".eml",
}


def extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""

    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages).strip()


def extract_docx(file_bytes: bytes) -> str:
    """Extract paragraphs from a DOCX file."""

    document = Document(BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()


def extract_txt(file_bytes: bytes) -> str:
    """Extract text from a TXT file."""

    return file_bytes.decode(
        "utf-8",
        errors="replace",
    ).strip()


def extract_eml(file_bytes: bytes) -> str:
    """Extract readable content from an EML email."""

    message = BytesParser(
        policy=policy.default
    ).parsebytes(file_bytes)

    parts = []

    # Email metadata
    for header in ["From", "To", "Subject", "Date"]:
        value = message.get(header)

        if value:
            parts.append(f"{header}: {value}")

    # Email body
    if message.is_multipart():
        for part in message.walk():

            if part.get_content_type() != "text/plain":
                continue

            if part.get_content_disposition() == "attachment":
                continue

            try:
                content = part.get_content()
            except Exception:
                content = ""

            if content and content.strip():
                parts.append(content.strip())

    else:
        try:
            content = message.get_content()
        except Exception:
            content = ""

        if content and content.strip():
            parts.append(content.strip())

    return "\n\n".join(parts).strip()


def extract_text(
    filename: str,
    file_bytes: bytes,
) -> str:
    """
    Extract text according to file extension.
    """

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format. "
            "Supported formats: PDF, DOCX, TXT, EML."
        )

    if extension == ".pdf":
        text = extract_pdf(file_bytes)

    elif extension == ".docx":
        text = extract_docx(file_bytes)

    elif extension == ".txt":
        text = extract_txt(file_bytes)

    elif extension == ".eml":
        text = extract_eml(file_bytes)

    else:
        text = ""

    if not text.strip():
        raise ValueError(
            "No readable text was found in the uploaded document."
        )

    return text