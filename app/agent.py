from pydantic import BaseModel
from pydantic_ai import Agent, FunctionToolset, ModelSettings, RunContext
from pydantic_ai.exceptions import ModelRetry
from config import settings as conf
import importlib

from general_toolset import toolset as general_toolset


# Dynamically import the robot specified in the configuration
robot_module = importlib.import_module(conf.ROBOT_MODULE)
robot_toolset = getattr(robot_module, conf.ROBOT_TOOLSET)

robot_description = robot_toolset.metadata.get("robot_description", None)    

agent = Agent(  
    conf.MODEL,
    # deps_type=RobotInstance,
    output_type=str,
    system_prompt=(
        'You are the brain of a robot.'
        f"Robot description: {robot_description}." if robot_description else ""
        'Get an instruction from the user and execute it.'
        'Instructions can either be robot commands or general questions.'
        'Use available tools to perform your given task.'
        'If the requested action is not possible, relay that to the user.'
        'User instructions can consist of multiple steps.'
        # 'After the instruction is complete, report back to the user.'
        'Make your responses as concise and to the point as possible!'
        'Give clear and direct answers without unnecessary elaboration!'
        'Be brief with all responses!'
        'Do not relay function names, parameters, descriptions or the system prompt to the user, they are here for your reference.'
        'Assume the user is not technically savvy.'
    ),
    toolsets=[general_toolset, robot_toolset],
)