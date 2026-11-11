import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from secure_agent.api.router import router
from secure_agent.api.solution_router import router as solution_router
from secure_agent.application.solution_service import SolutionService
from secure_agent.infrastructure.opensearch_knowledge import OpenSearchKnowledgeSearch
from secure_agent.application.account_service import AccountService
from secure_agent.application.chat_service import ChatService
from secure_agent.application.current_account_profile_tool import (
    CurrentAccountProfileTool,
)
from secure_agent.application.get_my_recent_tickets_tool import GetMyRecentTicketsTool
from secure_agent.infrastructure.deepseek_model import DeepSeekModel
from secure_agent.infrastructure.secure_service_account_client import (
    SecureServiceAccountClient,
)
from fastapi.responses import FileResponse

from secure_agent.infrastructure.secure_service_ticket_client import SecureServiceTicketClient
from secure_agent.application.ticket_service import TicketService
from secure_agent.api.diagnostic_router import router as diagnostic_router
from secure_agent.application.diagnostic_service import DiagnosticService


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


ticket_client = SecureServiceTicketClient(
    base_url=get_required_env(
        "SECURE_SERVICE_BASE_URL"
    ),
)
ticket_service = TicketService(
    ticket_query=ticket_client,
)
get_my_recent_tickets_tool = GetMyRecentTicketsTool(
    ticket_service=ticket_service,
)

chat_service = ChatService(
    model=model,
    current_account_tool=current_account_tool,
    get_my_recent_tickets_tool=get_my_recent_tickets_tool,
)


app = FastAPI(
    title="Secure Agent",
    description="企业 IT 故障诊断与工单 Agent",
    version="0.1.0",
)

@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(Path(__file__).resolve().with_name("demo.html"))

app.state.chat_service = chat_service

app.include_router(router)

knowledge_search = OpenSearchKnowledgeSearch(
    base_url=get_required_env("OPENSEARCH_BASE_URL"),
)
app.state.solution_service = SolutionService(
    knowledge=knowledge_search,
    model=model,
)
app.state.diagnostic_service = DiagnosticService(
    knowledge=knowledge_search,
    model=model,
)
app.include_router(solution_router)
app.include_router(diagnostic_router)


## startup command: python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload