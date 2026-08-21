"""
Simple retrieval layer for the RAG evaluation harness.

Uses TF-IDF + cosine similarity instead of a hosted embedding model, so this
runs fully offline with no API key and no model download. Swap in a real
embedding model (e.g. an embedding endpoint via the Model Gateway pattern,
or a local sentence-transformers model) later if you want to compare
retrieval quality between TF-IDF and dense embeddings -- that comparison
itself is a good thing to be able to talk about.
"""

import os
import re
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    doc_id: str
    text: str


def _chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Chunk on paragraph boundaries, merging short paragraphs up to max_chars."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if current and len(current) + len(p) > max_chars:
            chunks.append(current.strip())
            current = p
        else:
            current = (current + "\n\n" + p).strip()
    if current:
        chunks.append(current.strip())
    return chunks


class Retriever:
    def __init__(self, corpus_dir: str):
        self.chunks: list[Chunk] = []
        for fname in sorted(os.listdir(corpus_dir)):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(corpus_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            # strip the leading "# Title" line from the doc id text, keep it in content
            for chunk in _chunk_text(text):
                self.chunks.append(Chunk(doc_id=fname, text=chunk))

        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([c.text for c in self.chunks])

    def retrieve(self, query: str, k: int = 3) -> list[Chunk]:
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        ranked_idx = scores.argsort()[::-1][:k]
        return [self.chunks[i] for i in ranked_idx if scores[i] > 0]


if __name__ == "__main__":
    r = Retriever(os.path.join(os.path.dirname(__file__), "corpus"))
    print(f"Indexed {len(r.chunks)} chunks across corpus.\n")
    for q in [
        "Why does a BGP route flap?",
        "Tunnel is up but no traffic is passing",
        "device stuck on secondary sim",
    ]:
        print(f"Query: {q}")
        for c in r.retrieve(q, k=2):
            print(f"  [{c.doc_id}] {c.text[:90]}...")
        print()
