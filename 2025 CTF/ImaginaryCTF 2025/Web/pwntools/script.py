#!/usr/bin/env python3
from pwn import *
import re

INST_HOST, INST_PORT = "34.72.72.63", 4242
context.log_level = "info"

def spawn_instance():
    io = remote(INST_HOST, INST_PORT)
    # (Optional) read banner; don't block forever
    try:
        _ = io.recv(timeout=1.5)
    except EOFError:
        pass
    io.sendline(b"potato")

    # Grab everything until close (or short timeout)
    try:
        data = io.recvall(timeout=4) or b""
    except EOFError:
        data = b""
    finally:
        io.close()

    text = data.decode(errors="replace")
    log.info("Instancer output:\n" + text.strip())

    m_tok = re.search(r"\b[a-f0-9]{64}\b", text)
    m_url = re.search(r"http://(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})", text)
    if not (m_tok and m_url):
        raise ValueError("Couldn't parse token/URL.\n" + text)

    token = m_tok.group(0)
    ip = m_url.group(1)
    port = int(m_url.group(2))
    log.success(f"Token: {token}")
    log.success(f"HTTP: {ip}:{port}")
    return ip, port, token

def http_try(ip, port, method="GET", path="/", headers=None, body=b""):
    if headers is None: headers = {}
    ua = headers.pop("User-Agent", "pwntools")
    req = f"{method} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nUser-Agent: {ua}\r\nConnection: close\r\n"
    for k,v in headers.items():
        req += f"{k}: {v}\r\n"
    if method == "POST":
        req += f"Content-Length: {len(body)}\r\n"
    req += "\r\n"
    io = remote(ip, port)
    io.send(req.encode() + (body if method=="POST" else b""))
    resp = io.recvall(timeout=5) or b""
    io.close()
    return resp

def extract_flag(b):
    m = re.search(rb"ictf\{[^}]+\}", b)
    return m.group(0).decode() if m else None

def main():
    ip, port, token = spawn_instance()

    attempts = [
        ("GET", "/", {"X-Token": token}),
        ("GET", "/", {"Authorization": f"Bearer {token}"}),
        ("GET", "/", {"Cookie": f"token={token}"}),
        ("GET", "/", {"X-Auth-Token": token}),
        ("GET", "/", {"X-Instance-Token": token}),
        ("GET", f"/?token={token}", {}),
        ("GET", f"/flag?token={token}", {}),
        ("GET", "/flag", {"X-Token": token}),
        # “i love pwntools” vibes — keep UA as 'pwntools'
        ("GET", "/", {}),  # plain fetch to read exact instructions
        # fallback POST variants
        ("POST", "/flag", {"X-Token": token}, b""),
        ("POST", "/", {"X-Token": token}, b""),
    ]

    for method, path, hdrs, *rest in attempts:
        body = rest[0] if rest else b""
        log.info(f"Trying {method} {path} with headers {hdrs or {'User-Agent':'pwntools'}}")
        resp = http_try(ip, port, method, path, hdrs, body)
        flag = extract_flag(resp)
        if flag:
            log.success("FLAG: " + flag)
            return
        head = resp[:400].decode(errors="replace")
        log.debug("Preview:\n" + head)
        # If server tells us the exact header/param, you'll see it here.

    log.error("No flag yet — check previews above for the required header/param wording and add it to attempts.")

if __name__ == "__main__":
    main()
