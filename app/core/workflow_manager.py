from typing import Optional

from sqlalchemy.orm import Session
from app.config import get_settings
from app.core.index_manager import IndexManager
from app.models.project import Project
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from llama_index.core.agent.workflow import AgentWorkflow
from app.core.logging_config import get_logger


class WorkflowManager:
    def __init__(self, db_session: Session, project: Project):
        self.db_session = db_session
        self.project = project
        self.index_manager = IndexManager(db_session, project)
        self.logger = get_logger()

    def create_workflow(
        self, chat_request: Optional[ChatRequest] = None
    ) -> AgentWorkflow:

        query_tool = self.index_manager.get_query_engine_tool()

        # https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems

        system_prompt = (
            self.project.system_prompt or get_settings().default_system_prompt
        )
        return AgentWorkflow.from_tools_or_functions(
            tools_or_functions=[query_tool],
            llm=self.index_manager.llm(),
            system_prompt=str(system_prompt),
        )
