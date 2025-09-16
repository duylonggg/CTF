# solve.sage

# ---- Params from challenge ----
p  = 0xbde3c425157a83cbe69cee172d27e2ef9c1bd754ff052d4e7e6a26074efcea673eab9438dc45e0786c4ea54a89f9079ddb21
Xt = 0x686be42f9c3f431296a928c288145a847364bb259c9f5738270d48a7fba035377cc23b27f69d6ae0fad76d745fab25d504d5

F  = GF(p)
E  = EllipticCurve(F, [5, 7])

# Lấy r = prime factor thứ 4 (index 3) của |E| với small factors
fac = E.order().factor(limit=2**12)
if len(fac) < 4:
    raise RuntimeError(f"Không đủ small factors, hiện có: {fac}")
r = ZZ(fac[3][0])
print(f"[i] |E| factors (small): {fac}")
print(f"[i] r =", r)

def to_ascii_from_int(xi: Integer):
    # big-endian, bỏ leading zero-length
    nbytes = max(1, (xi.nbits()+7)//8)
    bs = xi.to_bytes(nbytes, 'big', signed=False)
    # chỉ nhận ASCII in được để giống flag content
    if any(b < 32 or b > 126 for b in bs):
        return None
    try:
        return bs.decode('ascii')
    except:
        return None

def check_inner(inner: str) -> bool:
    # Verify theo đúng chall: x = int.from_bytes(inner.encode(), 'big')
    x_int = Integer(int.from_bytes(inner.encode('ascii'), 'big'))
    try:
        P = E.lift_x(x_int)     # Sage tự mở rộng trường nếu cần
    except Exception:
        return False
    Q = r * P
    return Integer(Q[0]) % p == Xt % p

# Dựng Q với x = Xt (trên F hoặc F_{p^2})
cands = []
rhs = F(Xt)**3 + F(5)*F(Xt) + F(7)
if rhs.is_square():
    y = rhs.sqrt()
    cands = [E(F(Xt),  y), E(F(Xt), -y)]
else:
    K.<u> = GF(p**2)
    EK = EllipticCurve(K, [K(5), K(7)])
    xK = K(Xt)
    rhsK = xK**3 + K(5)*xK + K(7)
    if not rhsK.is_square():
        raise RuntimeError("Không dựng được Q ở cả GF(p^2) (bất thường).")
    yK = rhsK.sqrt()
    cands = [EK(xK,  yK), EK(xK, -yK)]

solutions = set()

for Q in cands:
    K = Q.curve().base_ring()
    EK = E.change_ring(K)
    N  = EK.cardinality()
    # tách N = r^e * M (gcd(M,r)=1)
    e  = 0
    T  = N
    while T % r == 0:
        T //= r
        e += 1
    M  = T
    print(f"[i] Field: GF(p^{K.degree()}), #E(K) = r^{e} * {M}")

    # --- (1) preimage nhanh: R = u * Q với u ≡ r^{-1} (mod M)
    try:
        u = inverse_mod(r, M)
        R = Integer(u) * Q
        xR = R[0]
        if xR in F:
            s = to_ascii_from_int(Integer(xR))
            if s:
                if check_inner(s):
                    solutions.add(f"ictf{{{s}}}")
                    print("[+] Found via inverse-trick:", f"ictf{{{s}}}")
    except ZeroDivisionError:
        pass

    # --- (2) Thử liệt kê r-division nếu chưa ra
    if not solutions:
        print("[i] Enumerating r-division points ...")
        divs = Q.division_points(r)
        print(f"[i] Got {len(divs)} preimages")
        for P in divs:
            xP = P[0]
            if xP in F:
                s = to_ascii_from_int(Integer(xP))
                if s and check_inner(s):
                    solutions.add(f"ictf{{{s}}}")
                    print("[+] Found via division_points:", f"ictf{{{s}}}")
                    break

if solutions:
    print("\n=== FLAG ===")
    for f in solutions:
        print(f)
else:
    print("[-] Chưa tìm được. Gợi ý: tăng factor(limit), hoặc thử cả GF(p^k) với k=4 (hiếm).")
