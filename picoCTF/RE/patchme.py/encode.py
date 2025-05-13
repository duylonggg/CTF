def str_xor(secret, key):
    # Extend key to secret length
    new_key = key
    i = 0
    while len(new_key) < len(secret):
        new_key += key[i]
        i = (i + 1) % len(key)
    return "".join([chr(ord(secret_c) ^ ord(new_key_c)) for (secret_c,new_key_c) in zip(secret,new_key)])

with open('flag.txt.enc', 'rb') as f:
    flag_enc = f.read()

# Giải mã với key "utilitarian"
decryption = str_xor(flag_enc.decode(), "utilitarian")
print("Flag:", decryption)

