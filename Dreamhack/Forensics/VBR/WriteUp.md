# Write Up

## 1. **Phân tích file**

```bash
file vbr.bin
```

Nhận được

```txt
file vbr.bin
vbr.bin: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "MSDOS5.0", sectors/cluster 8, reserved sectors 206, Media descriptor 0xf8, sectors/track 63, heads 255, hidden sectors 14338048, sectors 4096000 (volumes > 32 MB), FAT (32 bit), sectors/FAT 3993, serial number 0xea8ee8a, unlabeled
```

Ta thấy đây là file `FAT32` --> `A = 1`

Ta thấy `sectors = 4096000` --> Đây là tổng số `sector` trong file mà mỗi `sector` là `512 bytes` --> `B = 4096000 * 512`

Ta thấy `serial number = 0xea8ee8a` --> `C = 0xea8ee8a`

## 2. **Flag**

DH{2343104139}
