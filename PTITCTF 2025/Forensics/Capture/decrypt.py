# decrypt_flag.py
# Giải AES-GCM theo đúng logic Flag.TryReveal() & Embeds.*

from Crypto.Cipher import AES

# ===== Embeds =====
AesNonce = bytes([
    236, 85, 150, 249, 133, 223, 22, 97, 218, 211, 38, 76
])

AesTag = bytes([
     56,  74,  98, 242,  57, 243, 115, 204,
    222, 253,  56, 232, 197, 107,  14, 225
])

AesCiphertext = bytes([
    174,  48,   7, 100, 207,  26,  27, 150, 166, 144,  90, 153,
    225, 176, 222, 113, 164, 197, 167,  77, 133, 132, 235,  43,
     43, 115,  86,  82,  85, 184,  28,  28, 219, 201,  31, 202,
     70,  19, 137,  96, 159,  89, 137,  51, 168, 115
])

KeyShard1 = bytes([
    121, 165,  33,  10,  18, 197, 254, 212, 240, 253,  79, 245,
     53,  48, 123,  46, 142, 215,  38, 213,  25, 168,   2, 224,
     53,  25,   9, 191, 221, 152, 199, 246
])

KeyShard2 = bytes([
     63, 201,  64, 109,  80, 176, 151, 184, 148, 152,  61, 183,
     76, 120,  26,  71, 224, 179,  22, 230,  56, 137,  35, 193,
     20,  56,  40, 158, 252, 185, 230, 215
])

# ===== Reconstruct secret key (XOR) =====
assert len(KeyShard1) == 32 and len(KeyShard2) == 32
secretKey = bytes([a ^ b for a, b in zip(KeyShard1, KeyShard2)])

# ===== AES-GCM decrypt =====
cipher = AES.new(secretKey, AES.MODE_GCM, nonce=AesNonce)
plaintext = cipher.decrypt_and_verify(AesCiphertext, AesTag)

print(plaintext.decode("utf-8"))
