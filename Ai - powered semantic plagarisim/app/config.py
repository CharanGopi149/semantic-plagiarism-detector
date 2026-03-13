from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"

DIRECT_THRESHOLD = 0.92
SEMANTIC_THRESHOLD = 0.78
SUSPICIOUS_THRESHOLD = 0.62
MIN_SENTENCE_WORDS = 4
TOP_CANDIDATE_MATCHES = 5

SECTION_ALIASES = {
    "abstract": "Abstract",
    "introduction": "Introduction",
    "background": "Background",
    "literature review": "Literature Review",
    "related work": "Related Work",
    "methodology": "Methodology",
    "methods": "Methodology",
    "implementation": "Implementation",
    "analysis": "Analysis",
    "results": "Results",
    "discussion": "Discussion",
    "conclusion": "Conclusion",
    "references": "References",
}

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
