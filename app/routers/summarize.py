from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.index_manager import IndexManager
from app.db import get_db
from app.models.project import Project
from app.utils.auth import get_current_user
from pydantic import BaseModel
from llama_index.core import Document, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from app.routers.utils.dependencies import get_project_by_id
from typing import Optional
from app.services.prompt_service import PromptService

router = APIRouter(
    prefix="/projects/{project_id}/summarize",
    tags=["summarize"],
    responses={404: {"description": "Not found"}},
)


class SummarizeRequest(BaseModel):
    text: str
    labels: Optional[dict] = None
    prompt_id: Optional[str] = None


class SummarizeResponse(BaseModel):
    summary: str
    labels: dict


@router.post("", response_model=SummarizeResponse)
def summarize(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    project: Project = Depends(get_project_by_id),
):
    """
    Summarize the text for a project.
    """
    if request.prompt_id is None:
        system_prompt = project.system_prompt
    else:
        prompt_service = PromptService(db)
        system_prompt = prompt_service.get_prompt_by_id_or_prompt_id(request.prompt_id)
        if system_prompt is None:
            raise HTTPException(status_code=404, detail="Prompt not found")
        system_prompt = system_prompt.prompt

    index_manager = IndexManager(db, project)
    documents = [Document(text=request.text, metadata={"labels": request.labels})]
    splitter = SentenceSplitter(chunk_size=2048)
    nodes = splitter.get_nodes_from_documents(documents)
    summary_index = SummaryIndex(nodes)
    summary_query_engine = summary_index.as_query_engine(
        llm=index_manager.llm(),
        response_mode="tree_summarize",
        use_async=True,
    )
    summary = summary_query_engine.query(system_prompt)

    return SummarizeResponse(
        summary=summary.response,
        labels={"project_id": project.id},
    )
