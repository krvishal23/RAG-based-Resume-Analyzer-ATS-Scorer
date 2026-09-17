"""Text extraction for the resume formats supported by the UI."""

from __future__ import annotations

import io
import re
import zipfile
from html import unescape

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def _read_bytes(uploaded_file) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()
    if hasattr(uploaded_file, "read"):
        return uploaded_file.read()
    return bytes(uploaded_file)


def _pdf_text(data: bytes) -> str:
    if PdfReader is not None:
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raw = data.decode("latin-1", errors="ignore")
    strings = re.findall(r"\(([^()]*)\)\s*Tj", raw) or re.findall(r"\(([^()]*)\)", raw)
    return "\n".join(re.sub(r"\\([\\()])", r"\1", value) for value in strings)


def _docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    xml = re.sub(r"</w:p>|</w:tab>|<w:br[^>]*/>", "\n", xml)
    return unescape(re.sub(r"<[^>]+>", "", xml))


def extract_text(uploaded_file) -> str:
    """Return normalized text from a Streamlit UploadedFile or file-like object."""
    name = getattr(uploaded_file, "name", "").lower()
    data = _read_bytes(uploaded_file)
    if name.endswith(".docx"):
        text = _docx_text(data)
    elif name.endswith(".pdf"):
        text = _pdf_text(data)
    else:
        text = data.decode("utf-8-sig", errors="replace")
    return re.sub(r"[ \t]+", " ", text).strip()