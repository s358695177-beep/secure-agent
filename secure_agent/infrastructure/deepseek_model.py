from typing import Any, cast

from openai import APIError, OpenAI

from secure_agent.ports.model import (
    ModelResult,
    ModelServiceError,
    ToolCall,
    ToolDefinition,
)


class DeepSeekModel:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str,
        system_prompt: str,
        timeout_seconds: float,
        max_retries: int,
        max_tokens: int,
        thinking_type: str,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model_name = model_name
        self._system_prompt = system_prompt
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._max_tokens = max_tokens
        self._thinking_type = thinking_type

    def generate(
        self,
        message: str,
        tools: list[ToolDefinition] | None = None,
        tool_call: ToolCall | None = None,
        tool_result: str | None = None,
    ) -> ModelResult:
        if (tool_call is None) != (tool_result is None):
            raise ValueError(
                "tool_call 和 tool_result 必须同时提供"
            )

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self._system_prompt,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        if tool_call is not None and tool_result is not None:
            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.call_id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": tool_call.arguments,
                                },
                            }
                        ],
                    },
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.call_id,
                        "content": tool_result,
                    },
                ]
            )

        try:
            with OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                max_retries=self._max_retries,
            ) as client:
                response = client.chat.completions.create(
                    model=self._model_name,
                    messages=cast(Any, messages),
                    tools=cast(Any, tools),
                    max_tokens=self._max_tokens,
                    extra_body={
                        "thinking": {
                            "type": self._thinking_type,
                        },
                    },
                )
        except APIError as error:
            raise ModelServiceError(
                "模型服务调用失败"
            ) from error

        choice = response.choices[0]

        tool_calls = tuple(
            ToolCall(
                call_id=item.id,
                name=item.function.name,
                arguments=item.function.arguments,
            )
            for item in (choice.message.tool_calls or [])
        )

        return ModelResult(
            answer=choice.message.content or "",
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls,
        )