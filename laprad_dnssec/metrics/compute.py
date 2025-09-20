
# metrics/compute.py
import json, math
import numpy as np

def upstream_qps(total_upstream_queries:int, duration_s:int) -> float:
    return total_upstream_queries / max(1, duration_s)

def cache_hit_rate(hits:int, total:int) -> float:
    return hits / total if total > 0 else 0.0

def cpu_per_request(cpu_percent:float, qps:float) -> float:
    if qps <= 0: return math.nan
    return cpu_percent / qps

def p_tail(values_ms, p=95):
    if not values_ms: return math.nan
    arr = np.array(values_ms, dtype=float)
    return float(np.percentile(arr, p))

def summarize_loadgen(loadgen_json_path:str):
    with open(loadgen_json_path, "r") as f:
        s = json.load(f)
    total = s.get("ok",0) + s.get("err",0)
    return {
        "ok": s.get("ok",0),
        "err": s.get("err",0),
        "total": total,
        "rtt_p95_ms": p_tail(s.get("rtts_ms",[]), 95),
        "rtt_p99_ms": p_tail(s.get("rtts_ms",[]), 99),
        "avg_bytes": s.get("bytes",0) / max(1, s.get("ok",1)),
    }

def combine_for_report(duration_s:int,
                       upstream_queries:int,
                       cache_hits:int,
                       total_responses:int,
                       cpu_percent:float,
                       loadgen_summary:dict):
    qps = upstream_qps(upstream_queries, duration_s)
    return {
        "upstream_qps": qps,
        "cache_hit_pct": 100.0 * cache_hit_rate(cache_hits, total_responses),
        "cpu_per_req_rel": cpu_per_request(cpu_percent, qps),
        "p95_ms": loadgen_summary.get("rtt_p95_ms"),
        "p99_ms": loadgen_summary.get("rtt_p99_ms"),
    }
