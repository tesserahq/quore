# Define a Pydantic model for the request body
from typing import Dict, Optional
from pydantic import BaseModel


class IngestTextRequest(BaseModel):
    ref_id: str
    text: str
    labels: Optional[Dict[str, str]] = None
