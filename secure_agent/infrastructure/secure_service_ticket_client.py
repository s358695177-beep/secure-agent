import httpx

from secure_agent.ports.ticket import RecentTicket, TicketQueryError


class SecureServiceTicketClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def get_my_recent_tickets(
        self,
        access_token: str,
    ) -> list[RecentTicket]:
        try:
            response = httpx.get(
                f"{self._base_url}/tickets/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=5.0,
                trust_env=False,
            )

            response.raise_for_status()

            body = response.json()
            data = body["data"]
            if not isinstance(data, list):
                raise TypeError("工单查询响应的 data 应为列表")
                        
            return [
                RecentTicket(
                    ticket_id=item["ticketId"],
                    status=item["status"],
                    created_at=item["createdAt"],
                    summary=item["summary"],
                )
                for item in data
            ]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise TicketQueryError(
                "SecureService 工单查询失败"
            ) from error