# solve.sage — LLL (Sage) nhanh hơn nhiều
from sage.all import *
import ast, re

txt = open("output.txt").read()
A = vector(ZZ, ast.literal_eval(re.search(r'P\s*=\s*(\[[\s\S]*?\])', txt).group(1)))
C = ast.literal_eval(re.search(r'C\s*=\s*(\[[\s\S]*?\])', txt).group(1))

def solve_block(A, Cj, Qbits=96):
    n = len(A); S = sum(A)
    Q = Integer(1) << Qbits; hQ = Q//2
    # lattice (n+1)x(n+1)
    B = Matrix(ZZ, n+1, n+1)
    for i in range(n):
        B[i,i] = Q
        B[i,n] = A[i]
    for i in range(n):
        B[n,i] = hQ
    B[n,n] = S - 2*Cj
    R = B.LLL()
    for v in R.rows():
        first = v[:n]; last = v[n]
        if last == 0 and all(abs(abs(x)-hQ) <= 1 for x in first):
            bits = [1 if x < 0 else 0 for x in first]
            if sum(A[i]*bits[i] for i in range(n)) == Cj:
                return bits
    return None

def bits_to_bytes_be(bits):
    out = []
    for i in range(0,len(bits),8):
        b = 0
        for k in range(8):
            b = (b<<1) | bits[i+k]
        out.append(b)
    return bytes(out)

pt = b""
for j, Cj in enumerate(C):
    bits = solve_block(A, Cj)
    if bits is None:
        # tăng Qbits nếu cần
        for qb in (104,112,120,128):
            bits = solve_block(A, Cj, Qbits=qb)
            if bits: break
    assert bits is not None, f"Block {j} failed"
    pt += bits_to_bytes_be(bits)

print("[+] Plaintext:", pt)
m = re.search(rb'fwectf\{[^}]*\}', pt)
if m: print("[+] Flag:", m.group(0).decode())
