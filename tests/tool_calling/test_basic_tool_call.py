import util
from util import mock_settings
import path



def test_basic_tool_call(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import agent as a  # type: ignore
    

    result = a.agent.run_sync("Crouch down.")

    messages = result.all_messages()
    tool_calls = util.parse_tool_calls_from_response(messages)

    assert len(tool_calls) == 1,                                            f"Expected exactly one tool call, but found {len(tool_calls)}."
    assert tool_calls[0].tool_name == "crouch",                             f"Expected tool call to be 'crouch', but got '{tool_calls[0].tool_name}'."
    assert tool_calls[0].args in ({}, "{}"),                                f"Expected tool call arguments to be empty, but got {tool_calls[0].args}."
