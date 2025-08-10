# -*- coding: utf-8 -*-
# BDSec CTF 2025 – Minar '52 Enigma
# Script tái tạo flag từ chương trình dịch ngược

v22 = 0x1B69081F0E736C4F
v23_part1 = 1282
v23_part2 = 0x6F707E090B5646B2
v23_part3 = -15810
v25 = 842348849
v26 = 1261904656

# Xây dựng mảng byte v22 và v23 như trên stack
v22_bytes = v22.to_bytes(8, 'little')

v23 = bytearray(12)
v23[0:2] = v23_part1.to_bytes(2, 'little', signed=False)
v23[2:10] = v23_part2.to_bytes(8, 'little', signed=False)
v23[10:12] = v23_part3.to_bytes(2, 'little', signed=True)

# Khởi tạo mảng v24
v24 = bytearray(21)
v24[0] = 66  # 'B'

for i in range(1, 20):
    idx = i - 8
    byte_val = v22_bytes[idx + 8] if idx < 0 else v23[idx]
    a = byte_val ^ 0xCC
    b = (v25 >> (8 * (i & 3))) & 0xFF
    c = (v26 >> (8 * (i & 3))) & 0xFF
    v24[i] = (a - b - c) & 0xFF

# Hiển thị mảng v24 ở dạng hex và ASCII
print("🔍 Hexdump v24:")
print(' '.join(f'{b:02x}' for b in v24))

# Lọc ký tự in được
ascii_secret = ''.join(chr(b) if 32 <= b < 127 else '?' for b in v24[:-1])
print("\n🔓 Decoded ASCII:", ascii_secret)

# In ra flag
print(f"\n🏁 Flag: BDSEC{{{ascii_secret}}}")

