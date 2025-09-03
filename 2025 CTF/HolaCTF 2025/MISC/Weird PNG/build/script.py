# build/script_fixed.py
from pathlib import Path

p = Path("weird.png")
data = p.read_bytes()

# PNG: 8 (sig) + 4 (len) + 4 ('IHDR') + 13 (IHDR data) + 4 (CRC) = 33 bytes
assert data[:8] == b"\x89PNG\r\n\x1a\n"
ihdr_len = int.from_bytes(data[8:12], "big")
assert data[12:16] == b"IHDR" and ihdr_len == 13
offset = 8 + 4 + 4 + ihdr_len + 4

boot = data[offset:offset+512]  # boot sector (kết thúc 55 AA)

out = []
i = 0
while i < len(boot):
    if boot[i] == 0xB8:                       # mov ax, imm16
        if i+2 >= len(boot): break
        ax = boot[i+1] | (boot[i+2] << 8)
        i += 3
        if i+2 < len(boot) and boot[i] == 0x35:   # xor ax, imm16 (tùy chọn)
            ax ^= (boot[i+1] | (boot[i+2] << 8))
            i += 3
        if i < len(boot) and boot[i] == 0x50:     # push ax
            out.append(ax)
            i += 1
        else:
            continue
    else:
        i += 1

# LIFO -> POP ra theo chiều ngược, mỗi word -> 2 ký tự (little-endian)
s = ''.join(chr(w & 0xFF) + chr((w >> 8) & 0xFF) for w in reversed(out))
print(s)
