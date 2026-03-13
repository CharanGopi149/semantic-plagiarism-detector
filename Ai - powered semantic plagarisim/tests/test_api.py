from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analysis_endpoint_flags_similarity() -> None:
    payload = {
        "title": "Assignment 1",
        "assignment_text": (
            "Introduction\n"
            "Adaptive learning platforms tailor guidance for students when instructors cannot provide one-on-one support.\n\n"
            "Methodology\n"
            "Smart grids rely on forecasting models to balance variable renewable generation with real-time electricity demand.\n"
        ),
        "source_texts": [
            {
                "name": "Source A",
                "text": (
                    "Introduction\n"
                    "Intelligent tutoring systems personalize instruction by adapting examples and pacing to each learner.\n\n"
                    "Methodology\n"
                    "Smart grids rely on forecasting models to balance variable renewable generation with real-time electricity demand.\n"
                ),
                "origin": "manual",
            }
        ],
        "include_sample_sources": False,
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["flagged_sentences"] >= 1
    classifications = {item["classification"] for item in body["matches"]}
    assert "direct" in classifications or "semantic" in classifications


def test_upload_endpoint_ignores_empty_file_inputs() -> None:
    response = client.post(
        "/api/analyze-upload",
        data={
            "title": "Demo Assignment",
            "assignment_text": (
                "Introduction\n"
                "Smart grids rely on forecasting models to balance variable renewable generation with real-time electricity demand.\n"
            ),
            "use_sample_sources": "true",
        },
        files={
            "assignment_file": ("", b"", "application/octet-stream"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["sources_considered"] >= 1
