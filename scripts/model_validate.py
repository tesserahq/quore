# Local dev: poetry run python

from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.tools import FunctionTool
import asyncio


def echo(text: str) -> str:
    """Return the provided text unchanged."""
    return text


echo_tool = FunctionTool.from_defaults(
    fn=echo,
    name="echo",
    description="Echo back the provided text as-is.",
)

llm = Ollama(model="deepseek-r1:8b")

workflow = AgentWorkflow.from_tools_or_functions(
    tools_or_functions=[echo_tool],
    llm=llm,
    system_prompt="You're a helpful assistant that can search the web for information.",
)


async def main():
    r = await workflow.run(user_msg="What's the current stock price of NVIDIA?")
    print(r)


asyncio.run(main())
