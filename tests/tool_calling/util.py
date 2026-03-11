from pydantic_ai.messages import ModelResponse, ModelMessage, ToolCallPart
from pydantic_ai import ModelResponse, result
import pytest

import path


def parse_tool_calls_from_response(messages: list[ModelMessage]) -> list[ToolCallPart]:
    """
    Helper function to extract all tool calls from the agent's response messages.
    """
    tool_calls: list[ToolCallPart] = []
    for msg in messages:
        if isinstance(msg, ModelResponse):
            for tc in msg.tool_calls:
                # pydantic-ai can store args as JSON string or dict; normalize to dict
                if isinstance(tc.args, str):
                    tc.args = tc.args_as_dict()
                tool_calls.append(tc)

    return tool_calls


@pytest.fixture
def mock_settings():
    
    from config import Settings # type: ignore
    return Settings(ROBOT_MODULE = "robots.test_robot", ROBOT_TOOLSET= "toolset", MODEL = "openai:gpt-5-mini")
        