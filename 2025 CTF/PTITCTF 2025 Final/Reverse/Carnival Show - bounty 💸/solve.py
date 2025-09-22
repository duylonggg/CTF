aQwertyuiopasdf = b"QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm0123456789-_"
aN0Dbg = b"n0_dbg^_^"
byte_2220 = [
    0x87,0xA4,0x55,0x21,0xAC,0x4B,0x57,0xAE,0x13,0xAB,
    0x5D,0x97,0x5C,0xFD,0xF0,0xB5,0xCA,0x5D,0x22,0xCF,
    0xE7,0xE0,0x3F,0x98,0x49,0x58,0x06,0xAF,0x87,0x90,
    0x50,0xBC,0xE3,0xA9,0x30,0xFC,0xE0,0xB3,0x8F,0xAE,
    0x4C,0x04,0x56,0x39,0x76,0xC0,0x39,0x93,0xDC,0x08,
    0x21,0xF7,0xC2,0xE2,0x56,0xFC,0xFE,0x16,0xDE,0x43
]

def fnv():
    h = 0x811C9DC5
    for b in aN0Dbg:
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h

def last():
    v = (fnv() ^ 0x9E377985) & 0xFFFFFFFF
    result = []
    for j in range(60):
        a = ((v ^ ((v << 13) & 0xFFFFFFFF)) >> 17) & 0xFFFFFFFF
        b = (v << 13) & 0xFFFFFFFF
        u = (a ^ v ^ b) & 0xFFFFFFFF
        v = (v ^ a ^ b ^ ((32 * u) & 0xFFFFFFFF)) & 0xFFFFFFFF

        idx = j - (j // 9 + (((0xE38E38E38E38E38F * j) >> 64) & 0xFFFFFFFFFFFFFFF8))
        result.append((v + aN0Dbg[idx % len(aN0Dbg)]) & 0xFF)
    return result

def xorr(c_bytes, prng):
    return [c ^ p for c, p in zip(c_bytes, prng)]

def rotation(eperm):
    enc = []
    v31 = 1
    for i in range(0, len(eperm), 4):
        block = eperm[i:i+4]
        s = v31 & 3
        if s:
            rotated = block[-s:] + block[:-s]
        else:
            rotated = block[:]
        enc.extend(rotated)
        v31 += 3
    return bytes(enc)

def base64_decode(enc_bytes):
    pad_byte = ord('.')
    inv = {aQwertyuiopasdf[i]: i for i in range(len(aQwertyuiopasdf))}
    out = bytearray()
    for i in range(0, len(enc_bytes), 4):
        chunk = enc_bytes[i:i + 4]
        if len(chunk) < 4:
            chunk = chunk.ljust(4, bytes([pad_byte]))
        pad_count = chunk.count(pad_byte)
        vals = [(0 if b == pad_byte else inv.get(b, 0)) for b in chunk]
        v = (vals[0] << 18) | (vals[1] << 12) | (vals[2] << 6) | vals[3]
        b1 = (v >> 16) & 0xFF
        b2 = (v >> 8) & 0xFF
        b3 = v & 0xFF
        if pad_count == 0:
            out += bytes([b1, b2, b3])
        elif pad_count == 1:
            out += bytes([b1, b2])
        elif pad_count == 2:
            out += bytes([b1])
    return bytes(out)

def decode():
    xorr_result = xorr(byte_2220, last())
    encoded_bytes = rotation(xorr_result)
    decoded = base64_decode(encoded_bytes)
    return decoded


flag = decode()
print(flag.decode())
