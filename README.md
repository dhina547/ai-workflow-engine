# Minimal Workflow Engine – Data Quality Pipeline (Option C)

A simplified workflow/graph engine built using **FastAPI**, **Python**, and a **rule-based data quality pipeline**. Developed as part of the **AI Engineering Internship Assignment**.

This engine supports:
* Nodes as Python functions
* Shared mutable state
* Directed edges (node → next node)
* Conditional branching
* Looping until a condition is met
* FastAPI endpoints for creating/running workflows
* Execution logs

---

## 🚀 1. Features

### 🔧 Workflow Engine
* **Node registration**
* **Shared state dictionary**
* **Directed edges + branching** (`next`, `next_on_pass`, `next_on_fail`)
* **Looping** until quality criteria are satisfied
* **Execution logs**
* **Background execution**

### 📊 Data Quality Pipeline (Option C)
Nodes implemented:
1.  **Profile data** — basic statistics, missing %, numeric summary
2.  **Identify anomalies** — z-score > 3
3.  **Generate rules** — mean ± 3×std
4.  **Apply rules** — clipping rule-based corrections
5.  **Evaluate** — loop until `anomaly_count ≤ anomaly_threshold`

The pipeline repeats until data becomes “clean”.

---

## 📁 2. Project Structure

```text
repo-root/
│
├── app/
│   ├── main.py              # FastAPI app + endpoints
│   ├── engine.py            # Core workflow engine
│   ├── tools.py             # Profiling, anomaly detection, rules, apply rules
│   ├── workflows.py         # Data Quality Pipeline (Option C)
│   ├── models.py            # Pydantic models for API requests
│   └── __init__.py
│
├── requirements.txt         # Python dependencies
├── README.md                # Documentation (this file)
└── .gitignore
```
## ▶️ 3. How to Run

### 1️⃣ Install dependencies

```text

pip install -r requirements.txt

```

###2️⃣ Start the FastAPI server

```bash

uvicorn app.main:app --reload

```

###3️⃣ Open the API documentation

Navigate to:

http://127.0.0.1:8000/docs

This will show the interactive Swagger UI.


##🧪 4. Example Usage


###Step 1 — Create a graph
POST /graph/create

```bash


{
  "graph": {},
  "name": "data_quality_pipeline"
}
```
Response:

JSON
```bash

{ "graph_id": "YOUR_GRAPH_ID" }
```

###Step 2 — Run the graph
POST /graph/run

Example initial_state:

```bash

{
  "graph_id": "YOUR_GRAPH_ID",
  "initial_state": {
    "data": [
      {"id": 1, "value": 10},
      {"id": 2, "value": 1000},
      {"id": 3, "value": -999},
      {"id": 4, "value": 12}
    ],
    "anomaly_threshold": 0,
    "max_loops": 5
  }
}
```
Response:

JSON
```bash

{
  "run_id": "YOUR_RUN_ID",
  "started": true
}
```
###Step 3 — Check run status
GET /graph/state/{run_id}

Example result:

JSON
```bash

{
  "state": {
    "anomaly_count": 0,
    "_loops": 1,
    "status": "done"
  },
  "log": [
    {"msg": "Running node: profile"},
    {"msg": "Running node: identify"},
    {"msg": "Running node: generate_rules"},
    {"msg": "Running node: apply_rules"},
    {"msg": "Running node: evaluate"}
  ],
  "finished": true
}
```
#🧠 5. How It Works
Workflow Engine Flow
Plaintext

profile → identify → generate_rules → apply_rules → evaluate
         
If evaluate sets pass = false, pipeline loops back to identify.

Loop stops when:

anomaly_count ≤ anomaly_threshold, OR

max_loops reached
---


#📌 6. What This Engine Demonstrates
✔ Correct API design

✔ Understanding of state → transition → loop

✔ Clean backend architecture

✔ Async background execution

✔ Practical example workflow

✔ Modular, extensible design
---


#📈 7. Improvements with More Time
Add WebSocket streaming logs

Persist graphs and runs in SQLite/Postgres

Add authentication

Add config-driven dynamic graph definitions

Add visualization of graph execution
---


#📄 8. Requirements
fastapi

uvicorn[standard]

pydantic

pandas

numpy



