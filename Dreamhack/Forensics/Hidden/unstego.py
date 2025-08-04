#!/usr/bin/env python3
import zlib, base64
from PIL import Image

# 1. Mở ảnh stego
img = Image.open("flag.png")
px = img.load()
w, h = img.size

# 2. Đọc tất cả bit LSB theo thứ tự R, G, B
bits = []
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

# 3. Ghép mỗi 8 bit thành 1 byte
data = bytes(
    sum((bits[i + j] << (7 - j)) for j in range(8)) 
    for i in range(0, len(bits) // 8 * 8, 8)
)

# 4. Giải nén zlib
try:
    decompressed = zlib.decompress(data)
except Exception as e:
    print("❌ Lỗi decompress:", e)
    exit(1)

# 5. Giải Base64
try:
    decoded = base64.b64decode(decompressed)
except Exception as e:
    print("❌ Lỗi Base64 decode:", e)
    exit(1)

# 6. XOR ngược với key 0x55
plain = bytes(c ^ 0x55 for c in decoded)

# 7. In kết quả
print(plain.decode('utf-8', errors='ignore'))

