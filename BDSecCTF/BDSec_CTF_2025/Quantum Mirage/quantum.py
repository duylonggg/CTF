from Crypto.Util.number import *
import hashlib
import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

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

def H(m, k):
    q = bytearray()
    for i, t in enumerate(m):
        s = (t ^ k[i % len(k)])
        s = ((s << 3) | (s >> 5)) & 0xFF
        s ^= X[i % len(X)] & 0xFF
        q.append(s)
    return bytes(q)

class Y:
    def __init__(self):
        self.a = [
            b"phase_shift_001",
            b"binary_singularity",
            b"entropic_veil_layer",
            b"qbit_spectrum_field"
        ]
        self.b = b"simple_seed_123"

    def P(self, msg):
        c = G(self.a[0], 10)[:16]
        r1 = base64.b64encode(msg).decode()

        d = G(self.b, 5)
        r2 = H(msg, d)

        e = zlib.compress(r2)

        r3 = r2
        for i in range(3):
            f = G(self.a[i+1], i+1)
            r3 = bytes([(z ^ f[j % len(f)]) for j, z in enumerate(r3)])

        return {
            'x': r1,
            'y': base64.b64encode(r2).decode(),
            'z': base64.b64encode(e).decode(),
            'w': base64.b64encode(r3).decode(),
            'junk': base64.b64encode(get_random_bytes(64)).decode()
        }

# Challenge Generation
C = Y()
msg = b"BDSEC{Something_like_this}"
R = C.P(msg)


for k, v in R.items():
    output += f"{k}: {v}\n"

output += "entropy_check: [0.7234, 0.8901, 0.6543, 0.9876]\n"
output += "symbol_map: {'A': 12, 'B': 8, 'C': 15, 'D': 9}\n"
output += "known_structure_detected: True\n"
output += "suggested_vector: symbolic_mapping\n"
output += "predicted_block_size: 16\n"
output += "type_inferred: byte_subst\n"
output += f"Source strings: {C.a}\n"
output += f"Magic array: {X}\n"
output += "Hint: Direct path may be surprisingly effective\n"

print(output)
with open('output.txt', 'w') as f:
    f.write(output)
