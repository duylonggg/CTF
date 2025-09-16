#!/usr/bin/env python3
from pwn import remote
import os, json, hashlib, time, random

# === helpers: hash & merkle (khớp server) ===
def sha256(b: bytes) -> bytes: return hashlib.sha256(b).digest()
def hexf(b: bytes) -> str: return b.hex()

def commit_vertex(v: int, color_label: int, nonce: bytes) -> bytes:
    return sha256(b"vertex:" + str(v).encode() + b":" + str(color_label).encode() + b":" + nonce)

# --- Merkle tree (bytes) + update O(log n) ---
def build_merkle_levels(leaves_bytes):
    """Return levels: levels[0]=leaves (bytes), ..., levels[-1]=[root]"""
    if not leaves_bytes:
        empty = sha256(b"")
        return [[empty]]
    levels = [list(leaves_bytes)]
    cur = levels[0]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            L = cur[i]
            R = cur[i+1] if i+1 < len(cur) else L  # duplicate last
            nxt.append(sha256(L + R))
        levels.append(nxt)
        cur = nxt
    return levels

def root_hex(levels):
    return hexf(levels[-1][0])

def update_leaf(levels, idx, new_hash):
    """In-place update leaf at index idx with new_hash (bytes), O(log n)."""
    levels[0][idx] = new_hash
    i = idx
    for h in range(len(levels) - 1):
        layer = levels[h]
        parent = levels[h+1]
        j = i // 2
        if i % 2 == 0:
            L = layer[i]
            R = layer[i+1] if i+1 < len(layer) else L
            parent[j] = sha256(L + R)
        else:
            L = layer[i-1]
            R = layer[i]
            parent[j] = sha256(L + R)
        i = j

def merkle_proof_for_index(levels, index):
    """Proof from in-memory levels (bytes) → [(sibling_hex, sibling_is_left), ...]."""
    proof = []
    idx = index
    for h in range(len(levels) - 1):
        layer = levels[h]
        if idx % 2 == 0:
            sib = idx + 1 if idx + 1 < len(layer) else idx
            proof.append((hexf(layer[sib]), False))
        else:
            sib = idx - 1
            proof.append((hexf(layer[sib]), True))
        idx //= 2
    return proof

# --- commit helper (giữ nguyên) ---
def commit_vertex(v: int, color_label: int, nonce: bytes) -> bytes:
    return sha256(b"vertex:" + str(v).encode() + b":" + str(color_label).encode() + b":" + nonce)

def fs_index(root_hex: str, m: int) -> int:
    return int.from_bytes(hashlib.sha256(root_hex.encode()).digest(), "big") % m

# === solve one round: incremental merkle ===
def solve_round(n, edges, max_attempts=256):
    # random màu chuẩn -> P(diff) ≈ 2/3
    colors = [random.randint(0, 2) for _ in range(n)]
    # nonces & leaves ban đầu
    nonces = [os.urandom(16) for _ in range(n)]
    leaves = [commit_vertex(i, colors[i], nonces[i]) for i in range(n)]
    levels = build_merkle_levels(leaves)

    # thử đổi root bằng cách đổi đúng 1 lá mỗi lần (O(log n))
    pick = 0  # chỉ số lá để xoay vòng cập nhật
    for _ in range(max_attempts):
        rhex = root_hex(levels)
        idx = fs_index(rhex, len(edges))
        u, v = edges[idx]
        if colors[u] != colors[v]:
            # build openings chỉ cho u,v
            openings = {}
            for w in (u, v):
                openings[str(w)] = {
                    "color": colors[w],
                    "nonce": hexf(nonces[w]),
                    "merkle_proof": merkle_proof_for_index(levels, w),
                }
            return {"merkle_root": rhex, "openings": openings}

        # chưa được → đổi 1 nonce & cập nhật lên root
        # xoay vòng lá để “nhảy” không gian root rộng hơn
        pick = (pick + 7919) % n  # bước nhảy prime để tránh lặp ngắn
        nonces[pick] = os.urandom(16)
        newleaf = commit_vertex(pick, colors[pick], nonces[pick])
        update_leaf(levels, pick, newleaf)

    # cực xui: random lại cả màu & rebuild 1 lần
    colors = [random.randint(0, 2) for _ in range(n)]
    for i in range(n):
        nonces[i] = os.urandom(16)
        leaves[i] = commit_vertex(i, colors[i], nonces[i])
    levels = build_merkle_levels(leaves)
    rhex = root_hex(levels)
    idx = fs_index(rhex, len(edges))
    u, v = edges[idx]
    openings = {}
    for w in (u, v):
        openings[str(w)] = {
            "color": colors[w],
            "nonce": hexf(nonces[w]),
            "merkle_proof": merkle_proof_for_index(levels, w),
        }
    return {"merkle_root": rhex, "openings": openings}

def main():
    host, port = "zkpow.chal.imaginaryctf.org", 1337
    io = remote(host, port)

    # banner
    io.recvuntil(b"==zk-proof-of-work: enabled==")

    for r in range(50):
        io.recvuntil(b"==round")
        io.recvline()  # consume the rest of '==round i=='
        line = io.recvline()  # the big JSON line: {"n":..., "edges":[...]}
        job = json.loads(line.decode())
        n, edges = job["n"], job["edges"]

        t0 = time.time()
        proof = solve_round(n, edges)
        payload = json.dumps(proof, separators=(",", ":")).encode()
        io.sendline(payload)                # gửi ngay, không chờ 'proof:'
        status = io.recvline(timeout=10)    # sẽ thấy 'proof: verified!' hoặc 'proof: too slow!'
        print(f"[round {r}] {status and status.strip().decode()} (solve {time.time()-t0:.3f}s)")
        if not status or b"too slow" in status or b"failed" in status:
            io.close()
            return  # hoặc bọc vòng retry phiên

    # nếu qua 50 vòng, server in flag
    rest = io.recvall(timeout=2).decode(errors="ignore")
    print(rest)

if __name__ == "__main__":
    main()
