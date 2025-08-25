# Forensics - Memory

## Xem các tiến trình

Bài này anh em sẽ dùng `Volatility3` để xem file `.raw` này nhé

Link tải anh em lên `GitHub` tìm là thấy

```bash
$ ~/volatility3/vol.py -f memory.raw windows.pslist
Volatility 3 Framework 2.26.2
Progress:  100.00               PDB scanning finished
PID     PPID    ImageFileName   Offset(V)       Threads Handles SessionId       Wow64   CreateTime      ExitTime        File output

4       0       System  0x83047167e040  130     -       N/A     False   2025-07-24 05:02:27.000000 UTC  N/A     Disabled
496     4       smss.exe        0x83047288e580  2       -       N/A     False   2025-07-24 05:02:27.000000 UTC  N/A     Disabled
600     592     csrss.exe       0x830472b24580  10      -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
688     496     smss.exe        0x830472cd0080  0       -       1       False   2025-07-24 05:02:29.000000 UTC  2025-07-24 05:02:29.000000 UTC  Disabled
696     592     wininit.exe     0x830472cd4080  1       -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
708     688     csrss.exe       0x830472ce1080  12      -       1       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
756     688     winlogon.exe    0x830472cf91c0  3       -       1       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
824     696     services.exe    0x830472d2a340  6       -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
832     696     lsass.exe       0x830472cfa080  7       -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
916     756     fontdrvhost.ex  0x830472d3a580  5       -       1       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
924     696     fontdrvhost.ex  0x830472d9f580  5       -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
960     824     svchost.exe     0x830472daa580  16      -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
476     824     svchost.exe     0x830473127240  11      -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
1000    756     dwm.exe 0x830473179580  12      -       1       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
1092    824     svchost.exe     0x830472b47580  60      -       0       False   2025-07-24 05:02:29.000000 UTC  N/A     Disabled
1120    824     svchost.exe     0x830472b5d580  18      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1136    824     svchost.exe     0x830472b67580  15      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1156    824     svchost.exe     0x830472b73580  24      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1300    824     svchost.exe     0x830472bd7580  49      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1440    4       MemCompression  0x83047168b580  14      -       N/A     False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1480    824     svchost.exe     0x83047168e580  21      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1520    824     svchost.exe     0x8304716ff580  8       -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1548    824     svchost.exe     0x830473007240  5       -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1560    824     svchost.exe     0x8304716f2580  9       -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1676    824     svchost.exe     0x83047305b580  13      -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1772    824     svchost.exe     0x830472ee8580  7       -       0       False   2025-07-24 05:02:30.000000 UTC  N/A     Disabled
1864    824     spoolsv.exe     0x830472f12580  8       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
1360    824     svchost.exe     0x830472fc9580  5       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
1544    824     svchost.exe     0x830472fda580  11      -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2080    824     SecurityHealth  0x83047309a580  7       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2096    824     vm3dservice.ex  0x8304730d9580  3       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2104    824     vmtoolsd.exe    0x8304730bc580  14      -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2112    824     svchost.exe     0x8304730bb240  5       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2120    824     VGAuthService.  0x8304730bf580  2       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2200    2096    vm3dservice.ex  0x8304739a3580  4       -       1       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2300    960     WmiPrvSE.exe    0x8304739e9580  9       -       0       False   2025-07-24 05:02:31.000000 UTC  N/A     Disabled
2824    824     dllhost.exe     0x830473c29580  12      -       0       False   2025-07-24 05:02:33.000000 UTC  N/A     Disabled
2912    824     msdtc.exe       0x830473c71340  9       -       0       False   2025-07-24 05:02:33.000000 UTC  N/A     Disabled
3180    1092    sihost.exe      0x830473db6080  8       -       1       False   2025-07-24 05:03:13.000000 UTC  N/A     Disabled
3208    824     svchost.exe     0x830473dc3580  10      -       1       False   2025-07-24 05:03:13.000000 UTC  N/A     Disabled
3244    1092    taskhostw.exe   0x830473deb080  10      -       1       False   2025-07-24 05:03:13.000000 UTC  N/A     Disabled
3392    1136    ctfmon.exe      0x830473e3a580  7       -       1       False   2025-07-24 05:03:13.000000 UTC  N/A     Disabled
3496    756     userinit.exe    0x830473e95080  0       -       1       False   2025-07-24 05:03:13.000000 UTC  2025-07-24 05:03:39.000000 UTC  Disabled
3516    3496    explorer.exe    0x830473ea3080  89      -       1       False   2025-07-24 05:03:13.000000 UTC  N/A     Disabled
3852    960     ShellExperienc  0x830473fa7380  27      -       1       False   2025-07-24 05:03:15.000000 UTC  N/A     Disabled
3956    960     SearchUI.exe    0x83047404d080  26      -       1       False   2025-07-24 05:03:15.000000 UTC  N/A     Disabled
4028    960     RuntimeBroker.  0x830473dc5580  3       -       1       False   2025-07-24 05:03:15.000000 UTC  N/A     Disabled
4128    960     RuntimeBroker.  0x8304740d3580  4       -       1       False   2025-07-24 05:03:16.000000 UTC  N/A     Disabled
4388    824     SearchIndexer.  0x830474278580  14      -       0       False   2025-07-24 05:03:17.000000 UTC  N/A     Disabled
5092    3516    vmtoolsd.exe    0x830474393340  11      -       1       False   2025-07-24 05:03:27.000000 UTC  N/A     Disabled
4824    824     svchost.exe     0x830473dff580  18      -       0       False   2025-07-24 05:04:12.000000 UTC  N/A     Disabled
4584    960     dllhost.exe     0x83047472d080  6       -       1       False   2025-07-24 05:58:56.000000 UTC  N/A     Disabled
2772    824     svchost.exe     0x83047184a3c0  5       -       0       False   2025-07-24 06:03:34.000000 UTC  N/A     Disabled
3764    4388    SearchProtocol  0x830473c56580  9       -       0       False   2025-07-24 06:57:51.000000 UTC  N/A     Disabled
1824    4388    SearchFilterHo  0x830473cc1140  7       -       0       False   2025-07-24 06:57:51.000000 UTC  N/A     Disabled
2820    3516    KeePass.exe     0x830474300080  11      -       1       False   2025-07-24 06:57:53.000000 UTC  N/A     Disabled
3612    3516    notepad++.exe   0x83047455a580  7       -       1       False   2025-07-24 06:57:55.000000 UTC  N/A     Disabled
1888    960     dllhost.exe     0x830474405580  7       -       1       False   2025-07-24 06:57:56.000000 UTC  N/A     Disabled
1684    960     dllhost.exe     0x830473c3c3c0  7       -       0       False   2025-07-24 06:57:56.000000 UTC  N/A     Disabled
2352    3516    FTK Imager.exe  0x830474592080  14      -       1       False   2025-07-24 06:57:56.000000 UTC  N/A     Disabled
3524    3516    DumpIt.exe      0x83047213f580  2       -       1       True    2025-07-24 06:58:01.000000 UTC  N/A     Disabled
208     3524    conhost.exe     0x830473ebc2c0  5       -       1       False   2025-07-24 06:58:01.000000 UTC  N/A     Disabled
```

---

## Dump file

Sau khi xem các tiến trình và biết offset của các file, chúng ta sẽ dump nó ra

Tạo 2 folder để dump

```bash
$ mkdir -p dumps/keepass dumps/notepadpp
```

Bắt đầu dump dữ liệu theo virtual address đã có

```bash
$ ~/volatility3/vol.py -f memory.raw -o dumps/keepass windows.memmap --pid 2820 --dump
$ ~/volatility3/vol.py -f memory.raw -o dumps/notepadpp windows.memmap --pid 3612 --dump
```

---

## Kiểm tra file

Sau khi dump ra thì anh em sẽ kiểm tra các file đã dump

```bash
$ file dumps/keepass/pid.2820.dmp 
dumps/keepass/pid.2820.dmp: PE32+ executable for MS Windows 4.00 (GUI), Intel i386 Mono/.Net assembly, 3 sections

$ file dumps/notepadpp/pid.3612.dmp 
dumps/notepadpp/pid.3612.dmp: data
```

Thấy file đầu tiên là 1 file thực thi

Vậy thì tôi sẽ dùng IDA để dịch ngược xem sao

---

## IDA

Sau khi mở IDA anh em sẽ xem các xâu chứa trong đấy thì sẽ phát hiện ra 3 phần của AES

```txt
AES_IV=InitializationVe 
AES_ENC_DATA=rNxBkug3ri07khz2rKqQY+bv6GyhHZD/gbM4y2lUAUDENzGNDYeu1eNCWl9cTkyo 
AES_KEY=PTIT_CTF2025_KEY
```

Giải mã thử

---

## Giải mã AES

Giải mã bằng `aes_decrypt.py`

```python
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
```

Nhận được chuỗi sau

```bash
$ python3 aes_decrypt.py 
KEY(len=%d) = 16 b'PTIT_CTF2025_KEY'
IV (len=16) = b'InitializationVe'
CIPH(b64)   = rNxBkug3ri07khz2rKqQY+bv6GyhHZD/gbM4y2lUAUDENzGNDYeu1eNCWl9cTkyo

[AES-128-CBC (PKCS7)] len=42
utf-8: PassDB: NoCurrentThreatsInVirus&Protection
```

Đây là mật khẩu cho `KeePass DB`

---

## Tìm KeePass DB

Sử dụng plugin `filescan`

```bash
$ ~/volatility3/vol.py -f memory.raw windows.filescan | grep -i '\.kdbx'
0x830473042a10.0\Users\REM\Desktop\Hacker\database.kdbx
```

---

## Dump KeePass DB

Bây giờ chúng ta sẽ dump `database.kdbx` ra

Tạo folder để dump

```bash
$ mkdir out_kdbx
```

Dump theo virtuall address

```bash
$ ~/volatility3/vol.py -f memory.raw -o out_kdbx \
  windows.dumpfiles --virtaddr 0x830473042a10
```

---

## Xem KeePass Database

Sử dụng phần mềm `KeePassXC` để xem cho dễ hoặc anh em dùng lệnh cũng được

Cái này tôi không cap lại màn được nên tôi sẽ nói luôn pass nhé, chắc do nó bảo mật

```txt
NowY0uC4nF1ndM3!
```

Hoặc đây là cách dùng lệnh

```bash
$ DB=out_kdbx/database.kdbx 
PASS='NoCurrentThreatsInVirus&Protection'

$ keepassxc-cli ls -R "$DB" <<< "$PASS" 
Enter password to unlock out_kdbx/database.kdbx: 
docs_secret 
General/ 
 [empty] 
Windows/ 
 [empty] 
Network/ 
 [empty] 
Internet/ 
 [empty] 
eMail/ 
 [empty] 
Homebanking/ 
 [empty] 
Recycle Bin/ 
 Sample Entry #2 
 Sample Entry 
 realdocx
```

Xem `realdocx`

```bash
$ keepassxc-cli show -s "$DB" 'Recycle Bin/realdocx' <<< "$PASS" 
Enter password to unlock out_kdbx/database.kdbx: 
Title: realdocx 
UserName: 
Password: NowY0uC4nF1ndM3! 
URL: 
Notes: 
Uuid: {a2e1ac72-1750-c340-9d61-c23f59733d2c} 
Tags:
```

---

## Đọc file docxx

Trong `notepad++` anh em sẽ thấy file `real.txt`

Mở nó bằng word sẽ yêu cầu mật khẩu

Anh em nhập mật khẩu từ `realdocx` là sẽ mở được

---

## Flag

Flag: PTITCTF{M3m0ry_Dumppppppppp!}