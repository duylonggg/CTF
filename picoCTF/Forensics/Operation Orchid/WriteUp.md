# Write Up

Giải nén file

```bash 
gunzip disk.flag.img.gz
```

Ta nhận được file `img`

Đọc các khối dữ liệu trong file

```bash 
$ mmls disk.flag.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000206847   0000204800   Linux (0x83)
003:  000:001   0000206848   0000411647   0000204800   Linux Swap / Solaris x86 (0x82)
004:  000:002   0000411648   0000819199   0000407552   Linux (0x83)
```

Thử truy cập vào patition cuối cùng

```bash
fls -o 0000411648 disk.flag.img
d/d 460:        home
d/d 11: lost+found
d/d 12: boot
d/d 13: etc
d/d 81: proc
d/d 82: dev
d/d 83: tmp
d/d 84: lib
d/d 87: var
d/d 96: usr
d/d 106:        bin
d/d 120:        sbin
d/d 466:        media
d/d 470:        mnt
d/d 471:        opt
d/d 472:        root
d/d 473:        run
d/d 475:        srv
d/d 476:        sys
d/d 2041:       swap
V/V 51001:      $OrphanFiles
```

Vào thử folder `root`

```bash
$ fls -o 0000411648 disk.flag.img 472
r/r 1875:       .ash_history
r/r * 1876(realloc):    flag.txt
r/r 1782:       flag.txt.enc
```

Ghi lại file `.ash_history` và `flag.txt.enc` ra ngoài

```bash
$ icat -o 0000411648 disk.flag.img 1875 > ash_history.txt
$ icat -o 0000411648 disk.flag.img 1782 > flag.txt.enc
```

Đọc file `flag.txt.enc`

```bash
$ cat flag.txt.enc
Salted__�ށ��e��B�J�c�$QE&$��4jM�KGeE�1�^Ȥ7� ���؎$�'%
```

Đọc file `ash_history`

```bash
$ cat ash_history.txt
touch flag.txt
nano flag.txt
apk get nano
apk --help
apk add nano
nano flag.txt
openssl
openssl aes256 -salt -in flag.txt -out flag.txt.enc -k unbreakablepassword1234567
shred -u flag.txt
ls -al
halt
```

Ta thấy nó được mã hóa `openssl` với pass là `unbreakablepassword1234567`

Giải mã

```bash
$ openssl aes256 -d -salt -in flag.txt.enc -out flag.txt -k unbreakablepassword1234567
```

Flag: picoCTF{h4un71ng_p457_5113beab}
