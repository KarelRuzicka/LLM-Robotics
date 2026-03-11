from unittest import result

import util
from util import mock_settings
import path



def test_param_tool_call(monkeypatch, mock_settings):
    
    monkeypatch.setattr("config.settings", mock_settings)
    
    import agent as a  # type: ignore
    

    result = a.agent.run_sync("Rotate 90 degrees to the right.")

    messages = result.all_messages()
    tool_calls = util.parse_tool_calls_from_response(messages)

    assert len(tool_calls) == 1,                                                            f"Expected exactly one tool call, but found {len(tool_calls)}."
    assert tool_calls[0].tool_name == "turn_right",                                         f"Expected tool call to be 'turn_right', but got '{tool_calls[0].tool_name}'."
    tool_arg_count = len(tool_calls[0].args)  # type: ignore
    assert tool_arg_count == 1,                                                            f"Expected exactly one argument for the tool call but got {tool_arg_count}."
    tool_arg_name = list(tool_calls[0].args.keys())[0]  # type: ignore
    assert tool_arg_name == "degrees",                                                     f"Expected argument name to be 'degrees' but got '{tool_arg_name}'."
    tool_arg_value = list(tool_calls[0].args.values())[0]  # type: ignore
    assert tool_arg_value == 90,                                                            f"Expected argument value to be 90 but got {tool_arg_value}."