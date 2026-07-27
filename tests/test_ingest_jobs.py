from fastapi.testclient import TestClient

from app.main import app, jobs


def test_get_ingestion_job_returns_full_completed_state() -> None:
    jobs.clear()
    jobs["job-1"] = {
        "job_id": "job-1",
        "status": "completed",
        "progress": 100,
        "files": [
            {
                "original_filename": "guide.pdf",
                "stored_filename": "guide.pdf",
                "status": "completed",
                "chunks": 4,
                "warnings": ["empty final page"],
                "error": None,
            }
        ],
        "total_chunks": 4,
        "created_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:01:00+00:00",
    }

    response = TestClient(app).get("/ingest/job-1")

    assert response.status_code == 200
    assert response.json() == jobs["job-1"]


def test_get_ingestion_job_returns_queued_state_and_404_for_unknown_job() -> None:
    jobs.clear()
    jobs["queued-job"] = {
        "job_id": "queued-job",
        "status": "queued",
        "progress": 0,
        "files": [],
        "total_chunks": 0,
        "created_at": "2026-01-01T00:00:00+00:00",
        "finished_at": None,
    }
    client = TestClient(app)

    queued = client.get("/ingest/queued-job")
    missing = client.get("/ingest/not-a-job")

    assert queued.status_code == 200
    assert queued.json()["status"] == "queued"
    assert queued.json()["progress"] == 0
    assert missing.status_code == 404
