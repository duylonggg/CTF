# Write Up

## Xem các phân vùng trong file

```bash
$ mmls disko-2.dd
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000053247   0000051200   Linux (0x83)
003:  000:001   0000053248   0000118783   0000065536   Win95 FAT32 (0x0b)
004:  -------   0000118784   0000204799   0000086016   Unallocated
```

Chúng ta sẽ tách phân vùng `Linux` và `Win95 FAT32` ra vì đây là 2 phân vùng quan trọng nhất và có khả năng chứa flag

```bash
$ dd if=disko-2.dd of=fat32_partition.dd bs=512 skip=53248 count=65536
$ dd if=disko-2.dd of=linux_partition.dd bs=512 skip=2048 count=51200
```

Sau đó tìm kiếm trong 2 phân vùng này xem có flag không

```bash
$ strings fat32_partition.dd | grep -Eo 'picoCTF{[^}]+}'
picoCTF{4_P4Rt_1t_i5_903d13af}
picoCTF{4_P4Rt_1t_i5_393da1f0}
picoCTF{4_P4Rt_1t_i5_1930da3f}
picoCTF{4_P4Rt_1t_i5_a0f313d9}
picoCTF{4_P4Rt_1t_i5_3d1309af}
picoCTF{4_P4Rt_1t_i5_30f931da}
picoCTF{4_P4Rt_1t_i5_1a33f09d}
picoCTF{4_P4Rt_1t_i5_913a30df}
picoCTF{4_P4Rt_1t_i5_331d0f9a}
picoCTF{4_P4Rt_1t_i5_339d0fa1}
picoCTF{4_P4Rt_1t_i5_91fda330}
picoCTF{4_P4Rt_1t_i5_09a331df}
picoCTF{4_P4Rt_1t_i5_339a10df}
picoCTF{4_P4Rt_1t_i5_0ad1393f}
picoCTF{4_P4Rt_1t_i5_13d093af}
picoCTF{4_P4Rt_1t_i5_310d39fa}
picoCTF{4_P4Rt_1t_i5_039fda13}
picoCTF{4_P4Rt_1t_i5_a031d9f3}
picoCTF{4_P4Rt_1t_i5_d3f1039a}
picoCTF{4_P4Rt_1t_i5_31a03fd9}
picoCTF{4_P4Rt_1t_i5_a9d0f313}
picoCTF{4_P4Rt_1t_i5_1f03d3a9}
picoCTF{4_P4Rt_1t_i5_9a013f3d}
picoCTF{4_P4Rt_1t_i5_f33d091a}
picoCTF{4_P4Rt_1t_i5_1d9fa303}
picoCTF{4_P4Rt_1t_i5_a3f9103d}
picoCTF{4_P4Rt_1t_i5_f19a03d3}
picoCTF{4_P4Rt_1t_i5_93fda130}
picoCTF{4_P4Rt_1t_i5_30df3a91}
picoCTF{4_P4Rt_1t_i5_09ad13f3}
picoCTF{4_P4Rt_1t_i5_a0913df3}
picoCTF{4_P4Rt_1t_i5_913d03af}
picoCTF{4_P4Rt_1t_i5_f19d3a03}
picoCTF{4_P4Rt_1t_i5_f3019a3d}
picoCTF{4_P4Rt_1t_i5_309dfa13}
picoCTF{4_P4Rt_1t_i5_0a193f3d}
picoCTF{4_P4Rt_1t_i5_f9033d1a}
picoCTF{4_P4Rt_1t_i5_f3013da9}
picoCTF{4_P4Rt_1t_i5_33f0da91}
picoCTF{4_P4Rt_1t_i5_a1f033d9}
picoCTF{4_P4Rt_1t_i5_f3d0139a}
picoCTF{4_P4Rt_1t_i5_af91303d}
picoCTF{4_P4Rt_1t_i5_af9d0133}
picoCTF{4_P4Rt_1t_i5_f9331ad0}
picoCTF{4_P4Rt_1t_i5_39fa01d3}
picoCTF{4_P4Rt_1t_i5_a1df3903}
picoCTF{4_P4Rt_1t_i5_1daf9033}
picoCTF{4_P4Rt_1t_i5_931afd03}
picoCTF{4_P4Rt_1t_i5_0d93a13f}
picoCTF{4_P4Rt_1t_i5_903a13fd}

$ strings linux_partition.dd | grep -Eo 'picoCTF{[^}]+}'
picoCTF{4_P4Rt_1t_i5_90a3f3d1}
```

## Flag

picoCTF{4_P4Rt_1t_i5_90a3f3d1}
