from llama_index.core.tools.function_tool import FunctionTool
from llama_index.core.workflow import Context
from llama_index.core.workflow import JsonSerializer


def debug_tool(ctx: Context, input: dict):
    """
    Debug tool for testing

    Parameters:
        input (dict): The input to the tool

    Returns:
        dict: The input
    """
    print(ctx.to_dict(serializer=JsonSerializer()))
    return {"from_user": input}


def get_tools():
    return [
        FunctionTool.from_defaults(debug_tool),
    ]
