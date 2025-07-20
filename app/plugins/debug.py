from llama_index.core.tools.function_tool import FunctionTool
from llama_index.core.workflow import Context
from llama_index.core.workflow import JsonSerializer
import logging


def debug_tool(ctx: Context, input: dict):
    """
    Debug tool for testing

    Parameters:
        input (dict): The input to the tool

    Returns:
        dict: The input
    """
    logger = logging.getLogger("uvicorn")
    logger.info(f"🔍 DEBUG TOOL CALLED with input: {input}")
    logger.info(f"🔍 DEBUG TOOL CONTEXT: {ctx.to_dict(serializer=JsonSerializer())}")
    return {"from_user": input, "debug_info": "Tool executed successfully"}


def echo_tool(ctx: Context, message: str):
    """
    Simple echo tool for testing tool execution

    Parameters:
        message (str): The message to echo

    Returns:
        dict: Echoed message with timestamp
    """
    logger = logging.getLogger("uvicorn")
    logger.info(f"🔊 ECHO TOOL CALLED with message: {message}")
    return {"echo": message, "status": "success"}


def get_tools():
    """Get debug tools for testing."""
    return [
        FunctionTool.from_defaults(
            fn=debug_tool,
            name="debug_tool",
            description="A debug tool for testing tool execution. Pass any input and it will return it with debug info.",
        ),
        FunctionTool.from_defaults(
            fn=echo_tool,
            name="echo_tool",
            description="A simple echo tool that returns the input message. Useful for testing if tools are working.",
        ),
    ]
