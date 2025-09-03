FLAG = b"PTITCTF{?????????????????????}"
from Crypto.Util.number import getPrime, isPrime, bytes_to_long
def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, "big")

def magicc(n: int) -> int:
        B = bin(n)[2:]
        M = ''.join('01' if b == '0' else '11' for b in B)
        return int(M, 2)
    
def keygen(nbit: int):
        while True:
            p = getPrime(nbit)
            r = magicc(p)             
            B = bin(p)[2:] + '1' * nbit
            q = int(B, 2)              
            if isPrime(q) and isPrime(r):
                return q, r 
def build_magic_constants(magic_bytes: bytes, e: int, nbit=256):
    Q, R = keygen(nbit)            
    n = Q * R
    m = bytes_to_long(magic_bytes)
    c = pow(m, e, n)
    return e, n, c           
N = int("7fed997cfb3a3e8440142aba39d2c62ef03e773f8d98d7d373b3e8336903ca122cdffa11fd4de735776c9aefdd1607c70f0c403bd745d2e3065fede7f22dbfa94ea22b833b2442bd474a88694305b0f389162ca25eddf2673baeb3b6a2855842a0a0a022a2a222a28802a2022888822a8a20aa20a28022a08088200a8a800801", 16)
C = int("16c88a06c4203b9ce6f5f652a52f449ce37347afb5cb25b0a1bf0b105f158246bd64adb2b6f2a563fa747d31b9ba4af54efd9449f6b75b1ea83015fefb1e1d206f20ca31fdf47ee45bbb382c9aa6e7ff7946f9973a2edebdb412bdc48e9a157cb36eb2e599c9c0a27153983d316b0d9ce08ef9d06f536b2ff29cf5393fba056d", 16)       
class Blake2b:
    __slots__ = ("h","t0","t1","f0","f1","buf","digest_size","closed","_had_key","_reveal","_ksp")

    IV = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179,
    ]

    SIGMA = [
        [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15],
        [14,10, 4, 8, 9,15,13, 6, 1,12, 0, 2,11, 7, 5, 3],
        [11, 8,12, 0, 5, 2,15,13,10,14, 3, 6, 7, 1, 9, 4],
        [ 7, 9, 3, 1,13,12,11,14, 2, 6, 5,10, 4, 0,15, 8],
        [ 9, 0, 5, 7, 2, 4,10,15,14, 1,11,12, 6, 8, 3,13],
        [ 2,12, 6,10, 0,11, 8, 3, 4,13, 7, 5,15,14, 1, 9],
        [12, 5, 1,15,14,13, 4,10, 0, 7, 6, 3, 9, 2, 8,11],
        [13,11, 7,14,12, 1, 3, 9, 5, 0,15, 4, 8, 6, 2,10],
        [ 6,15,14, 9,11, 3, 0, 8,12, 2,13, 7, 1, 4,10, 5],
        [10, 2, 8, 4, 7, 6, 1, 5,15,11, 9,14, 3,12, 13, 0],
        [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14, 15],
        [14,10, 4, 8, 9,15,13, 6, 1,12, 0, 2,11, 7, 5, 3],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0, 0, 0, 0, 0, 0],  
    ]

    MASK = (1<<64) - 1
    BLOCK_SIZE = 128

    @classmethod
    def _exp_from_sigma(cls) -> int:     
        s10 = cls.SIGMA[12][:10]  
        return int(''.join(str(x) for x in s10))

    def __init__(self, data=b"", *, digest_size=64, key=b"", salt=b"", person=b""):
        if not (1 <= digest_size <= 64):
            raise ValueError("digest_size must be in 1..64")
        if len(key) > 64:
            raise ValueError("key length must be <= 64")
        if len(salt) > 16:
            raise ValueError("salt length must be <= 16")
        if len(person) > 16:
            raise ValueError("person length must be <= 16")

        self.digest_size = digest_size
        self.h = self.IV[:]
        self.t0 = 0; self.t1 = 0
        self.f0 = 0; self.f1 = 0
        self.buf = b""
        self.closed = False
        self._had_key = bool(key)
        self._reveal = False
        self._ksp = (key or b"") + (salt or b"") + (person or b"")

        # Param block
        param = bytearray(64)
        param[0] = digest_size & 0xff
        param[1] = len(key) & 0xff
        param[2] = 1  # fanout
        param[3] = 1  # depth
        salt_b = (salt + b"\x00"*16)[:16]
        person_b = (person + b"\x00"*16)[:16]
        param[24:40] = salt_b
        param[40:56] = person_b

        for i in range(8):
            w = int.from_bytes(param[i*8:(i+1)*8], "little")
            self.h[i] ^= w

        if key:
            block = (key + b"\x00"*(self.BLOCK_SIZE - len(key)))[:self.BLOCK_SIZE]
            self._add_counter(self.BLOCK_SIZE)
            self._compress(block, is_last=False)

        if data:
            self.update(data)

    @staticmethod
    def _rotr64(x, n):
        return ((x >> n) | ((x << (64 - n)) & Blake2b.MASK)) & Blake2b.MASK

    def _G(self, v, a, b, c, d, x, y):
        m = self.MASK
        v[a] = (v[a] + v[b] + x) & m
        v[d] = self._rotr64(v[d] ^ v[a], 32)
        v[c] = (v[c] + v[d]) & m
        v[b] = self._rotr64(v[b] ^ v[c], 24)
        v[a] = (v[a] + v[b] + y) & m
        v[d] = self._rotr64(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & m
        v[b] = self._rotr64(v[b] ^ v[c], 63)

    def _add_counter(self, inc):
        t0 = self.t0 + inc
        self.t1 = (self.t1 + (t0 >> 64)) & self.MASK
        self.t0 = t0 & self.MASK

    def _compress(self, block, is_last):
        m = [int.from_bytes(block[i*8:(i+1)*8], "little") for i in range(16)]
        v = self.h[:] + self.IV[:]
        v[12] ^= self.t0
        v[13] ^= self.t1
        if is_last:
            v[14] ^= self.MASK  

        for r in range(12):
            s = self.SIGMA[r]
            self._G(v, 0, 4,  8, 12, m[s[0]],  m[s[1]])
            self._G(v, 1, 5,  9, 13, m[s[2]],  m[s[3]])
            self._G(v, 2, 6, 10, 14, m[s[4]],  m[s[5]])
            self._G(v, 3, 7, 11, 15, m[s[6]],  m[s[7]])
            self._G(v, 0, 5, 10, 15, m[s[8]],  m[s[9]])
            self._G(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
            self._G(v, 2, 7,  8, 13, m[s[12]], m[s[13]])
            self._G(v, 3, 4,  9, 14, m[s[14]], m[s[15]])

        for i in range(8):
            self.h[i] = (self.h[i] ^ v[i] ^ v[i + 8]) & self.MASK

    def update(self, data: bytes):
        if self.closed:
            raise ValueError("cannot update() after digest()")
        if not data:
            return
        self.buf += data
        while len(self.buf) > self.BLOCK_SIZE:
            block = self.buf[:self.BLOCK_SIZE]
            self.buf = self.buf[self.BLOCK_SIZE:]
            self._add_counter(self.BLOCK_SIZE)
            self._compress(block, is_last=False)

        
    def _finalize(self):
        if self.closed:
            return

        only_key_processed = (self.t0 == (self.BLOCK_SIZE if self._had_key else 0))
        if only_key_processed:
            m = bytes_to_long(self.buf)
            E = self._exp_from_sigma()
            if pow(m % N, E, N) == C:
                self._reveal = True

        self._add_counter(len(self.buf))
        last_block = self.buf + b"\x00" * (self.BLOCK_SIZE - len(self.buf))
        self._compress(last_block, is_last=True)
        self.closed = True
        self.buf = b""

    def digest(self) -> bytes:
        self._finalize()
        out = b"".join(h.to_bytes(8, "little") for h in self.h)
        return out[:self.digest_size]

    def hexdigest(self) -> str:
        return self.digest().hex()

def blake2b(data=b"") -> Blake2b:
    return Blake2b(data, digest_size=64, key=b"N", salt=b"C", person=b"")

if __name__ == "__main__":
    s = input("Nhập chuỗi cần băm: ")
    data = s.encode("utf-8")
    h = blake2b(data)
    d = h.digest()
    if getattr(h, "_reveal", False):
        print(FLAG.decode(errors="ignore"))
    else:
        print(d.hex())
