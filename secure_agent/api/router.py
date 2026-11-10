from fastapi import APIRouter, Depends, Header, HTTPException

from secure_agent.api.dependencies import get_chat_service
from secure_agent.api.schemas.chat import ChatRequest, ChatResponse
from secure_agent.application.chat_service import (
    ChatAuthenticationError,
    ChatService,
    UnsupportedToolError,
)
from secure_agent.ports.account import AccountQueryError
from secure_agent.ports.model import ModelServiceError
from secure_agent.api.dependencies import extract_access_token
from secure_agent.ports.ticket import TicketQueryError

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "secure-agent",
    }


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    authorization: str | None = Header(default=None),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    access_token = extract_access_token(authorization)

    try:
        result = service.chat(
            message=payload.message,
            access_token=access_token,
        )
    except ChatAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="调用业务查询工具需要 Access Token",
        ) from None
    except UnsupportedToolError:
        raise HTTPException(
            status_code=502,
            detail="模型请求了不支持的工具",
        ) from None
    except AccountQueryError:
        raise HTTPException(
            status_code=502,
            detail="Java 业务服务查询失败",
        ) from None
    except ModelServiceError:
        raise HTTPException(
            status_code=502,
            detail="模型服务调用失败，请检查网络、余额或模型配置",
        ) from None
    except TicketQueryError:
        raise HTTPException(
        status_code=502,
        detail="工单查询暂时不可用",
    ) from None

    return ChatResponse(
        answer=result.answer,
        finish_reason=result.finish_reason,
    )