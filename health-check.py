#!/usr/bin/env python3
import time, sys, hashlib
import requests

CHECKS = [
  # (name, url, expected_status, max_ms, expected_substring_or_none)
  ("edge", "https://sf.epochtimes.com/favicon.ico", 200, 800, None),
  ("app",  "https://sf.epochtimes.com/timeline", 200, 1500, None),
]

TIMEOUT = 5
RETRIES = 3

def one(name, url, expected, max_ms, substr):
    t0 = time.time()
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "healthcheck/1.0"})
    ms = int((time.time()-t0)*1000)

    ok = (r.status_code == expected) and (ms <= max_ms)
    if substr is not None:
        ok = ok and (substr in r.text)

    return ok, f"{name} code={r.status_code} latency_ms={ms} len={len(r.content)}"

def main():
    last = []
    for _ in range(RETRIES):
        last = []
        all_ok = True
        for c in CHECKS:
            ok, msg = one(*c)
            last.append((ok, msg))
            all_ok = all_ok and ok
        if all_ok:
            print("OK " + " | ".join(m for _, m in last))
            return 0
        time.sleep(1)

    bad = " | ".join(m for ok, m in last if not ok)
    print("ALERT " + bad, file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())