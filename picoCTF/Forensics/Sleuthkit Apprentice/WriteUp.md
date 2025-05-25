# Write Up

Bài này chúng ta sẽ thực hành sử dụng `Sleuthkit`

Một bộ kỹ năng phổ biến để xử lý những bài `disk image`

```txt
| Lệnh          | Tên đầy đủ                | Mục đích                                                          | Cờ (flags) thường dùng              | Ví dụ                                                   |
| ------------- | ------------------------- | ----------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------- |
| `mmls`        | **Partition Layout**      | Hiển thị bảng phân vùng của disk image                            | *(không bắt buộc)*                  | `mmls disk.img`                                         |
| `fls`         | **File List**             | Duyệt cây thư mục (listing files/folders từ một phân vùng cụ thể) | `-o <sector>` (offset sector), `-r` | `fls -o 360448 disk.img`<br>`fls -o 360448 -r disk.img` |
| `icat`        | **File Extract**          | Trích xuất nội dung file theo inode từ một phân vùng              | `-o <sector>`                       | `icat -o 360448 disk.img 2371`                          |
| `ils`         | **Inode List**            | Liệt kê thông tin inode trong phân vùng                           | `-o <sector>`                       | `ils -o 360448 disk.img`                                |
| `fsstat`      | **Filesystem Stats**      | Thông tin tổng quan về hệ thống tập tin của phân vùng             | `-o <sector>`                       | `fsstat -o 360448 disk.img`                             |
| `blkls`       | **Block List**            | Trích xuất raw data các blocks không được gán (unallocated)       | `-o <sector>`                       | `blkls -o 360448 disk.img > unalloc.bin`                |
| `tsk_recover` | **Recover Deleted Files** | Phục hồi toàn bộ file đã xóa (nếu còn) từ phân vùng               | `-o <sector>` + thư mục output      | `tsk_recover -o 360448 disk.img recovered/`             |
| `fsls`        | **Filesystem List**       | Liệt kê nội dung thư mục như `ls`, nhưng dùng trên image          | `-o <sector>`                       | `fsls -o 360448 disk.img`                               |
```

Đầu tiên chúng ta sử dụng lệnh `mmls` để xem phân vùng của `disk image`

```bash
$ mmls disk.flag.img
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000206847   0000204800   Linux (0x83)
003:  000:001   0000206848   0000360447   0000153600   Linux Swap / Solaris x86 (0x82)
004:  000:002   0000360448   0000614399   0000253952   Linux (0x83)
```

Chúng ta nhận thấy nó có 2 `patrition` là `Linux(0x83)`

Chúng ta sẽ duyệt file/folders của từng `patrition` này

```bash
$ fls -o 0000360448 disk.flag.img
d/d 451:   home
d/d 11: lost+found
d/d 12: boot
d/d 1985:  etc
d/d 1986:  proc
d/d 1987:  dev
d/d 1988:  tmp
d/d 1989:  lib
d/d 1990:  var
d/d 3969:  usr
d/d 3970:  bin
d/d 1991:  sbin
d/d 1992:  media
d/d 1993:  mnt
d/d 1994:  opt
d/d 1995:  root
d/d 1996:  run
d/d 1997:  srv
d/d 1998:  sys
d/d 2358:  swap
V/V 31745: $OrphanFiles
```

Nhận thấy có thư mục `root`

Thử duyệt file/folder của thử mục này

``bash
$ fls -o 0000360448 disk.flag.img 1995
r/r 2363:  .ash_history
d/d 3981:  my_folder
```

Thấy thư mục `my_folder` --> có thể chứa flag

Duyệt file/folder của thư mục này tiếp

```bash
$ fls -o 0000360448 disk.flag.img 3981
r/r * 2082(realloc):    flag.txt
r/r 2371:  flag.uni.txt
```

Chúng ta thấy 1 file `flag.uni.txt` 

Đọc file này và lấy ra flag


```bash
$ icat -o 0000360448 disk.flag.img 2371
picoCTF{by73_5urf3r_adac6cb4}
```

