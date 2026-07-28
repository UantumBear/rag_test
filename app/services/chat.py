import os
from functools import lru_cache
from typing import Protocol, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class ChatConfigurationError(RuntimeError):
    """LLM 서비스에 필요한 환경 설정이 없을 때 사용하는 예외이다."""


class ChatState(TypedDict):
    """LangGraph의 질문 처리 단계 사이에서 공유하는 상태이다."""

    question: str
    answer: str


class ChatModel(Protocol):
    """채팅 서비스가 LLM 모델에 요구하는 최소 호출 계약이다."""

    def invoke(self, input: list[BaseMessage]) -> BaseMessage:
        """메시지 목록을 받아 모델이 생성한 메시지를 반환한다.

        Args:
            input: 사용자 질문을 포함한 LangChain 메시지 목록이다.

        Returns:
            모델이 생성한 답변 메시지이다.
        """
        ...


class ChatService:
    """LangGraph로 일반 질문을 LLM에 전달하는 서비스를 제공한다."""

    def __init__(self, model: ChatModel) -> None:
        """LLM 모델을 받아 한 단계짜리 질문 처리 그래프를 준비한다.

        Args:
            model: 메시지 목록을 받아 AI 메시지를 반환하는 LangChain 모델이다.
        """
        self._model = model
        graph = StateGraph(ChatState)
        graph.add_node("generate_answer", self._generate_answer)
        graph.add_edge(START, "generate_answer")
        graph.add_edge("generate_answer", END)
        self._graph = graph.compile()

    def ask(self, question: str) -> str:
        """질문을 그래프에 전달하고 LLM의 텍스트 답변을 반환한다.

        Args:
            question: 사용자가 입력한 일반 질문이다.

        Returns:
            LLM이 생성한 문자열 답변이다.

        Raises:
            TypeError: LLM이 문자열이 아닌 형식의 답변을 반환한 경우 발생한다.
        """
        result = self._graph.invoke({"question": question, "answer": ""})
        return result["answer"]

    def _generate_answer(self, state: ChatState) -> dict[str, str]:
        """현재 질문으로 LLM을 호출해 그래프 상태에 저장할 답변을 만든다.

        Args:
            state: 질문과 현재 답변을 담은 LangGraph 상태이다.

        Returns:
            새로 생성한 답변 필드만 포함한 상태 변경값이다.

        Raises:
            TypeError: LLM 응답 내용이 문자열이 아닌 경우 발생한다.
        """
        response = self._model.invoke([HumanMessage(content=state["question"])])
        if not isinstance(response.content, str):
            raise TypeError("LLM 응답은 문자열이어야 합니다.")
        return {"answer": response.content}


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """환경 변수로 구성한 애플리케이션 공용 채팅 서비스를 반환한다.

    최초 호출 시 서비스를 한 번 생성하고 이후 요청에서는 같은 인스턴스를
    재사용한다.

    Returns:
        OpenAI 채팅 모델과 연결된 공용 채팅 서비스이다.

    Raises:
        ChatConfigurationError: ``OPENAI_API_KEY``가 설정되지 않은 경우
            발생한다.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ChatConfigurationError("OPENAI_API_KEY가 설정되지 않았습니다.")

    model_name = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    model = ChatOpenAI(api_key=api_key, model=model_name)
    return ChatService(model)
