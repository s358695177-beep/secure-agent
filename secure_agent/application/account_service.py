from secure_agent.ports.account import AccountProfile, AccountQueryPort


class AccountService:
    def __init__(self, account_query: AccountQueryPort) -> None:
        self._account_query = account_query

    def get_current_profile(
        self,
        access_token: str,
    ) -> AccountProfile:
        return self._account_query.get_current_profile(access_token)