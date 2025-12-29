import logging
from typing import Any, Dict, Optional
from llama_index.core.agent.workflow.workflow_events import ToolCallResult, ToolCall
from app.core.callbacks.base import EventCallback
from app.schemas.ai_schemas.agent.agent_run_event import AgentRunEvent
from app.schemas.ai_schemas.agent.agent_run_type import AgentRunEventType


class ToolDebugCallback(EventCallback):
    """
    Debug callback that captures and logs all tool execution details.
    This helps debug MCP tool execution issues.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("uvicorn")
        self.tool_calls: Dict[str, Dict[str, Any]] = {}
        self.call_counter = 0

    async def run(self, event: Any) -> Any:
        """Process events and log tool execution details."""

        self.logger.info(f"ToolDebugCallback: {event}")

        # Log tool calls when they're initiated
        if isinstance(event, ToolCall):
            self.call_counter += 1
            call_id = f"call_{self.call_counter}"

            self.logger.info(f"🔧 TOOL CALL INITIATED: {event.tool_name}")
            self.logger.info(f"Tool call details: {event.model_dump()}")

            # Store tool call for later reference - use available attributes
            tool_call_data = {"tool_name": event.tool_name, "status": "initiated"}

            # Try to get arguments from the tool call data if available
            try:
                if hasattr(event, "tool_call_data") and event.tool_call_data:
                    tool_call_data["args"] = event.tool_call_data
                elif hasattr(event, "arguments") and event.arguments:
                    tool_call_data["args"] = event.arguments
                else:
                    tool_call_data["args"] = "No arguments available"
            except Exception as e:
                self.logger.info(f"Could not extract tool arguments: {e}")
                tool_call_data["args"] = "Error extracting arguments"

            self.tool_calls[call_id] = tool_call_data

            # Create a debug event to send to frontend
            debug_event = AgentRunEvent(
                name="tool_debug",
                msg=f"Tool '{event.tool_name}' called",
                event_type=AgentRunEventType.PROGRESS,
                data={
                    "tool_name": event.tool_name,
                    "args": tool_call_data["args"],
                    "status": "initiated",
                    "call_id": call_id,
                },
            )
            return event, debug_event

        # Log tool call results
        elif isinstance(event, ToolCallResult):
            self.logger.info(f"✅ TOOL CALL RESULT: {event.tool_name}")
            self.logger.info(f"Tool result details: {event.model_dump()}")

            # Find the corresponding tool call by tool name (since we don't have tool_call_id)
            matching_call_id = None
            for call_id, details in self.tool_calls.items():
                if (
                    details["tool_name"] == event.tool_name
                    and details["status"] == "initiated"
                ):
                    matching_call_id = call_id
                    break

            if matching_call_id:
                self.tool_calls[matching_call_id]["status"] = "completed"
                self.tool_calls[matching_call_id][
                    "result"
                ] = event.tool_output.raw_output
                self.tool_calls[matching_call_id]["error"] = getattr(
                    event.tool_output, "error", None
                )

            # Log the actual result content
            try:
                result_content = event.tool_output.raw_output
                self.logger.info(f"Tool '{event.tool_name}' returned: {result_content}")

                # Check for errors
                if hasattr(event.tool_output, "error") and event.tool_output.error:
                    self.logger.error(
                        f"Tool '{event.tool_name}' failed with error: {event.tool_output.error}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Error processing tool result for '{event.tool_name}': {e}"
                )

            # Create a debug event to send to frontend
            debug_event = AgentRunEvent(
                name="tool_debug",
                msg=f"Tool '{event.tool_name}' completed",
                event_type=AgentRunEventType.PROGRESS,
                data={
                    "tool_name": event.tool_name,
                    "result": str(event.tool_output.raw_output),
                    "status": "completed",
                    "error": getattr(event.tool_output, "error", None),
                    "call_id": matching_call_id,
                },
            )
            return event, debug_event

        return event

    async def on_complete(self, final_response: str) -> Any:
        """Log summary of all tool executions."""
        if self.tool_calls:
            self.logger.info(
                f"📊 TOOL EXECUTION SUMMARY: {len(self.tool_calls)} tools executed"
            )
            for call_id, details in self.tool_calls.items():
                self.logger.info(f"  - {details['tool_name']}: {details['status']}")
                if details.get("error"):
                    self.logger.error(f"    Error: {details['error']}")

        return None

    @classmethod
    def from_default(cls, *args: Any, **kwargs: Any) -> "ToolDebugCallback":
        """Create a new instance with default values."""
        return cls()
