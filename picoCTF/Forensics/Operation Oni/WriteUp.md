 # Write Up

Đọc các phân vùng trong file disk image

```bash
$ mmls disk.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000206847   0000204800   Linux (0x83)
003:  000:001   0000206848   0000471039   0000264192   Linux (0x83)
```

Vào phân vùng 

```bash
$ fls -o 0000206848 disk.img
d/d 458:        home
d/d 11: lost+found
d/d 12: boot
d/d 13: etc
d/d 79: proc
d/d 80: dev
d/d 81: tmp
d/d 82: lib
d/d 85: var
d/d 94: usr
d/d 104:        bin
d/d 118:        sbin
d/d 464:        media
d/d 468:        mnt
d/d 469:        opt
d/d 470:        root
d/d 471:        run
d/d 473:        srv
d/d 474:        sys
V/V 33049:      $OrphanFiles
```

Vào `root`

```bash
$ fls -o 0000206848 disk.img 470
r/r 2344:       .ash_history
d/d 3916:       .ssh
```

Vào folder `.ssh`

```bash
$ fls -o 0000206848 disk.img 3916
r/r 2345:       id_ed25519
r/r 2346:       id_ed25519.pub
```

Ghi file `id_ed25519` ra ngoài

```bash
$ icat -o 0000206848 disk.img 2345 > id_ed25519
```

File này là mật khẩu đề dùng ssh

```txt
$ file id_ed25519
id_ed25519: OpenSSH private key
```

Chuyển file về dạng private rồi ssh

```bash
mkdir -p ~/oni_work
cp id_ed25519 ~/oni_work/
chmod 600 ~/oni_work/id_ed25519
```

SSH

```bash
ssh -i ~/oni_work/id_ed25519 -p 64668 ctf-player@saturn.picoctf.net
```

Flag: picoCTF{k3y_5l3u7h_b5066e83}

