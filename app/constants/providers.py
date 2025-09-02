from typing import Literal, Optional
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import MockEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.llms.mock import MockLLM
from app.core.logging_config import get_logger

OPENAI_PROVIDER = "openai"
HUGGINGFACE_PROVIDER = "huggingface"
OLLAMA_PROVIDER = "ollama"
MOCK_PROVIDER = "mock"

# Define the available LLM providers
LLM_PROVIDERS = (
    OPENAI_PROVIDER,
    HUGGINGFACE_PROVIDER,
    OLLAMA_PROVIDER,
    MOCK_PROVIDER,
)

LLMProviderType = Literal[
    "openai",
    "huggingface",
    "ollama",
    "mock",
]

logger = get_logger()


def get_llm_provider(
    provider_name: str, model_name: str, api_key: Optional[str] = None, **kwargs
):
    logger.debug(
        f"Creating LLM provider: {provider_name}, model: {model_name}, api_key present: {api_key is not None}",
        extra={"provider_name": provider_name, "model_name": model_name},
    )
    provider_map = {
        OPENAI_PROVIDER: lambda: OpenAI(model=model_name, api_key=api_key),
        OLLAMA_PROVIDER: lambda: Ollama(
            model=model_name,
            base_url=kwargs.get("base_url", "http://localhost:11434"),
        ),
        HUGGINGFACE_PROVIDER: lambda: HuggingFaceLLM(
            model=model_name,
        ),
        MOCK_PROVIDER: lambda: MockLLM(),
    }
    try:
        provider = provider_map[provider_name.lower()]()
        logger.debug(
            f"Provider created: {provider}",
            extra={"provider_name": provider_name, "model_name": model_name},
        )
        return provider
    except KeyError:
        raise ValueError(f"Unknown embedding provider: {provider_name}")


def get_embedding_provider(
    provider_name: str, model_name: str, api_key: Optional[str] = None
):
    provider_map = {
        OPENAI_PROVIDER: lambda: OpenAIEmbedding(
            model_name=model_name, api_key=api_key
        ),
        HUGGINGFACE_PROVIDER: lambda: HuggingFaceEmbedding(model_name=model_name),
        OLLAMA_PROVIDER: lambda: OllamaEmbedding(model_name=model_name),
        MOCK_PROVIDER: lambda: MockEmbedding(embed_dim=1536),
    }
    try:
        provider = provider_map[provider_name.lower()]()
        logger.debug(
            f"Embedding Provider created: {provider}",
            extra={"provider_name": provider_name, "model_name": model_name},
        )
        return provider
    except KeyError:
        raise ValueError(f"Unknown embedding provider: {provider_name}")

def get_llm_models(provider_name: str) -> list[dict]:
    """
    Returns a list of available LLM models for the specified provider.
    """
    provider_models = {
        OPENAI_PROVIDER: [
            {
                "llm": "gpt-4o",
                "default": True,
            }
        ],
        HUGGINGFACE_PROVIDER: [
            {
                "llm": "sentence-transformers/all-MiniLM-L6-v2",
                "default": True,
            }
        ],
        OLLAMA_PROVIDER: [
            {
                "llm": "llama3.1:8b",
                "default": False,
            },
            {
                "llm": "gemma3:4b",
                "default": False,
            },
            {
                "llm": "gemma2:9b",
                "default": False,
            },
            {
                "llm": "gemma:2b",
                "default": False,
            },
            {
                "llm": "gemma:7b",
                "default": False,
            },
            {
                "llm": "deepseek-r1:8b",
                "default": False,
            },
            
        ],
        MOCK_PROVIDER: [
            {
                "llm": "mock",
                "default": True,
            }
        ],
    }
    return provider_models[provider_name.lower()]

def get_embedding_models(provider_name: str, include_mock: bool = False) -> list[dict]:
    """
    Returns a list of available embedding models for the specified provider.
    Each model entry contains information about dimensions, performance metrics, and other relevant details.

    Args:
        provider_name: The name of the provider to get models for
        include_mock: Whether to include the mock provider in the results (default: False)
    """
    provider_models = {
        OPENAI_PROVIDER: [
            {
                "embed_model": "text-embedding-3-small",
                "default_embed_dim": 1536,
                "available_dimensions": [512, 1536],
                "max_tokens": 8192,
                "miracl_avg": 44.0,
                "mteb_avg": 62.3,
                "default": True,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            },
            {
                "embed_model": "text-embedding-3-large",
                "default_embed_dim": 3072,
                "available_dimensions": [256, 1024, 3072],
                "max_tokens": 8192,
                "miracl_avg": 54.9,
                "mteb_avg": 64.6,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            },
            {
                "embed_model": "text-embedding-ada-002",
                "default_embed_dim": 1536,
                "available_dimensions": [1536],
                "max_tokens": 8192,
                "miracl_avg": 31.4,
                "mteb_avg": 61.0,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            },
        ],
        HUGGINGFACE_PROVIDER: [
            {
                "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
                "default_embed_dim": 384,
                "available_dimensions": [384],
                "max_tokens": 512,
                "miracl_avg": 32.1,
                "mteb_avg": 58.9,
                "default": True,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            }
        ],
        OLLAMA_PROVIDER: [
            {
                "embed_model": "nomic-embed-text:v1.5",
                "default_embed_dim": 768,
                "available_dimensions": [768],
                "max_tokens": 8192,
                "miracl_avg": 35.2,
                "mteb_avg": 59.1,
                "default": True,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            }
        ],
        MOCK_PROVIDER: [
            {
                "embed_model": "mock-embedding",
                "default_embed_dim": 1536,
                "available_dimensions": [1536],
                "max_tokens": 8192,
                "miracl_avg": 0.0,
                "mteb_avg": 0.0,
                "hnsw_m": 16,
                "hnsw_ef_search": 100,
                "hnsw_dist_method": "vector_cosine_ops",
                "hnsw_ef_construction": 200,
            }
        ],
    }

    try:
        if provider_name.lower() == MOCK_PROVIDER and not include_mock:
            raise ValueError(
                "Mock provider is not included by default. Set include_mock=True to include it."
            )
        return provider_models[provider_name.lower()]
    except KeyError:
        raise ValueError(f"Unknown embedding provider: {provider_name}")
