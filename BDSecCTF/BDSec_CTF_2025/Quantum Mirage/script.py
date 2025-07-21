from Crypto.Util.number import *
import hashlib
import base64

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

# Inputs
enc_b64 = "FL6gWSgGl71j8RANN2yzz9XckwawQ8MXqE7IAOVygOclZiHgi161L7s="
enc = base64.b64decode(enc_b64)

# Step 1: Undo XOR layers
a = [
    b"phase_shift_001",
    b"binary_singularity",
    b"entropic_veil_layer",
    b"qbit_spectrum_field"
]

r3 = enc
for i in reversed(range(1, 4)):
    key = G(a[i], i)
    r3 = bytes([b ^ key[j % len(key)] for j, b in enumerate(r3)])

# Step 2: Undo H()
b = b"simple_seed_123"
key = G(b, 5)
original = H_inv(r3, key)

print("Decrypted:", original)

