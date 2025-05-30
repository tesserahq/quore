import asyncio
import logging
from typing import AsyncGenerator, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
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
)
from app.core.callbacks.stream_handler import StreamHandler
from app.core.workflow_manager import WorkflowManager
from app.core.logging_config import get_logger
from app.db import get_db
from app.schemas.ai_schemas.chat.chat_request import ChatRequest
from app.utils.auth import get_current_user
from app.utils.vercel_stream import VercelStreamResponse
from sqlalchemy.orm import Session
from app.models.project import Project
from app.utils.dependencies import get_project_by_id


def assistant_router() -> APIRouter:
    router = APIRouter(prefix="/projects/{project_id}/assistant")

    @router.post("")
    async def chat(
        request: ChatRequest,
        background_tasks: BackgroundTasks,
        project: Project = Depends(get_project_by_id),
        db_session: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ) -> StreamingResponse:
        logger = get_logger()
        logger.debug(f"Chat route: Starting chat request for project {project.id}")

        workflow_manager = WorkflowManager(db_session, project)

        try:
            user_message = request.messages[-1].to_llamaindex_message()
            chat_history = [
                message.to_llamaindex_message() for message in request.messages[:-1]
            ]
            logger.debug(
                f"Chat route: Processing chat request with {len(chat_history)} messages in history"
            )

            # TODO: review why we are passing the request object here
            workflow = workflow_manager.create_workflow(chat_request=request)
            logger.debug("Chat route: Created workflow successfully")

            workflow_handler = workflow.run(
                user_msg=user_message.content,
                chat_history=chat_history,
                memory=workflow_manager.index_manager.get_chat_memory(
                    str(project.id), current_user.id
                ),
            )
            logger.debug(
                "Chat route: Started workflow execution with user message: %s",
                user_message.content,
            )

            callbacks: list[EventCallback] = [
                SourceNodesFromToolCall(),
            ]
            if request.config and request.config.next_question_suggestions:
                logger.debug("Chat route: Adding next question suggestions callback")
                callbacks.append(SuggestNextQuestions(db_session, project, request))
            stream_handler = StreamHandler(
                workflow_handler=workflow_handler,
                callbacks=callbacks,
            )
            logger.debug("Chat route: Initialized stream handler with callbacks")

            return VercelStreamResponse(
                content_generator=_stream_content(stream_handler, request, logger),
            )
        except Exception as e:
            logger.error(f"Chat route: Error in chat endpoint: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    return router


async def _stream_content(
    handler: StreamHandler,
    request: ChatRequest,
    logger: logging.Logger,
) -> AsyncGenerator[str, None]:
    logger.debug("Starting content streaming")

    async def _text_stream(
        event: Union[AgentStream, StopEvent],
    ) -> AsyncGenerator[str, None]:
        if isinstance(event, AgentStream):
            # Normally, if the stream is a tool call, the delta is always empty
            # so it's not a text stream.
            if len(event.tool_calls) == 0:
                logger.debug(f"Streaming text delta: {event.delta}")
                yield event.delta
        elif isinstance(event, StopEvent):
            logger.debug("Received StopEvent")
            if isinstance(event.result, str):
                logger.debug(f"Streaming final result string: {event.result}")
                yield event.result
            elif isinstance(event.result, AsyncGenerator):
                logger.debug("Streaming final result from AsyncGenerator")
                async for chunk in event.result:
                    if isinstance(chunk, str):
                        yield chunk
                    elif hasattr(chunk, "delta") and chunk.delta:
                        yield chunk.delta

    try:
        logger.debug("Starting to process stream events")
        async for event in handler.stream_events():
            if isinstance(event, (AgentStream, StopEvent)):
                logger.debug(f"Processing {type(event).__name__} event")
                async for chunk in _text_stream(event):
                    handler.accumulate_text(chunk)
                    yield VercelStreamResponse.convert_text(chunk)
            elif isinstance(event, dict):
                logger.debug(f"Processing dictionary event: {event}")
                yield VercelStreamResponse.convert_data(event)
            elif hasattr(event, "to_response"):
                logger.debug(
                    f"Processing event with to_response method: {type(event).__name__}"
                )
                event_response = event.to_response()
                yield VercelStreamResponse.convert_data(event_response)
            else:
                # Ignore unnecessary agent workflow events
                if not isinstance(event, (AgentInput, AgentSetup)):
                    logger.debug(f"Processing other event type: {type(event).__name__}")
                    yield VercelStreamResponse.convert_data(event.model_dump())

    except asyncio.CancelledError:
        logger.warning("Client cancelled the request!")
        await handler.cancel_run()
    except Exception as e:
        logger.error(f"Error in stream response: {e}", exc_info=True)
        yield VercelStreamResponse.convert_error(str(e))
        await handler.cancel_run()
    finally:
        logger.debug("Finished content streaming")
