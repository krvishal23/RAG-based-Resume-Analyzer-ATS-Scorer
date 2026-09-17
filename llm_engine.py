"""Grounded local answer generation without an external API or model download."""

from __future__ import annotations

import re

MODEL_OPTIONS = {"Local extractive assistant": "local-extractive"}
DEFAULT_MODEL_LABEL = next(iter(MODEL_OPTIONS))


class LocalLLM:
    def __init__(self, model_name: str = "local-extractive"):
        self.model_name = model_name

    def load(self) -> None:
        return None

    def generate(self, chunks: list[dict[str, str]], question: str) -> str:
        if not chunks:
            return "I could not find relevant resume content for that question."
        query_terms = set(re.findall(r"[a-z0-9+#.-]+", question.lower()))
        candidates = []
        for chunk in chunks:
            for sentence in re.split(r"(?<=[.!?])\s+", chunk["text"]):
                terms = set(re.findall(r"[a-z0-9+#.-]+", sentence.lower()))
                candidates.append((len(query_terms & terms), sentence.strip(), chunk["section"]))
        candidates.sort(key=lambda item: item[0], reverse=True)
        selected = []
        seen = set()
        for _, sentence, section in candidates:
            if sentence and sentence not in seen:
                selected.append(f"[{section}] {sentence}")
                seen.add(sentence)
            if len(selected) == 4:
                break
        return "Based on the uploaded resume:\n\n" + "\n".join(f"- {item}" for item in selected)