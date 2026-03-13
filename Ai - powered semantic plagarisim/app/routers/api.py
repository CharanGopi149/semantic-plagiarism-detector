from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas import AnalysisResult, AnalyzePayload, SourceTextInput
from app.services.document_loader import SourceDocument, fetch_url_source, load_demo_assignment, load_sample_sources, load_upload
from app.services.plagiarism_engine import PlagiarismEngine

router = APIRouter(prefix="/api", tags=["analysis"])
engine = PlagiarismEngine()


def _has_selected_file(upload: UploadFile | None) -> bool:
    return upload is not None and bool((upload.filename or "").strip())


async def _collect_sources(
    source_texts: list[SourceTextInput],
    source_urls: list[str],
    sample_enabled: bool,
) -> list[SourceDocument]:
    sources = [SourceDocument(name=item.name, text=item.text, origin=item.origin, url=str(item.url) if item.url else None) for item in source_texts]
    for url in source_urls:
        sources.append(await fetch_url_source(url))
    if sample_enabled:
        sources.extend(load_sample_sources())
    return sources


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/sources/library")
async def source_library() -> dict[str, object]:
    sources = load_sample_sources()
    return {
        "demo_assignment": load_demo_assignment(),
        "sources": [
            {
                "name": source.name,
                "origin": source.origin,
                "text": source.text,
                "url": source.url,
            }
            for source in sources
        ],
    }


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_json(payload: AnalyzePayload) -> AnalysisResult:
    sources = await _collect_sources(payload.source_texts, [str(url) for url in payload.source_urls], payload.include_sample_sources)
    if not sources:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one source document, URL, or enable the sample source library.",
        )

    try:
        return engine.analyze(document_title=payload.title, assignment_text=payload.assignment_text, sources=sources)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/analyze-upload", response_model=AnalysisResult)
async def analyze_upload(
    title: Annotated[str, Form()] = "Student Submission",
    assignment_text: Annotated[str | None, Form()] = None,
    assignment_file: Annotated[UploadFile | None, File()] = None,
    source_files: Annotated[list[UploadFile], File()] = [],
    source_urls: Annotated[str | None, Form()] = None,
    use_sample_sources: Annotated[bool, Form()] = False,
) -> AnalysisResult:
    if not _has_selected_file(assignment_file) and not (assignment_text or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide assignment text or upload an assignment file.")

    if _has_selected_file(assignment_file):
        assignment_document = await load_upload(assignment_file, origin="student")
        assignment_text = assignment_document.text

    sources: list[SourceDocument] = []
    for upload in source_files:
        if _has_selected_file(upload):
            sources.append(await load_upload(upload, origin="upload"))

    url_entries = [line.strip() for line in (source_urls or "").splitlines() if line.strip()]
    for url in url_entries:
        sources.append(await fetch_url_source(url))

    if use_sample_sources:
        sources.extend(load_sample_sources())

    if not sources:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload source files, add source URLs, or enable the sample source library.",
        )

    try:
        return engine.analyze(document_title=title, assignment_text=assignment_text or "", sources=sources)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
