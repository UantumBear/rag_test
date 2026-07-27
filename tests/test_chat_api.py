from fastapi.testclient import TestClient

from app.main import app, ragger


def test_chat_returns_three_document_sources_without_top_score(monkeypatch) -> None:
    chunks = [
        {
            "original_filename": "guide.pdf",
            "stored_filename": "guide.pdf",
            "page": number,
            "text": f"Evidence passage {number}",
            "similarity_score": 0.95 - number / 100,
        }
        for number in range(1, 4)
    ]
    monkeypatch.setattr(ragger, "search", lambda question, top_k: chunks[:top_k])
    monkeypatch.setattr("app.main._generate_answer", lambda question, found: "Grounded answer")

    response = TestClient(app).post("/chat", json={"question": "What does the guide say?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Grounded answer",
        "sources": [
            {
                "original_filename": "guide.pdf",
                "stored_filename": "guide.pdf",
                "page": number,
                "text": f"Evidence passage {number}",
                "similarity_score": 0.95 - number / 100,
            }
            for number in range(1, 4)
        ],
    }
    assert "top_score" not in response.json()


def test_chat_rejects_blank_questions_and_does_not_call_search(monkeypatch) -> None:
    monkeypatch.setattr(ragger, "search", lambda question, top_k: (_ for _ in ()).throw(AssertionError()))

    response = TestClient(app).post("/chat", json={"question": "   "})

    assert response.status_code == 422


def test_chat_returns_fixed_answer_below_relevance_threshold(monkeypatch) -> None:
    monkeypatch.setattr(
        ragger,
        "search",
        lambda question, top_k: [{"stored_filename": "weak.pdf", "page": 1, "text": "weak", "similarity_score": 0.69}],
    )

    response = TestClient(app).post("/chat", json={"question": "Unrelated question"})

    assert response.status_code == 200
    assert response.json()["answer"] == "문서에서 답을 찾지 못했습니다."
