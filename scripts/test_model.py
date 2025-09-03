# Local dev: poetry run python

from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import AgentWorkflow
import asyncio
from typing import Any, AsyncGenerator, Union

llm = Ollama(model="deepseek-r1:8b")

workflow = AgentWorkflow.from_tools_or_functions(
    tools_or_functions=[],
    llm=llm,
    system_prompt="You're a helpful assistant that can search the web for information.",
)


async def main():
    r = await workflow.run(user_msg="What's the current stock price of NVIDIA?")
    print(r)


asyncio.run(main())
