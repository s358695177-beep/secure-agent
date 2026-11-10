import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from secure_agent.api.router import router
from secure_agent.application.account_service import AccountService
from secure_agent.application.chat_service import ChatService
from secure_agent.application.current_account_profile_tool import (
    CurrentAccountProfileTool,
)
from secure_agent.infrastructure.deepseek_model import DeepSeekModel
from secure_agent.infrastructure.secure_service_account_client import (
    SecureServiceAccountClient,
)


load_dotenv(
    Path(__file__).parent / ".env",
    encoding="utf-8-sig",
)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"{name} 未配置")

    return value.strip()

##the LLM instance 
model = DeepSeekModel(
    api_key=get_required_env("DEEPSEEK_API_KEY"),
    base_url=get_required_env("DEEPSEEK_BASE_URL"),
    model_name=get_required_env("DEEPSEEK_MODEL"),
    system_prompt=get_required_env("AGENT_SYSTEM_PROMPT"),
    timeout_seconds=float(
        get_required_env("DEEPSEEK_TIMEOUT_SECONDS")
    ),
    max_retries=int(
        get_required_env("DEEPSEEK_MAX_RETRIES")
    ),
    max_tokens=int(
        get_required_env("DEEPSEEK_MAX_TOKENS")
    ),
    thinking_type=get_required_env(
        "DEEPSEEK_THINKING_TYPE"
    ),
)


account_client = SecureServiceAccountClient(
    base_url=get_required_env(
        "SECURE_SERVICE_BASE_URL"
    ),
)


account_service = AccountService(
    account_query=account_client,
)


current_account_tool = CurrentAccountProfileTool(
    account_service=account_service,
)


chat_service = ChatService(
    model=model,
    current_account_tool=current_account_tool,
)


app = FastAPI(
    title="Secure Agent",
    description="企业 IT 故障诊断与工单 Agent",
    version="0.1.0",
)


app.state.chat_service = chat_service
app.state.account_service = account_service


app.include_router(router)