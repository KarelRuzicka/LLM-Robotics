import util
from util import mock_settings
import path



def test_basic_tool_call(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import agent as a  # type: ignore
    

    result = a.agent.run_sync("Hello, what is your name?")

    messages = result.all_messages()
    tool_calls = util.parse_tool_calls_from_response(messages)

    assert len(tool_calls) == 0,                                            f"Expected no tool calls, but found {len(tool_calls)}."
