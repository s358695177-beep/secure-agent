import json

from secure_agent.application.current_account_profile_tool import (
    CurrentAccountProfileTool,
)
from secure_agent.ports.model import ModelPort, ModelResult


class ChatAuthenticationError(Exception):
    pass


class UnsupportedToolError(Exception):
    pass


class ChatService:
    def __init__(
        self,
        model: ModelPort,
        current_account_tool: CurrentAccountProfileTool | None = None,
    ) -> None:
        self._model = model
        self._current_account_tool = current_account_tool

    def chat(
        self,
        message: str,
        access_token: str | None = None,
    ) -> ModelResult:
        tools = None

        if self._current_account_tool is not None:
            tools = [self._current_account_tool.definition]

        first_result = self._model.generate(
            message=message,
            tools=tools,
        )

        if not first_result.tool_calls:
            return first_result

        if len(first_result.tool_calls) != 1:
            raise UnsupportedToolError(
                "当前只允许模型一次调用一个工具"
            )

        tool_call = first_result.tool_calls[0]

        if self._current_account_tool is None:
            raise UnsupportedToolError("没有可执行的工具")

        if tool_call.name != self._current_account_tool.name:
            raise UnsupportedToolError(
                f"不支持的工具：{tool_call.name}"
            )

        try:
            arguments = json.loads(tool_call.arguments)
        except json.JSONDecodeError as error:
            raise UnsupportedToolError(
                "模型生成的工具参数不是合法 JSON"
            ) from error

        if arguments != {}:
            raise UnsupportedToolError(
                "当前账户查询工具不接受参数"
            )

        if access_token is None:
            raise ChatAuthenticationError(
                "缺少 Access Token"
            )

        tool_result = self._current_account_tool.execute(
            access_token
        )

        final_result = self._model.generate(
            message=message,
            tools=tools,
            tool_call=tool_call,
            tool_result=tool_result,
        )

        if final_result.tool_calls:
            raise UnsupportedToolError(
                "模型在工具执行后再次请求调用工具"
            )

        return final_result