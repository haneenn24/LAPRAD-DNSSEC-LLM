
# experiments/e1_rr_ttl_floor/run_e1.py
# E1: RRset TTL Floor — vary RR TTL and min-cache-ttl; warm vs cold cache.
import os, json
from pathlib import Path
from utils.loadgen import run as lg_run
from utils.bind_tools import rndc_flush, set_min_cache_ttl, set_rr_ttl
from metrics.compute import summarize_loadgen, combine_for_report

# Inline config (Python only, no YAML)
CONFIG = {
    "resolver_ip": "127.0.0.1",
    "zone": "test.example",
    "duration_s": 60,
    "qps": 200,
    "mix_ratio": 0.5,
    "matrix": {
        "rr_ttl_s": [2, 10, 60],
        "min_cache_ttl_s": [0, 60],
        "cache_state": ["cold", "warm"]
    }
}

def main():
    outdir = Path("experiments/e1_rr_ttl_floor/out"); outdir.mkdir(parents=True, exist_ok=True)

    for rr_ttl in CONFIG["matrix"]["rr_ttl_s"]:
        for min_ttl in CONFIG["matrix"]["min_cache_ttl_s"]:
            for state in CONFIG["matrix"]["cache_state"]:
                tag = f"rr{rr_ttl}_min{min_ttl}_{state}"
                print(f"=== E1 case: {tag} ===")
                set_rr_ttl(rr_ttl)
                set_min_cache_ttl(min_ttl)

                if state == "cold":
                    rndc_flush()

                stats = lg_run("mixed", CONFIG["resolver_ip"], CONFIG["zone"], CONFIG["qps"], CONFIG["duration_s"], CONFIG["mix_ratio"])
                raw_path = outdir / f"{tag}_loadgen.json"
                with open(raw_path, "w") as f:
                    json.dump(stats, f)

                # Replace these placeholders with parsed values from named stats in your setup
                upstream_queries = stats["ok"] + stats["err"]
                cache_hits = int(stats["ok"] * 0.5)
                total_responses = stats["ok"] + stats["err"]
                cpu_percent = 0.0

                lg_sum = summarize_loadgen(raw_path)
                row = combine_for_report(CONFIG["duration_s"], upstream_queries, cache_hits, total_responses, cpu_percent, lg_sum)
                row["case"] = tag

                csv_path = outdir / "e1_results.csv"
                header = not csv_path.exists()
                with open(csv_path, "a") as f:
                    if header:
                        f.write("case,upstream_qps,cache_hit_pct,cpu_per_req_rel,p95_ms,p99_ms\n")
                    f.write(f"{row['case']},{row['upstream_qps']:.2f},{row['cache_hit_pct']:.2f},{row['cpu_per_req_rel']:.6f},{row['p95_ms']:.2f},{row['p99_ms']:.2f}\n")
                print(f"[done] {tag}")

if __name__ == "__main__":
    main()
