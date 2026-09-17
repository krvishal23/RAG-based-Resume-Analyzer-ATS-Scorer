"""Transparent, deterministic resume checks."""

from __future__ import annotations

import re


def score_resume(text: str) -> dict:
    words = re.findall(r"\b\w+\b", text)
    lower = text.lower()
    checks = [
        ("Readable length", 20, 150 <= len(words) <= 900, "Aim for roughly 150-900 words."),
        ("Contact information", 20, bool(re.search(r"(?:@|\+?\d[\d ()-]{7,})", text)), "Include an email address and phone number."),
        ("Core sections", 20, sum(name in lower for name in ("experience", "education", "skills")) >= 2, "Use clear Experience, Education, and Skills headings."),
        ("Action language", 20, bool(re.search(r"\b(led|built|created|improved|managed|designed|delivered)\b", lower)), "Describe work with strong action verbs."),
        ("Quantified impact", 20, bool(re.search(r"\b\d+(?:%|\+|\s*(?:years?|users?|projects?|months?))\b", lower)), "Add measurable outcomes such as percentages, users, or time saved."),
    ]
    breakdown = [{"criterion": name, "score": points if passed else 0, "max": points, "note": "Pass" if passed else note} for name, points, passed, note in checks]
    return {"total_score": sum(item["score"] for item in breakdown), "word_count": len(words), "breakdown": breakdown}