# PEMPEM 🔪 (PTIT CTF 2025)

![alt text](image.png)

## Mục tiêu

Khôi phục **khóa riêng RSA** từ phần thông tin còn sót lại trong `private.pem`, sau đó dùng khóa này để giải mã bản mã trong `ciphertext.txt` và lấy được flag

---

## Phân tích

Trước tiên, ta cần phân tích phần còn lại của `private.pem`. Đây là một khóa riêng RSA dạng PEM (PEM = Base64 của cấu trúc DER ASN.1). Mở tệp cho thấy nội dung Base64 bị cắt cụt (không đầy đủ). Ta tiến hành:

- Giải mã Base64 phần còn lại để thu được chuỗi byte DER
- Phân tích cấu trúc DER: Theo chuẩn PKCS#1, khóa riêng RSA bao gồm một SEQUENCE chứa 9 số nguyên (INTEGER) lần lượt là: `version`, `n` (modulus), `e` (public exponent), `d` (private exponent), `p` (prime1), `q` (prime2), `dP` (exponent1 = d mod (p-1)), `dQ` (exponent2 = d mod (q-1)), `qInv` (coefficient = q^(-1) mod p)

Do khóa đã hỏng nên có thể các trường đầu bị mất, nhưng dựa vào thứ tự, phần cuối của tệp còn lại có khả năng chính là các trường prime2 (`q`) và exponent1 (`dP`) (và có thể một phần của exponent2). Thật vậy, sau khi giải mã Base64:

- Ta nhận thấy xuất hiện 2 số nguyên lớn (ASN.1 INTEGER) liên tiếp với độ dài xấp xỉ bằng một nửa độ dài modulus. Điều này phù hợp với kích thước của prime2 q (~2048 bit) và exponent1 dP (~2048 bit)
- Kiểm tra thêm: `q` thường là số nguyên tố 2048-bit, `dP = d mod (p-1)` cũng có độ lớn tương đương p. Phần DER cho thấy hai số này có độ dài 257 byte (có byte 0x00 đầu do số dương MSB=1) – điều khẳng định đây có thể là q và dP

Như vậy, ta trích xuất được:

- q – giá trị số nguyên tố thứ hai của khóa RSA
- dP = d mod (p-1) – giá trị mũ riêng lẻ cho modulo p

---

## ý tưởng khai thác

Biết được q và dP, ta có thể tìm p dựa trên tính chất của RSA:

Vì $dP = d \bmod (p-1)$, nên tồn tại một số nguyên $k$ sao cho:

```txt
d≡dP(mod(p−1))⟹d=dP+k(p−1)
```

Ta cũng có công thức $e \cdot d \equiv 1 \pmod{\phi(n)}$, trong đó $\phi(n)=(p-1)(q-1)$. Đặc biệt, $e \cdot d \equiv 1 \pmod{(p-1)}$ và $e \cdot d \equiv 1 \pmod{(q-1)}$. Xét modulo $p-1$:

```txt
e⋅d≡1(mod(p−1))
```

Thay $d = dP + k(p-1)$ vào, ta được:

```txt
e⋅dP+ke(p−1)≡1(mod(p−1))⟹e⋅dP≡1(mod(p−1))
```

Do đó:

$(p-1)$ là ước của $(e \cdot dP - 1)$. Nói cách khác, $e \cdot dP - 1 = h \cdot (p-1)$ với một số nguyên $h$ nào đó

Bài toán giờ quy về: Tính $K = e \cdot dP - 1$. Số $K$ này sẽ chia hết cho $p-1$. Nếu ta phân tích thừa số (factor) được $K$, thì một trong các thừa số của $K$ cộng 1 sẽ bằng $p$. Cụ thể, ta tìm một ước số $u$ của $K$ sao cho $u + 1$ là số nguyên tố có độ dài bit phù hợp (~2048 bit) – đó chính là ứng viên cho $p$. Thử lần lượt các thừa số (đặc biệt các thừa số lớn) của $K$ để tìm ra $p$

> **Lưu ý**
> Trong thực tế, $K$ rất lớn (cỡ 2064 bit). Tuy nhiên, do cấu trúc CRT, $p-1$ thường có các ước số nhỏ từ $e$ hoặc các giá trị liên quan. Ta có thể chia thử (trial division) $K$ cho các số nguyên tố nhỏ và vừa để tách các thừa số nhỏ. Khi loại bỏ hết các thừa số nhỏ, nếu phần còn lại của $K$ (gọi là $K'$) cộng 1 là số nguyên tố lớn, nhiều khả năng đó chính là $p$. (Đây chính là cách tiếp cận trong bài: “chia thử để tìm $p = K/h + 1$ là số nguyên tố”, tức là tìm ước $h$ sao cho $K/h + 1$ prime)

---

## Tính toán khóa riêng

### Bước 1: Tìm $p$ từ $dP$ và $q$

- Từ `private.pem` phân tích, ta thu được:
  - $q$ (một số nguyên ~2048 bit)
  - $dP$ (một số nguyên ~2048 bit)
- Giả sử (đoán) $e = 65537$ (0x10001, một giá trị công khai thường dùng). Thật ra nếu đề bài không cho $e$, ta có thể ngầm định 65537 vì rất phổ biến
- Tính $K = e \cdot dP - 1$
- Thực hiện trial division trên $K$: Chia $K$ lần lượt cho các prime nhỏ. Kết quả tìm được một loạt thừa số nhỏ như: 2, 3, 13, 19, 23, 1789, 12347,... (các giá trị này có thể khác nhau tùy trường hợp cụ thể). Giả sử tập hợp các thừa số nhỏ tìm được là $S$
- Chia hết các thừa số đó, ta thu được phần còn lại $K'$ (rất lớn, cỡ >2000 bit). Kiểm tra $K' + 1$:
  - Nếu $K' + 1$ là số nguyên tố lớn ~2048 bit, thì $p = K' + 1$
  - (Nếu chưa phải, có thể cần tìm tiếp thừa số của $K'$ bằng cách khác, nhưng trong bài này giả sử $K' + 1$ đã là prime)
- Kết quả thu được $p$ (prime1) – số nguyên tố thứ nhất của khóa RSA

### Bước 2: Khôi phục các tham số khóa riêng khác

- Tính $n = p \times q$ (modulus)
- Tính $\phi(n) = (p-1)(q-1)$
- Tính $d$ – exponent riêng đầy đủ: đây là nghịch đảo modulo của $e$ mod $\phi(n)$. Ta dùng thuật toán Euclid mở rộng hoặc hàm thư viện để tìm $d$ thỏa mãn $d \cdot e \equiv 1 \pmod{\phi(n)}$
- Bây giờ đã có $(n, e, d, p, q)$. Ta cũng có thể tính lại $dQ = d \bmod (q-1)$ và $qInv = q^{-1} \bmod p$ để hoàn thiện đủ thông tin khóa RSA (điều này không bắt buộc để giải mã nhưng kiểm tra cho nhất quán)

---

## Giải mã ciphertext

Sau khi có khóa riêng đầy đủ, việc giải mã bản mã RSA trở nên đơn giản. Bản mã `ciphertext.txt` cho dưới dạng một số nguyên lớn (rất dài). Gọi số này là $C$. Flag được mã hóa có thể ở dạng plaintext ASCII hoặc chuỗi byte.

Ta giải mã bằng cách tính:

```txt
M=C^d mod n
```

Trong đó $d$ là khóa riêng vừa tìm được. Kết quả $M$ là bản rõ (plaintext) dưới dạng số nguyên. Đổi $M$ ra chuỗi byte (theo big-endian) sẽ thu được thông điệp gốc

Tùy thuộc vào cách mã hóa, có thể cần loại bỏ padding PKCS#1: Trong RSA, nếu plaintext được padding theo PKCS#1 v1.5, chuỗi byte của $M$ sẽ bắt đầu bằng byte `0x00 0x02`, tiếp theo là các byte padding ngẫu nhiên, một byte `0x00` phân tách, rồi đến dữ liệu thật. Khi đó ta bỏ phần padding trước byte `0x00` thứ hai để lấy dữ liệu thông điệp. Nếu plaintext không padding (ví dụ chỉ chuyển thẳng flag thành số), thì trực tiếp chuyển $M$ thành chuỗi ký tự

---

## Script

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# solve_pempem.py — Recover RSA private key from truncated PEM (q & dP fragment)
#
# Usage: python3 solve_pempem.py
# Requires: private.pem, ciphertext.txt in the same folder.
#
import base64, re, sys, math, random
from typing import List, Tuple

# ------------- I/O helpers -------------
def read_ciphertext(path: str) -> int:
    with open(path, "rb") as f:
        s = f.read().strip()
    # allow decimal / hex
    try:
        return int(s, 0)
    except Exception:
        s2 = re.sub(rb"[^0-9A-Fa-fx]", b"", s)
        if s2.startswith(b"0x") or s2.startswith(b"0X"):
            return int(s2, 16)
        return int(s2, 10)

def load_pem_der_bytes(path: str) -> bytes:
    data = open(path, "rb").read()
    # keep only base64-like lines
    b64 = b"".join([
        ln.strip() for ln in data.splitlines()
        if b"-----" not in ln and re.fullmatch(rb"[A-Za-z0-9+/=]+", ln.strip() or b"", flags=0)
    ])
    if not b64:
        b64 = re.sub(rb"[^A-Za-z0-9+/=]", b"", data)
    return base64.b64decode(b64)

# ------------- ASN.1 INTEGER parser (minimal) -------------
def parse_asn1_integers(der: bytes) -> List[int]:
    out = []
    i, n = 0, len(der)
    while i < n:
        if der[i] != 0x02:     # INTEGER tag
            i += 1
            continue
        i += 1
        if i >= n: break
        L = der[i]; i += 1
        if L & 0x80:
            nlen = L & 0x7F
            if i + nlen > n: break
            L = int.from_bytes(der[i:i+nlen], "big"); i += nlen
        if i + L > n: break
        val = der[i:i+L]; i += L
        # positive INTEGER may be prefixed with 0x00
        if len(val) > 0 and val[0] == 0x00:
            val = val[1:]
        if len(val) == 0:
            continue
        out.append(int.from_bytes(val, "big"))
    return out

# ------------- Number theory utils -------------
def is_probable_prime(n: int, k: int = 16) -> bool:
    if n < 2: return False
    small = [2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small:
        if n % p == 0:
            return n == p
    # Miller–Rabin
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n-2)
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for __ in range(s-1):
            x = (x * x) % n
            if x == n-1:
                break
        else:
            return False
    return True

def egcd(a: int, b: int):
    if b == 0: return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def invmod(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m

def sieve_primes(limit: int) -> List[int]:
    if limit < 2: return []
    bs = bytearray(b"\x01")*(limit+1)
    bs[0:2] = b"\x00\x00"
    for i in range(2, int(limit**0.5)+1):
        if bs[i]:
            step = i
            start = i*i
            bs[start:limit+1:step] = b"\x00"*(((limit-start)//step)+1)
    return [i for i,v in enumerate(bs) if v]

# ------------- Recover q & dP -------------
def guess_q_dp(der: bytes) -> Tuple[int,int]:
    ints = parse_asn1_integers(der)
    # Keep big ints (>= ~1024 bits); here target ~2048-bit
    bigs = [x for x in ints if x.bit_length() >= 900]
    if len(bigs) < 2:
        raise RuntimeError("Không đủ INTEGER lớn trong DER.")
    # Pick q = prime among the top bit-length; dp = another big non-prime
    bigs_sorted = sorted(bigs, key=lambda z: z.bit_length(), reverse=True)
    q = None
    for x in bigs_sorted:
        if is_probable_prime(x):
            q = x
            break
    if q is None:
        raise RuntimeError("Không tìm được q nguyên tố.")
    dp = None
    for x in bigs_sorted:
        if x != q:
            dp = x
            if not is_probable_prime(dp):
                break
    if dp is None:
        raise RuntimeError("Không tìm được dP (một số lớn không nguyên tố).")
    return q, dp

# ------------- Recover p from K = e*dP - 1 -------------
def small_factor_hunt(K: int, max_prime_trial: int = 300000) -> Tuple[int, list]:
    """Factor out small primes from K; return (K_remainder, list of (p,e))."""
    primes = sieve_primes(max_prime_trial)
    small_factors = []
    # Factor out 2's quickly
    cnt2 = 0
    while K % 2 == 0:
        K //= 2; cnt2 += 1
    if cnt2:
        small_factors.append((2, cnt2))
    for p in primes[1:]:  # skip 2
        if p > max_prime_trial: break
        if K % p == 0:
            c = 0
            while K % p == 0:
                K //= p; c += 1
            small_factors.append((p, c))
        # heuristic early stop
        if K.bit_length() < 64:
            break
    return K, small_factors

def generate_h_candidates(small_factors: list, extra_candidates: list = None,
                          max_combo: int = 200000, max_h: int = 10**22) -> List[int]:
    """Build h from small prime-powers; include any extra known candidates."""
    hs = [1]
    # sort by p^e increasing to grow h gently
    items = sorted(small_factors, key=lambda pe: pe[0]**pe[1])
    for p, e in items:
        new_hs = hs[:]
        pe_pow = 1
        for _ in range(e):
            pe_pow *= p
            for h in hs:
                h2 = h * pe_pow
                if h2 <= max_h:
                    new_hs.append(h2)
        hs = sorted(set(new_hs))
        if len(hs) > max_combo:
            hs = hs[:max_combo]
    if extra_candidates:
        for c in extra_candidates:
            if c not in hs:
                hs.append(c)
    return hs

def recover_p_from_K(K: int, target_bits: int,
                     prefer_h_near: List[int] = None,
                     small_trial: int = 300000) -> int | None:
    # Try explicit preferred h first (e.g., 37041 from the writeup summary)
    if prefer_h_near:
        for h in prefer_h_near:
            if h > 0 and K % h == 0:
                cand = K // h + 1
                if cand.bit_length() == target_bits and is_probable_prime(cand):
                    return cand
    # Factor small primes out of K
    K_rem, smalls = small_factor_hunt(K, max_prime_trial=small_trial)
    # Build h candidates (include '1' by default)
    extras = [1]
    if prefer_h_near:
        extras += [x for x in prefer_h_near if x not in extras]
    h_candidates = generate_h_candidates(smalls, extra_candidates=extras, max_combo=300000)
    # Try h candidates (small first)
    for h in h_candidates:
        if K % h != 0: 
            continue
        cand = K // h + 1
        # quick bit-size filter then primality
        if cand.bit_length() == target_bits and is_probable_prime(cand):
            return cand
    # As a last-ditch: also try dividing K by small integers around 65537 (unlikely but quick)
    for h in range(65537-5000, 65537+5001):
        if h <= 0: continue
        if K % h == 0:
            cand = K // h + 1
            if cand.bit_length() == target_bits and is_probable_prime(cand):
                return cand
    return None

# ------------- Main solve -------------
def main():
    pem = "private.pem"
    ct  = "ciphertext.txt"
    try:
        der = load_pem_der_bytes(pem)
    except Exception as e:
        print("[!] Lỗi đọc/giải mã PEM:", e); sys.exit(1)

    q, dP = guess_q_dp(der)
    print(f"[+] q bitlen = {q.bit_length()} (prime? {is_probable_prime(q)})")
    print(f"[+] dP bitlen = {dP.bit_length()} (prime? {is_probable_prime(dP)})")

    e = 65537
    K = e*dP - 1

    # Theo tóm tắt đã tìm được h = 37041; ta thử ngay trước.
    prefer_h = [37041]
    p = recover_p_from_K(K, target_bits=q.bit_length(), prefer_h_near=prefer_h, small_trial=300000)
    if p is None:
        print("[!] Chưa khôi phục được p — hãy tăng small_trial (ví dụ 1_000_000).")
        sys.exit(1)
    print(f"[+] p bitlen = {p.bit_length()} (prime? {is_probable_prime(p)})")

    n   = p * q
    phi = (p - 1) * (q - 1)
    try:
        d = pow(e, -1, phi)  # Python 3.8+
    except ValueError:
        d = invmod(e, phi)

    print(f"[+] n bitlen = {n.bit_length()}")

    C = read_ciphertext(ct)
    M = pow(C, d, n)
    mlen = (n.bit_length() + 7) // 8
    msg = M.to_bytes(mlen, "big")

    # Unpad PKCS#1 v1.5 nếu cần
    flag_bytes = None
    if len(msg) >= 11 and msg[0] == 0x00 and msg[1] == 0x02:
        sep = msg.find(b"\x00", 2)
        if sep != -1:
            flag_bytes = msg[sep+1:]
    if flag_bytes is None:
        flag_bytes = msg.lstrip(b"\x00")

    try:
        flag_str = flag_bytes.decode("utf-8")
    except Exception:
        flag_str = flag_bytes.decode("latin-1", errors="ignore")

    print("[+] Flag:", flag_str)

if __name__ == "__main__":
    main()

```

---

## Flag

Flag: `PTITCTF{Pr1v4t3_K3y_G3n3r4t10n_1s_Fun!}`
