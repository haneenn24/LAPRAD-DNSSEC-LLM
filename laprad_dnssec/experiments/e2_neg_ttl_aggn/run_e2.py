
# experiments/e2_neg_ttl_aggn/run_e2.py
# E2: Negative TTL × Aggressive Negative Caching — NX proofs cost and AggNeg benefits.
import os, json
from pathlib import Path
from utils.loadgen import run as lg_run
from utils.bind_tools import rndc_flush, enable_aggressive_neg, set_negative_ttl
from metrics.compute import summarize_loadgen, combine_for_report

CONFIG = {
    "resolver_ip": "127.0.0.1",
    "zone": "test.example",
    "duration_s": 60,
    "qps": 200,
    "matrix": {
        "neg_ttl_s": [2, 10, 60],
        "aggressive_neg": [False, True]
    }
}

def main():
    outdir = Path("experiments/e2_neg_ttl_aggn/out"); outdir.mkdir(parents=True, exist_ok=True)

    for neg_ttl in CONFIG["matrix"]["neg_ttl_s"]:
        for aggn in CONFIG["matrix"]["aggressive_neg"]:
            tag = f"neg{neg_ttl}_aggn{'on' if aggn else 'off'}"
            print(f"=== E2 case: {tag} ===")
            set_negative_ttl(neg_ttl)
            enable_aggressive_neg(on=aggn)
            rndc_flush()

            stats = lg_run("misses", CONFIG["resolver_ip"], CONFIG["zone"], CONFIG["qps"], CONFIG["duration_s"])
            raw_path = outdir / f"{tag}_loadgen.json"
            with open(raw_path, "w") as f:
                json.dump(stats, f)

            upstream_queries = stats["ok"] + stats["err"]
            cache_hits = 0
            total_responses = stats["ok"] + stats["err"]
            cpu_percent = 0.0

            lg_sum = summarize_loadgen(raw_path)
            row = combine_for_report(CONFIG["duration_s"], upstream_queries, cache_hits, total_responses, cpu_percent, lg_sum)
            row["case"] = tag

            csv_path = outdir / "e2_results.csv"
            header = not csv_path.exists()
            with open(csv_path, "a") as f:
                if header:
                    f.write("case,upstream_qps,cache_hit_pct,cpu_per_req_rel,p95_ms,p99_ms\n")
                f.write(f"{row['case']},{row['upstream_qps']:.2f},{row['cache_hit_pct']:.2f},{row['cpu_per_req_rel']:.6f},{row['p95_ms']:.2f},{row['p99_ms']:.2f}\n")
            print(f"[done] {tag}")

if __name__ == "__main__":
    main()
