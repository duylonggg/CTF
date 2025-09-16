#!/usr/bin/env python3
import sys, re, argparse

def load_permutation(path):
    nums = list(map(int, re.findall(r'\d+', open(path, encoding="utf-8", errors="ignore").read())))
    if not nums:
        raise SystemExit("No integers found in permutation file.")
    N = len(nums)
    s = set(nums)
    if s != set(range(1, N+1)):
        raise SystemExit(f"Permutation must be 1..N with no gaps. Got N={N}, unique={len(s)}, min={min(nums)}, max={max(nums)}")
    return nums

def normalize_bytes(b, strip_ws=False):
    if strip_ws:
        # remove CR/LF/TAB/space
        b = b.replace(b'\r', b'').replace(b'\n', b'').replace(b'\t', b'').replace(b' ', b'')
    return b

def get_scrambled(args, N):
    if args.text is not None:
        b = args.text.encode('utf-8', errors='strict')
        return normalize_bytes(b, args.strip)
    if args.scrambled == "-":
        b = sys.stdin.buffer.read()
        return normalize_bytes(b, args.strip)
    # else file path
    b = open(args.scrambled, 'rb').read()
    return normalize_bytes(b, args.strip)

def unpermute(permutation, scrambled_bytes):
    # permutation[k] = original_index at current position (1-based)
    N = len(permutation)
    plain = bytearray(N)
    for k, orig in enumerate(permutation, start=1):
        if orig < 1 or orig > N:
            raise SystemExit(f"Bad perm value {orig} at index {k}")
        try:
            plain[orig-1] = scrambled_bytes[k-1]
        except IndexError:
            raise SystemExit(f"Scrambled length {len(scrambled_bytes)} is shorter than expected {N}.")
    return bytes(plain)

def main():
    ap = argparse.ArgumentParser(description="Unpermute a transposition-only ciphertext using a 1..N permutation.")
    ap.add_argument("permutation", help="path to permutation file (list of integers 1..N in scrambled order)")
    ap.add_argument("scrambled", nargs="?", default="-", help="path to scrambled bytes (or '-' to read from stdin). Ignored if --text is used.")
    ap.add_argument("--text", help="inline scrambled text instead of a file (use quotes).")
    ap.add_argument("--strip", action="store_true", help="strip whitespace (CR/LF/TAB/space) from scrambled before use")
    ap.add_argument("-o", "--out", default="recovered.txt", help="output file (default: recovered.txt)")
    args = ap.parse_args()

    perm = load_permutation(args.permutation)
    N = len(perm)
    scr = get_scrambled(args, N)
    if len(scr) != N:
        print(f"[!] Scrambled length = {len(scr)}, permutation N = {N}.", file=sys.stderr)
        print("    Tips:", file=sys.stderr)
        print("     - If your scrambled is text copied from a webpage, try --strip to remove accidental newlines/spaces.", file=sys.stderr)
        print("     - Make sure the payload truly has exactly one byte per position (use a monospace dump).", file=sys.stderr)
        sys.exit(1)

    plain = unpermute(perm, scr)
    open(args.out, "wb").write(plain)
    print(f"[+] Wrote {args.out} ({len(plain)} bytes)")

    m = re.search(rb'FORTID\{[^}\r\n]*\}', plain, flags=re.IGNORECASE)
    if m:
        print("[FLAG]", m.group(0).decode('utf-8', errors='ignore'))
    else:
        print("[-] No FORTID{...} auto-detected. Open the output file to read the paragraphs/flag.")

if __name__ == "__main__":
    main()
