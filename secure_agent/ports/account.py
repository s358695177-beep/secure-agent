from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AccountProfile:
    user_id: int
    username: str
    created_at: str


class AccountQueryError(Exception):
    pass


class AccountQueryPort(Protocol):
    def get_current_profile(
        self,
        access_token: str,
    ) -> AccountProfile:
        ...