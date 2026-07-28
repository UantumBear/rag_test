from typing import Any

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, BaseMessage

from app.api.chat import resolve_chat_service
from app.main import app
from app.services.chat import ChatService


class RecordingChatModel:
    """테스트 질문을 기록하고 정해진 AI 답변을 반환한다."""

    def __init__(self, answer: str) -> None:
        """테스트에서 반환할 답변을 저장한다.

        Args:
            answer: 모델 호출 결과로 사용할 문자열이다.
        """
        self.answer = answer
        self.received_messages: list[list[BaseMessage]] = []

    def invoke(
        self,
        input: list[BaseMessage],
        config: Any = None,
        **kwargs: Any,
    ) -> AIMessage:
        """전달된 메시지를 기록하고 준비된 AI 메시지를 반환한다.

        Args:
            input: 서비스가 모델에 전달한 메시지 목록이다.
            config: LangChain 호출 설정이며 이 테스트에서는 사용하지 않는다.
            **kwargs: 추가 호출 옵션이며 이 테스트에서는 사용하지 않는다.

        Returns:
            준비된 문자열을 포함한 AI 메시지이다.
        """
        self.received_messages.append(input)
        return AIMessage(content=self.answer)


def test_chat_returns_llm_answer() -> None:
    model = RecordingChatModel("서울입니다.")
    service = ChatService(model)
    app.dependency_overrides[resolve_chat_service] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post("/chat", json={"question": "한국의 수도는?"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "서울입니다."}
    assert model.received_messages[0][0].content == "한국의 수도는?"


def test_chat_rejects_empty_question() -> None:
    service = ChatService(RecordingChatModel("사용되지 않음"))
    app.dependency_overrides[resolve_chat_service] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post("/chat", json={"question": ""})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


def test_chat_returns_503_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post("/chat", json={"question": "안녕하세요?"})

    assert response.status_code == 503
    assert response.json() == {"detail": "LLM 서비스를 사용할 수 없습니다."}
