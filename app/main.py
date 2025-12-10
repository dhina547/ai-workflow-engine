# app/main.py
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import Dict, Any
from .engine import GraphEngine
from .workflows import register_pipeline, get_pipeline_graph
from .models import GraphCreateRequest, GraphCreateResponse, RunRequest, RunResponse

app = FastAPI(title="Minimal Data Quality Workflow Engine")

# In-memory stores (simple for assignment)
GRAPHS: Dict[str, Dict[str, Any]] = {}
RUNS: Dict[str, Dict[str, Any]] = {}

engine = GraphEngine()
# register the pipeline nodes
register_pipeline(engine)

@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(req: GraphCreateRequest):
    graph_id = str(uuid.uuid4())
    # If user provided graph, use it; otherwise use default pipeline graph
    graph_def = req.graph if req.graph else get_pipeline_graph()
    GRAPHS[graph_id] = {"graph": graph_def, "name": req.name}
    return {"graph_id": graph_id}

def default_logger(run_id: str):
    def _log(msg: str):
        entry = {"msg": msg}
        RUNS[run_id]["log"].append(entry)
    return _log

@app.post("/graph/run", response_model=RunResponse)
async def run_graph(req: RunRequest, background_tasks: BackgroundTasks):
    graph_entry = GRAPHS.get(req.graph_id)
    if not graph_entry:
        raise HTTPException(status_code=404, detail="graph_id not found")
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {"state": dict(req.initial_state), "log": [], "finished": False}
    graph_def = graph_entry["graph"]

    async def _runner():
        logger = default_logger(run_id)
        logger(f"Starting run {run_id}")
        try:
            final_state, log = await engine.run_graph(graph_def, RUNS[run_id]["state"], run_logger=logger)
            RUNS[run_id]["state"] = final_state
            RUNS[run_id]["execution_log"] = log
            RUNS[run_id]["finished"] = True
            logger(f"Run finished. loops: {final_state.get('_loops')}, anomaly_count: {final_state.get('anomaly_count')}")
        except Exception as e:
            RUNS[run_id]["error"] = str(e)
            RUNS[run_id]["finished"] = True
            logger(f"Run error: {e}")

    # run in background
    background_tasks.add_task(_runner)
    return {"run_id": run_id, "started": True}

@app.get("/graph/state/{run_id}")
async def get_run_state(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run_id not found")
    return {"state": run.get("state"), "log": run.get("log"), "finished": run.get("finished"), "error": run.get("error", None)}
