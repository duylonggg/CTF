#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util import Counter

# ---- Thay các giá trị tại đây nếu cần ----
AES_KEY_ASCII = "PTIT_CTF2025_KEY"
AES_IV_ASCII  = "InitializationVe"
AES_CIPH_B64  = "rNxBkug3ri07khz2rKqQY+bv6GyhHZD/gbM4y2lUAUDENzGNDYeu1eNCWl9cTkyo"
# -----------------------------------------

KEY = AES_KEY_ASCII.encode("utf-8")
IV  = AES_IV_ASCII.encode("utf-8")
CIPH = base64.b64decode(AES_CIPH_B64)

def show(name, data: bytes):
    print(f"\n[{name}] len={len(data)}")
    try:
        s = data.decode("utf-8")
        print("utf-8:", s)
    except UnicodeDecodeError:
        print("hex:", data.hex())

def decrypt():
    try:
        pt = AES.new(KEY, AES.MODE_CBC, IV).decrypt(CIPH)
        pt = unpad(pt, 16)
        show("AES-128-CBC (PKCS7)", pt)
    except Exception as e:
        print("[AES-128-CBC] fail:", e)

def main():
    print("KEY(len=%d) =", len(KEY), KEY)
    print("IV (len=%d) =" % len(IV), IV)
    print("CIPH(b64)   =", AES_CIPH_B64)
    decrypt()

if __name__ == "__main__":
    main()
