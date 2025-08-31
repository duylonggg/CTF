# solve_fast_byte_MITM.py
# Byte-level meet-in-the-middle + modulo bitset pruning for low-density knapsack (Merkle-Hellman style)
# Usage: python3 solve_fast_byte_MITM.py [output.txt]

import re, ast, sys, string
from typing import List, Tuple

def parse_output_txt(path="output.txt"):
    s = open(path, "r", encoding="utf-8").read()
    P = ast.literal_eval(re.search(r'P\s*=\s*(\[[\s\S]*?\])', s).group(1))
    C = ast.literal_eval(re.search(r'C\s*=\s*(\[[\s\S]*?\])', s).group(1))
    assert len(P) == 64, f"Expected 64 weights, got {len(P)}"
    return P, C

def bits_to_bytes_be(bits64):
    out = bytearray()
    for b in range(8):
        v = 0
        for k in range(8):
            v = (v << 1) | bits64[b*8 + k]
        out.append(v)
    return bytes(out)

def solve_block_bytelevel(A: List[int], T: int, fixed=None, allowed=None, modulii=None):
    """
    A: 64 weights; T: target sum of the block
    fixed: {byte_index: byte_value} (0..7); allowed: set of allowed byte values
    modulii: list of moduli (mix of powers of two and primes) for pruning
    returns: bytes(8) or None
    """
    fixed = fixed or {}
    if allowed is None:
        allowed = set(range(32,127))  # printable fallback
    modulii = modulii or [8191, 12289, 1<<14]  # fast & strong

    # Build contributions per byte (8 weights -> 1 byte)
    contribs = []
    for i in range(8):
        seg = A[8*i:8*i+8]
        opts = []
        if i in fixed:
            b = fixed[i]
            tot = sum(seg[k] for k in range(8) if ((b >> (7-k)) & 1))
            opts.append((b, tot))
        else:
            for b in allowed:
                tot = sum(seg[k] for k in range(8) if ((b >> (7-k)) & 1))
                opts.append((b, tot))
        contribs.append(opts)

    # Order bytes to search: fewest options first, then smaller sum span
    order = list(range(8))
    def span(i):
        vs = [t for _,t in contribs[i]]
        return (max(vs)-min(vs)) if vs else 0
    order.sort(key=lambda i: (len(contribs[i]), span(i)))
    contribs = [contribs[i] for i in order]

    # Suffix residue bitsets per modulus (byte-level)
    mod_data = []
    for m in modulii:
        mask = (1<<m) - 1
        # Per-byte residue sets
        S = []
        for i in range(8):
            bits = 0
            for _, tot in contribs[i]:
                bits |= (1 << (tot % m))
            S.append(bits)
        # Suffix convolution: suff[i] = residues from bytes i..7
        suff = [0]*9
        suff[8] = 1
        for i in range(7, -1, -1):
            base = suff[i+1]
            cur = 0
            x = S[i]
            while x:
                lb = x & -x
                r = (lb.bit_length()-1)
                # rotate base by r (circular on m bits)
                cur |= ((base << r) | (base >> (m - r))) & mask
                x ^= lb
            suff[i] = cur
        mod_data.append({'m': m, 'mask': mask, 'suff': suff, 'targ': T % m})

    # Range bounds to prune by sums
    suf_min = [0]*9
    suf_max = [0]*9
    for i in range(7, -1, -1):
        vals = [t for _,t in contribs[i]]
        suf_min[i] = min(vals) + suf_min[i+1]
        suf_max[i] = max(vals) + suf_max[i+1]

    # DFS over 8 bytes with strong pruning
    sol = [None]*8
    def dfs(i, cur, res_mods):
        if i == 8:
            return cur == T
        # bound by sums
        if cur + suf_min[i] > T or cur + suf_max[i] < T:
            return False
        # modulo suffix check (need residue achievable by remaining bytes)
        for j, md in enumerate(mod_data):
            need = (md['targ'] - (res_mods[j] % md['m'])) % md['m']
            if ((md['suff'][i] >> need) & 1) == 0:
                return False
        # heuristic: pick options close to remaining need
        tgt_left = T - cur
        mid = (suf_min[i+1] + suf_max[i+1]) // 2
        opts = sorted(contribs[i], key=lambda x: abs(x[1] - (tgt_left - mid)))
        for bval, tot in opts:
            # per-step modulo prune for the *next* suffix
            new_res = []
            ok = True
            for j, md in enumerate(mod_data):
                m = md['m']
                r = (res_mods[j] + (tot % m)) % m
                need = (md['targ'] - r) % m
                if ((md['suff'][i+1] >> need) & 1) == 0:
                    ok = False; break
                new_res.append(r)
            if not ok:
                continue
            sol[i] = bval
            if dfs(i+1, cur+tot, tuple(new_res)):
                return True
        sol[i] = None
        return False

    start_res = tuple(0 for _ in mod_data)
    if not dfs(0, 0, start_res):
        return None, order
    # map back to original byte indexes
    out = [0]*8
    for pos, idx in enumerate(order):
        out[idx] = sol[pos]
    return bytes(out), order

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "output.txt"
    P, C = parse_output_txt(path)

    # Allowed sets
    ALPHA_CTFlike = set(ord(c) for c in (string.ascii_uppercase + string.digits + "_ -"))
    PRINTABLE = set(range(32, 127))

    out = bytearray()

    for j, T in enumerate(C):
        # Block 0: khóa 'fwectf{' cho 7 byte đầu
        if j == 0:
            fixed = {i: b for i, b in enumerate(b"fwectf{")}
            allowed = ALPHA_CTFlike
        else:
            fixed = {}
            allowed = ALPHA_CTFlike

        blk, _ = solve_block_bytelevel(P, T, fixed=fixed, allowed=allowed, modulii=[8191, 12289, 1<<14])
        if blk is None:
            # widen to all printable if CTFlike set fails
            blk, _ = solve_block_bytelevel(P, T, fixed=fixed, allowed=PRINTABLE, modulii=[8191, 12289, 1<<14])
            if blk is None:
                print(f"[!] Block {j}: no solution under ASCII assumptions. Try adding more moduli (e.g., 1<<15) or relax constraints.")
                return
        out += blk
        print(f"[block {j}] {blk}   ({blk.decode('utf-8', errors='replace')})")

    try:
        s = out.decode("utf-8")
    except:
        s = out.hex()
    print("\nRecovered:", s)

if __name__ == "__main__":
    main()
