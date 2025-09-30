# SunshineCTF 2025 — Access Code (Satellite Terminal) — Writeup (Tiếng Việt)

Tài liệu này mô tả **chi tiết từng bước**, mọi công cụ và script mình đã dùng để khôi phục **access code** (cũng chính là flag) từ cartridge **PEGASUS** được cung cấp. Bạn có thể làm theo để tái hiện kết quả.

---

## Tệp thử thách

Các tệp được cung cấp (đường dẫn như mình dùng trong môi trường làm việc):

```txt
/mnt/data/runpeg            # Trình chạy máy ảo PEGASUS kèm debugger (EAR)
/mnt/data/libear.so         # Runtime PEG
/mnt/data/libeardbg.so      # Addon debugger
/mnt/data/AccessCode.peg    # Cartridge/chương trình cần phân tích
```

Chương trình yêu cầu nhập **security access code**. Gõ `forgot` thì nó in ra một **digest 32 byte** (không phải flag). Mục tiêu là khôi phục **access code thật** để chương trình in `Access granted!`. Access code đúng có dạng `sun{...}` và là **flag**.

---

## Tóm tắt nhanh (TL;DR)

1. Chạy cartridge kèm **debugger** và mở **UNIX socket** để gửi input từ ngoài.
2. Đặt breakpoint bên trong hàm **Gimli hash update** để xem **plaintext** nào được đưa vào hash.
3. Bắt được 3 khối hấp thụ “bulk” (`sun{`, `th3_`, `fun_p`) và sau đó là vòng lặp **per-byte** giải mã ký tự rồi hấp thụ dần phần đuôi.
4. Nối các byte thu được theo đúng thứ tự: `sun{` + `th3_` + `fun_p` + `4r7_15_nEAR` + `}`.
5. Nhập `sun{th3_fun_p4r7_15_nEAR}` → **Access granted!** (đúng flag).

---

## Môi trường & kiểm tra nhanh

- Hệ điều hành: Linux
- Python 3.10+
- (Tuỳ chọn) `nc`/`socat` để nói chuyện qua UNIX socket
- Có thể thử `hashcat` để xác thực “đường cụt”

### Chạy thường

```bash
chmod +x /mnt/data/runpeg
/mnt/data/runpeg /mnt/data/AccessCode.peg
```

Màn hình:

```
Input security access code:
>
```

### Thử `forgot` (để quan sát)

Nhập:
```
forgot
```

Kết quả (ví dụ):

```
f33e5289cd2d110546cc1dce76affff61faef703ed4e2a3580baee52f7c10cdb
```

Chuỗi này nhìn giống SHA‑256 nên mình **đã thử** Hashcat (để ghi nhận đường cụt):

```bash
hashcat -m 1400 -a 0 \
  f33e5289cd2d110546cc1dce76affff61faef703ed4e2a3580baee52f7c10cdb \
  /usr/share/wordlists/rockyou.txt -O
```

Kết quả: **Exhausted**, không tìm thấy. Kết luận: digest **không phải** SHA‑256 của 1 từ phổ thông; sau đó ta xác minh digest là của **Gimli** (thuật toán hash mà chương trình dùng) tính trên **access code thật** do chương trình **tự lắp ghép**.

> Ghi chú: Mình có chuẩn bị 1 script brute SHA‑256 (không cần cho lời giải, chỉ để tham khảo).

```python
#!/usr/bin/env python3
# crack_access_code.py  (đường cụt, không cần cho lời giải)
import argparse, hashlib, itertools, time, string

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

ALPH = {
    'd': string.digits,
    'l': string.ascii_lowercase,
    'u': string.ascii_uppercase,
    'a': string.ascii_letters + string.digits,
}

def expand_mask(mask):
    pools = []
    i=0
    while i < len(mask):
        if mask[i] == '?' and i+1 < len(mask) and mask[i+1] in ALPH:
            pools.append(ALPH[mask[i+1]])
            i += 2
        else:
            pools.append(mask[i])
            i += 1
    return pools

def crack_wordlist(target, wordlist_path):
    t0=time.time()
    with open(wordlist_path, 'r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            s = line.rstrip('\r\n')
            if sha256_hex(s) == target:
                print(f"[HIT] {s}")
                print(f"[OK] time={time.time()-t0:.2f}s, tried={i:,}")
                return True
            if i % 500000 == 0:
                print(f"[.] tried {i:,}...")
    print("[X] not found in wordlist")
    return False

def crack_mask(target, mask):
    pools = []
    for p in expand_mask(mask):
        pools.append(p if isinstance(p, str) and len(p)>1 else [p])
    total = 1
    for it in pools: total *= len(it)
    print(f"[i] total candidates ~ {total:,}")
    t0=time.time()
    tried=0
    for combo in itertools.product(*pools):
        s = ''.join(combo)
        tried += 1
        if sha256_hex(s) == target:
            print(f"[HIT] {s}")
            print(f"[OK] time={time.time()-t0:.1f}s, tried={tried:,}")
            return True
        if tried % 5_000_000 == 0:
            print(f"[.] tried {tried:,}")
    print("[X] not found in this mask chunk")
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hash")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("-w","--wordlist")
    g.add_argument("-m","--mask")
    args = ap.parse_args()
    if args.wordlist: crack_wordlist(args.hash, args.wordlist)
    else: crack_mask(args.hash, args.mask)

if __name__ == "__main__":
    main()
```

---

## Debug với EAR (trình gỡ lỗi tích hợp)

Chạy cartridge kèm debugger:

```bash
/mnt/data/runpeg /mnt/data/AccessCode.peg --debug
```

**Lệnh debugger** dùng nhiều:

- `disasm <count> <addr>` — disassemble
- `b <addr>` — đặt breakpoint
- `c` — continue
- `registers` — xem thanh ghi (có alias như `PC`, `FP`, `S1`, `S2`)
- `context` — in trạng thái thread (tiện cho parse tự động)
- `hexdump <addr> <len> R` — đọc RAM
- `backtrace`, `vmmap` — hỗ trợ

### Dùng UNIX socket để gửi input

Mở socket cho **port 0** (stdin) để vừa dừng ở debugger vừa gửi input:

```bash
/mnt/data/runpeg /mnt/data/AccessCode.peg --debug --io-listen /tmp/ear.sock
# terminal khác:
printf "forgot\n" | nc -U /tmp/ear.sock
```

Trong writeup này mình dùng **Python** để tự động hoá: đặt breakpoint → gửi `forgot` → đọc “Thread state” → hexdump

---

## Xác định đường băm (hashing path)

Khi nhập `forgot`, cartridge đi vào routine **xây chuỗi access code thật** rồi băm bằng **Gimli**.

Hai điểm quan sát chính:

- **Call site `gimli_hash_update`** — rất tiện vì tại đây thanh ghi giữ **con trỏ và độ dài** plaintext sắp hấp thụ.
  - Breakpoint: `0x0532`
  - Trong “Thread state”, alias **`(S1)R8`** = **pointer**, **`(S2)R9`** = **length**
- **Vòng lặp hấp thụ từng byte** — bytes được **giải mã từ bảng** (PC‑relative) rồi đưa vào `gimli_absorb_byte`.
  - Điểm quan sát tuyệt vời: **`0x0729`** — ngay trước khi gọi absorb byte, **ký tự đã giải mã** nằm trong **A1**.
  - `gimli_absorb_byte` ở `0x04E9` (load tại `0x04F0`), nhưng đọc A1 ở `0x0729` gọn hơn nhiều.

### Các khối “bulk” (tại `0x0532`)

Đặt `b 0532`, gửi `forgot\n`, mỗi lần dừng lại ta đọc `S1..S1+S2`. Ba lần dừng đầu tiên lần lượt cho:

1) `sun{` (4 byte)
2) `th3_` (4 byte)
3) `fun_p` (5 byte — literal ở vùng rodata; xác nhận qua disasm PC‑relative)

Đúng như flow: đẩy immediate 16‑bit lên stack, rồi helper xuất tiếp 4 ký tự, rồi lấy literal 5 byte ở địa chỉ PC‑relative.

### Phần đuôi per‑byte (tại `0x0729`)

Sau `fun_p`, code vào vòng lặp; mỗi vòng giải mã 1 byte từ bảng và hấp thụ. Đặt breakpoint ở **`0x0729`**, gọi `registers` để đọc **A1** (ký tự **đã giải mã**).

Chuỗi thu được:

```
"4r7_15_nEAR}"
```

Ký tự `}` xuất hiện cuối cùng (nhìn thấy dừng ở `0x0734`).

### Ghép chuỗi hoàn chỉnh

Ghép đúng **thứ tự phát sinh** trong chương trình:

```
sun{ + th3_ + fun_p + 4r7_15_nEAR + }
```

→ **`sun{th3_fun_p4r7_15_nEAR}`**

---

## Xác thực

Chạy bình thường, nhập:

```
sun{th3_fun_p4r7_15_nEAR}
```

Kết quả:

```
Access granted!
```

Ngoài ra, có thể xác minh băm bằng debugger: dừng tại **`0x07E1`** (ngay trước `memcmp`), dump:

- **User digest** tại `[FP-0x22]`
- **Const digest** tại `[PC+0x24D]` (với `PC=0x07E1` → địa chỉ `0x0A2E`)

Hai buffer 32 byte **trùng nhau** khi access code đúng.

Script nhỏ (mình dùng trong lúc thử nghiệm) để test nhanh “digest có bằng nhau không”:

```python
# test_digest_equal.py
import subprocess, os, time, socket, fcntl, re, sys

def digest_equal(candidate: str) -> bool:
    sock="/tmp/ear.sock"
    try: os.unlink(sock)
    except: pass
    p=subprocess.Popen(
        ["./runpeg","./AccessCode.peg","--debug","--io-listen",sock],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=0
    )
    fd=p.stdout.fileno()
    fl=fcntl.fcntl(fd, fcntl.F_GETFL); fcntl.fcntl(fd, fcntl.F_SETFL, fl|os.O_NONBLOCK)

    def drain():
        out=b""
        while True:
            try: out+=os.read(fd,65536)
            except BlockingIOError: break
        return out.decode(errors="ignore")

    time.sleep(0.1); _=drain()
    p.stdin.write("b 07E1\nc\n"); p.stdin.flush()
    time.sleep(0.05)

    s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(sock)
    s.sendall((candidate+"\n").encode())
    time.sleep(0.2)
    out=drain()
    m=re.search(r"\(FP\)R10:\s*([0-9A-Fa-f]{4})", out)
    if not m: return False
    fp=int(m.group(1),16)
    digest_addr=(fp-0x22)&0xFFFF

    p.stdin.write(f"hexdump {digest_addr:04x} 32 R\n"); p.stdin.flush(); time.sleep(0.05)
    d=drain()
    p.stdin.write("hexdump 0a2e 32 R\n"); p.stdin.flush(); time.sleep(0.05)
    c=drain()

    def parse(txt):
        bs=[]
        for ln in txt.splitlines():
            if ln.startswith("R::"):
                words=re.findall(r"\b[0-9A-Fa-f]{4}\b", ln.split("|",1)[1])
                for w in words:
                    bs.append(int(w[:2],16)); bs.append(int(w[2:],16))
                    if len(bs)>=32: break
        return bytes(bs)[:32]

    user=parse(d); const=parse(c)
    return user==const

if __name__ == "__main__":
    print(digest_equal(sys.argv[1]))
```

---

## Script tự động hoá (mình đã dùng)

> Các script dưới đây **không sửa đổi** cartridge; chỉ **đọc** trạng thái khi bạn gõ `forgot`.

### 1) Bắt 3 khối bulk tại `0x0532`

```python
# capture_bulk_chunks.py
import subprocess, os, time, socket, fcntl, re

sock="/tmp/ear.sock"
try: os.unlink(sock)
except: pass

p=subprocess.Popen(
    ["./runpeg","./AccessCode.peg","--debug","--io-listen",sock],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, bufsize=0
)
fd=p.stdout.fileno()
fl=fcntl.fcntl(fd, fcntl.F_GETFL); fcntl.fcntl(fd, fcntl.F_SETFL, fl|os.O_NONBLOCK)

def drain():
    out=b""
    while True:
        try: out+=os.read(fd,65536)
        except BlockingIOError: break
    return out.decode(errors="ignore")

time.sleep(0.15); _=drain()
p.stdin.write("b 0532\nc\n"); p.stdin.flush()

s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(sock)
s.sendall(b"forgot\n")

chunks=[]
for _ in range(3):
    time.sleep(0.05)
    out = drain()
    m = re.findall(r"Thread state:\s+(.*?)\n\nNext instructions:", out, flags=re.S)
    block = m[-1]
    a = int(re.search(r"\(S1\)R8:\s*([0-9A-Fa-f]{4})", block).group(1), 16)
    l = int(re.search(r"\(S2\)R9:\s*([0-9A-Fa-f]+)", block).group(1), 16)
    p.stdin.write(f"hexdump {a:04x} {l} R\n"); p.stdin.flush(); time.sleep(0.02)
    dump = drain()
    data=[]
    for ln in dump.splitlines():
        if not ln.startswith("R::"): continue
        for w in ln.split("|",1)[1].split():
            if len(w)==4:
                data.append(int(w[:2],16)); 
                if len(data)>=l: break
                data.append(int(w[2:],16))
                if len(data)>=l: break
        if len(data)>=l: break
    chunks.append(bytes(data))
    p.stdin.write("c\n"); p.stdin.flush()

print([c.decode() for c in chunks])  # ['sun{','th3_','fun_p']
```

### 2) Bắt phần đuôi per-byte tại `0x0729`

```python
# capture_tail.py
import subprocess, os, time, socket, fcntl, re

sock="/tmp/ear.sock"
try: os.unlink(sock)
except: pass

p=subprocess.Popen(
    ["./runpeg","./AccessCode.peg","--debug","--io-listen",sock],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, bufsize=0
)
fd=p.stdout.fileno()
fl=fcntl.fcntl(fd, fcntl.F_GETFL); fcntl.fcntl(fd, fcntl.F_SETFL, fl|os.O_NONBLOCK)

def drain():
    out=b""
    while True:
        try: out+=os.read(fd,65536)
        except BlockingIOError: break
    return out.decode(errors="ignore")

time.sleep(0.15); _=drain()
p.stdin.write("b 0729\nb 0734\nc\n"); p.stdin.flush()

s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(sock)
s.sendall(b"forgot\n")

vals=[]
done=False
while not done:
    time.sleep(0.01)
    out=drain()
    if "A breakpoint was hit" in out:
        m=re.findall(r"Thread state:\s+(.*?)\n\nNext instructions:", out, flags=re.S)
        block = m[-1]
        pc=int(re.search(r"\(PC\)R14:\s*([0-9A-Fa-f]{4})", block).group(1),16)
        if pc==0x0729:
            p.stdin.write("registers\n"); p.stdin.flush(); time.sleep(0.002)
            regtxt=drain()
            a1=int(re.search(r"\(A1\)[^:]*:\s*([0-9A-Fa-f]{4})", regtxt).group(1),16) & 0xFF
            vals.append(a1)
            p.stdin.write("c\n"); p.stdin.flush()
        elif pc==0x0734:
            done=True
            p.stdin.write("c\n"); p.stdin.flush()

print(bytes(vals).decode())  # "4r7_15_nEAR}"
```

---

## Mốc địa chỉ quan trọng (đã dùng)

- `0x0532` — bên trong `gimli_hash_update`; `(S1,S2)` đang giữ (pointer, length) → cực tiện để đọc plaintext (`sun{`, `th3_`, `fun_p`).
- `0x04E9` / `0x04F0` — `gimli_absorb_byte` entry / load đầu tiên; có thể dùng, nhưng đọc tại `0x0729` gọn hơn.
- `0x0729` — vòng lặp per‑byte, **A1** chứa ký tự đã giải mã trước khi hấp thụ.
- `0x0734` — kết thúc vòng lặp (lấy làm điểm dừng).
- `0x07DC` / `0x07E1` — sau `gimli_hash_final`, trước `memcmp` với const digest.
- `PC+0x24D` tại `0x07E1` → `0x0A2E` — địa chỉ const digest 32 byte trong ROM.

Không cần đảo ngược bảng obfuscation; chỉ cần xem **A1** tại `0x0729` là đủ.

---

## Kinh nghiệm rút ra

- `forgot` là “gợi ý” rằng chương trình **tự lắp access code rồi băm** (Gimli). Đừng brute SHA‑256 vô ích.
- EAR rất mạnh: alias `S1/S2` ở call site giúp bắt plaintext cực dễ.
- Chuỗi được lắp kiểu hỗn hợp: literal 16‑bit, literal rodata, rồi “đuôi” per‑byte từ bảng PC‑relative.
- Các ngõ cụt (hashcat, đoán mò) là bình thường trong CTF RE — hãy ưu tiên **lấy sự thật từ runtime** bằng breakpoint/hexdump.

---

## Kết luận

**Flag:** `sun{th3_fun_p4r7_15_nEAR}`

`Access granted!` ✅
