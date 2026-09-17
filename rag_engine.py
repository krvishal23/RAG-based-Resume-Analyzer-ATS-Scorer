"""Dependency-free TF-IDF retrieval for resume chunks."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from text_chunker import ResumeChunk


@dataclass(frozen=True)
class RetrievedChunk:
    section: str
    text: str
    score: float


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9+#.-]*", value.lower())


class RAGEngine:
    def __init__(self, embedding_model_name: str | None = None, embedder=None):
        self.chunks: list[ResumeChunk] = []
        self.vectors: list[dict[str, float]] = []
        self.idf: dict[str, float] = {}

    def build_index(self, chunks: list[ResumeChunk]) -> None:
        self.chunks = chunks
        documents = [_tokens(chunk.text) for chunk in chunks]
        count = Counter(token for tokens in documents for token in set(tokens))
        total = max(len(documents), 1)
        self.idf = {token: math.log((total + 1) / (frequency + 1)) + 1 for token, frequency in count.items()}
        self.vectors = [self._vector(tokens) for tokens in documents]

    def _vector(self, tokens: list[str]) -> dict[str, float]:
        frequencies = Counter(tokens)
        vector = {token: (1 + math.log(value)) * self.idf.get(token, 1.0) for token, value in frequencies.items()}
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {token: value / norm for token, value in vector.items()}

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        if not self.chunks:
            return []
        query_vector = self._vector(_tokens(query))
        scored = []
        for chunk, vector in zip(self.chunks, self.vectors):
            score = sum(query_vector.get(token, 0.0) * value for token, value in vector.items())
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [RetrievedChunk(chunk.section, chunk.text, round(score, 4)) for score, chunk in scored[:top_k]]