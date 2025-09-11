from typing import Optional
from app.config import get_settings
from app.core.index_manager import IndexManager
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from app.schemas.ai_schemas.chat.workflow_manager_context import WorkflowManagerContext
from llama_index.core.agent.workflow import AgentWorkflow
from app.core.logging_config import get_logger
from app.plugins.datetime import get_tools as get_datetime_tools
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
        self.disable_tools = context.disable_tools

    # def wrap_tool_with_context(tool, initial_state):
    #     def tool_with_context(input: dict):
    #         # Inject initial state into the input
    #         input_with_context = {
    #             **input,
    #             "context": initial_state,
    #         }
    #         return tool(input_with_context)

    #     return tool_with_context

    def _fallback_system_prompt(self) -> str:
        """Project → workspace → global default."""
        project_prompt = getattr(self.project, "system_prompt", None)
        if project_prompt:
            return str(project_prompt)

        workspace = getattr(self.project, "workspace", None)
        workspace_prompt = (
            getattr(workspace, "system_prompt", None) if workspace else None
        )
        if workspace_prompt:
            return str(workspace_prompt)

        return get_settings().default_system_prompt

    def _resolve_system_prompt(self) -> str:
        """Use explicit ID if available, else fallback chain."""
        if self.system_prompt_id:
            prompt_service = PromptService(self.db_session)
            prompt = prompt_service.get_prompt_by_id_or_prompt_id(self.system_prompt_id)
            if prompt:
                self.logger.info(
                    f"Using system prompt from prompt ID: {self.system_prompt_id}"
                )
                return str(prompt.prompt)

            self.logger.warning(
                f"System prompt with ID {self.system_prompt_id} not found, falling back to defaults"
            )

        return self._fallback_system_prompt()

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
        system_prompt_text: str = self._resolve_system_prompt()

        if self.disable_tools:
            tools = []
        else:
            tools = await self.get_tools()
            tools.append(query_tool)

        self.logger.info(f"Creating workflow with {len(tools)} total tools")

        # Instantiate LLM once
        llm_instance = self.index_manager.llm()

        # Preflight: detect known Ollama models that don't support tools and fail fast
        try:
            model_name = getattr(llm_instance, "model", "")
            provider_name = getattr(self.project, "llm_provider", "").lower()
            if not self.disable_tools and len(tools) > 0 and provider_name == "ollama":
                if isinstance(model_name, str) and (
                    "deepseek-r1" in model_name.lower()
                ):
                    error_msg = (
                        f"Selected Ollama model '{model_name}' does not support tools. "
                        "Disable tools or choose a tool-capable model."
                    )
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
        except Exception as preflight_e:
            # If preflight raised intentionally, bubble it up; otherwise log and continue
            if isinstance(preflight_e, RuntimeError):
                raise
            self.logger.warning(
                f"Tool capability preflight check skipped: {preflight_e}"
            )

        workflow = AgentWorkflow.from_tools_or_functions(
            tools_or_functions=tools,
            # Revise this, the llm should come from the project settings
            llm=llm_instance,
            system_prompt=system_prompt_text,
            initial_state=self.initial_state,
            verbose=True,
        )

        return workflow

    def system_tools(self):
        return [*get_datetime_tools()]

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
