from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """LLM에 전달할 일반 질문을 표현한다."""

    question: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    """LLM이 생성한 답변을 표현한다."""

    answer: str
