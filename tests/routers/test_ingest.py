from uuid import uuid4
from unittest.mock import patch


def test_ingest_text_success(client, setup_project):
    """Test successful text ingestion."""
    project = setup_project
    request_data = {
        "ref_id": "test-ref-123",
        "text": "This is a test text to be ingested",
        "labels": {"source": "test", "type": "example"},
    }

    # Mock the Ingestor to avoid actual vector store operations
    with patch("app.core.ingestor.Ingestor.ingest_raw_text") as mock_ingest:
        mock_ingest.return_value = None
        response = client.post(f"/projects/{project.id}/ingest/text", json=request_data)

        assert response.status_code == 200
        assert response.json() == {
            "message": "Text successfully ingested into the vector store."
        }

        # Verify the ingest method was called with correct parameters
        mock_ingest.assert_called_once_with(
            request_data["ref_id"], request_data["text"], request_data["labels"]
        )


def test_ingest_text_invalid_project(client):
    """Test text ingestion with invalid project ID."""
    non_existent_id = uuid4()
    request_data = {
        "ref_id": "test-ref-123",
        "text": "This is a test text to be ingested",
        "labels": {"source": "test"},
    }

    response = client.post(
        f"/projects/{non_existent_id}/ingest/text", json=request_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_ingest_text_invalid_request(client, setup_project):
    """Test text ingestion with invalid request data."""
    project = setup_project
    invalid_request_data = {
        "ref_id": "test-ref-123",
        # Missing required 'text' field
        "labels": {"source": "test"},
    }

    response = client.post(
        f"/projects/{project.id}/ingest/text", json=invalid_request_data
    )
    assert response.status_code == 422  # Validation error


def test_ingest_text_without_labels(client, setup_project):
    """Test text ingestion without optional labels."""
    project = setup_project
    request_data = {
        "ref_id": "test-ref-123",
        "text": "This is a test text to be ingested",
        # No labels provided
    }

    with patch("app.core.ingestor.Ingestor.ingest_raw_text") as mock_ingest:
        mock_ingest.return_value = None
        response = client.post(f"/projects/{project.id}/ingest/text", json=request_data)

        assert response.status_code == 200
        assert response.json() == {
            "message": "Text successfully ingested into the vector store."
        }

        # Verify the ingest method was called with None for labels
        mock_ingest.assert_called_once_with(
            request_data["ref_id"], request_data["text"], None
        )
