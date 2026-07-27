import logging

from fastapi.testclient import TestClient

from app.main import RELEVANCE_THRESHOLD, app, ragger


def test_chat_returns_fixed_answer_and_logs_top_score_below_threshold(monkeypatch, caplog) -> None:
    """Low-relevance retrieval never invokes generation or exposes top_score."""
    score = RELEVANCE_THRESHOLD - 0.01
    monkeypatch.setattr(
        ragger,
        "search",
        lambda question, top_k: [
            {
                "original_filename": "weak.pdf",
                "stored_filename": "weak.pdf",
                "page": 1,
                "text": "weak evidence",
                "similarity_score": score,
            }
        ],
    )
    monkeypatch.setattr(
        "app.main._generate_answer",
        lambda question, chunks: (_ for _ in ()).throw(AssertionError("must not generate")),
    )

    with caplog.at_level(logging.INFO, logger="app.main"):
        response = TestClient(app).post("/chat", json={"question": "Unrelated question"})

    assert response.status_code == 200
    assert response.json()["answer"] == "문서에서 답을 찾지 못했습니다."
    assert "top_score" not in response.json()
    assert f"top_score={score:.4f}" in caplog.text
