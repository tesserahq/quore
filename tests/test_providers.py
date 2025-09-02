import pytest
from app.constants.providers import (
    get_embedding_models,
    get_embedding_provider,
    OPENAI_PROVIDER,
    HUGGINGFACE_PROVIDER,
    OLLAMA_PROVIDER,
    MOCK_PROVIDER,
)


def test_get_embedding_models_openai():
    """Test getting OpenAI embedding models."""
    models = get_embedding_models(OPENAI_PROVIDER)
    assert len(models) == 3
    assert any(model["embed_model"] == "text-embedding-3-small" for model in models)
    assert any(model["embed_model"] == "text-embedding-3-large" for model in models)
    assert any(model["embed_model"] == "text-embedding-ada-002" for model in models)


def test_get_embedding_models_huggingface():
    """Test getting HuggingFace embedding models."""
    models = get_embedding_models(HUGGINGFACE_PROVIDER)
    assert len(models) == 1
    assert models[0]["embed_model"] == "sentence-transformers/all-MiniLM-L6-v2"


def test_get_embedding_models_ollama():
    """Test getting Ollama embedding models."""
    models = get_embedding_models(OLLAMA_PROVIDER)
    assert len(models) == 1
    assert models[0]["embed_model"] == "nomic-embed-text:v1.5"


def test_get_embedding_models_mock_without_include():
    """Test that mock provider is not included by default."""
    with pytest.raises(ValueError, match="Mock provider is not included by default"):
        get_embedding_models(MOCK_PROVIDER)


def test_get_embedding_models_mock_with_include():
    """Test getting mock embedding models when explicitly included."""
    models = get_embedding_models(MOCK_PROVIDER, include_mock=True)
    assert len(models) == 1
    assert models[0]["embed_model"] == "mock-embedding"


def test_get_embedding_models_invalid_provider():
    """Test getting models for an invalid provider."""
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_embedding_models("invalid_provider")


def test_get_embedding_provider_openai():
    """Test getting OpenAI embedding provider."""
    provider = get_embedding_provider(
        OPENAI_PROVIDER, "text-embedding-3-small", "test-key"
    )
    assert provider is not None


def test_get_embedding_provider_huggingface():
    """Test getting HuggingFace embedding provider."""
    provider = get_embedding_provider(
        HUGGINGFACE_PROVIDER, "sentence-transformers/all-MiniLM-L6-v2"
    )
    assert provider is not None


def test_get_embedding_provider_ollama():
    """Test getting Ollama embedding provider."""
    provider = get_embedding_provider(OLLAMA_PROVIDER, "nomic-embed-text")
    assert provider is not None


def test_get_embedding_provider_mock():
    """Test getting mock embedding provider."""
    provider = get_embedding_provider(MOCK_PROVIDER, "mock-embedding")
    assert provider is not None


def test_get_embedding_provider_invalid():
    """Test getting provider for an invalid provider name."""
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_embedding_provider("invalid_provider", "some-model")
