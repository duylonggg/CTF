#!/usr/bin/env python3
from PIL import Image

img = Image.open('monster.png')
bits = []
for y in range(img.height):
    for x in range(img.width):
        r, g, b, _ = img.getpixel((x, y))
        bits.extend([r&1, g&1, b&1])

# Gom 8 bit thành 1 byte rồi thành ký tự
chars = []
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    val = sum(bit<<j for j,bit in enumerate(byte))
    if val == 0: break      # nếu ra NULL, coi như kết thúc
    chars.append(chr(val))
print(''.join(chars))

