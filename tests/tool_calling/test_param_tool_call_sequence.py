import util
from util import mock_settings
import path



def test_basic_tool_call(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import agent as a  # type: ignore
    
    
    result = a.agent.run_sync("Go forward 5 steps, then turn left 45 degrees, then step backward 3 steps.")

    messages = result.all_messages()
    tool_calls = util.parse_tool_calls_from_response(messages)

    assert len(tool_calls) == 3,                                            f"Expected exactly three tool calls, but found {len(tool_calls)}."
    tool_names = [call.tool_name for call in tool_calls]
    assert set(tool_names) == {"step_forward", "turn_left", "step_backward"}, f"Expected tool calls to include 'step_forward', 'turn_left', and 'step_backward', but got {tool_names}."
    assert tool_names == ["step_forward", "turn_left", "step_backward"],      f"Expected tool call sequence ['step_forward', 'turn_left', 'step_backward'], but got {tool_names}."
    tool_arg_counts = [len(call.args) for call in tool_calls]  # type: ignore
    assert tool_arg_counts == [1, 1, 1],                                   f"Expected each tool call to have one argument, but got {tool_arg_counts}."
    tool_arg_names = [list(call.args.keys()) for call in tool_calls]  # type: ignore
    assert tool_arg_names == [["steps"], ["degrees"], ["steps"]],          f"Expected tool call arguments to be ['steps'], ['degrees'], and ['steps'], but got {tool_arg_names}."
    tool_arg_values = [list(call.args.values()) for call in tool_calls]  # type: ignore
    assert tool_arg_values == [[5], [45], [3]],                            f"Expected tool call argument values to be [5], [45], and [3], but got {tool_arg_values}."                             
