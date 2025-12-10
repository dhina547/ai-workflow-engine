# Data Quality Pipeline - Minimal Workflow Engine

This project implements a minimal workflow/graph engine and an example data-quality pipeline (Option C from the assignment).

## Features
- Nodes are Python functions that read/modify a shared state.
- Tool registry (in `app/tools.py`) for profiling, anomaly detection, rules generation, and rule application.
- Edges and branching: evaluate node decides whether to loop back to `identify`.
- Looping: pipeline repeats until anomalies <= threshold or max loops reached.
- FastAPI endpoints:
  - `POST /graph/create` — create a graph (returns `graph_id`)
  - `POST /graph/run` — run a graph with `initial_state` (returns `run_id`)
  - `GET /graph/state/{run_id}` — get current state & logs

## How to run
1. Create virtual env and install:
```bash
python -m venv .venv
# linux/macos
source .venv/bin/activate
# windows (powershell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
