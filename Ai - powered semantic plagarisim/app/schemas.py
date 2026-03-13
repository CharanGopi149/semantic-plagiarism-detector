from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SourceTextInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1)
    origin: Literal["manual", "upload", "sample", "url"] = "manual"
    url: HttpUrl | None = None


class AnalyzePayload(BaseModel):
    title: str = Field(default="Student Submission", max_length=160)
    assignment_text: str = Field(..., min_length=1)
    source_texts: list[SourceTextInput] = Field(default_factory=list)
    source_urls: list[HttpUrl] = Field(default_factory=list)
    include_sample_sources: bool = False


class SourceDescriptor(BaseModel):
    name: str
    origin: str
    sentence_count: int
    section_count: int
    url: str | None = None


class SentenceMatch(BaseModel):
    student_sentence: str
    student_section: str
    source_sentence: str
    source_section: str
    source_name: str
    source_origin: str
    source_url: str | None = None
    classification: Literal["direct", "semantic", "suspicious", "original"]
    similarity_score: float
    lexical_score: float
    semantic_score: float
    tfidf_score: float


class SectionSummary(BaseModel):
    name: str
    sentence_count: int
    flagged_count: int
    direct_count: int
    semantic_count: int
    suspicious_count: int
    similarity_percentage: float


class SourceContribution(BaseModel):
    source_name: str
    origin: str
    contribution_percentage: float
    matched_sentences: int
    top_section: str | None = None


class SummaryMetrics(BaseModel):
    overall_similarity_percentage: float
    direct_match_percentage: float
    semantic_match_percentage: float
    suspicious_percentage: float
    original_percentage: float
    total_sentences: int
    flagged_sentences: int
    sources_considered: int


class ModelInfo(BaseModel):
    analyzer_name: str
    strategy: str
    vector_space: str


class AnalysisResult(BaseModel):
    document_title: str
    generated_at: datetime
    summary: SummaryMetrics
    sections: list[SectionSummary]
    matches: list[SentenceMatch]
    source_contributions: list[SourceContribution]
    sources: list[SourceDescriptor]
    model_info: ModelInfo
