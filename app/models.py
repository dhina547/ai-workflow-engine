# app/models.py
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class GraphCreateRequest(BaseModel):
    graph: Dict[str, Any]
    name: Optional[str] = "data_quality_pipeline"

class GraphCreateResponse(BaseModel):
    graph_id: str

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class RunResponse(BaseModel):
    run_id: str
    started: bool
