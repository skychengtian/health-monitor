#!/usr/bin/env python3
import os, time, sys
import requests

TIMEOUT = float(os.getenv("TIMEOUT", "5"))
RETRIES = int(os.getenv("RETRIES", "3"))

CHECKS = [
    # name, url, expected_status, max_latency_ms, expect_substring(optional)
    ("edge", os.getenv("URL_EDGE", "https://sf.epochtimes.com/favicon.ico"), 200, int(os.getenv("MAX_MS_EDGE", "800")), None),
    ("app",  os.getenv("URL_APP",  "https://sf.epochtimes.com/"),           200, int(os.getenv("MAX_MS_APP",  "1500")), None),
]

UA = os.getenv("UA", "healthcheck/1.0 (+github-actions)")

def check_one(name, url, expected, max_ms, substr):
    t0 = time.time()
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA}, allow_redirects=True)
    ms = int((time.time() - t0) * 1000)

    ok = (r.status_code == expected) and (ms <= max_ms)
    detail = f"{name} code={r.status_code} latency_ms={ms} url={url}"

    if substr is not None:
        ok = ok and (substr in r.text)
        detail += f" substr_ok={substr in r.text}"

    return ok, detail

def main():
    last = []
    for attempt in range(1, RETRIES + 1):
        last = []
        all_ok = True
        for c in CHECKS:
            ok, detail = check_one(*c)
            last.append((ok, detail))
            all_ok = all_ok and ok

        if all_ok:
            print("OK | " + " | ".join(d for _, d in last))
            return 0

        time.sleep(1)

    bad = " | ".join(d for ok, d in last if not ok)
    print("ALERT | " + bad, file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())