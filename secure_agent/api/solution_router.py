from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, StringConstraints

from secure_agent.application.solution_service import SolutionService
from secure_agent.ports.knowledge import KnowledgeSearchError
from secure_agent.ports.model import ModelServiceError


router = APIRouter()


class SolutionCheckRequest(BaseModel):
    question: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=2000,
    )]


class SolutionCheckResponse(BaseModel):
    status: Literal["matched", "no_solution"]
    article_id: str | None = None
    answer: str | None = None
    steps: list[str] = Field(default_factory=list)
    source: str | None = None


def get_solution_service(request: Request) -> SolutionService:
    return request.app.state.solution_service


@router.post("/solutions/check", response_model=SolutionCheckResponse)
def check_solution(
    payload: SolutionCheckRequest,
    service: SolutionService = Depends(get_solution_service),
) -> SolutionCheckResponse:
    try:
        result = service.check(payload.question)
    except KnowledgeSearchError:
        raise HTTPException(503, detail="The knowledge base is temporarily unavailable.") from None
    except ModelServiceError:
        raise HTTPException(502, detail="The model could not evaluate the solutions.") from None

    article = result.article
    if article is None:
        return SolutionCheckResponse(status="no_solution")
    return SolutionCheckResponse(
        status="matched",
        article_id=article.article_id,
        answer=result.answer,
        steps=list(article.steps),
        source=article.source,
    )
