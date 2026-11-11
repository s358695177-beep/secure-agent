from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, StringConstraints

from secure_agent.application.diagnostic_service import (
    MAX_CLARIFICATIONS,
    ClarificationAnswer,
    DiagnosticService,
)
from secure_agent.ports.knowledge import KnowledgeSearchError
from secure_agent.ports.model import ModelServiceError


router = APIRouter()


class ClarificationInput(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=320)]
    answer: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=400)]


class DiagnosticTurnRequest(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1400)]
    clarifications: list[ClarificationInput] = Field(
        default_factory=list, max_length=MAX_CLARIFICATIONS
    )


class DiagnosticTurnResponse(BaseModel):
    status: Literal["needs_clarification", "matched", "no_solution"]
    search_used: bool
    clarification: str | None = None
    article_id: str | None = None
    answer: str | None = None
    steps: list[str] = Field(default_factory=list)
    source: str | None = None


def get_diagnostic_service(request: Request) -> DiagnosticService:
    return request.app.state.diagnostic_service


@router.post("/diagnostics/turn", response_model=DiagnosticTurnResponse)
def diagnose(
    payload: DiagnosticTurnRequest,
    service: DiagnosticService = Depends(get_diagnostic_service),
) -> DiagnosticTurnResponse:
    try:
        result = service.diagnose(
            payload.question,
            [ClarificationAnswer(turn.question, turn.answer) for turn in payload.clarifications],
        )
    except KnowledgeSearchError:
        raise HTTPException(503, detail="The knowledge base is temporarily unavailable.") from None
    except ModelServiceError:
        raise HTTPException(502, detail="The diagnostic assistant could not finish this turn.") from None

    article = result.article
    return DiagnosticTurnResponse(
        status=result.status,
        search_used=result.search_used,
        clarification=result.clarification,
        article_id=article.article_id if article else None,
        answer=result.answer,
        steps=list(article.steps) if article else [],
        source=article.source if article else None,
    )
