import httpx

from secure_agent.ports.account import AccountProfile, AccountQueryError


class SecureServiceAccountClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def get_current_profile(
        self,
        access_token: str,
    ) -> AccountProfile:
        try:
            response = httpx.get(
                f"{self._base_url}/users/profile",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=5.0,
                trust_env=False,
            )

            response.raise_for_status()

            body = response.json()
            data = body["data"]

            return AccountProfile(
                user_id=data["userId"],
                username=data["username"],
                created_at=data["createdAt"],
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise AccountQueryError(
                "SecureService 账户信息查询失败"
            ) from error