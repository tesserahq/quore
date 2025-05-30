import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from llama_index.core.workflow import Workflow
from llama_index.core.types import MessageRole
from typing import Dict, Any


@pytest.fixture
def mock_workflow():
    workflow = MagicMock(spec=Workflow)

    class MockHandler:
        async def stream_events(self):
            yield {"data": "mock event"}

        async def cancel_run(self):
            return None

    handler = MockHandler()
    workflow.run = MagicMock(return_value=handler)
    return workflow


@pytest.mark.skip(reason="Skipping this test for now")
def test_chat_endpoint(client: TestClient, mock_workflow, setup_project):
    # Create a test chat request
    request_data: Dict[str, Any] = {
        "messages": [{"role": MessageRole.USER, "content": "Hello, how are you?"}],
        "config": {"next_question_suggestions": True},
    }

    project = setup_project
    # Make the request
    response = client.post(f"/projects/{project.id}/chat", json=request_data)

    # Check response status
    assert response.status_code == 200

    # Check response headers
    assert response.headers["content-type"].startswith("text/event-stream")

    # Check response content
    content = response.text
    assert content.startswith("8:")  # Verify it's a Vercel stream data event

    # Verify the workflow was called with correct parameters
    mock_workflow.run.assert_called_once()
    call_args = mock_workflow.run.call_args
    assert call_args.kwargs["user_msg"] == "Hello, how are you?"
    assert len(call_args.kwargs["chat_history"]) == 0


@pytest.mark.skip(reason="Skipping this test for now")
def test_chat_endpoint_error_handling(client: TestClient, setup_project):
    # Create a test chat request with invalid data
    request_data: Dict[str, Any] = {
        "messages": [
            {
                "role": "invalid_role",  # Invalid role should trigger an error
                "content": "Hello",
            }
        ]
    }

    project = setup_project

    # Make the request
    response = client.post(f"/projects/{project.id}/chat", json=request_data)

    # Check response status
    assert response.status_code == 422  # Validation error


@pytest.mark.skip(reason="Skipping this test for now")
def test_chat_endpoint_with_history(client: TestClient, mock_workflow, setup_project):
    # Create a test chat request with chat history
    request_data: Dict[str, Any] = {
        "messages": [
            {"role": MessageRole.ASSISTANT, "content": "Hi there!"},
            {"role": MessageRole.USER, "content": "How are you?"},
        ]
    }

    project = setup_project

    # Make the request
    response = client.post(f"/projects/{project.id}/chat", json=request_data)

    # Check response status
    assert response.status_code == 200

    # Verify the workflow was called with correct parameters
    mock_workflow.run.assert_called_once()
    call_args = mock_workflow.run.call_args
    assert call_args.kwargs["user_msg"] == "How are you?"
    assert len(call_args.kwargs["chat_history"]) == 1
    assert call_args.kwargs["chat_history"][0].content == "Hi there!"
