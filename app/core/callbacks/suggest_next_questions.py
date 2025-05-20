import logging
from typing import Any, Optional

from app.core.callbacks.base import EventCallback
from app.models.project import Project
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from app.services.suggest_next_question import (
    SuggestNextQuestionsService,
)
from sqlalchemy.orm import Session

logger = logging.getLogger("uvicorn")


class SuggestNextQuestions(EventCallback):
    """Processor for generating next question suggestions."""

    def __init__(
        self,
        db_session: Session,
        project: Project,
        chat_request: ChatRequest,
        logger: Optional[logging.Logger] = None,
    ):
        self.db_session = db_session
        self.project = project
        self.chat_request = chat_request
        self.accumulated_text = ""
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("uvicorn")

    async def on_complete(self, final_response: str) -> Any:
        if final_response == "":
            self.logger.warning(
                "SuggestNextQuestions is enabled but final response is empty, make sure your content generator accumulates text"
            )
            return None

        questions = await SuggestNextQuestionsService(
            self.db_session, self.project
        ).run(self.chat_request.messages, final_response)
        if questions:
            return {
                "type": "suggested_questions",
                "data": questions,
            }
        return None

    @classmethod
    def from_default(
        cls, db_session: Session, project: Project, chat_request: ChatRequest
    ) -> "SuggestNextQuestions":
        return cls(db_session=db_session, project=project, chat_request=chat_request)
