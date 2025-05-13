def rc4_decrypt(ciphertext, key_bytes):
    # Mô phỏng v7[512] = [key]*256 + [0..255]
    S = [key_bytes[i % len(key_bytes)] for i in range(256)] + [i for i in range(256)]
    j = 0

    # KSA (Key Scheduling Algorithm)
    for i in range(256):
        j = (S[i] + j + S[i + 256]) % 256
        S[i + 256], S[j + 256] = S[j + 256], S[i + 256]

    # PRGA (Pseudo-Random Generation Algorithm)
    out = []
    i = j = 0
    for byte in ciphertext:
        i = (i + 1) % 256
        j = (j + S[i + 256]) % 256
        S[i + 256], S[j + 256] = S[j + 256], S[i + 256]
        k = (S[i + 256] + S[j + 256]) % 256
        out.append(byte ^ S[k + 256])
    return bytes(out)

# Dữ liệu mã hóa sẵn từ biến v11 trong C
ciphertext = bytes([
    0x7D, 0x08, 0xED, 0x47, 0xE5, 0x00, 0x88,
    0x3A, 0x7A, 0x36, 0x02, 0x29, 0xE4
])

# Tính key = sub_4010C0(...) ^ 0xDEADBEEF
# Như phân tích ở trên, nếu có byte nào (byte ^ 0x55) == 0x99 thì trả về 19, nên key = 19 ^ 0xDEADBEEF
v7 = 0xDEADBEEF ^ 19

# Biến key thành 4 byte (little endian)
key = v7.to_bytes(4, 'little')

# Giải mã
flag = rc4_decrypt(ciphertext, key)

# In ra
print("Flag:", "Flag{" + flag.decode('latin1') + "}")

