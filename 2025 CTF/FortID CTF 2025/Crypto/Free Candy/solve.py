#!/usr/bin/env python3
from pwn import remote, context
from hashlib import sha256
import json, base64, random, time, re

# ===========================
# Config
# ===========================
context.log_level = "info"   # đổi "debug" để soi I/O
HOST = "0.cloud.chals.io"
PORT = 19521

# ===========================
# secp256k1 (thuần Python)
# ===========================
p  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a4 = 0
a6 = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G  = (Gx, Gy)
O  = None

def inv_mod(a, m): return pow(a % m, -1, m)

def ec_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return O
    if P != Q:
        lam = ((y2 - y1) * inv_mod((x2 - x1) % p, p)) % p
    else:
        lam = ((3 * x1 * x1 + a4) * inv_mod((2 * y1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P):
    k %= n
    if k == 0 or P is None: return O
    R, Q = O, P
    while k:
        if k & 1: R = ec_add(R, Q)
        Q = ec_add(Q, Q); k >>= 1
    return R

def r_from_k(k):
    R = ec_mul(k, G);  Rx = R[0]
    return Rx % n

def z_from_msg(m: bytes):
    return int.from_bytes(sha256(m).digest(), 'big') % n

def ecdsa_sign_raw(d, m_bytes, k):
    z = z_from_msg(m_bytes)
    while True:
        k %= n
        if k == 0: k = random.randrange(1, n)
        r = r_from_k(k)
        if r == 0:
            k = random.randrange(1, n); continue
        s = (inv_mod(k, n) * (z + r * d)) % n
        if s == 0:
            k = random.randrange(1, n); continue
        return r, s

# ===========================
# Berlekamp–Massey trên GF(n)
# ===========================
def berlekamp_massey(seq, mod):
    C = [1]; B = [1]
    L = 0; m = 1; b = 1
    for N in range(len(seq)):
        d = seq[N] % mod
        for i in range(1, L+1):
            d = (d + C[i] * seq[N - i]) % mod
        if d == 0:
            m += 1
            continue
        T = C + [0]*(N+1 - len(C))
        coef = (d * inv_mod(b, mod)) % mod
        B_ext = B + [0]*(N+1 - len(B))
        for i in range(m, N+1):
            if i < len(C):
                C[i] = (C[i] - coef * B_ext[i - m]) % mod
            else:
                C.append((-coef * B_ext[i - m]) % mod)
        if 2*L <= N:
            L_new = N + 1 - L
            B = T
            b = d
            L = L_new
            m = 1
        else:
            m += 1
    a = [(-C[i]) % mod for i in range(1, L+1)]
    return L, a  # x_k = sum_{j=1..L} a[j-1] * x_{k-j}

def build_states(tids, L):
    return [[x % n for x in tids[i:i+L]] for i in range(0, len(tids)-L+1)]

# ===========================
# Giải hệ tuyến tính mod n
# ===========================
def gauss_mod(A, b, mod):
    A = [row[:] for row in A]
    b = b[:]
    r, c = 0, 0
    nrow, ncol = len(A), len(A[0])
    where = [-1]*ncol
    while r < nrow and c < ncol:
        piv = None
        for i in range(r, nrow):
            if A[i][c] % mod != 0:
                piv = i; break
        if piv is None:
            c += 1; continue
        A[r], A[piv] = A[piv], A[r]
        b[r], b[piv] = b[piv], b[r]
        inv = inv_mod(A[r][c], mod)
        for j in range(c, ncol):
            A[r][j] = (A[r][j] * inv) % mod
        b[r] = (b[r] * inv) % mod
        for i in range(nrow):
            if i != r and A[i][c] != 0:
                factor = A[i][c] % mod
                for j in range(c, ncol):
                    A[i][j] = (A[i][j] - factor * A[r][j]) % mod
                b[i] = (b[i] - factor * b[r]) % mod
        where[c] = r
        r += 1; c += 1
    x = [0]*ncol
    for j in range(ncol):
        if where[j] != -1:
            x[j] = b[where[j]] % mod
    for i in range(nrow):
        s = 0
        for j in range(ncol):
            s = (s + A[i][j] * x[j]) % mod
        if s != b[i] % mod:
            raise ValueError("No solution / inconsistent system")
    return x

# ===========================
# I/O với server (rất bền)
# ===========================
B64_IN_LINE = re.compile(r'([A-Za-z0-9+/=]{60,})')  # vé dài: bắt base64 ở bất kỳ chỗ nào
MENU_ANCHOR = b"Claim your prize"  # dòng cuối menu

def _read_menu(io, tout=40):
    # Nuốt toàn bộ banner + menu
    io.recvuntil(MENU_ANCHOR, timeout=tout)
    try:
        io.recvline(timeout=2)  # nuốt newline sau anchor
    except Exception:
        pass

def _read_ticket_line(io, wait_secs=35):
    # Chờ tới khi thấy 1 dòng chứa base64 (có thể có tiền tố)
    deadline = time.time() + wait_secs
    while time.time() < deadline:
        try:
            line = io.recvline(timeout=3)
        except EOFError:
            return None
        if not line:
            continue
        s = line.decode("utf-8", "ignore").strip()
        m = B64_IN_LINE.search(s)
        if m:
            return m.group(1)
        # nếu vô tình in lại menu, caller sẽ xử lý
        if s.endswith("Claim your prize"):
            return None
    return None

def fetch_chain_once():
    """
    Lấy 1 chuỗi vé trong MỘT phiên:
      - 1) Get a free ticket
      - 2) Claim vé cuối; nếu ticket_id chẵn -> server reset -> in 'brand new ticket: <b64>'
         lặp đến khi không còn vé mới.
    Trả về: list các vé base64 (liên tiếp)
    """
    io = remote(HOST, PORT, timeout=60)
    tickets = []

    # 1) menu + get free
    _read_menu(io, tout=50)
    io.sendline(b"1")
    first_b64 = _read_ticket_line(io, wait_secs=50)
    if not first_b64:
        # có thể menu in lại xen giữa: thử hút menu nữa rồi chờ
        _read_menu(io, tout=20)
        first_b64 = _read_ticket_line(io, wait_secs=15)
    if not first_b64:
        io.close()
        return tickets
    tickets.append(first_b64)

    # 2) chain bằng claim
    while True:
        _read_menu(io, tout=25)
        io.sendline(b"2")
        io.recvuntil(b"Enter your ticket:", timeout=15)
        io.sendline(tickets[-1].encode())

        got_new = False
        deadline = time.time() + 20
        while time.time() < deadline:
            part = io.recvline(timeout=3)
            if not part:
                continue
            s = part.decode("utf-8", "ignore").strip()

            if "brand new ticket" in s:
                m = B64_IN_LINE.search(s)
                if m:
                    tickets.append(m.group(1))
                    got_new = True
                    break

            if s.startswith("You won some free candy"):
                got_new = False
                break

            if s.endswith("Claim your prize"):
                break

        if not got_new:
            break

    io.close()
    return tickets

def claim(ticket_b64):
    io = remote(HOST, PORT, timeout=60)
    _read_menu(io, tout=40)
    io.sendline(b"2")
    io.recvuntil(b"Enter your ticket:", timeout=20)
    io.sendline(ticket_b64.encode())

    chunks = []
    deadline = time.time() + 8
    while time.time() < deadline:
        part = io.recv(timeout=1)
        if part:
            chunks.append(part)
    io.close()
    return b"".join(chunks).decode("utf-8", "ignore")

# ===========================
# Parse ticket & canonical payload
# ===========================
def parse_ticket(b64s):
    raw = base64.b64decode(b64s)
    t = json.loads(raw.decode())
    tid = int(t["payload"]["ticket_id"])
    sig = bytes.fromhex(t["signature"])
    r = int.from_bytes(sig[:32], 'big')
    s = int.from_bytes(sig[32:], 'big')
    payload_bytes = json.dumps({"ticket_id": tid}, separators=(',', ':'), sort_keys=True).encode()
    z = z_from_msg(payload_bytes)
    return tid % n, r % n, s % n, z % n

# ===========================
# Giải end-to-end
# ===========================
def solve_once(max_sessions=80):
    """
    - Thử tối đa max_sessions phiên để kiếm chuỗi đủ dài (>= 2L+1, thường L=2).
    - Dựng hệ TUYẾN TÍNH trực tiếp:  [ s_i*state_i | -r_i ] · [u ; d] = z_i  (mod n)
      -> tránh ambiguity dấu k, lấy luôn private key d.
    """
    best = []
    for attempt in range(1, max_sessions+1):
        chain = fetch_chain_once()
        if len(chain) > len(best):
            best = chain
        context.log_level and context.log_level in ["info","debug"] and print(f"[info] session {attempt}: got {len(chain)} tickets; best={len(best)}")
        if len(best) >= 14:  # dư dả
            break

    if len(best) < 6:
        raise RuntimeError(f"Chuỗi vé quá ngắn ({len(best)}). Chạy lại script để gặp chuỗi dài hơn.")

    # Parse tất cả vé
    tids, rs, ss, zs = [], [], [], []
    for b64 in best:
        tid, r, s, z = parse_ticket(b64)
        tids.append(tid); rs.append(r); ss.append(s); zs.append(z)

    # Berlekamp–Massey để lấy bậc L và build states
    L, _ = berlekamp_massey(tids, n)
    if L < 2 and len(tids) >= 4:
        L = 2
    if len(tids) < 2*L + 1:
        raise RuntimeError(f"Cần ≥ {2*L+1} vé liên tiếp; hiện có {len(tids)} (L={L}).")
    states = build_states(tids, L)
    S = len(states)

    # Dựng hệ A w = b  với w = [u0..u_{L-1}, d]
    rows = []
    rhs  = []
    max_rows = min(S, L + 10)   # lấy dư vài dòng để ổn định
    for i in range(max_rows):
        st = states[i]
        row = [(ss[i] * st[k]) % n for k in range(L)] + [(-rs[i]) % n]
        rows.append(row)
        rhs.append(zs[i])

    # Giải w
    w = gauss_mod(rows, rhs, n)
    u = [w[k] % n for k in range(L)]
    d = w[L] % n

    # Verify nhanh trên 3 mẫu
    ok = 0
    for i in range(min(6, S)):
        k_i = sum((u[j]*states[i][j]) % n for j in range(L)) % n
        if k_i == 0: continue
        r_i, s_i, z_i = rs[i], ss[i], zs[i]
        s_check = (inv_mod(k_i, n) * (z_i + r_i * d)) % n
        if s_check == s_i:
            ok += 1
    if ok < 2:
        raise RuntimeError("Không xác minh được nghiệm (u,d). Hãy chạy lại để lấy chuỗi khác/ dài hơn.")

    # Ký ticket target
    tid_target = int.from_bytes(sha256(b"I'd like the flag please").digest(), 'big')
    payload_bytes = json.dumps({"ticket_id": tid_target}, separators=(',', ':'), sort_keys=True).encode()
    # k ngẫu nhiên
    for _ in range(64):
        k = random.randrange(1, n)
        r, s = ecdsa_sign_raw(d, payload_bytes, k)
        if r and s:
            break
    sig_hex = (r.to_bytes(32, 'big') + s.to_bytes(32, 'big')).hex()
    ticket = {"payload": {"ticket_id": tid_target}, "signature": sig_hex}
    ticket_b64 = base64.b64encode(json.dumps(ticket, separators=(',', ':'), sort_keys=True).encode()).decode()
    return ticket_b64

def main():
    tid_target = int.from_bytes(sha256(b"I'd like the flag please").digest(), 'big')
    print("tid_target =", tid_target)
    random.seed(int(time.time()*1000) & 0xffffffff)
    ticket_b64 = solve_once()
    print("[+] Submitting crafted ticket...")
    resp = claim(ticket_b64)
    print(resp)

if __name__ == "__main__":
    main()
