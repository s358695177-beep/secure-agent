from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RecentTicket:
    ticket_id: int
    status: str
    created_at: str
    summary: str


class TicketQueryError(Exception):
    pass


class TicketQueryPort(Protocol):
    def get_my_recent_tickets(
        self,
        access_token: str,
    ) -> list[RecentTicket]:
        ...