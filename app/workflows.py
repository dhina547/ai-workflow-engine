# app/workflows.py
from .tools import profile_data, identify_anomalies, generate_rules, apply_rules
from typing import Dict, Any

def register_pipeline(engine):
    """
    Registers nodes for the Data Quality Pipeline:
    Nodes: profile -> identify -> generate_rules -> apply_rules -> evaluate
    evaluate decides whether to loop back to 'identify' or finish.
    """
    # profile node: produce profile and keep data
    def profile_node(state: Dict[str, Any]) -> Dict[str, Any]:
        out = profile_data({"data": state.get("data")})
        return {"profile": out["profile"], "row_count": out["row_count"]}

    def identify_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return identify_anomalies(state)

    def generate_rules_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return generate_rules(state)

    def apply_rules_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return apply_rules(state)

    def evaluate_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set state['pass'] True if anomaly_count <= threshold else False.
        Threshold comes from state['anomaly_threshold'] (default 0).
        Also increment a loop counter to avoid infinite loops.
        """
        threshold = int(state.get("anomaly_threshold", 0))
        anomaly_count = int(state.get("anomaly_count", 0))
        loops = int(state.get("_loops", 0)) + 1
        state_update = {"_loops": loops}
        state_update["pass"] = anomaly_count <= threshold
        state_update["status"] = "done" if state_update["pass"] else "retry"
        # safety: force pass if too many loops
        if loops > int(state.get("max_loops", 5)):
            state_update["pass"] = True
            state_update["status"] = "forced_done"
        return state_update

    engine.register_node("profile", profile_node)
    engine.register_node("identify", identify_node)
    engine.register_node("generate_rules", generate_rules_node)
    engine.register_node("apply_rules", apply_rules_node)
    engine.register_node("evaluate", evaluate_node)

# Graph definition factory
def get_pipeline_graph():
    return {
        "start": "profile",
        "edges": {
            "profile": {"next": "identify"},
            "identify": {"next": "generate_rules"},
            "generate_rules": {"next": "apply_rules"},
            "apply_rules": {"next": "evaluate"},
            "evaluate": {"next_on_pass": None, "next_on_fail": "identify"}
        }
    }
