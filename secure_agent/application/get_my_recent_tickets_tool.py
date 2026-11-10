from dataclasses import asdict
import json

from secure_agent.application.ticket_service import TicketService


class GetMyRecentTicketsTool:
    name = "get_my_recent_tickets"

    definition = {
        "type": "function",
        "function": {
            "name": name,
            "description": "列出当前已认证用户最近的工单",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    }

    def __init__(self, ticket_service: TicketService) -> None:
        self._ticket_service = ticket_service

    def execute(self, access_token: str) -> str:
        tickets = self._ticket_service.get_my_recent_tickets(access_token)

        return json.dumps(
            {"tickets": [asdict(ticket) for ticket in tickets]},
            ensure_ascii=False,
        )