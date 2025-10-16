from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, List, Tuple

STOPWORDS: set[str] = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "from",
    "have",
    "will",
    "your",
    "into",
    "about",
    "there",
    "which",
    "their",
    "would",
    "these",
    "could",
    "should",
    "while",
    "where",
    "also",
    "because",
    "been",
    "being",
    "over",
    "once",
    "after",
    "before",
    "just",
    "like",
    "when",
    "then",
    "into",
    "than",
    "through",
    "each",
    "more",
    "some",
    "many",
    "much",
}


def summarize_text(text: str, max_sentences: int = 2, max_length: int = 320) -> str:
    """Return a lightweight summary by selecting the first sentences."""
    stripped = text.strip()
    if not stripped:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", stripped)
    summary = " ".join(sentences[:max_sentences])
    summary = summary.strip()
    if len(summary) > max_length:
        summary = summary[: max_length - 1].rsplit(" ", 1)[0] + "…"
    return summary


def extract_keywords(
    text: str, top_k: int = 5, extra_stopwords: Iterable[str] | None = None
) -> List[str]:
    """Very small keyword extractor based on frequency filtering."""
    if not text:
        return []

    stopwords = STOPWORDS.copy()
    if extra_stopwords:
        stopwords.update(word.lower() for word in extra_stopwords)

    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-]+\b", text.lower())
    candidates = [
        token for token in tokens if len(token) > 3 and token not in stopwords
    ]
    if not candidates:
        return []

    counts = Counter(candidates)
    return [word for word, _ in counts.most_common(top_k)]


def build_summary_and_tags(
    title: str, content: str | None
) -> Tuple[str, List[str]]:
    """Generate a summary and keyword tags using title and content."""
    base_text = " ".join(filter(None, [title.strip(), (content or "").strip()])).strip()
    if not base_text:
        return "", []

    summary = summarize_text(base_text)
    tags = extract_keywords(base_text, extra_stopwords=[word for word in title.lower().split()])
    return summary, tags
