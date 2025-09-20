
# utils/loadgen.py
# Simple load generator using dnspython.
# Modes: "hits", "misses", "mixed"
import time, random, argparse
import dns.resolver

def _rand_label(n=8):
    import string
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(n))

def query_once(resolver, name, qtype="A"):
    try:
        start = time.time()
        ans = resolver.resolve(name, qtype, lifetime=3.0)
        rtt = (time.time() - start) * 1000.0
        size = sum(len(r.to_text()) for r in ans)
        return True, rtt, size
    except Exception:
        return False, None, 0

def run(mode, resolver_ip, zone, qps, duration_s, mix_ratio=0.5):
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = [resolver_ip]
    res.timeout = 3.0
    res.lifetime = 3.0

    end = time.time() + duration_s
    interval = 1.0 / max(1, qps)
    stats = {"ok":0, "err":0, "bytes":0, "rtts_ms":[]}

    while time.time() < end:
        if mode == "hits":
            name = f"www.{zone}"
        elif mode == "misses":
            name = f"{_rand_label()}.{zone}"
        else:  # mixed
            name = f"www.{zone}" if random.random() < mix_ratio else f"{_rand_label()}.{zone}"

        ok, rtt, size = query_once(res, name, qtype="A")
        if ok:
            stats["ok"] += 1
            stats["bytes"] += size
            if rtt is not None:
                stats["rtts_ms"].append(rtt)
        else:
            stats["err"] += 1
        time.sleep(interval)
    return stats

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["hits","misses","mixed"], required=True)
    ap.add_argument("--resolver", required=True, help="Resolver IP (e.g., 127.0.0.1)")
    ap.add_argument("--zone", required=True, help="Authoritative test zone, e.g., test.example")
    ap.add_argument("--qps", type=int, default=100)
    ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--mix_ratio", type=float, default=0.5, help="For mixed mode: fraction of hits")
    args = ap.parse_args()
    s = run(args.mode, args.resolver, args.zone, args.qps, args.duration, args.mix_ratio)
    print(s)

if __name__ == "__main__":
    cli()
