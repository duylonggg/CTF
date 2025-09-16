#!/usr/bin/env python3
from pwn import remote, context
import base64, re, time

# ===== kCTF PoW (Sloth) inline =====
VERSION='s'
MODULUS=(1<<1279)-1
def _b64e(n:int)->str:
    size=(n.bit_length()//24)*3+3
    return base64.b64encode(n.to_bytes(size,'big')).decode()
def _b64d_num(s:str)->int:
    return int.from_bytes(base64.b64decode(s.encode()),'big')
def _dec_chal(enc:str):
    ver,*rest=enc.split('.')
    assert ver==VERSION
    return list(map(_b64d_num,rest))
def _enc_chal(arr): return '.'.join([VERSION]+list(map(_b64e,arr)))
def _sloth_root(x,d,p):
    e=(p+1)//4
    for _ in range(d): x=pow(x,e,p)^1
    return x
def _sloth_square(y,d,p):
    for _ in range(d): y=pow(y^1,2,p)
    return y
def solve_pow_token(chal:str)->str:
    diff,x=_dec_chal(chal)
    y=_sloth_root(x,diff,MODULUS)
    sol=_enc_chal([y])
    yy=_dec_chal(sol)[0]
    assert x==_sloth_square(yy,diff,MODULUS) or MODULUS-x==_sloth_square(yy,diff,MODULUS)
    return sol

# ===== Challenge I/O =====
HOST="feistier-network.chal.imaginaryctf.org"; PORT=1337
SEED=0
context.log_level="info"
B64LINE=re.compile(rb"^[A-Za-z0-9+/]{44,}={0,2}\s*$")

def wait_for(io, needle:bytes, tout=5.0):
    buf=b""
    t0=time.time()
    while time.time()-t0 < tout:
        try:
            chunk=io.recv(4096, timeout=0.5)
        except: chunk=b""
        if chunk:
            buf+=chunk
            if needle in buf: return True
    return False

def pass_pow(io):
    token=None
    # đọc tới 'Solution?'
    t0=time.time()
    while time.time()-t0<15:
        line=io.recvline(timeout=2).decode('utf-8','ignore')
        if "kctf-pow" in line and "solve " in line:
            token=line.split("solve",1)[1].strip().split()[0]
        if line.strip().endswith("Solution?"):
            break
    if not token: raise RuntimeError("Không lấy được PoW token")
    io.sendline(solve_pow_token(token).encode())

def b64_of_int(n:int)->bytes:
    b=n.to_bytes((n.bit_length()+7)//8 or 1,'big')
    return base64.b64encode(b)

def recv_b64(io, tries=200, tout=2.0):
    for _ in range(tries):
        try: line=io.recvline(timeout=tout)
        except: line=b""
        if not line: continue
        s=line.strip()
        if B64LINE.fullmatch(s): return s
    return None

def get_flag_ct(seed:int)->bytes:
    io=remote(HOST,PORT,level="error")
    pass_pow(io)
    # server hỏi seed bằng input() ngay, cứ gửi luôn
    io.sendline(b64_of_int(seed))
    # đợi menu
    wait_for(io, b") print custom message", tout=5.0)
    io.sendline(b"1")
    ct=recv_b64(io)
    io.close()
    if not ct: raise RuntimeError("Không nhận ciphertext flag")
    return ct

def enc(seed:int, msg_b64:bytes)->bytes|None:
    io=remote(HOST,PORT,level="error")
    pass_pow(io)
    io.sendline(b64_of_int(seed))
    wait_for(io, b") print custom message", tout=5.0)
    io.sendline(b"2")
    # cực kỳ quan trọng: chờ đúng prompt 'sure what's the message: '
    ok = wait_for(io, b"sure what's the message", tout=5.0)
    if not ok:
        # fallback: một số instance in prompt ngay trước khi đọc
        time.sleep(0.2)
    io.sendline(msg_b64)
    out=recv_b64(io, tries=400, tout=2.0)
    io.close()
    return out

def swap_halves_b64(b64s:str)->bytes:
    b=base64.b64decode(b64s)
    b=b[32:]+b[:32]
    return base64.b64encode(b)

def looks_flag(b:bytes)->bool:
    s=b.rstrip(b"\x00").decode("utf-8","ignore")
    return s.startswith("ictf{") and "}" in s

def main():
    print(f"[*] Lấy C_flag với seed={SEED}")
    C=get_flag_ct(SEED)
    print("[+] C =", C.decode())

    # A) E(C)
    print("[*] Thử A: E(C)")
    outA=enc(SEED, C)
    if outA:
        raw=base64.b64decode(outA)
        if looks_flag(raw):
            print("[+] Flag (A):", raw.rstrip(b"\x00").decode()); return

    # B) swap->E->swap
    print("[*] Thử B: swap->E->swap")
    Cswap=swap_halves_b64(C.decode())
    outB=enc(SEED, Cswap)
    if outB:
        raw=base64.b64decode(outB)
        raw=raw[32:]+raw[:32]
        if looks_flag(raw):
            print("[+] Flag (B):", raw.rstrip(b"\x00").decode()); return

    print("[-] Không ra bằng A/B. Nếu bản server đúng hệt chal.py bạn dump, bài này không thể giải crypto.")
    print("    Nếu vẫn nghi server khác mã, mình sẽ thêm bộ 'probe' nhiều biến thể để tự xác định bug và in flag.")

if __name__=="__main__":
    main()
