# Vision Plugin

The Vision plugin provides image analysis capabilities using OpenAI's Vision API. It allows you to analyze images from URLs, extract text using OCR, and provide detailed descriptions of visual content.

## Features

- **Image Analysis**: Comprehensive analysis of images with custom prompts
- **Text Extraction**: OCR capabilities to extract text from images
- **Content Description**: Detailed visual descriptions of image content
- **URL Support**: Works with any publicly accessible image URL
- **Error Handling**: Robust error handling for network issues and API failures

## Tools Available

### 1. analyze_image

Analyzes an image from a URL using OpenAI's Vision capabilities.

**Parameters:**
- `image_url` (str): The URL of the image to analyze
- `analysis_prompt` (Optional[str]): Custom prompt for image analysis
- `detail_level` (str): Level of detail for analysis ("low", "high", "auto")

**Returns:**
- Dictionary containing analysis results, image URL, and success status

**Example:**
```python
result = analyze_image(
    image_url="https://example.com/image.jpg",
    analysis_prompt="What objects and colors do you see?",
    detail_level="high"
)
```

### 2. extract_text_from_image

Extracts text content from an image using OCR capabilities.

**Parameters:**
- `image_url` (str): The URL of the image to extract text from

**Returns:**
- Dictionary containing extracted text, image URL, and success status

**Example:**
```python
result = extract_text_from_image("https://example.com/document.jpg")
```

### 3. describe_image_content

Provides a detailed description of the visual content in an image.

**Parameters:**
- `image_url` (str): The URL of the image to describe

**Returns:**
- Dictionary containing description, image URL, and success status

**Example:**
```python
result = describe_image_content("https://example.com/landscape.jpg")
```

## Setup

### Prerequisites

1. **OpenAI API Key**: You need a valid OpenAI API key with access to GPT-4 Vision
2. **Python Dependencies**: The plugin requires the following packages:
   - `llama-index-llms-openai` (for OpenAI integration)
   - `fastmcp` (for plugin framework)

### Configuration

1. Set your OpenAI API key in the environment:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Or configure it in your application settings:
   ```python
   from app.config import get_settings
   settings = get_settings()
   settings.openai_api_key = "your-api-key-here"
   ```

## Usage with LlamaIndex FunctionAgent

### Basic Setup

```python
from llama_index.core.agent import FunctionAgent
from llama_index.llms.openai import OpenAI
from app.plugins.vision import get_tools
from app.config import get_settings

# Get OpenAI API key
settings = get_settings()
llm = OpenAI(
    model="gpt-4-vision-preview",
    api_key=settings.openai_api_key,
    max_tokens=1000
)

# Get vision tools
vision_tools = get_tools()

# Create FunctionAgent
agent = FunctionAgent.from_tools(
    tools=vision_tools,
    llm=llm,
    system_prompt="You are a helpful AI assistant with vision capabilities.",
    verbose=True
)
```

### Example Queries

```python
# Analyze an image
response = await agent.achat("Please analyze this image: https://example.com/image.jpg")

# Extract text from an image
response = await agent.achat("Extract any text from this image: https://example.com/document.jpg")

# Describe image content
response = await agent.achat("Describe what you see in this image: https://example.com/photo.jpg")
```

## Integration with Workflow Manager

The Vision plugin is automatically included in the system tools when using the WorkflowManager:

```python
from app.core.workflow_manager import WorkflowManager

# The vision tools will be automatically available
workflow_manager = WorkflowManager(db_session, project, access_token)
workflow = await workflow_manager.create_workflow()
```

## Error Handling

The plugin includes comprehensive error handling:

- **Network Errors**: Handles image download failures
- **API Errors**: Manages OpenAI API issues
- **Invalid URLs**: Validates image URLs
- **Missing API Key**: Checks for OpenAI API key configuration

All errors are logged and returned in a structured format:

```python
{
    "image_url": "https://example.com/image.jpg",
    "error": "Error message here",
    "success": False
}
```

## Performance Considerations

- **Image Size**: Large images may take longer to process
- **API Limits**: Be aware of OpenAI API rate limits and costs
- **Network**: OpenAI handles image fetching directly from URLs
- **Caching**: Consider implementing caching for frequently analyzed images

## Security Considerations

- **URL Validation**: The plugin downloads images from provided URLs
- **API Key Security**: Ensure your OpenAI API key is properly secured
- **Image Content**: Be aware that the plugin can analyze any image content
- **Rate Limiting**: Implement appropriate rate limiting for production use

## Testing

Run the test suite to verify the plugin functionality:

```bash
pytest tests/app/plugins/test_vision.py -v
```

## Example Use Cases

1. **Document Analysis**: Extract text from scanned documents
2. **Image Classification**: Analyze and categorize images
3. **Content Moderation**: Check images for inappropriate content
4. **Accessibility**: Generate descriptions for visually impaired users
5. **E-commerce**: Analyze product images for cataloging

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Ensure your OpenAI API key is set in the environment or configuration

2. **"Image URL not accessible"**
   - Check that the image URL is publicly accessible
   - Verify the URL is valid and the image exists

3. **"Model not found"**
   - Ensure you have access to GPT-4 Vision in your OpenAI account

4. **Rate limit errors**
   - Implement rate limiting or upgrade your OpenAI plan

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To contribute to the Vision plugin:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure error handling is robust
5. Test with various image types and URLs 