# app/engine.py
import asyncio
import uuid
from typing import Callable, Dict, Any, Optional, Tuple, List

Node = Callable[[Dict[str, Any]], Dict[str, Any]]

class GraphEngine:
    def __init__(self):
        # node registry: name -> function
        self.nodes: Dict[str, Node] = {}

    def register_node(self, name: str, fn: Node):
        self.nodes[name] = fn

    async def run_graph(self, graph_def: Dict[str, Any], initial_state: Dict[str, Any], run_logger: Optional[Callable[[str], None]]=None) -> Tuple[Dict[str, Any], List[Dict[str,Any]]]:
        """
        graph_def expected shape:
        {
          "start": "profile",
          "edges": {
              "profile": {"next": "identify"},
              "identify": {"next": "generate_rules"},
              "generate_rules": {"next": "apply_rules"},
              "apply_rules": {"next": "evaluate"},
              "evaluate": {"next_on_pass": null, "next_on_fail": "identify"}
          }
        }
        Looping achieved via evaluate node deciding next path.
        """
        state = dict(initial_state)
        log: List[Dict[str,Any]] = []
        current = graph_def.get("start")
        run_id = str(uuid.uuid4())

        async def call_node(node_name: str, state: Dict[str,Any]) -> Dict[str,Any]:
            fn = self.nodes.get(node_name)
            if fn is None:
                raise ValueError(f"Node {node_name} not registered")
            maybe = fn(state)
            if asyncio.iscoroutine(maybe):
                maybe = await maybe
            return maybe

        while current:
            entry = {"node": current, "before_state_snapshot": {k: state.get(k) for k in list(state)[:10]}}
            if run_logger:
                run_logger(f"Running node: {current}")
            try:
                new_state = await call_node(current, state)
            except Exception as e:
                entry["error"] = str(e)
                log.append(entry)
                if run_logger:
                    run_logger(f"Error in node {current}: {e}")
                break

            state.update(new_state)
            entry["after_state_snapshot"] = {k: state.get(k) for k in list(state)[:10]}
            log.append(entry)

            # decide next node from graph_def edges
            edges = graph_def.get("edges", {})
            node_edge = edges.get(current, {})

            # support branching keys: next, next_on_pass, next_on_fail
            if "next" in node_edge:
                current = node_edge["next"]
            elif "next_on_pass" in node_edge and "next_on_fail" in node_edge:
                # evaluate should set state['pass'] = True/False
                cond = state.get("pass", False)
                current = node_edge["next_on_pass"] if cond else node_edge["next_on_fail"]
            else:
                current = None

            # safety: avoid infinite loop by max iterations
            if len(log) > 500:
                raise RuntimeError("Too many iterations; possible infinite loop")
        return state, log
