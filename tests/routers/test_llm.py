from app.constants.providers import LLM_PROVIDERS, MOCK_PROVIDER


def test_get_llm_providers(client):
    """Test GET /llm/providers endpoint."""
    response = client.get("/llm/providers")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

    # Check that all providers except mock are present
    provider_names = {provider["name"] for provider in data["data"]}
    expected_providers = set(LLM_PROVIDERS) - {MOCK_PROVIDER}
    assert provider_names == expected_providers

    # Check that each provider has the required fields
    for provider in data["data"]:
        assert "name" in provider
        assert "embedding_models" in provider
        assert isinstance(provider["embedding_models"], list)

        # Check that each embedding model has the required fields
        for model in provider["embedding_models"]:
            assert "embed_model" in model
            assert "default_embed_dim" in model
            assert "available_dimensions" in model
            assert "max_tokens" in model
            assert "miracl_avg" in model
            assert "mteb_avg" in model
