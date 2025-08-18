#!/usr/bin/env python3
from pwn import remote

HOST = "play.scriptsorcerers.xyz"   # thay bằng host
PORT = 10314                        # thay bằng port

def ask_num(conn, n):
    conn.recvuntil(b"Choice:")
    conn.sendline(b"1")
    conn.recvuntil(b"Enter a number:")
    conn.sendline(str(n).encode())
    # read printed int(div)\n (line)
    out = conn.recvline().strip()
    # some services may echo prompts differently; adjust if needed
    try:
        return int(out)
    except:
        # fallback: read until we find a line that's 0/1
        for _ in range(5):
            line = conn.recvline().strip()
            if line in [b"0", b"1"]:
                return int(line)
        raise

def guess_secret(conn, s):
    conn.recvuntil(b"Choice:")
    conn.sendline(b"2")
    conn.recvuntil(b"Enter secret number:")
    conn.sendline(str(s).encode())
    return conn.recvline(timeout=2)

def main():
    conn = remote(HOST, PORT)
    low = 1 << 127
    high = (1 << 128) - 1

    while low < high:
        mid = (low + high + 1) // 2
        r = ask_num(conn, mid)
        if r == 1:
            low = mid
        else:
            high = mid - 1
    # low is the secret
    res = guess_secret(conn, low)
    print("Result:", res)
    conn.close()

if __name__ == "__main__":
    main()
