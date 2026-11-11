from dataclasses import dataclass
from typing import Protocol

ToolDefinition = dict[str, object]

class ModelServiceError(Exception):
    pass

@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: str

@dataclass(frozen=True)
class ModelResult:
    answer: str
    finish_reason: str | None
    tool_calls: tuple[ToolCall, ...] = ()

class ModelPort(Protocol):
    def generate(
        self,
        message: str,
        tools: list[ToolDefinition] | None = None,
        tool_call: ToolCall | None = None,
        tool_result: str | None = None,
        *,
        system_prompt: str | None = None,
        json_mode: bool = False,
    ) -> ModelResult:
        ...