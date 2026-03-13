from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.config import MIN_SENTENCE_WORDS, SECTION_ALIASES

HEADING_RE = re.compile(r"^(#{1,6}\s+)?([A-Za-z][A-Za-z0-9\s,&/-]{1,80})[:.]?$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
WORD_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass(slots=True)
class SectionChunk:
    name: str
    text: str
    inferred: bool = False


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return collapse_whitespace(lowered)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def lexical_similarity(left: str, right: str) -> float:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0

    sequence_score = SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = set(tokenize(left_norm))
    right_tokens = set(tokenize(right_norm))
    token_score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens) if left_tokens and right_tokens else 0.0

    return round((0.65 * sequence_score) + (0.35 * token_score), 4)


def _looks_like_heading(line: str) -> str | None:
    candidate = collapse_whitespace(line.replace("#", " "))
    if not candidate:
        return None

    normalized = normalize_text(candidate)
    alias = SECTION_ALIASES.get(normalized)
    if alias:
        return alias

    match = HEADING_RE.match(candidate)
    if not match:
        return None

    words = candidate.split()
    if len(words) > 8:
        return None
    if candidate.endswith(".") and len(words) > 3:
        return None
    if candidate.isupper() or candidate.istitle():
        return candidate.title()
    return None


def split_into_sentences(text: str) -> list[str]:
    normalized = collapse_whitespace(text.replace("\n", " "))
    if not normalized:
        return []

    raw_sentences = SENTENCE_SPLIT_RE.split(normalized)
    sentences = [sentence.strip() for sentence in raw_sentences if sentence.strip()]
    filtered = [sentence for sentence in sentences if len(tokenize(sentence)) >= MIN_SENTENCE_WORDS]
    return filtered or sentences


def _chunk_by_paragraphs(paragraphs: list[str]) -> list[SectionChunk]:
    if not paragraphs:
        return []

    if len(paragraphs) <= 2:
        return [SectionChunk(name="Document Overview", text="\n\n".join(paragraphs), inferred=True)]

    labels = ["Opening", "Core Discussion", "Closing"]
    base_size = max(1, len(paragraphs) // 3)
    chunks: list[SectionChunk] = []
    cursor = 0
    for index, label in enumerate(labels):
        if cursor >= len(paragraphs):
            break
        current = paragraphs[cursor:] if index == len(labels) - 1 else paragraphs[cursor : cursor + base_size]
        cursor += base_size
        if current:
            chunks.append(SectionChunk(name=label, text="\n\n".join(current), inferred=True))
    return chunks


def extract_sections(text: str) -> list[SectionChunk]:
    cleaned = text.replace("\r\n", "\n")
    lines = [line.rstrip() for line in cleaned.splitlines()]

    sections: list[SectionChunk] = []
    current_name = "Document Overview"
    current_lines: list[str] = []
    detected_headings = 0

    def flush_current() -> None:
        nonlocal current_lines
        body = collapse_whitespace("\n".join(current_lines))
        if body:
            sections.append(SectionChunk(name=current_name, text=body, inferred=False))
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_lines and current_lines[-1] != "":
                current_lines.append("")
            continue

        heading = _looks_like_heading(stripped)
        if heading:
            flush_current()
            current_name = heading
            detected_headings += 1
            continue

        current_lines.append(stripped)

    flush_current()

    if detected_headings > 0 and sections:
        return sections

    paragraphs = [collapse_whitespace(block) for block in cleaned.split("\n\n") if collapse_whitespace(block)]
    fallback = _chunk_by_paragraphs(paragraphs)
    if fallback:
        return fallback

    body = collapse_whitespace(cleaned)
    return [SectionChunk(name="Document Overview", text=body, inferred=True)] if body else []


def flatten_sentences(sections: Iterable[SectionChunk]) -> list[tuple[str, str]]:
    flattened: list[tuple[str, str]] = []
    for section in sections:
        for sentence in split_into_sentences(section.text):
            flattened.append((section.name, sentence))
    return flattened
