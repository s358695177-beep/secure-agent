from fastapi import HTTPException, Request

from secure_agent.application.chat_service import ChatService


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service

def extract_access_token(
    authorization: str | None,
) -> str | None:
    if authorization is None:
        return None

    scheme, separator, token = authorization.partition(" ")

    if (
        scheme.lower() != "bearer"
        or not separator
        or not token.strip()
    ):
        raise HTTPException(
            status_code=401,
            detail="Authorization 请求头格式错误",
        )

    return token.strip()