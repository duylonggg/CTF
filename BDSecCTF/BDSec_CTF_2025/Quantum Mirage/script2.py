from Crypto.Util.number import *
import hashlib

X = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476,
     0xC3D2E1F0, 0x76543210, 0xFEDCBA98, 0x89ABCDEF]

def G(a, b):
    d = a
    for i in range(b):
        if i % 4 == 0:
            d = hashlib.sha256(d).digest()
        elif i % 4 == 1:
            d = hashlib.blake2b(d, digest_size=32).digest()
        elif i % 4 == 2:
            d = hashlib.md5(d).digest() * 2
        else:
            d = hashlib.sha1(d).digest() + d[:12]
    return d

def H_inv(m, k):
    q = bytearray()
    for i, t in enumerate(m):
        s = t ^ (X[i % len(X)] & 0xFF)
        s = ((s >> 3) | (s << 5)) & 0xFF
        s ^= k[i % len(k)]
        q.append(s)
    return bytes(q)

# === Your current decrypted bytes from previous step ===
r2 = b'wQf\x04\xbb\xf4\x11\x95\xcd\x96)\xbd\x04\x83P\xc8\x04u\xc5n\xc0\xcf\xa5T\x92y\xd1\xfcf\x86\xcf\x12QJV3\xcf\xffU\xc7\xd6'

# Recreate key from b = b"simple_seed_123"
b = b"simple_seed_123"
key = G(b, 5)

# Recover the original message
original_msg = H_inv(r2, key)

print("✅ Flag:", original_msg.decode())
for b in original_msg:
    print(chr(b) if 32 <= b <= 126 else '.', end='')

