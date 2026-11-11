from dataclasses import dataclass
from typing import Protocol


class KnowledgeSearchError(Exception):
    pass


@dataclass(frozen=True)
class KnowledgeArticle:
    article_id: str
    symptom: str
    applies_when: str
    steps: tuple[str, ...]
    source: str


class KnowledgeSearchPort(Protocol):
    def search(self, question: str) -> list[KnowledgeArticle]:
        ...
