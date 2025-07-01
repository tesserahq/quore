import pytest
from unittest.mock import Mock, patch, MagicMock
from app.models.project import Project


class TestVisionPlugin:
    """Test cases for the vision plugin."""

    @patch("app.plugins.vision.get_settings")
    @patch("app.plugins.vision.OpenAI")
    @pytest.mark.skip(reason="Skipping this test for now")
    def test_analyze_image_success(self, mock_openai, mock_settings):
        """Test successful image analysis."""
        # Import the actual function
        from app.plugins.vision import get_tools

        # Setup mocks
        mock_settings.return_value.openai_api_key = "test-api-key"

        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "This is a test image analysis result"
        )
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Get the actual function from the tools (without project)
        tools = get_tools()
        analyze_image_tool = next(
            tool for tool in tools if tool.name == "analyze_image"
        )
        result = analyze_image_tool.fn(image_url="https://example.com/image.jpg")

        assert result["success"] is True
        assert result["image_url"] == "https://example.com/image.jpg"
        assert "analysis" in result

    @patch("app.plugins.vision.get_settings")
    @patch("app.plugins.vision.OpenAI")
    @pytest.mark.skip(reason="Skipping this test for now")
    def test_analyze_image_with_project(self, mock_openai, mock_settings):
        """Test successful image analysis with project context."""
        from app.plugins.vision import get_tools

        # Setup mocks
        mock_settings.return_value.openai_api_key = "test-api-key"

        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "This is a test image analysis result"
        )
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create a mock project
        mock_project = Mock(spec=Project)
        mock_project.id = "test-project-id"
        mock_project.vision_analysis_prompt = "Custom project prompt"
        mock_project.vision_model = "gpt-4o-mini"

        # Get the actual function from the tools (with project)
        tools = get_tools(project=mock_project)
        analyze_image_tool = next(
            tool for tool in tools if tool.name == "analyze_image"
        )
        result = analyze_image_tool.fn(image_url="https://example.com/image.jpg")

        assert result["success"] is True
        assert result["image_url"] == "https://example.com/image.jpg"
        assert "analysis" in result
        assert result["project_id"] == "test-project-id"

    @patch("app.plugins.vision.get_settings")
    @pytest.mark.skip(reason="Skipping this test for now")
    def test_analyze_image_no_api_key(self, mock_settings):
        """Test image analysis without API key."""
        from app.plugins.vision import get_tools

        mock_settings.return_value.openai_api_key = None

        # Get the actual function from the tools
        tools = get_tools()
        analyze_image_tool = next(
            tool for tool in tools if tool.name == "analyze_image"
        )
        result = analyze_image_tool.fn(image_url="https://example.com/image.jpg")

        assert result["success"] is False
        assert "error" in result
        assert "OpenAI API key not configured" in result["error"]

    @patch("app.plugins.vision.get_settings")
    @patch("app.plugins.vision.OpenAI")
    @pytest.mark.skip(reason="Skipping this test for now")
    def test_analyze_image_with_project_specific_prompt(
        self, mock_openai, mock_settings
    ):
        """Test image analysis using project-specific prompt."""
        from app.plugins.vision import get_tools

        # Setup mocks
        mock_settings.return_value.openai_api_key = "test-api-key"

        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Project-specific analysis result"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create a mock project with custom prompt
        mock_project = Mock(spec=Project)
        mock_project.id = "test-project-id"
        mock_project.vision_analysis_prompt = (
            "Analyze this image for real estate purposes"
        )
        mock_project.vision_model = "gpt-4o-mini"

        # Get the actual function from the tools (with project)
        tools = get_tools(project=mock_project)
        analyze_image_tool = next(
            tool for tool in tools if tool.name == "analyze_image"
        )
        result = analyze_image_tool.fn(image_url="https://example.com/image.jpg")

        assert result["success"] is True
        assert result["image_url"] == "https://example.com/image.jpg"
        assert "analysis" in result
        assert result["project_id"] == "test-project-id"

        # Verify the project-specific prompt was used
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        content = messages[0]["content"]
        text_content = next(item["text"] for item in content if item["type"] == "text")
        assert "real estate purposes" in text_content

    @patch("app.plugins.vision.get_settings")
    @patch("app.plugins.vision.OpenAI")
    @pytest.mark.skip(reason="Skipping this test for now")
    def test_analyze_image_with_custom_prompt(self, mock_openai, mock_settings):
        """Test image analysis with custom prompt."""
        from app.plugins.vision import get_tools

        mock_settings.return_value.openai_api_key = "test-api-key"

        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Custom analysis result"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        custom_prompt = "What colors are in this image?"
        # Get the actual function from the tools
        tools = get_tools()
        analyze_image_tool = next(
            tool for tool in tools if tool.name == "analyze_image"
        )
        result = analyze_image_tool.fn(
            image_url="https://example.com/image.jpg",
            analysis_prompt=custom_prompt,
            detail_level="high",
        )

        assert result["success"] is True
        # Verify the custom prompt was used in the LLM call
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        content = messages[0]["content"]
        text_content = next(item["text"] for item in content if item["type"] == "text")
        assert custom_prompt in text_content

    @pytest.mark.skip(reason="Skipping this test for now")
    def test_create_analyze_image_wrapper(self):
        """Test the wrapper function creation."""
        from app.plugins.vision import create_analyze_image_wrapper

        # Create a mock project
        mock_project = Mock(spec=Project)
        mock_project.id = "test-project-id"
        mock_project.vision_analysis_prompt = "Custom project prompt"
        mock_project.vision_model = "gpt-4o-mini"

        # Create the wrapper
        wrapper = create_analyze_image_wrapper(mock_project)

        # Verify the wrapper is callable and has the right signature
        assert callable(wrapper)

        # Test that the wrapper can be called with the expected parameters
        with patch("app.plugins.vision.analyze_image") as mock_analyze:
            mock_analyze.return_value = {"success": True, "test": "result"}

            result = wrapper(
                image_url="https://example.com/image.jpg",
                analysis_prompt="test prompt",
                detail_level="high",
            )

            # Verify the underlying function was called with the project
            mock_analyze.assert_called_once_with(
                image_url="https://example.com/image.jpg",
                analysis_prompt="test prompt",
                detail_level="high",
                project=mock_project,
            )

            assert result == {"success": True, "test": "result"}
