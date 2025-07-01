#!/usr/bin/env python3
"""
Example script demonstrating how to use the Vision plugin with LlamaIndex FunctionAgent.

This script shows how to:
1. Create a FunctionAgent with vision capabilities
2. Analyze images from URLs
3. Extract text from images
4. Describe image content

Requirements:
- OpenAI API key configured
- Valid image URLs for testing
"""

import asyncio
from typing import List
from llama_index.core.agent import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from app.plugins.vision import (
    analyze_image,
    extract_text_from_image,
    describe_image_content,
    get_tools,
)
from app.config import get_settings


async def create_vision_agent() -> FunctionAgent:
    """
    Create a FunctionAgent with vision capabilities.

    Returns:
        FunctionAgent: Configured agent with vision tools
    """
    # Get OpenAI API key
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError(
            "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )

    # Create LLM with vision model
    llm = OpenAI(
        model="gpt-4-vision-preview", api_key=settings.openai_api_key, max_tokens=1000
    )

    # Get vision tools
    vision_tools = get_tools()

    # Create system prompt for vision agent
    system_prompt = """
    You are a helpful AI assistant with vision capabilities. You can:
    1. Analyze images and provide detailed descriptions
    2. Extract text from images using OCR
    3. Describe visual content in images
    
    When a user provides an image URL, you can use the available tools to:
    - analyze_image: Comprehensive image analysis with custom prompts
    - extract_text_from_image: Extract text content from images
    - describe_image_content: Provide detailed visual descriptions
    
    Always be helpful and provide detailed, accurate responses about image content.
    """

    # Create FunctionAgent
    agent = FunctionAgent.from_tools(
        tools=vision_tools, llm=llm, system_prompt=system_prompt, verbose=True
    )

    return agent


async def example_usage():
    """Example usage of the vision agent."""

    # Create the agent
    agent = await create_vision_agent()

    # Example image URLs (replace with actual URLs for testing)
    test_images = [
        "https://example.com/sample-image.jpg",  # Replace with actual URL
        "https://example.com/document-image.jpg",  # Replace with actual URL
    ]

    # Example queries
    queries = [
        f"Please analyze this image: {test_images[0]}",
        f"Extract any text from this image: {test_images[1]}",
        f"Describe what you see in this image: {test_images[0]}",
    ]

    print("=== Vision Agent Example ===\n")

    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 50)

        try:
            response = await agent.achat(query)
            print(f"Response: {response.message.content}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "=" * 60 + "\n")


async def test_individual_tools():
    """Test individual vision tools directly."""

    print("=== Testing Individual Vision Tools ===\n")

    # Example image URL (replace with actual URL)
    test_image_url = "https://example.com/test-image.jpg"

    # Test analyze_image
    print("1. Testing analyze_image tool:")
    try:
        result = analyze_image(
            image_url=test_image_url,
            analysis_prompt="What objects and colors do you see in this image?",
            detail_level="high",
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "-" * 40 + "\n")

    # Test extract_text_from_image
    print("2. Testing extract_text_from_image tool:")
    try:
        result = extract_text_from_image(test_image_url)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "-" * 40 + "\n")

    # Test describe_image_content
    print("3. Testing describe_image_content tool:")
    try:
        result = describe_image_content(test_image_url)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function to run the examples."""
    print("Vision Plugin Example")
    print("====================")
    print(
        "This example demonstrates how to use the Vision plugin with LlamaIndex FunctionAgent."
    )
    print("Make sure you have:")
    print("1. OpenAI API key configured")
    print("2. Valid image URLs for testing")
    print("3. Internet connection to download images")
    print("\n")

    # Run examples
    asyncio.run(example_usage())
    asyncio.run(test_individual_tools())


if __name__ == "__main__":
    main()
