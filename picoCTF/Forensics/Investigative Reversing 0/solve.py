# 26 byte hex từ mystery.png
data = bytes.fromhex("70 69 63 6F 43 54 4B 80 6B 35 7A 73 69 64 36 71 5F 33 64 36 35 39 66 35 37 7D")

original = bytearray()

# Byte 0–5: giữ nguyên
original.extend(data[0:6])

# Byte 6–14: trừ 5
for i in range(6, 15):
    original.append((data[i] - 5) % 256)

# Byte 15: cộng lại 3
original.append((data[15] + 3) % 256)

# Byte 16–25: giữ nguyên
original.extend(data[16:26])

# In flag
print("Flag:")
print(original.decode())

