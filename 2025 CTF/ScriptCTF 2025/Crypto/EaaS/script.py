from pwn import *

HOST, PORT = "play.scriptsorcerers.xyz", 10488
def bxor(a,b): return bytes(x^y for x,y in zip(a,b))

r = remote(HOST, PORT)

# 0) Email
r.recvuntil(b"Your Email is: ")
email = r.recvline().strip().decode()
email_b = email.encode()
log.info(f"Email: {email} (len={len(email_b)})")

# 1) 6-block password, only force P2 and P6 later
token   = b"," + email_b + b","          # length 31
t2      = token[:16]                      # first 16 bytes
t3_tail = token[16:]                      # last 15 bytes

B1 = b"A"*16
B2 = b"Z"*16
B3 = t3_tail + b"X"                       # preload tail of token
B4 = b"W"*16
B5 = b"W"*16
B6 = b"Q"*16
P  = B1 + B2 + B3 + B4 + B5 + B6
assert len(P) == 96 and email_b not in P and b"@script.sorcerer" not in P

# 2) Encryption oracle (login)
r.sendlineafter(b"Enter secure password (in hex): ", P.hex().encode())
r.recvuntil(b"Please use this key for future login: ")
C = bytes.fromhex(r.recvline().strip().decode())
assert len(C) == 96
C1,C2,C3,C4,C5,C6 = [C[i:i+16] for i in range(0,96,16)]

# 3) Flip C1 to set P2 = t2, flip C5 to set P6 = "@script.sorcerer"
dom_ok = b"@script.sorcerer"
C1p = bxor(C1, bxor(B2, t2))
C5p = bxor(C5, bxor(B6, dom_ok))
Cmod = C1p + C2 + C3 + C4 + C5p + C6

# 4) Send forged email
r.sendlineafter(b"Enter your choice: ", b"2")
r.sendlineafter(b"Enter encrypted email (in hex): ", Cmod.hex().encode())
resp = r.recvline().decode(errors="ignore").strip()
log.success(resp)  # "Email sent!"

# 5) Read the flag robustly
r.sendlineafter(b"Enter your choice: ", b"1")
r.recvuntil(b"[2] Get flag\n")
line1 = r.recvline(timeout=5).decode(errors="ignore").rstrip()
print(line1)
if line1.startswith("New email!"):
    sender = r.recvline(timeout=5).decode(errors="ignore").rstrip()
    r.recvuntil(b"Body: ", timeout=5)
    flag = r.recvline(timeout=5).decode(errors="ignore").strip()
    print(sender)
    print("Body:", flag)   # <-- scriptCTF{...}
r.close()