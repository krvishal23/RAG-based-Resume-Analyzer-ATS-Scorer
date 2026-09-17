"""Small, section-aware chunker used by the local retriever."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeChunk:
    section: str
    text: str


_HEADINGS = {
    "summary": "Summary", "profile": "Summary", "objective": "Summary",
    "experience": "Experience", "work experience": "Experience", "employment": "Experience",
    "education": "Education", "skills": "Skills", "technical skills": "Skills",
    "projects": "Projects", "certifications": "Certifications", "awards": "Awards",
}


def chunk_resume(text: str, max_chars: int = 900) -> list[ResumeChunk]:
    chunks: list[ResumeChunk] = []
    section = "Resume"
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        content = " ".join(buffer).strip()
        for start in range(0, len(content), max_chars):
            piece = content[start : start + max_chars].strip()
            if piece:
                chunks.append(ResumeChunk(section, piece))
        buffer = []

    for line in text.splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        key = clean.lower().rstrip(":")
        if key in _HEADINGS:
            flush()
            section = _HEADINGS[key]
        elif clean:
            buffer.append(clean)
    flush()
    return chunks or [ResumeChunk("Resume", text.strip())]