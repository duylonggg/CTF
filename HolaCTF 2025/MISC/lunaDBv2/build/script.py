# needs: pip install pycryptodome
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import io, sys

H_START = bytes.fromhex('FF1337FF')
H_END   = bytes.fromhex('FFCAFEFF')
D_START = bytes.fromhex('FF7270FF')
D_END   = bytes.fromhex('FFEDEDFF')
F_START = bytes.fromhex('FFDEADFF')
F_END   = bytes.fromhex('FFBEEFFF')

def read_leb128_unsigned(f):
    res = 0; shift = 0
    while True:
        b = f.read(1)
        if not b: raise EOFError("leb128 eof")
        b = b[0]
        res |= ((b & 0x7F) << shift)
        if not (b & 0x80): break
        shift += 7
    return res

def read_field(f, want_bytes=False):
    flag = f.read(1)
    if not flag: raise EOFError("flag eof")
    flag = flag[0]
    if flag == 0x00:
        return b'' if want_bytes else ''
    if flag in (0x0b, 0x0c):
        n = read_leb128_unsigned(f)
        data = f.read(n)
        return data if (flag == 0x0c or want_bytes) else data.decode('utf-8', 'ignore')
    raise ValueError(f'bad flag {flag:#x}')

def bit_index(u64):
    if u64 in (0, 0xFFFFFFFFFFFFFFFF): return None
    return (u64.bit_length() - 1)  # vì chỉ set 1 bit -> idx

with open("secret.lunadb", "rb") as fh:
    blob = fh.read()

d0 = blob.find(D_START)+len(D_START)
d1 = blob.find(D_END)
f0 = blob.find(F_START)+len(F_START)
f1 = blob.find(F_END)

# footer -> các DES key 8 byte
keys = [blob[i:i+8] for i in range(f0, f1, 8)]

f = io.BytesIO(blob[d0:d1])
flag = None
while f.tell() < (d1 - d0):
    if (d1 - d0) - f.tell() < 2:
        break
    note_id = int.from_bytes(f.read(2), 'little')
    token   = read_field(f)
    first   = read_field(f)
    last    = read_field(f)
    email   = read_field(f)
    title   = read_field(f)
    keyfld  = int.from_bytes(f.read(8), 'little')
    enc     = read_field(f, want_bytes=True)
    f.seek(8+8+1, 1)  # skip creation, modification, suspended

    idx = bit_index(keyfld)
    if idx is None or not enc or idx >= len(keys): 
        continue
    pt = unpad(DES.new(keys[idx], DES.MODE_ECB).decrypt(enc), 8, style='pkcs7')
    s = pt.decode('utf-8', 'ignore')
    if "HOLACTF{" in s:
        flag = s.strip('\x00')
        break

print(flag)
