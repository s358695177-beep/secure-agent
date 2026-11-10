import json

from secure_agent.application.account_service import AccountService


class CurrentAccountProfileTool:
    name = "get_current_account_profile"

    definition = {
        "type": "function",
        "function": {
            "name": name,
            "description": "查询当前已认证用户的账户资料",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    }

    def __init__(self, account_service: AccountService) -> None:
        self._account_service = account_service

    def execute(self, access_token: str) -> str:
        profile = self._account_service.get_current_profile(access_token)

        return json.dumps(
            {
                "user_id": profile.user_id,
                "username": profile.username,
                "created_at": profile.created_at,
            },
            ensure_ascii=False,
        )