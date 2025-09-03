# Forensics - Summoner 2

## Tìm kiếm

Bài này chúng ta sẽ tìm kiếm chuỗi "PTITCTF" trong toàn bộ folder

```bash
$ grep -Rao 'PTITCTF{[^}]*}' "Summoner 2/"
Summoner 2/Neco/Windows 7 x64-Snapshot6.vmem:PTITCTF{W1P3R!!!_S3nd_h3Lp_P1e4Sss!!!}
Summoner 2/Neco/Windows 7 x64.vmdk:PTITCTF{W1P3R!!!_S3nd_h3Lp_P1e4Sss!!!}
Summoner 2/Neco/Windows 7 x64.vmdk:PTITCTF{W1P3R!!!_S3nd_h3Lp_P1e4Sss!!!}
```

---

## Flag

Flag: PTITCTF{W1P3R!!!_S3nd_h3Lp_P1e4Sss!!!}