import logging
import os
import re
from typing import List, Optional, Union

from llama_index.core.prompts import PromptTemplate
from llama_index.core.settings import Settings
from app.core.index_manager import IndexManager
from app.models.project import Project
from app.schemas.ai_schemas.chat.chat_api_message import ChatAPIMessage
from sqlalchemy.orm import Session
from app.core.logging_config import get_logger

logger = get_logger()


class SuggestNextQuestionsService:
    """
    Suggest the next questions that user might ask based on the conversation history.
    """

    def __init__(self, db_session: Session, project: Project):
        self.db_session = db_session
        self.project = project
        self.prompt = PromptTemplate(
            r"""
You're a helpful assistant! Your task is to suggest the next questions that user might interested in to keep the conversation going.
Here is the conversation history
---------------------
{conversation}
---------------------
Given the conversation history, please give me 3 questions that user might ask next!
Your answer should be wrapped in three sticks without any index numbers and follows the following format:
\`\`\`
<question 1>
<question 2>
<question 3>
\`\`\`
"""
        )

    def get_configured_prompt(self) -> PromptTemplate:
        prompt = os.getenv("NEXT_QUESTION_PROMPT", None)
        if not prompt:
            return self.prompt
        return PromptTemplate(prompt)

    async def suggest_next_questions_all_messages(
        self,
        messages: List[ChatAPIMessage],
    ) -> Optional[List[str]]:
        """
        Suggest the next questions that user might ask based on the conversation history.
        """
        prompt_template = self.get_configured_prompt()

        try:
            # Reduce the cost by only using the last two messages
            last_user_message = None
            last_assistant_message = None
            for message in reversed(messages):
                if message.role == "user":
                    last_user_message = f"User: {message.content}"
                elif message.role == "assistant":
                    last_assistant_message = f"Assistant: {message.content}"
                if last_user_message and last_assistant_message:
                    break
            conversation: str = f"{last_user_message}\n{last_assistant_message}"

            # Call the LLM and parse questions from the output
            prompt = prompt_template.format(conversation=conversation)
            llm = IndexManager(self.db_session, self.project).llm()
            output = await llm.acomplete(prompt)
            return self._extract_questions(output.text)

        except Exception as e:
            logger.error(f"Error when generating next question: {e}")
            return None

    def _extract_questions(self, text: str) -> Union[List[str], None]:
        content_match = re.search(r"```(.*?)```", text, re.DOTALL)
        content = content_match.group(1) if content_match else None
        if not content:
            return None
        return [q.strip() for q in content.split("\n") if q.strip()]

    async def run(
        self,
        chat_history: List[ChatAPIMessage],
        response: str,
    ) -> Optional[List[str]]:
        """
        Suggest the next questions that user might ask based on the chat history and the last response.
        """
        messages = [
            *chat_history,
            ChatAPIMessage(role="assistant", content=response),  # type: ignore
        ]
        return await self.suggest_next_questions_all_messages(messages)
