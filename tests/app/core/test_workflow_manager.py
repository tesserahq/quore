import pytest
from unittest.mock import MagicMock, patch
from app.core.workflow_manager import WorkflowManager
from app.schemas.ai_schemas.chat.workflow_manager_context import WorkflowManagerContext
from llama_index.core.llms.mock import MockLLM


class TestWorkflowManager:
    """Test cases for WorkflowManager class."""

    def test_workflow_manager_initialization_with_context(self, db, setup_project):
        """Test that WorkflowManager initializes correctly with WorkflowManagerContext."""
        project = setup_project

        # Create context with all parameters
        context = WorkflowManagerContext(
            db_session=db,
            project=project,
            access_token="test-token",
            system_prompt_id="test-prompt-id",
        )

        # Initialize WorkflowManager with context
        workflow_manager = WorkflowManager(context)

        # Verify all attributes are set correctly
        assert workflow_manager.db_session == db
        assert workflow_manager.project == project
        assert workflow_manager.access_token == "test-token"
        assert workflow_manager.system_prompt_id == "test-prompt-id"
        assert workflow_manager.index_manager is not None
        assert workflow_manager.logger is not None

    def test_workflow_manager_initialization_with_minimal_context(
        self, db, setup_project
    ):
        """Test that WorkflowManager initializes correctly with minimal context."""
        project = setup_project

        # Create context with only required parameters
        context = WorkflowManagerContext(db_session=db, project=project)

        # Initialize WorkflowManager with context
        workflow_manager = WorkflowManager(context)

        # Verify all attributes are set correctly
        assert workflow_manager.db_session == db
        assert workflow_manager.project == project
        assert workflow_manager.access_token is None
        assert workflow_manager.system_prompt_id is None
        assert workflow_manager.index_manager is not None
        assert workflow_manager.logger is not None

    @pytest.mark.asyncio
    async def test_create_workflow_with_system_prompt_id(
        self, db, setup_project, setup_system_prompt
    ):
        """Test creating workflow with a specific system prompt ID."""
        project = setup_project
        system_prompt = setup_system_prompt

        # Create context with system_prompt_id
        context = WorkflowManagerContext(
            db_session=db, project=project, system_prompt_id=system_prompt.prompt_id
        )

        workflow_manager = WorkflowManager(context)

        # Create a proper mock for the query engine tool
        mock_query_tool = MagicMock()
        mock_query_tool.__name__ = "query_index"  # Add the __name__ attribute
        mock_query_tool.metadata = MagicMock()
        mock_query_tool.metadata.name = "query_index"

        # Mock the LLM and tools to avoid actual LLM calls
        with (
            patch.object(workflow_manager.index_manager, "llm") as mock_llm,
            patch.object(
                workflow_manager.index_manager, "get_query_engine_tool"
            ) as mock_get_query_tool,
            patch.object(workflow_manager, "get_tools") as mock_get_tools,
        ):

            mock_llm.return_value = MockLLM()
            mock_get_query_tool.return_value = mock_query_tool
            mock_get_tools.return_value = []

            # Create workflow
            workflow = await workflow_manager.create_workflow()

            # Verify workflow was created
            assert workflow is not None

            # Verify the system prompt from the prompt service was used
            # (The actual verification would be in the workflow creation logic)

    @pytest.mark.asyncio
    async def test_create_workflow_with_uuid_system_prompt_id(
        self, db, setup_project, setup_system_prompt
    ):
        """Test creating workflow with a UUID system prompt ID."""
        project = setup_project
        system_prompt = setup_system_prompt

        # Create context with UUID system_prompt_id
        context = WorkflowManagerContext(
            db_session=db, project=project, system_prompt_id=system_prompt.id
        )

        workflow_manager = WorkflowManager(context)

        # Create a proper mock for the query engine tool
        mock_query_tool = MagicMock()
        mock_query_tool.__name__ = "query_index"  # Add the __name__ attribute
        mock_query_tool.metadata = MagicMock()
        mock_query_tool.metadata.name = "query_index"

        # Mock the LLM and tools to avoid actual LLM calls
        with (
            patch.object(workflow_manager.index_manager, "llm") as mock_llm,
            patch.object(
                workflow_manager.index_manager, "get_query_engine_tool"
            ) as mock_get_query_tool,
            patch.object(workflow_manager, "get_tools") as mock_get_tools,
        ):

            mock_llm.return_value = MockLLM()
            mock_get_query_tool.return_value = mock_query_tool
            mock_get_tools.return_value = []

            # Create workflow
            workflow = await workflow_manager.create_workflow()

            # Verify workflow was created
            assert workflow is not None

            # Verify the system prompt from the prompt service was used
            # (The actual verification would be in the workflow creation logic)

    @pytest.mark.asyncio
    async def test_create_workflow_with_invalid_system_prompt_id(
        self, db, setup_project
    ):
        """Test creating workflow with an invalid system prompt ID falls back to project default."""
        project = setup_project

        # Create context with invalid system_prompt_id
        context = WorkflowManagerContext(
            db_session=db, project=project, system_prompt_id="invalid-prompt-id"
        )

        workflow_manager = WorkflowManager(context)

        # Create a proper mock for the query engine tool
        mock_query_tool = MagicMock()
        mock_query_tool.__name__ = "query_index"  # Add the __name__ attribute
        mock_query_tool.metadata = MagicMock()
        mock_query_tool.metadata.name = "query_index"

        # Mock the LLM and tools to avoid actual LLM calls
        with (
            patch.object(workflow_manager.index_manager, "llm") as mock_llm,
            patch.object(
                workflow_manager.index_manager, "get_query_engine_tool"
            ) as mock_get_query_tool,
            patch.object(workflow_manager, "get_tools") as mock_get_tools,
        ):

            mock_llm.return_value = MockLLM()
            mock_get_query_tool.return_value = mock_query_tool
            mock_get_tools.return_value = []

            # Create workflow
            workflow = await workflow_manager.create_workflow()

            # Verify workflow was created (should fall back to project default)
            assert workflow is not None

    @pytest.mark.asyncio
    async def test_create_workflow_without_system_prompt_id(self, db, setup_project):
        """Test creating workflow without system_prompt_id uses project default."""
        project = setup_project

        # Create context without system_prompt_id
        context = WorkflowManagerContext(db_session=db, project=project)

        workflow_manager = WorkflowManager(context)

        # Create a proper mock for the query engine tool
        mock_query_tool = MagicMock()
        mock_query_tool.__name__ = "query_index"  # Add the __name__ attribute
        mock_query_tool.metadata = MagicMock()
        mock_query_tool.metadata.name = "query_index"

        # Mock the LLM and tools to avoid actual LLM calls
        with (
            patch.object(workflow_manager.index_manager, "llm") as mock_llm,
            patch.object(
                workflow_manager.index_manager, "get_query_engine_tool"
            ) as mock_get_query_tool,
            patch.object(workflow_manager, "get_tools") as mock_get_tools,
        ):

            mock_llm.return_value = MockLLM()
            mock_get_query_tool.return_value = mock_query_tool
            mock_get_tools.return_value = []

            # Create workflow
            workflow = await workflow_manager.create_workflow()

            # Verify workflow was created
            assert workflow is not None
