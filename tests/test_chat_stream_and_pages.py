from fastapi.testclient import TestClient

from app.main import app, ragger


def test_chat_page_loads_the_streaming_ui() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "/static/chat.js" in response.text
    assert "문서 채팅" in response.text
    assert "EventSource" in TestClient(app).get("/static/chat.js").text


def test_chat_stream_sends_answer_then_sources(monkeypatch) -> None:
    chunks = [{
        "original_filename": "guide.pdf",
        "stored_filename": "guide.pdf",
        "page": 2,
        "text": "The guide evidence.",
        "similarity_score": 0.91,
    }]
    monkeypatch.setattr(ragger, "search", lambda question, top_k: chunks)
    monkeypatch.setattr("app.main._generate_answer", lambda question, found: "Live grounded answer")

    response = TestClient(app).post("/chat/stream", json={"question": "What does it say?"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'event: answer\ndata: {"text": "Live grounded answer"}' in response.text
    assert 'event: sources\ndata: [{"original_filename": "guide.pdf"' in response.text
    assert "event: done" in response.text


def test_chat_stream_rejects_blank_question() -> None:
    response = TestClient(app).post("/chat/stream", json={"question": "   "})

    assert response.status_code == 422
