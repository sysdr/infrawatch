import numpy as np
import pandas as pd
from scipy import stats

METRICS = ["page_views", "sessions", "revenue", "response_time", "error_rate"]

def compute_correlation_matrix(db_rows: list, method: str = "pearson") -> dict:
    df = pd.DataFrame([{
        "page_views":    r.page_views,
        "sessions":      r.sessions,
        "revenue":       r.revenue,
        "response_time": r.response_time,
        "error_rate":    r.error_rate,
    } for r in db_rows])

    if df.empty or len(df) < 3:
        return {"metrics": METRICS, "matrix": [], "pairs": []}

    matrix = []
    pairs  = []
    for m1 in METRICS:
        row = []
        for m2 in METRICS:
            if method == "spearman":
                r, p = stats.spearmanr(df[m1], df[m2])
            else:
                r, p = stats.pearsonr(df[m1], df[m2])
            r = round(float(r), 4) if not np.isnan(r) else 0.0
            p = round(float(p), 6) if not np.isnan(p) else 1.0
            row.append(r)
            if m1 < m2:
                pairs.append({
                    "x": m1, "y": m2,
                    "correlation": r, "p_value": p,
                    "significant": p < 0.05,
                })
        matrix.append(row)

    return {"metrics": METRICS, "matrix": matrix, "pairs": pairs, "method": method}
