from fastapi.testclient import TestClient

from app.main import app, jobs, ragger


def test_ingest_returns_a_job_id_and_runs_in_background(monkeypatch, tmp_path):
    jobs.clear()
    monkeypatch.setattr("app.main.UPLOAD_DIRECTORY", tmp_path)
    seen = []

    def ingest_many(uploads, upload_directory):
        seen.extend(uploads)
        return {"status": "completed", "files": [], "total_chunks": 0}

    monkeypatch.setattr(ragger, "ingest_many", ingest_many)
    client = TestClient(app)
    response = client.post(
        "/ingest",
        files=[("files", ("one.pdf", b"%PDF-1.4 one", "application/pdf")), ("files", ("two.pdf", b"%PDF-1.4 two", "application/pdf"))],
    )

    assert response.status_code == 202
    assert response.json()["job_id"] in jobs
    assert [name for name, _ in seen] == ["one.pdf", "two.pdf"]
