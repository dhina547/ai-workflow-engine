# app/tools.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Simple profiling: missing percentage, mean, std for numeric columns
def profile_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expect payload to have either:
    - 'data_csv' : CSV string
    - OR 'data' : list-of-dicts (records)
    """
    if "data" in payload:
        df = pd.DataFrame(payload["data"])
    elif "data_csv" in payload:
        from io import StringIO
        df = pd.read_csv(StringIO(payload["data_csv"]))
    else:
        raise ValueError("No data provided to profile")

    profile = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in df.columns:
        col_data = df[col]
        profile[col] = {
            "dtype": str(col_data.dtype),
            "missing_count": int(col_data.isna().sum()),
            "missing_pct": float(col_data.isna().mean())
        }
        if col in numeric_cols:
            profile[col].update({
                "mean": float(col_data.mean(skipna=True)),
                "std": float(col_data.std(skipna=True)),
                "min": float(col_data.min(skipna=True)) if not col_data.dropna().empty else None,
                "max": float(col_data.max(skipna=True)) if not col_data.dropna().empty else None,
            })
    return {"profile": profile, "row_count": int(len(df)), "__df_preview_head": df.head(2).to_dict(orient="records")}

# Identify anomalies using z-score threshold
def identify_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expects state to have 'data' (list of dicts)
    Returns anomaly indices and counts
    """
    import pandas as pd
    import numpy as np
    data = state.get("data")
    if data is None:
        return {"anomalies": {}, "anomaly_count": 0}

    df = pd.DataFrame(data)
    numeric = df.select_dtypes(include=[np.number])
    anomalies = {}
    total = 0
    for col in numeric.columns:
        series = numeric[col].dropna()
        if series.empty:
            anomalies[col] = []
            continue
        mean = series.mean()
        std = series.std()
        if std == 0 or np.isnan(std):
            anomalies[col] = []
            continue
        z = (numeric[col] - mean) / std
        mask = z.abs() > 3  # z-score threshold
        idxs = list(df[mask.fillna(False)].index)
        anomalies[col] = idxs
        total += len(idxs)
    return {"anomalies": anomalies, "anomaly_count": int(total)}

# Generate simple rules from profile: for numeric cols mean +/- 3*std
def generate_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    profile = state.get("profile")
    if not profile:
        return {"rules": {}}
    rules = {}
    for col, info in profile.items():
        dtype = info.get("dtype", "")
        if dtype.startswith("float") or dtype.startswith("int") or "int" in dtype:
            mean = info.get("mean")
            std = info.get("std")
            if mean is None or std is None:
                continue
            low = mean - 3 * std
            high = mean + 3 * std
            rules[col] = {"min_allowed": low, "max_allowed": high, "action": "clip"}
    return {"rules": rules}

# Apply rules: clip numeric columns to allowed range; return new anomaly count
def apply_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    data = state.get("data")
    rules = state.get("rules", {})
    if not data or not rules:
        return {}
    df = pd.DataFrame(data)
    for col, rule in rules.items():
        if col in df.columns:
            if rule.get("action") == "clip":
                df[col] = df[col].clip(lower=rule["min_allowed"], upper=rule["max_allowed"])
    new_data = df.to_dict(orient="records")
    state_update = {"data": new_data}
    # Re-identify anomalies after applying rules
    ident = identify_anomalies({"data": new_data})
    state_update.update(ident)
    return state_update
