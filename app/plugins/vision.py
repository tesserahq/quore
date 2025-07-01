from typing import Optional, Dict, Any
from fastmcp import FastMCP
from llama_index.core.tools import FunctionTool
from openai import OpenAI
from app.core.logging_config import get_logger
from app.config import get_settings
from app.models.project import Project

logger = get_logger()


def analyze_image(
    image_url: str,
    analysis_prompt: Optional[str] = None,
    detail_level: str = "auto",
    project: Optional[Project] = None,
) -> Dict[str, Any]:
    """
    Analyze an image from a URL using OpenAI's Vision capabilities.

    Parameters:
        image_url (str): The URL of the image to analyze
        analysis_prompt (Optional[str]): Custom prompt for image analysis.
                                       If not provided, a general analysis will be performed.
        detail_level (str): Level of detail for image analysis ("low", "high", "auto")
        project (Optional[Project]): Project instance for context and settings

    Returns:
        Dict[str, Any]: Analysis results containing description and insights
    """
    try:
        # Get OpenAI API key from settings
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        # Create OpenAI client with vision model
        client = OpenAI(api_key=settings.openai_api_key)

        # Use project-specific analysis prompt if available, otherwise use default
        if not analysis_prompt:
            if project and project.vision_analysis_prompt:
                analysis_prompt = project.vision_analysis_prompt
            else:
                analysis_prompt = """
                Please analyze this image and provide a comprehensive description including:
                1. What you see in the image
                2. Any text or objects that are visible
                3. The overall context or setting
                4. Any notable details or patterns
                5. Potential use cases or applications
                
                Be detailed but concise in your analysis.
                """

        # Use project-specific vision model if available
        model = "gpt-4o-mini"  # Default model
        if project and project.vision_model:
            model = project.vision_model

        # Create the message with image URL directly
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": detail_level},
                    },
                ],
            }
        ]

        # Get the analysis
        response = client.chat.completions.create(
            model=model, messages=messages, max_tokens=1000
        )

        return {
            "image_url": image_url,
            "analysis": response.choices[0].message.content,
            "success": True,
            "project_id": str(project.id) if project else None,
        }

    except Exception as e:
        logger.error(f"Error analyzing image {image_url}: {e}")
        return {"image_url": image_url, "error": str(e), "success": False}


def create_analyze_image_wrapper(project: Project):
    """
    Create a wrapper function for analyze_image with the project pre-set.

    Parameters:
        project (Project): The project instance to use for context

    Returns:
        function: A function that can be used with FunctionTool
    """

    def analyze_image_wrapper(
        image_url: str,
        analysis_prompt: Optional[str] = None,
        detail_level: str = "auto",
    ) -> Dict[str, Any]:
        """
        Analyze an image from a URL using OpenAI's Vision capabilities.
        This wrapper has the project context pre-set.

        Parameters:
            image_url (str): The URL of the image to analyze
            analysis_prompt (Optional[str]): Custom prompt for image analysis.
                                           If not provided, project-specific or default prompt will be used.
            detail_level (str): Level of detail for image analysis ("low", "high", "auto")

        Returns:
            Dict[str, Any]: Analysis results containing description and insights
        """
        return analyze_image(
            image_url=image_url,
            analysis_prompt=analysis_prompt,
            detail_level=detail_level,
            project=project,
        )

    return analyze_image_wrapper


# def extract_text_from_image(image_url: str) -> Dict[str, Any]:
#     """
#     Extract text content from an image using OCR capabilities.

#     Parameters:
#         image_url (str): The URL of the image to extract text from

#     Returns:
#         Dict[str, Any]: Extracted text and metadata
#     """
#     try:
#         # Get OpenAI API key from settings
#         settings = get_settings()
#         if not settings.openai_api_key:
#             raise ValueError("OpenAI API key not configured")

#         # Create OpenAI client with vision model
#         llm = OpenAI(
#             model="gpt-4-vision-preview",
#             api_key=settings.openai_api_key,
#             max_tokens=1000,
#         )

#         # Prepare the OCR prompt
#         ocr_prompt = """
#         Please extract all text content from this image.
#         Return the text exactly as it appears, maintaining:
#         - Line breaks and formatting
#         - Punctuation and spacing
#         - Any special characters or symbols

#         If there's no text in the image, respond with "No text found in image."
#         """

#         # Create the message with image URL directly
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": ocr_prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": image_url, "detail": "high"},
#                     },
#                 ],
#             }
#         ]

#         # Get the text extraction
#         response = llm.complete(messages=messages)

#         return {
#             "image_url": image_url,
#             "extracted_text": response.text,
#             "success": True,
#         }

#     except Exception as e:
#         logger.error(f"Error extracting text from image {image_url}: {e}")
#         return {"image_url": image_url, "error": str(e), "success": False}


# def describe_image_content(image_url: str) -> Dict[str, Any]:
#     """
#     Provide a detailed description of the visual content in an image.

#     Parameters:
#         image_url (str): The URL of the image to describe

#     Returns:
#         Dict[str, Any]: Detailed description of the image content
#     """
#     try:
#         # Get OpenAI API key from settings
#         settings = get_settings()
#         if not settings.openai_api_key:
#             raise ValueError("OpenAI API key not configured")

#         # Create OpenAI client with vision model
#         llm = OpenAI(
#             model="gpt-4-vision-preview",
#             api_key=settings.openai_api_key,
#             max_tokens=1000,
#         )

#         # Prepare the description prompt
#         description_prompt = """
#         Please provide a detailed description of what you see in this image. Include:

#         1. Main subjects and objects
#         2. Colors and visual elements
#         3. Composition and layout
#         4. Background and setting
#         5. Any actions or interactions
#         6. Mood or atmosphere
#         7. Quality and style of the image

#         Be descriptive and thorough in your analysis.
#         """

#         # Create the message with image URL directly
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": description_prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": image_url, "detail": "high"},
#                     },
#                 ],
#             }
#         ]

#         # Get the description
#         response = llm.complete(messages=messages)

#         return {"image_url": image_url, "description": response.text, "success": True}

#     except Exception as e:
#         logger.error(f"Error describing image {image_url}: {e}")
#         return {"image_url": image_url, "error": str(e), "success": False}


def get_tools(project: Optional[Project] = None):
    """
    Return the vision tools as LlamaIndex FunctionTools.

    Parameters:
        project (Optional[Project]): Project instance for context. If provided, tools will be wrapped with project context.

    Returns:
        List[FunctionTool]: List of vision tools
    """
    if project:
        # Create wrapped tools with project context
        analyze_image_wrapper = create_analyze_image_wrapper(project)
        return [
            FunctionTool.from_defaults(analyze_image_wrapper),
            # FunctionTool.from_defaults(extract_text_from_image),
            # FunctionTool.from_defaults(describe_image_content),
        ]
    else:
        # Return tools without project context (for backward compatibility)
        return [
            FunctionTool.from_defaults(analyze_image),
            # FunctionTool.from_defaults(extract_text_from_image),
            # FunctionTool.from_defaults(describe_image_content),
        ]
