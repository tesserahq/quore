import json
from typing import Any, Dict, List, Optional, Type, get_type_hints
from pydantic import BaseModel, create_model
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.core.index_manager import IndexManager
from app.core.plugin_manager.manager import PluginManager
from app.models.project import Project
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from llama_index.core.agent.workflow import AgentWorkflow
from app.core.logging_config import get_logger
from app.plugins.datetime import get_tools as get_datetime_tools
from app.plugins.debug import get_tools as get_debug_tools
from app.services.plugin import PluginService
from llama_index.core.tools import FunctionTool
from llama_index.core.tools.types import DefaultToolFnSchema
from mcp.types import Tool as MCPTool


class WorkflowManager:
    def __init__(
        self,
        db_session: Session,
        project: Project,
        access_token: HTTPAuthorizationCredentials,
    ):
        self.db_session = db_session
        self.project = project
        self.index_manager = IndexManager(db_session, project)
        self.logger = get_logger()
        self.access_token = access_token

    # def wrap_tool_with_context(tool, initial_state):
    #     def tool_with_context(input: dict):
    #         # Inject initial state into the input
    #         input_with_context = {
    #             **input,
    #             "context": initial_state,
    #         }
    #         return tool(input_with_context)

    #     return tool_with_context

    async def create_workflow(
        self, chat_request: Optional[ChatRequest] = None
    ) -> AgentWorkflow:

        query_tool = self.index_manager.get_query_engine_tool()

        # tools_with_context = [
        #     self.wrap_tool_with_context(query_tool, {"token": self.access_token.credentials})
        # ]

        # https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems

        system_prompt = (
            self.project.system_prompt or get_settings().default_system_prompt
        )
        return AgentWorkflow.from_tools_or_functions(
            tools_or_functions=[query_tool, *(await self.get_tools())],
            llm=self.index_manager.llm(),
            system_prompt=str(system_prompt),
        )

    def system_tools(self):
        return [*get_datetime_tools(), *get_debug_tools()]

    def enabled_plugins(self):
        plugin_service = PluginService(self.db_session)
        return plugin_service.get_project_plugins(self.project.id)

    def _convert_to_function_tool(self, tool: MCPTool) -> FunctionTool:
        """Convert a FastMCP Tool to a LlamaIndex FunctionTool."""

        def tool_function(**kwargs):
            # The actual function implementation will be handled by the MCP client
            return kwargs

        # Convert the JSON schema to a DefaultToolFnSchema
        schema = DefaultToolFnSchema(input=json.dumps(tool.inputSchema))

        return FunctionTool.from_defaults(
            fn=tool_function,
            name=tool.name,
            description=tool.description,
            fn_schema=schema,
        )

    async def get_tools(self):
        enabled_plugins = self.enabled_plugins()
        enabled_tools = []
        for plugin in enabled_plugins:
            tools = await PluginManager(db=self.db_session, plugin=plugin).get_tools()
            # Convert each FastMCP Tool to a LlamaIndex FunctionTool
            function_tools = [self._convert_to_function_tool(tool) for tool in tools]
            enabled_tools.extend(function_tools)
        # TODO: Add system tools: why *self.system_tools(),  are not working?
        return [*enabled_tools]

    # async def get_tools(self):
    #     return [*self.system_tools(), *(await self.estate_buddy_mcp_tools())]

    # async def estate_buddy_mcp_tools(self):
    #     # allowed_tools=["tool1", "tool2"]
    #     client = BasicMCPClient(
    #         "http://localhost:8002/mcp/",
    #         headers={"Authorization": f"Bearer {self.access_token.credentials}"},
    #     )
    #     tools = await aget_tools_from_mcp_url(
    #         "http://localhost:8002/mcp/",
    #         client=client,
    #         allowed_tools=[
    #             "list_accounts",
    #             "create_account",
    #             "get_account",
    #             "update_account",
    #             "delete_account",
    #         ],
    #     )
    #     return tools
