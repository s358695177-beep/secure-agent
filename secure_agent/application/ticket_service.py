from secure_agent.ports.ticket import RecentTicket, TicketQueryPort


class TicketService:
    def __init__(self, ticket_query: TicketQueryPort) -> None:
        self._ticket_query = ticket_query

    def get_my_recent_tickets(
        self,
        access_token: str,
    ) -> list[RecentTicket]:
        return self._ticket_query.get_my_recent_tickets(access_token)