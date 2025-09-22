g_flag_enc = bytes([
    0x71,0xBE,0x3D,0xF5,0x64,0x7B,0xB8,0xF5,0x6D,0xBA,0x97,0xA2,0x0A,0xB6,0x1A,0x50,
    0xBD,0xBF,0x4F,0x73,0xA1,0xA7,0xF7,0xB8,0xBF,0x36,0x62,0xDB,0x10,0x91,0x65,0xB5,
    0x78,0xE0,0x94,0xB8,0xAE,0xD9,0x3A
])

def ror8(x, n):
    n &= 7
    x &= 0xFF
    return ((x >> n) | ((x << (8 - n)) & 0xFF)) & 0xFF

def decode(v13: int) -> bytes:
    out = bytearray()
    v16 = 85  # starts at 85, +7 each step
    for i, b in enumerate(g_flag_enc):
        # s = i - (i/5 + (((0xCCCCCCCCCCCCCCCD * i) >> 64) & 0xFC))
        magic = (0xCCCCCCCCCCCCCCCD * i) >> 64  # floor(4*i/5)
        s = i - (i // 5 + (magic & 0xFC))
        r = ror8(b, s)
        v18 = (v16 & 0xFF) ^ r
        v16 = (v16 + 7) & 0xFFFFFFFF
        k = (v13 >> (8 * (i & 3))) & 0xFF  # 4-byte key cycling
        out.append(v18 ^ k)
    return bytes(out)

if __name__ == "__main__":
    import sys
    # v13 chọn theo nhánh anti-debug (v8 >= 2)
    v13 = 0x80655774
    if len(sys.argv) > 1:
        v13 = int(sys.argv[1], 0)  # cho phép truyền 0x... hoặc thập phân
    pt = decode(v13)
    try:
        print(pt.decode("ascii"))
    except UnicodeDecodeError:
        print(pt)
