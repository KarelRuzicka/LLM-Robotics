import inspect
from pydantic_ai import Tool


def class_name(instance):
    """
    Returns the class name instance.
    """
    return type(instance).__name__

def class_doc(instance):
    """
    Returns the class docstring.
    """
    return type(instance).__doc__ or "No description available."

def methods_as_tools(instance):
    """
    Converts public methods of an instance into Pydantic AI Tools.
    """
    tools = []
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        if not name.startswith('_'):
            tool = Tool(method)
            tools.append(tool)
    return tools
