#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# solve.py — PEMPEM 🔪
#
# Yêu cầu: Python 3.8+ (dùng pow(..., -1, mod)), không phụ thuộc ngoài.
#
import base64, re, sys, math, random
from typing import List, Tuple

# ---------- Utils ----------
def read_ciphertext(path: str) -> int:
    with open(path, "rb") as f:
        s = f.read().strip()
    try:
        return int(s)
    except ValueError:
        # cho phép hex (0x...) hoặc base10 có dấu xuống dòng
        s2 = re.sub(rb"[^0-9A-Fa-fx]", b"", s)
        if s2.startswith(b"0x") or s2.startswith(b"0X"):
            return int(s2, 16)
        return int(s2, 10)

def load_pem_der_bytes(path: str) -> bytes:
    data = open(path, "rb").read()
    # Lọc những dòng base64 hợp lệ
    b64 = b"".join([ln.strip() for ln in data.splitlines()
                    if b"-----" not in ln and re.fullmatch(rb"[A-Za-z0-9+/=]+", ln.strip() or b"", flags=0)])
    if not b64:
        # fallback: lấy toàn bộ và strip non-base64
        b64 = re.sub(rb"[^A-Za-z0-9+/=]", b"", data)
    return base64.b64decode(b64)

def parse_asn1_integers(der: bytes) -> List[int]:
    """Rất đơn giản: quét tag 0x02 (INTEGER), đọc length (short/long form), cắt ra value (bỏ leading 0x00)."""
    i, out = 0, []
    n = len(der)
    while i < n:
        if der[i] != 0x02:
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
        # ASN.1 INTEGER có thể có 0x00 đầu để giữ số dương
        if len(val) > 0 and val[0] == 0x00:
            val = val[1:]
        if len(val) == 0:
            continue
        out.append(int.from_bytes(val, "big"))
    return out

# Miller-Rabin
def is_probable_prime(n: int, k: int = 16) -> bool:
    if n < 2: return False
    small_primes = [2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 = 2^s * d
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

def egcd(a: int, b: int) -> Tuple[int,int,int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def invmod(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m

def sieve_primes(limit: int) -> List[int]:
    bs = bytearray(b"\x01") * (limit+1)
    bs[0:2] = b"\x00\x00"
    for i in range(2, int(limit**0.5)+1):
        if bs[i]:
            step = i
            start = i*i
            bs[start:limit+1:step] = b"\x00" * (((limit - start)//step)+1)
    return [i for i, v in enumerate(bs) if v]

# ---------- Recover workflow ----------
def recover_q_dp(der: bytes) -> Tuple[int, int]:
    ints = parse_asn1_integers(der)
    # chọn các số có độ dài >= 128 bytes (>= 1024-bit)
    bigs = [x for x in ints if x.bit_length() >= 768]  # ngưỡng an toàn
    if len(bigs) < 2:
        raise RuntimeError("Không tìm đủ INTEGER lớn trong DER (cần >= 2).")
    # q là prime lớn nhất, dP là số lớn còn lại (không prime) gần kích thước q
    bigs_sorted = sorted(bigs, key=lambda x: x.bit_length(), reverse=True)
    q = None
    dp = None
    for x in bigs_sorted:
        if is_probable_prime(x):
            q = x
            break
    if q is None:
        # nếu không tìm thấy prime nào, thử giả định phần tử đầu là q
        q = bigs_sorted[0]
    # dP: chọn một phần tử khác với q, ưu tiên không prime
    for x in bigs_sorted:
        if x != q:
            dp = x
            if not is_probable_prime(dp):
                break
    if dp is None:
        # fallback: lấy phần tử lớn tiếp theo
        dp = bigs_sorted[1]
    return q, dp

def try_recover_p_from_k(K: int, max_prime_trial: int = 200000, combo_depth: int = 14) -> int:
    """
    Thử tách h từ các prime nhỏ của K rồi test p = K/h + 1.
    - max_prime_trial: sàng prime nhỏ tới ngưỡng này.
    - combo_depth: giới hạn backtracking theo số prime-power gán vào h (tránh nổ tổ hợp).
    """
    # factor out 2-powers trước (rất thường gặp)
    tw = (K & -K).bit_length() - 1  # số bit 0 cuối = bậc của 2
    while K % 2 == 0:
        K //= 2

    primes = sieve_primes(max_prime_trial)
    small_factors = []
    for p in primes[1:]:  # bỏ 2 vì đã xử lý
        if p > max_prime_trial:
            break
        if K % p == 0:
            cnt = 0
            while K % p == 0:
                K //= p
                cnt += 1
            small_factors.append((p, cnt))
        # Heuristic stop nếu K quá nhỏ
        if K.bit_length() < 64:
            break

    # Base candidate: h = 2^tw * product of some subset of (p^cnt)
    base_two = 1 << tw

    # Greedy test 1: thử h = base_two
    cand = K  # K hiện giờ là K / (product small prime powers đã tách)
    p_candidate = cand + 1
    if is_probable_prime(p_candidate):
        return p_candidate

    # Greedy test 2: thử h = base_two * (một prime-power lớn) lần lượt
    for (prime, cnt) in small_factors:
        h = base_two * (prime ** cnt)
        if (K * (1)) % 1 == 0:  # no-op để dễ đọc
            p_candidate = ( (K) // 1 )  # K ở đây đã sau khi chia hết smalls -> giữ nguyên
        p_candidate = ( (K) * 1 )  # giữ K, h đã ăn ở ngoài khi tách? ta cần làm đúng:
        # Ta có K_orig = (2^tw) * (prod small_factors) * K  (K hiện còn phần lớn)
        # h ứng viên là một phần của (2^tw * prod small_factors). Khi chọn h, ta thực tế xét:
        #   p-1 = K_orig / h  =>  p = K_orig/h + 1
        # Để tránh rối, ta tái dựng K_orig:
    # Tái dựng K_orig:
    K_orig = (1 << tw)
    for (prime, cnt) in small_factors:
        K_orig *= (prime ** cnt)
    K_orig *= K

    # Test nhanh: h chỉ dùng 2^tw
    if is_probable_prime(K_orig // base_two + 1):
        return K_orig // base_two + 1

    # Test theo từng prime-power đơn lẻ (kết hợp với 2^tw)
    for (prime, cnt) in small_factors:
        h = base_two * (prime ** cnt)
        if K_orig % h == 0:
            p_candidate = K_orig // h + 1
            if is_probable_prime(p_candidate):
                return p_candidate

    # Backtracking hạn chế độ sâu để kết hợp vài prime-power
    # Sắp theo kích thước để thử những thằng "to" trước
    small_factors.sort(key=lambda x: x[0]**x[1], reverse=True)

    best = None
    def dfs(idx, depth, h_acc):
        nonlocal best
        if best is not None:
            return
        if depth > combo_depth:
            return
        # thử ứng viên hiện tại
        if K_orig % h_acc == 0:
            p_cand = K_orig // h_acc + 1
            if is_probable_prime(p_cand):
                best = p_cand
                return
        # tiếp tục thêm prime-power
        for j in range(idx, len(small_factors)):
            p, c = small_factors[j]
            h_next = h_acc * (p ** c)
            # pruning thô: nếu h_next > K_orig, bỏ
            if h_next > K_orig:
                continue
            dfs(j+1, depth+1, h_next)

    dfs(0, 0, base_two)
    if best is not None:
        return best
    raise RuntimeError("Không tìm được p trong phạm vi thử. Tăng 'max_prime_trial' hoặc 'combo_depth'.")

def main():
    pem_path = "private.pem"
    ct_path  = "ciphertext.txt"
    try:
        der = load_pem_der_bytes(pem_path)
    except Exception as e:
        print("[!] Lỗi đọc/giải mã PEM:", e)
        sys.exit(1)

    ints = parse_asn1_integers(der)
    if not ints:
        print("[!] Không trích được INTEGER nào từ DER.")
        sys.exit(1)

    # Chọn q, dP
    q, dP = recover_q_dp(der)
    print("[+] q bitlen =", q.bit_length())
    print("[+] dP bitlen =", dP.bit_length())

    # e mặc định
    e = 65537
    K = e * dP - 1

    # Tách các ước nhỏ và thử hồi phục p
    try:
        p = try_recover_p_from_k(K, max_prime_trial=200000, combo_depth=16)
    except RuntimeError as ex:
        print("[!] Không khôi phục được p với thông số mặc định.")
        print("    Gợi ý: tăng max_prime_trial (ví dụ 1_000_000) hoặc combo_depth.")
        raise

    print("[+] p bitlen =", p.bit_length())

    # Khôi phục n, phi, d
    n = p * q
    phi = (p - 1) * (q - 1)
    try:
        d = pow(e, -1, phi)  # Python 3.8+
    except ValueError:
        # fallback nếu Python cũ
        d = invmod(e, phi)

    print("[+] n bitlen =", n.bit_length())

    # Đọc ciphertext & giải
    C = read_ciphertext(ct_path)
    M = pow(C, d, n)
    mlen = (n.bit_length() + 7) // 8
    msg = M.to_bytes(mlen, "big")

    # Gỡ padding PKCS#1 v1.5 nếu có
    flag_bytes = None
    if len(msg) >= 11 and msg[0] == 0x00 and msg[1] == 0x02:
        sep = msg.find(b"\x00", 2)
        if sep != -1:
            flag_bytes = msg[sep+1:]
    if flag_bytes is None:
        # không padding hoặc không chuẩn -> lột các 0x00 đầu
        flag_bytes = msg.lstrip(b"\x00")

    try:
        flag_str = flag_bytes.decode("utf-8")
    except Exception:
        flag_str = flag_bytes.decode("latin-1", errors="ignore")

    print("[+] Flag:", flag_str)

if __name__ == "__main__":
    main()