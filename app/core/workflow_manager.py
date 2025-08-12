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
from app.schemas.ai_schemas.chat.workflow_manager_context import WorkflowManagerContext
from llama_index.core.agent.workflow import AgentWorkflow
from app.core.logging_config import get_logger
from app.plugins.datetime import get_tools as get_datetime_tools
from app.plugins.debug import get_tools as get_debug_tools
from app.services.plugin_service import PluginService
from app.services.prompt_service import PromptService
from llama_index.core.tools import FunctionTool
from mcp.types import Tool as MCPTool
from llama_index.tools.mcp import aget_tools_from_mcp_url
from llama_index.tools.mcp import BasicMCPClient


class WorkflowManager:
    def __init__(
        self,
        context: WorkflowManagerContext,
    ):
        self.db_session = context.db_session
        self.project = context.project
        self.index_manager = IndexManager(context.db_session, context.project)
        self.logger = get_logger()
        self.access_token = context.access_token
        self.system_prompt_id = context.system_prompt_id
        self.initial_state = context.initial_state or {}

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

        self.logger.info("Creating AgentWorkflow")

        query_tool = self.index_manager.get_query_engine_tool()
        self.logger.debug("Query tool loaded")

        # tools_with_context = [
        #     self.wrap_tool_with_context(query_tool, {"token": self.access_token.credentials})
        # ]

        # https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems

        # Determine which system prompt to use
        if self.system_prompt_id:
            # Use the specified system prompt from the prompts table
            prompt_service = PromptService(self.db_session)
            prompt = prompt_service.get_prompt_by_id_or_prompt_id(self.system_prompt_id)
            if prompt:
                system_prompt = prompt.prompt
                self.logger.info(
                    f"Using system prompt from prompt ID: {self.system_prompt_id}"
                )
            else:
                self.logger.warning(
                    f"System prompt with ID {self.system_prompt_id} not found, falling back to defaults"
                )
                system_prompt = (
                    str(self.project.system_prompt)
                    if getattr(self.project, "system_prompt", None)
                    else (
                        str(getattr(self.project.workspace, "system_prompt", None))
                        if getattr(self.project, "workspace", None)
                        and getattr(self.project.workspace, "system_prompt", None)
                        else get_settings().default_system_prompt
                    )
                )
        else:
            # Use project's default system prompt, then workspace, then global default
            system_prompt = (
                str(self.project.system_prompt)
                if getattr(self.project, "system_prompt", None)
                else (
                    str(getattr(self.project.workspace, "system_prompt", None))
                    if getattr(self.project, "workspace", None)
                    and getattr(self.project.workspace, "system_prompt", None)
                    else get_settings().default_system_prompt
                )
            )

        tools = await self.get_tools()
        all_tools = [query_tool, *tools]

        self.logger.info(f"Creating workflow with {len(all_tools)} total tools")

        workflow = AgentWorkflow.from_tools_or_functions(
            tools_or_functions=all_tools,
            # Revise this, the llm should come from the project settings
            llm=self.index_manager.llm(),
            system_prompt=str(system_prompt),
            initial_state=self.initial_state,
        )

        self.logger.info("AgentWorkflow created successfully")
        return workflow

    def system_tools(self):
        return [*get_datetime_tools(), *get_debug_tools()]

    def enabled_plugins(self):
        plugin_service = PluginService(self.db_session)
        return plugin_service.get_project_plugins(self.project.id)

    def _convert_to_function_tool(self, tool: MCPTool) -> FunctionTool:
        """Convert a FastMCP Tool to a LlamaIndex FunctionTool."""

        def tool_function(**kwargs):
            # The actual function implementation will be handled by the MCP client
            self.logger.debug(f"MCP Tool '{tool.name}' called with args: {kwargs}")
            return kwargs

        self.logger.debug(f"Converting MCP tool '{tool.name}' to FunctionTool")

        return FunctionTool.from_defaults(
            fn=tool_function,
            name=tool.name,
            description=tool.description,
        )

    async def get_tools(self):
        enabled_plugins = self.enabled_plugins()
        self.logger.info(f"Loading tools from {len(enabled_plugins)} enabled plugins")

        enabled_tools = []
        for plugin in enabled_plugins:
            self.logger.debug(f"Loading tools from plugin: {plugin.name}")
            try:
                # Get tools from the plugin using the generic MCP method
                plugin_tools = await self.get_mcp_tools_from_plugin(plugin)
                self.logger.info(
                    f"Plugin '{plugin.name}' provided {len(plugin_tools)} tools"
                )
                enabled_tools.extend(plugin_tools)

            except Exception as e:
                self.logger.error(
                    f"Error loading tools from plugin '{plugin.name}': {e}"
                )

        system_tools = self.system_tools()
        self.logger.info(f"Adding {len(system_tools)} system tools")

        all_tools = [*enabled_tools, *system_tools]
        self.logger.info(f"Total tools loaded: {len(all_tools)}")

        # Log all tool names for debugging
        tool_names = [
            tool.metadata.name if hasattr(tool, "metadata") else str(tool)
            for tool in all_tools
        ]
        self.logger.debug(f"Available tools: {tool_names}")

        return all_tools

    async def get_mcp_tools_from_plugin(self, plugin):
        """Get MCP tools from a specific plugin using its endpoint URL and allowed tools."""
        # TODO: Im sure there is a better way to handle this, but for now this works
        # Get the allowed tools from the plugin's tools list
        allowed_tools = []
        if plugin.tools:
            allowed_tools = [
                tool.get("name") for tool in plugin.tools if tool.get("name")
            ]

        if not allowed_tools:
            self.logger.warning(f"No tools found in plugin '{plugin.name}'")
            return []

        self.logger.debug(
            f"Getting tools from plugin '{plugin.name}' at {plugin.endpoint_url}"
        )
        self.logger.debug(f"Allowed tools: {allowed_tools}")

        # Get headers using the credential service if the plugin has credentials
        headers = None
        if plugin.credential_id:
            from app.services.credential_service import CredentialService

            credential_service = CredentialService(self.db_session)
            headers = credential_service.apply_credentials(
                plugin.credential_id, access_token=self.access_token
            )
            self.logger.debug(
                f"Applied credentials for plugin '{plugin.name}': {list(headers.keys())}"
            )

        # Create MCP client with plugin's endpoint URL and credentials
        client = BasicMCPClient(
            plugin.endpoint_url,
            headers=headers,
        )

        # Get tools from the MCP server
        tools = await aget_tools_from_mcp_url(
            plugin.endpoint_url,
            client=client,
            allowed_tools=allowed_tools,
        )

        self.logger.info(
            f"Successfully loaded {len(tools)} tools from plugin '{plugin.name}'"
        )
        return tools
