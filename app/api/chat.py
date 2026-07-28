from fastapi import APIRouter, Depends, HTTPException, status

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat import (
    ChatConfigurationError,
    ChatService,
    get_chat_service,
)

router = APIRouter(prefix="/chat", tags=["chat"])


def resolve_chat_service() -> ChatService:
    """요청에서 사용할 채팅 서비스를 가져온다.

    Returns:
        애플리케이션에서 재사용하는 채팅 서비스이다.

    Raises:
        HTTPException: LLM 서비스 환경 설정이 준비되지 않은 경우 503 상태로
            변환해 발생시킨다.
    """
    try:
        return get_chat_service()
    except ChatConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM 서비스를 사용할 수 없습니다.",
        ) from error


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(resolve_chat_service),
) -> ChatResponse:
    """일반 질문을 LLM에 전달하고 생성된 답변을 반환한다.

    Args:
        request: 길이가 검증된 사용자 질문이다.
        service: 의존성 주입으로 제공되는 채팅 서비스이다.

    Returns:
        LLM의 텍스트 답변을 담은 응답 모델이다.
    """
    return ChatResponse(answer=service.ask(request.question))
