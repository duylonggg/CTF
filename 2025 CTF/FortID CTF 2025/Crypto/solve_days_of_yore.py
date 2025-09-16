#!/usr/bin/env python3
import sys, re

def load_permutation(path):
    import re
    nums = list(map(int, re.findall(r'\d+', open(path, encoding="utf-8", errors="ignore").read())))
    if not nums:
        raise SystemExit("No integers found in permutation file.")
    N = len(nums)
    if set(nums) != set(range(1, N+1)):
        raise SystemExit("Permutation file must contain a permutation of 1..N with N numbers. Got N=%d but unique=%d, min=%d, max=%d" % (N, len(set(nums)), min(nums), max(nums)))
    return nums

def load_scrambled(path, N):
    data = open(path, 'rb').read()
    # If data length equals N, assume it's already one-byte-per-position
    if len(data) == N:
        return data
    # Else, try to decode as utf-8 text and take characters
    txt = data.decode('utf-8', errors='replace')
    chars = list(txt)
    if len(chars) != N:
        raise SystemExit(f"Scrambled text length {len(chars)} doesn't match permutation size {N}.")
    return bytes(''.join(chars), 'utf-8', errors='ignore')

def unpermute(permutation, scrambled_bytes):
    # permutation[k] = original_index at current position k+1
    # We want plain[original_index-1] = scrambled_bytes[k]
    N = len(permutation)
    plain = bytearray(N)
    for k, orig in enumerate(permutation, start=1):
        plain[orig-1] = scrambled_bytes[k-1]
    return bytes(plain)

def main():
    if len(sys.argv) != 3:
        print("Usage: solve.py permutation.txt scrambled.txt")
        sys.exit(2)
    perm = load_permutation(sys.argv[1])
    N = len(perm)
    scr = load_scrambled(sys.argv[2], N)
    plain = unpermute(perm, scr)
    open("recovered.txt", "wb").write(plain)
    print("[+] Wrote recovered.txt (%d bytes)" % len(plain))
    m = re.search(rb'FORTID\\{[^\\n\\r}]*\\}', plain, flags=re.IGNORECASE)
    if m:
        print("[FLAG]", m.group(0).decode('utf-8', errors='ignore'))
    else:
        print("[-] No FORTID{...} found automatically. Open recovered.txt to read.")
if __name__ == "__main__":
    main()
