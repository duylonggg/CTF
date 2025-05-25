# Write Up

Sử dụng lệnh `mmls`

```bash
$ mmls disk.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000204799   0000202752   Linux (0x83) 
```

Điền `Length` của Linux là lấy được flag

Flag: picoCTF{mm15_f7w!} 
