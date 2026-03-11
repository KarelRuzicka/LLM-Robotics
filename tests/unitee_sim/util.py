from pydantic_ai.messages import ModelResponse, ModelMessage, ToolCallPart
from pydantic_ai import ModelResponse, result
import pytest

import path


@pytest.fixture
def mock_settings():
    
    from config import Settings # type: ignore
    return Settings(ROBOT_MODULE = "robots.unitree_sim", ROBOT_TOOLSET= "toolset", MODEL = "openai:gpt-5-mini")
        