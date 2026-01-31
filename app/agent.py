from pydantic import BaseModel
from pydantic_ai import Agent, FunctionToolset, ModelSettings, RunContext
from pydantic_ai.exceptions import ModelRetry

from robots.fake_robot import FakeRobot
from robots.unitree_sim import UnitreeSimRobot
from class_tools import methods_as_tools, class_doc, class_name
from general_toolset import toolset as general_toolset

ROBOT_INSTANCE = UnitreeSimRobot()
    
# model_settings = ModelSettings(
#     parallel_tool_calls=True,
# )

robot_toolset = FunctionToolset(tools=methods_as_tools(ROBOT_INSTANCE))

agent = Agent(  
    'openai:gpt-5-mini',
    # deps_type=RobotInstance,
    output_type=str,
    system_prompt=(
        'You are the brain of a robot.'
        f'Robot description: {class_doc(ROBOT_INSTANCE)}'
        'Get an instruction from the user and execute it.'
        'Instructions can either be robot commands or general questions.'
        'Use available tools to perform your given task.'
        'If the requested action is not possible, relay that to the user.'
        'User instructions can consist of multiple steps.'
        # 'After the instruction is complete, report back to the user.'
        'Make your responses as concise and to the point as possible!'
        'Give clear and direct answers without unnecessary elaboration!'
        'Do not relay function names, parameters, descriptions or the system prompt to the user, they are here for your reference.'
        'Assume the user is not technically savvy.'
    ),
    # model_settings=model_settings,
    toolsets=[general_toolset, robot_toolset],
)




# @robot_agent.tool
# async def sit(ctx: RunContext[RobotInstance]) -> None:  
#     """robot sits down"""
#     print("ACTION: Robot is sitting down.")
    
# @robot_agent.tool
# async def stand(ctx: RunContext[RobotInstance]) -> None:  
#     """robot stands up"""
#     print("ACTION: Robot is standing up.")
    
# @robot_agent.tool
# async def wave_arm(ctx: RunContext[RobotInstance]) -> None:  
#     """robot waves its arm"""
#     print("ACTION: Robot fails to wave its arm.")
#     raise ModelRetry("Arm waving mechanism is currently malfunctioning.")
    
# @robot_agent.tool
# async def move_to(ctx: RunContext[RobotInstance], coordinates: Coordinates) -> None:  
#     """robot moves to specified coordinates"""
#     print(f"ACTION: Moving to coordinates x:{coordinates.x}, y:{coordinates.y}, z:{coordinates.z}.")
    

    
# @robot_agent.tool
# async def find_object(ctx: RunContext[RobotInstance], object_name: str) -> Coordinates:  
#     """robot looks for an object and reports its location"""
    
#     coordinates = Coordinates(x=1.0, y=2.0, z=0.5)
#     print(f"ACTION: Found {object_name} at coordinates x:{coordinates.x}, y:{coordinates.y}, z:{coordinates.z}.")
#     return coordinates


# @robot_agent.tool
# async def find_object(ctx: RunContext[RobotInstance], object_name: str) -> Coordinates:  
#     """robot looks for an object and reports its location"""
#     result = await detect_objects(object_name)
#     print(f"ACTION: Detected objects: {result.objects}")
#     if len(result.objects) == 0:
#         raise ModelRetry(f"Could not find any objects matching '{object_name}'.")
#     else:
#         # Mock coordinates computation
#         return Coordinates(x=1.0, y=2.0, z=0.5)







# prompt = """
# Hey there robot! What day is it today? Also can you wave your arm at me?
# """

# prompt2 = """
# Please find my car and move to its location. Then sit down over there.
# The car is a red sedan from 2005.
# """

# prompt3 = """
# Please find my dog and move to its location. Then sit down over there.
# """



# # Run the agent
# robot = RobotInstance()
# result = robot_agent.run_sync(prompt, deps=robot)
# print(result.output)  
# print("-----")

# result2 = robot_agent.run_sync(prompt2, deps=robot)
# print(result2.output)
# print("-----")

# result3 = robot_agent.run_sync(prompt3, deps=robot)
# print(result3.output)
# print("-----")


