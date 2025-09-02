from fastapi import APIRouter
from app.constants.providers import (
    LLM_PROVIDERS,
    get_embedding_models,
    MOCK_PROVIDER,
    get_llm_models,
)
from app.schemas.common import ListResponse
from app.schemas.llm import Provider

router = APIRouter(
    prefix="/llm",
    tags=["llm"],
    responses={404: {"description": "Not found"}},
)


@router.get("/providers", response_model=ListResponse[Provider])
def get_llm_providers():
    """Get the list of available LLM providers and their embedding models."""
    providers_info = [
        Provider(
            name=provider,
            embedding_models=get_embedding_models(provider),
            available_llms=get_llm_models(provider),
        )
        for provider in LLM_PROVIDERS
        if provider != MOCK_PROVIDER
    ]
    return ListResponse(data=providers_info)
