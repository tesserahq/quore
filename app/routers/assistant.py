import asyncio
import logging
from typing import Annotated, Any, AsyncGenerator, Dict, Union
import uuid

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from llama_index.core.agent.workflow.workflow_events import (
    AgentInput,
    AgentSetup,
    AgentStream,
)
from llama_index.core.workflow import StopEvent
from app.core.callbacks import (
    EventCallback,
    SourceNodesFromToolCall,
    SuggestNextQuestions,
    ToolDebugCallback,
)
from app.core.callbacks.stream_handler import StreamHandler
from app.core.workflow_manager import WorkflowManager
from app.core.logging_config import get_logger
from app.db import get_db
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from app.schemas.ai_schemas.chat.workflow_manager_context import WorkflowManagerContext
from app.utils.auth import get_current_user
from app.utils.vercel_stream import VercelStreamResponse
from sqlalchemy.orm import Session
from app.models.project import Project
from app.routers.utils.dependencies import get_access_token, get_project_by_id

router = APIRouter(prefix="/projects/{project_id}/assistant")


@router.post("/init")
def init_assistant(
    project: Project = Depends(get_project_by_id),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    # TODO: We should store this session in the database and associate with the chat later.
    return {
        "session_id": str(uuid.uuid4()),
    }


def assistant_router() -> APIRouter:
    @router.post("")
    async def chat(
        request: ChatRequest,
        project: Project = Depends(get_project_by_id),
        db_session: Session = Depends(get_db),
        current_user=Depends(get_current_user),
        token: str = Depends(get_access_token),
    ) -> StreamingResponse:
        logger = get_logger()
        debug_mode = bool(
            getattr(request, "config", None)
            and getattr(request.config, "debug_mode", False)
        )

        logger.info(f"Chat route: Starting chat request for project {project.id}")

        # Enable debug logging if debug mode is enabled
        if debug_mode:
            logger.info("🔧 Debug mode enabled - setting verbose logging")
            # Set llama_index logger to DEBUG level for more verbose output
            import logging

            logging.getLogger("llama_index").setLevel(logging.DEBUG)

        # Create workflow manager context
        context = WorkflowManagerContext(
            db_session=db_session,
            project=project,
            access_token=token,
            system_prompt_id=getattr(request.config, "system_prompt_id", None),
            initial_state=getattr(request.config, "initial_state", None),
        )

        workflow_manager = WorkflowManager(context)

        user_message = request.messages[-1].to_llamaindex_message()
        chat_history = [
            message.to_llamaindex_message() for message in request.messages[:-1]
        ]
        logger.info(
            f"Chat route: Processing chat request with {len(chat_history)} messages in history"
        )

        # TODO: review why we are passing the request object here
        workflow = await workflow_manager.create_workflow(chat_request=request)
        logger.info("Chat route: Created workflow successfully")

        # TODO: Should we start a new session if the session_id is not provided?
        session_id = getattr(request.config, "session_id", None) or str(uuid.uuid4())

        workflow_handler = workflow.run(
            user_msg=user_message.content,
            chat_history=chat_history,
            memory=workflow_manager.index_manager.get_chat_memory(
                session_id,
            ),
        )
        logger.info(
            "Chat route: Started workflow execution with user message: %s",
            user_message.content,
        )

        callbacks: list[EventCallback] = [
            SourceNodesFromToolCall(),
        ]

        # Add debug callback if debug mode is enabled
        if debug_mode:
            logger.info("Chat route: Adding tool debug callback")
            callbacks.append(ToolDebugCallback(logger))

        if getattr(request, "config", None) and getattr(
            request.config, "next_question_suggestions", False
        ):
            logger.info("Chat route: Adding next question suggestions callback")
            callbacks.append(SuggestNextQuestions(db_session, project, request))
        stream_handler = StreamHandler(
            workflow_handler=workflow_handler,
            callbacks=callbacks,
        )
        logger.info("Chat route: Initialized stream handler with callbacks")

        return VercelStreamResponse(
            content_generator=_stream_content(stream_handler, request, logger),
        )

    return router


async def _stream_content(
    handler: StreamHandler,
    request: ChatRequest,
    logger: logging.Logger,
) -> AsyncGenerator[str, None]:
    logger.info("Starting content streaming")

    async def _text_stream(
        event: Union[AgentStream, StopEvent],
    ) -> AsyncGenerator[str, None]:
        logger.info(f"Text stream: Processing {type(event).__name__} event")
        if isinstance(event, AgentStream):
            # Normally, if the stream is a tool call, the delta is always empty
            # so it's not a text stream.
            logger.info(f"Event.tool_calls: {event.tool_calls}")
            logger.info(f"Event.delta: {event.delta}")
            if len(event.tool_calls) == 0:
                logger.info(f"Streaming text delta: {event.delta}")
                yield event.delta
        elif isinstance(event, StopEvent):
            logger.info("Received StopEvent")
            if isinstance(event.result, str):
                logger.info(f"Streaming final result string: {event.result}")
                yield event.result
            elif isinstance(event.result, AsyncGenerator):
                logger.info("Streaming final result from AsyncGenerator")
                async for chunk in event.result:
                    if isinstance(chunk, str):
                        yield chunk
                    elif hasattr(chunk, "delta") and chunk.delta:
                        yield chunk.delta

    # try:
    logger.info("Stream content: Starting to process stream events")
    async for event in handler.stream_events():
        logger.info(f"Stream content: Processing {type(event).__name__} event")
        logger.info(
            f"Stream content: isinstance(event, (AgentStream, StopEvent)): {isinstance(event, (AgentStream, StopEvent))}"
        )
        if isinstance(event, (AgentStream, StopEvent)):
            async for chunk in _text_stream(event):
                logger.info(f"Stream content: Processing chunk: {chunk}")
                handler.accumulate_text(chunk)
                yield VercelStreamResponse.convert_text(chunk)
        elif isinstance(event, dict):
            logger.info(f"Stream content: Processing dictionary event: {event}")
            yield VercelStreamResponse.convert_data(event)
        elif hasattr(event, "to_response"):
            logger.info(
                f"Stream content: Processing event with to_response method: {type(event).__name__}"
            )
            event_response = event.to_response()
            yield VercelStreamResponse.convert_data(event_response)
        else:
            # Ignore unnecessary agent workflow events
            if not isinstance(event, (AgentInput, AgentSetup)):
                logger.info(
                    f"Stream content: Processing other event type: {type(event).__name__}"
                )
                yield VercelStreamResponse.convert_data(event.model_dump())

    # except asyncio.CancelledError:
    #     logger.warning("Client cancelled the request!")
    #     await handler.cancel_run()
    # except Exception as e:
    #     logger.error(f"Error in stream response: {e}", exc_info=True)
    #     yield VercelStreamResponse.convert_error(str(e))
    #     await handler.cancel_run()
    # finally:
    #     logger.info("Finished content streaming")
