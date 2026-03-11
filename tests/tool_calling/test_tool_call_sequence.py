import util
from util import mock_settings
import path



def test_basic_tool_call(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import agent as a  # type: ignore
    

    result = a.agent.run_sync("First crouch, then stand up, then wave your right arm.")

    messages = result.all_messages()
    tool_calls = util.parse_tool_calls_from_response(messages)

    assert len(tool_calls) == 3,                                            f"Expected exactly three tool calls, but found {len(tool_calls)}."
    tool_names = [call.tool_name for call in tool_calls]
    assert set(tool_names) == {"crouch", "stand", "wave_right_arm"},        f"Expected tool calls to include 'crouch', 'stand', and 'wave_right_arm', but got {tool_names}."
    assert tool_names == ["crouch", "stand", "wave_right_arm"],             f"Expected tool call sequence ['crouch', 'stand', 'wave_right_arm'], but got {tool_names}."
    tool_args = [call.args for call in tool_calls]
    assert tool_args == [{}, {}, {}],                                       f"Expected all tool call arguments to be empty, but got {tool_args}."
