
# utils/bind_tools.py
# Helpers: cold/warm cache and simple config toggles (instructions).
import subprocess

def rndc_flush():
    subprocess.run(["rndc", "flush"], check=False)

def enable_aggressive_neg(on=True, named_conf_options_path="/etc/bind/named.conf.options"):
    state = "on" if on else "off"
    print(f"[note] Toggle Aggressive NSEC caching -> {state} (edit {named_conf_options_path} and 'rndc reload').")

def set_min_cache_ttl(seconds:int, conf_path:str="/etc/bind/named.conf.options"):
    print(f"[action] Set 'min-cache-ttl {seconds};' in {conf_path} and 'rndc reload'.")

def set_rr_ttl(seconds:int, zone_path:str="/var/lib/bind/test.example.zone"):
    print(f"[action] Ensure RR TTL in zone file is {seconds}s (template + resign), then 'rndc reload'.")

def set_negative_ttl(seconds:int, soa_path:str="/var/lib/bind/test.example.zone"):
    print(f"[action] Set SOA minimum/negative TTL to {seconds}s, resign zone, then 'rndc reload'.")

def set_key_ttl(seconds:int):
    print(f"[action] Ensure DNSKEY/DS TTL ≈ {seconds}s in your signer template, resign, then 'rndc reload'.")
