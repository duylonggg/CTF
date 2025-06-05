# Write Up

Unzip file

```bash
gunzip dds2-alpine.flag.img.gz
```

Kiểm tra các phân vùng của ảnh

```bash
$ mmls dds2-alpine.flag.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000262143   0000260096   Linux (0x83)
```

Kiểm tra các file trong offset `0000002048`

```bash
$ fls -o 0000002048 dds2-alpine.flag.img
d/d 26417:      home
d/d 11: lost+found
r/r 12: .dockerenv
d/d 20321:      bin
d/d 4065:       boot
d/d 6097:       dev
d/d 2033:       etc
d/d 8129:       lib
d/d 14225:      media
d/d 16257:      mnt
d/d 18289:      opt
d/d 16258:      proc
d/d 18290:      root
d/d 16259:      run
d/d 18292:      sbin
d/d 12222:      srv
d/d 16260:      sys
d/d 18369:      tmp
d/d 12223:      usr
d/d 14229:      var
V/V 32513:      $OrphanFiles
```

Vào `root`

```bash
$ fls -o 0000002048 dds2-alpine.flag.img 18290
r/r 18291:      down-at-the-bottom.txt
```

Tải file `.txt` về

```bash
$ icat -o 0000002048 dds2-alpine.flag.img 18291 > down-at-the-bottom.txt
```

Đọc file và lấy ra 

Flag: picoCTF{f0r3ns1c4t0r_n0v1c3_f5565e7b}
