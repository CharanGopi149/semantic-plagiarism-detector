# AI-Powered Semantic Plagiarism Detection System

An end-to-end plagiarism detection application built from scratch with:

- FastAPI backend
- Responsive frontend served by the backend
- Hybrid ML pipeline for exact and semantic similarity detection
- Section-wise analysis and highlighted sentence matches

## Features

- Detects direct copied text and high-overlap near-verbatim content
- Flags paraphrased sentences using a hybrid TF-IDF, character n-gram, and latent semantic analysis pipeline
- Breaks reports down by section such as introduction, methodology, and conclusion
- Highlights suspicious sentences and shows the best matched source sentence
- Supports pasted text, file uploads, and source URLs
- Includes a built-in demo corpus for quick evaluation

## Project Structure

```text
app/
  main.py
  routers/api.py
  services/
static/
templates/
data/
  corpus/
tests/
```

## Setup

1. Create a virtual environment:

```bat
python -m venv .venv
```

2. Install dependencies:

```bat
.venv\Scripts\python -m pip install -r requirements.txt
```

3. Run the application:

```bat
.venv\Scripts\python -m uvicorn app.main:app --reload
```

4. Open the app in your browser:

```text
http://127.0.0.1:8000
```

## API Endpoints

- `GET /api/health`
- `GET /api/sources/library`
- `POST /api/analyze` for JSON payloads
- `POST /api/analyze-upload` for multipart form submissions

## Machine Learning Pipeline

The plagiarism engine compares documents at sentence level using:

- lexical similarity from sequence matching and token overlap
- word-level TF-IDF vectors
- character n-gram TF-IDF vectors
- latent semantic analysis with truncated SVD

These signals are fused into a final similarity score and then classified as:

- `direct`
- `semantic`
- `suspicious`
- `original`

## Testing

```bat
.venv\Scripts\python -m pytest
```

## Deployment

This project is now prepared for deployment in two common ways:

### Render

The repository includes `render.yaml` for a web service deployment.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Health check:

```text
/healthz
```

### Docker

The repository also includes a `Dockerfile` for container-based platforms.

Build locally:

```text
docker build -t semantic-plagiarism-detector .
```

Run locally:

```text
docker run -p 8000:8000 semantic-plagiarism-detector
```

## Notes

- Section detection works best when assignments contain headings such as `Introduction`, `Methodology`, or `Conclusion`.
- URLs are fetched live and converted to readable text when possible.
- The included sample corpus and demo assignment are useful for presentations and project submissions.
