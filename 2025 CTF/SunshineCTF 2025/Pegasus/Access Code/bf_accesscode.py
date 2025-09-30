
#!/usr/bin/env python3
import argparse, binascii, itertools, multiprocessing as mp, os, string, sys, time

# ---------------- Gimli permutation + hash (128-bit rate, 256-bit capacity) ----------------

def _rol32(x, n):
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def _gimli_permute(state):
    # state: list of 12 uint32
    for r in range(24, 0, -1):
        for c in range(4):
            x = state[0*4 + c]
            y = state[1*4 + c]
            z = state[2*4 + c]

            x0 = _rol32(x, 24)
            y0 = _rol32(y, 9)
            z0 = z & 0xFFFFFFFF

            state[2*4 + c] = (x0 ^ ((z0 << 1) & 0xFFFFFFFF) ^ (((y0 & z0) << 2) & 0xFFFFFFFF)) & 0xFFFFFFFF
            state[1*4 + c] = (y0 ^ x0 ^ (((x0 | z0) << 1) & 0xFFFFFFFF)) & 0xFFFFFFFF
            state[0*4 + c] = (z0 ^ y0 ^ (((x0 & y0) << 3) & 0xFFFFFFFF)) & 0xFFFFFFFF

        if r % 4 == 0:
            # big swap
            state[0], state[1] = state[1], state[0]
            state[2], state[3] = state[3], state[2]
        elif r % 4 == 2:
            # small swap
            state[0], state[2] = state[2], state[0]
            state[1], state[3] = state[3], state[1]

        if r % 4 == 0:
            state[0] = (state[0] ^ ((0x9e377900 | r) & 0xFFFFFFFF)) & 0xFFFFFFFF

        # keep 32-bit
        for i in range(12):
            state[i] &= 0xFFFFFFFF
    return state

def gimli_hash(msg: bytes, outlen: int = 32, rate: int = 16) -> bytes:
    state = [0] * 12
    i = 0
    # absorb full blocks
    while len(msg) - i >= rate:
        for j in range(rate // 4):
            word = int.from_bytes(msg[i+4*j:i+4*j+4], "little")
            state[j] = (state[j] ^ word) & 0xFFFFFFFF
        _gimli_permute(state)
        i += rate
    # pad 10*1
    block = bytearray(rate)
    rem = msg[i:]
    block[:len(rem)] = rem
    block[len(rem)] = 0x01
    block[-1] ^= 0x80
    for j in range(rate // 4):
        word = int.from_bytes(block[4*j:4*j+4], "little")
        state[j] = (state[j] ^ word) & 0xFFFFFFFF
    _gimli_permute(state)
    # squeeze
    out = bytearray()
    while len(out) < outlen:
        for j in range(rate // 4):
            out += (state[j] & 0xFFFFFFFF).to_bytes(4, "little")
            if len(out) >= outlen:
                break
        if len(out) < outlen:
            _gimli_permute(state)
    return bytes(out[:outlen])

# ---------------- Search space helpers ----------------

SETS = {
    "digits": string.digits,
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "alnum": string.ascii_letters + string.digits,
    "hex": "0123456789abcdef",
}

def iter_space(fmt: str, length: int, prefix: str = "", suffix: str = ""):
    chars = SETS[fmt]
    if length == 0:
        yield prefix + suffix
        return
    for combo in itertools.product(chars, repeat=length):
        yield prefix + ("".join(combo)) + suffix

def worker(task):
    # task: (chunk, fmt, length, prefix, suffix, target_hex, found_flag)
    start, step, fmt, length, prefix, suffix, target, found = task
    # stride over the first character to split work
    chars = SETS[fmt]
    for first_idx in range(start, len(chars), step):
        if found.is_set():  # early stop
            return None
        first_char = chars[first_idx]
        # generate rest
        if length == 1:
            candidate = (prefix + first_char + suffix).encode()
            if gimli_hash(candidate) == target:
                found.set()
                return candidate.decode()
            continue
        for tail in itertools.product(chars, repeat=length-1):
            if found.is_set():
                return None
            s = prefix + first_char + ("".join(tail)) + suffix
            if gimli_hash(s.encode()) == target:
                found.set()
                return s
    return None

def main():
    ap = argparse.ArgumentParser(description="Bruteforce Access Code for SunshineCTF cartridge using Gimli-hash.")
    ap.add_argument("--target", required=True, help="Target 32-byte hex digest (from 'forgot' hint).")
    ap.add_argument("--fmt", choices=list(SETS.keys()), default="digits", help="Charset format.")
    ap.add_argument("--length", type=int, default=6, help="Length of the unknown core string (excluding prefix/suffix).")
    ap.add_argument("--prefix", default="", help="Optional fixed prefix to prepend.")
    ap.add_argument("--suffix", default="", help="Optional fixed suffix to append.")
    ap.add_argument("--procs", type=int, default=max(1, mp.cpu_count() - 1), help="Number of processes.")
    args = ap.parse_args()

    try:
        target = binascii.unhexlify(args.target.strip())
    except Exception:
        print("[-] Invalid --target hex.", file=sys.stderr)
        sys.exit(2)

    if len(target) != 32:
        print("[-] Target digest must be 32 bytes (64 hex).", file=sys.stderr)
        sys.exit(2)

    print(f"[+] Target = {args.target}")
    print(f"[+] Space  = fmt={args.fmt} length={args.length} prefix='{args.prefix}' suffix='{args.suffix}'")
    print(f"[+] Procs  = {args.procs}")
    t0 = time.time()

    mgr = mp.Manager()
    found = mgr.Event()

    tasks = []
    for start in range(args.procs):
        tasks.append((start, args.procs, args.fmt, args.length, args.prefix, args.suffix, target, found))

    with mp.Pool(processes=args.procs) as pool:
        for res in pool.imap_unordered(worker, tasks):
            if res:
                print(f"[+] FOUND: {res}")
                print(f"[+] FLAG:  sun{{{res}}}")
                found.set()
                pool.terminate()
                break

    dt = time.time() - t0
    if not found.is_set():
        print("[-] Not found in this space.")
    print(f"[i] Time: {dt:.2f}s")

if __name__ == "__main__":
    main()
