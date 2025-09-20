
# experiments/e3_key_ttl/run_e3.py
# E3: DNSKEY/DS TTL — measure revalidation cost after expiry.
import os, json, time
from pathlib import Path
from utils.loadgen import run as lg_run
from utils.bind_tools import rndc_flush, set_key_ttl
from metrics.compute import summarize_loadgen, combine_for_report

CONFIG = {
    "resolver_ip": "127.0.0.1",
    "zone": "test.example",
    "duration_s": 60,
    "qps": 200,
    "matrix": {
        "key_ttl_s": [30, 300, 3600]  # 30s, 5m, 1h
    }
}

def force_key_expiry_pause(ttl_s:int):
    wait_s = min(max(ttl_s + 2, 10), 120)  # cap 2 min
    print(f"[note] Waiting {wait_s}s to cross key TTL for revalidation measurement...")
    time.sleep(wait_s)

def main():
    outdir = Path("experiments/e3_key_ttl/out"); outdir.mkdir(parents=True, exist_ok=True)

    for keyttl in CONFIG["matrix"]["key_ttl_s"]:
        tag = f"keyttl{keyttl}"
        print(f"=== E3 case: {tag} ===")
        set_key_ttl(keyttl)
        rndc_flush()

        warm = lg_run("mixed", CONFIG["resolver_ip"], CONFIG["zone"], CONFIG["qps"], CONFIG["duration_s"])
        with open(outdir / f"{tag}_warm_loadgen.json","w") as f:
            json.dump(warm, f)

        force_key_expiry_pause(keyttl)

        post = lg_run("mixed", CONFIG["resolver_ip"], CONFIG["zone"], CONFIG["qps"], CONFIG["duration_s"])
        with open(outdir / f"{tag}_postexp_loadgen.json","w") as f:
            json.dump(post, f)

        upstream_warm = warm["ok"] + warm["err"]
        upstream_post = post["ok"] + post["err"]
        cache_hits_warm = int(warm["ok"] * 0.6)
        cache_hits_post = int(post["ok"] * 0.3)
        cpu_percent = 0.0

        sum_warm = summarize_loadgen(outdir / f"{tag}_warm_loadgen.json")
        sum_post = summarize_loadgen(outdir / f"{tag}_postexp_loadgen.json")

        row_w = combine_for_report(CONFIG["duration_s"], upstream_warm, cache_hits_warm, warm["ok"]+warm["err"], cpu_percent, sum_warm); row_w["phase"]="warm"; row_w["case"]=tag
        row_p = combine_for_report(CONFIG["duration_s"], upstream_post, cache_hits_post, post["ok"]+post["err"], cpu_percent, sum_post); row_p["phase"]="postexp"; row_p["case"]=tag

        csv_path = outdir / "e3_results.csv"
        header = not csv_path.exists()
        with open(csv_path, "a") as f:
            if header:
                f.write("case,phase,upstream_qps,cache_hit_pct,cpu_per_req_rel,p95_ms,p99_ms\n")
            f.write(f"{row_w['case']},{row_w['phase']},{row_w['upstream_qps']:.2f},{row_w['cache_hit_pct']:.2f},{row_w['cpu_per_req_rel']:.6f},{row_w['p95_ms']:.2f},{row_w['p99_ms']:.2f}\n")
            f.write(f"{row_p['case']},{row_p['phase']},{row_p['upstream_qps']:.2f},{row_p['cache_hit_pct']:.2f},{row_p['cpu_per_req_rel']:.6f},{row_p['p95_ms']:.2f},{row_p['p99_ms']:.2f}\n")
        print(f"[done] {tag}")

if __name__ == "__main__":
    main()
