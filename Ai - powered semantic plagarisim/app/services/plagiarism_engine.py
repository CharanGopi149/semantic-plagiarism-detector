from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np
from scipy.sparse import hstack
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import Normalizer

from app.config import DIRECT_THRESHOLD, SEMANTIC_THRESHOLD, SUSPICIOUS_THRESHOLD, TOP_CANDIDATE_MATCHES
from app.schemas import AnalysisResult, ModelInfo, SectionSummary, SentenceMatch, SourceContribution, SourceDescriptor, SummaryMetrics
from app.services.document_loader import SourceDocument
from app.services.text_processing import extract_sections, flatten_sentences, lexical_similarity, normalize_text


@dataclass(slots=True)
class SentenceUnit:
    section: str
    text: str
    source_name: str
    source_origin: str
    source_url: str | None = None


class PlagiarismEngine:
    """Hybrid analyzer combining lexical overlap and latent semantic similarity."""

    def __init__(self) -> None:
        self.analyzer_name = "Hybrid Semantic Plagiarism Engine"
        self.strategy = "TF-IDF + character n-grams + latent semantic analysis"
        self.vector_space = "sentence-level cosine similarity"

    def analyze(self, document_title: str, assignment_text: str, sources: list[SourceDocument]) -> AnalysisResult:
        student_sections = extract_sections(assignment_text)
        student_sentences = [
            SentenceUnit(section=section_name, text=sentence, source_name=document_title, source_origin="student")
            for section_name, sentence in flatten_sentences(student_sections)
        ]

        source_descriptors: list[SourceDescriptor] = []
        source_sentence_units: list[SentenceUnit] = []
        for source in sources:
            source_sections = extract_sections(source.text)
            flattened = flatten_sentences(source_sections)
            source_descriptors.append(
                SourceDescriptor(
                    name=source.name,
                    origin=source.origin,
                    sentence_count=len(flattened),
                    section_count=len(source_sections),
                    url=source.url,
                )
            )
            source_sentence_units.extend(
                SentenceUnit(
                    section=section_name,
                    text=sentence,
                    source_name=source.name,
                    source_origin=source.origin,
                    source_url=source.url,
                )
                for section_name, sentence in flattened
            )

        if not student_sentences:
            raise ValueError("The assignment did not contain enough readable sentences to analyze.")
        if not source_sentence_units:
            raise ValueError("At least one source document is required for comparison.")

        student_texts = [item.text for item in student_sentences]
        source_texts = [item.text for item in source_sentence_units]
        combined_texts = student_texts + source_texts

        tfidf_matrix, semantic_matrix = self._build_vector_spaces(combined_texts)
        student_count = len(student_sentences)
        student_tfidf = tfidf_matrix[:student_count]
        source_tfidf = tfidf_matrix[student_count:]
        student_semantic = semantic_matrix[:student_count]
        source_semantic = semantic_matrix[student_count:]

        tfidf_scores = cosine_similarity(student_tfidf, source_tfidf)
        semantic_scores = cosine_similarity(student_semantic, source_semantic)

        normalized_source_lookup = defaultdict(list)
        for index, sentence in enumerate(source_sentence_units):
            normalized_source_lookup[normalize_text(sentence.text)].append(index)

        matches: list[SentenceMatch] = []
        section_buckets: dict[str, list[SentenceMatch]] = defaultdict(list)
        source_weights = Counter()

        for row_index, student_sentence in enumerate(student_sentences):
            match = self._score_sentence(
                student_sentence=student_sentence,
                source_sentences=source_sentence_units,
                tfidf_row=tfidf_scores[row_index],
                semantic_row=semantic_scores[row_index],
                exact_lookup=normalized_source_lookup,
            )
            matches.append(match)
            section_buckets[student_sentence.section].append(match)

            if match.classification != "original":
                weight = self._classification_weight(match.classification) * (match.similarity_score / 100.0)
                source_weights[match.source_name] += weight

        matches.sort(key=lambda item: (self._classification_rank(item.classification), item.similarity_score), reverse=True)
        sections = self._build_section_summaries(student_sections, section_buckets)
        source_contributions = self._build_source_contributions(source_weights, matches)
        summary = self._build_summary(matches, source_descriptors)

        return AnalysisResult(
            document_title=document_title,
            generated_at=datetime.now(timezone.utc),
            summary=summary,
            sections=sections,
            matches=matches,
            source_contributions=source_contributions,
            sources=source_descriptors,
            model_info=ModelInfo(
                analyzer_name=self.analyzer_name,
                strategy=self.strategy,
                vector_space=self.vector_space,
            ),
        )

    def _build_vector_spaces(self, texts: list[str]) -> tuple[Any, np.ndarray]:
        word_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True, min_df=1)
        char_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)

        word_matrix = word_vectorizer.fit_transform(texts)
        char_matrix = char_vectorizer.fit_transform(texts)
        dense_tfidf = hstack([word_matrix * 0.75, char_matrix * 0.25]).tocsr()

        normalized_tfidf = Normalizer(copy=False).fit_transform(dense_tfidf)
        max_components = min(128, dense_tfidf.shape[0] - 1, dense_tfidf.shape[1] - 1)
        if max_components >= 2:
            reduced = TruncatedSVD(n_components=max_components, random_state=42).fit_transform(dense_tfidf)
            normalized_semantic = Normalizer(copy=False).fit_transform(reduced)
        else:
            normalized_semantic = normalized_tfidf.toarray()

        return normalized_tfidf, normalized_semantic

    def _score_sentence(
        self,
        student_sentence: SentenceUnit,
        source_sentences: list[SentenceUnit],
        tfidf_row: np.ndarray,
        semantic_row: np.ndarray,
        exact_lookup: dict[str, list[int]],
    ) -> SentenceMatch:
        normalized_student = normalize_text(student_sentence.text)
        exact_hits = exact_lookup.get(normalized_student, [])
        candidate_indexes: set[int] = set(exact_hits)

        candidate_strength = (0.6 * semantic_row) + (0.4 * tfidf_row)
        if len(source_sentences) <= TOP_CANDIDATE_MATCHES:
            candidate_indexes.update(range(len(source_sentences)))
        else:
            top_indexes = np.argsort(candidate_strength)[-TOP_CANDIDATE_MATCHES:]
            candidate_indexes.update(int(index) for index in top_indexes.tolist())

        best_index = 0
        best_result: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        for index in candidate_indexes:
            lexical_score = lexical_similarity(student_sentence.text, source_sentences[index].text)
            semantic_score = float(semantic_row[index])
            tfidf_score = float(tfidf_row[index])
            total_score = round((0.55 * semantic_score) + (0.25 * tfidf_score) + (0.20 * lexical_score), 4)
            if total_score > best_result[0]:
                best_index = index
                best_result = (total_score, lexical_score, semantic_score, tfidf_score)

        matched_source = source_sentences[best_index]
        total_score, lexical_score, semantic_score, tfidf_score = best_result
        classification = self._classify(
            exact_hit=best_index in exact_hits,
            lexical_score=lexical_score,
            semantic_score=semantic_score,
            tfidf_score=tfidf_score,
            total_score=total_score,
        )

        return SentenceMatch(
            student_sentence=student_sentence.text,
            student_section=student_sentence.section,
            source_sentence=matched_source.text,
            source_section=matched_source.section,
            source_name=matched_source.source_name,
            source_origin=matched_source.source_origin,
            source_url=matched_source.source_url,
            classification=classification,
            similarity_score=round(total_score * 100, 2),
            lexical_score=round(lexical_score * 100, 2),
            semantic_score=round(semantic_score * 100, 2),
            tfidf_score=round(tfidf_score * 100, 2),
        )

    def _classify(
        self,
        *,
        exact_hit: bool,
        lexical_score: float,
        semantic_score: float,
        tfidf_score: float,
        total_score: float,
    ) -> str:
        if exact_hit or lexical_score >= DIRECT_THRESHOLD or (semantic_score >= 0.90 and tfidf_score >= 0.88):
            return "direct"
        if semantic_score >= SEMANTIC_THRESHOLD or total_score >= 0.76:
            return "semantic"
        if total_score >= SUSPICIOUS_THRESHOLD or lexical_score >= 0.70 or tfidf_score >= 0.74:
            return "suspicious"
        return "original"

    def _build_section_summaries(self, student_sections, section_buckets: dict[str, list[SentenceMatch]]) -> list[SectionSummary]:
        summaries: list[SectionSummary] = []
        for section in student_sections:
            matches = section_buckets.get(section.name, [])
            sentence_count = len(matches)
            direct_count = sum(1 for match in matches if match.classification == "direct")
            semantic_count = sum(1 for match in matches if match.classification == "semantic")
            suspicious_count = sum(1 for match in matches if match.classification == "suspicious")
            flagged_count = direct_count + semantic_count + suspicious_count
            similarity_percentage = round(
                sum(self._classification_weight(match.classification) * (match.similarity_score / 100.0) for match in matches)
                / max(sentence_count, 1)
                * 100,
                2,
            )
            summaries.append(
                SectionSummary(
                    name=section.name,
                    sentence_count=sentence_count,
                    flagged_count=flagged_count,
                    direct_count=direct_count,
                    semantic_count=semantic_count,
                    suspicious_count=suspicious_count,
                    similarity_percentage=similarity_percentage,
                )
            )
        return summaries

    def _build_source_contributions(self, source_weights: Counter, matches: list[SentenceMatch]) -> list[SourceContribution]:
        if not source_weights:
            return []

        source_sections = defaultdict(Counter)
        source_match_counts = Counter()
        for match in matches:
            if match.classification == "original":
                continue
            source_sections[match.source_name][match.source_section] += 1
            source_match_counts[match.source_name] += 1

        total_weight = sum(source_weights.values()) or 1.0
        contributions: list[SourceContribution] = []
        for source_name, weight in source_weights.most_common():
            top_section = source_sections[source_name].most_common(1)[0][0] if source_sections[source_name] else None
            contributions.append(
                SourceContribution(
                    source_name=source_name,
                    origin=next((match.source_origin for match in matches if match.source_name == source_name), "source"),
                    contribution_percentage=round((weight / total_weight) * 100, 2),
                    matched_sentences=source_match_counts[source_name],
                    top_section=top_section,
                )
            )
        return contributions

    def _build_summary(self, matches: list[SentenceMatch], sources: list[SourceDescriptor]) -> SummaryMetrics:
        total_sentences = len(matches)
        direct = [match for match in matches if match.classification == "direct"]
        semantic = [match for match in matches if match.classification == "semantic"]
        suspicious = [match for match in matches if match.classification == "suspicious"]
        flagged = direct + semantic + suspicious
        overall_similarity = round(
            sum(self._classification_weight(match.classification) * (match.similarity_score / 100.0) for match in matches)
            / max(total_sentences, 1)
            * 100,
            2,
        )
        direct_percentage = round(len(direct) / max(total_sentences, 1) * 100, 2)
        semantic_percentage = round(len(semantic) / max(total_sentences, 1) * 100, 2)
        suspicious_percentage = round(len(suspicious) / max(total_sentences, 1) * 100, 2)
        original_percentage = round(100 - (direct_percentage + semantic_percentage + suspicious_percentage), 2)

        return SummaryMetrics(
            overall_similarity_percentage=overall_similarity,
            direct_match_percentage=direct_percentage,
            semantic_match_percentage=semantic_percentage,
            suspicious_percentage=suspicious_percentage,
            original_percentage=max(original_percentage, 0.0),
            total_sentences=total_sentences,
            flagged_sentences=len(flagged),
            sources_considered=len(sources),
        )

    @staticmethod
    def _classification_weight(label: str) -> float:
        return {
            "direct": 1.0,
            "semantic": 0.8,
            "suspicious": 0.55,
            "original": 0.0,
        }[label]

    @staticmethod
    def _classification_rank(label: str) -> int:
        return {
            "original": 0,
            "suspicious": 1,
            "semantic": 2,
            "direct": 3,
        }[label]
