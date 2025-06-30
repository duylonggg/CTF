# Write Up

Để làm được bài này, chúng ta cần có kiên thức là `Slack Space : Không gian thừa`

Cấu trúc lưu trữ hệ thống file:

- Hệ thống file chia ổ đĩa thành các block (trên ext3/ext4 thường là 4 KB; trên NTFS gọi là cluster thường từ 4 KB trở lên)
- Khi lưu một file, hệ thống file cấp phát cho nó một số block nguyên
  - Ví dụ: file dài 1000 bytes sẽ được lưu trong 1 block (4 KB), dù nó chỉ cần chưa đầy 1 KB

File size vs Block size

| Thuộc tính       | Giá trị ví dụ | Giải thích                                           |
| ---------------- | ------------- | ---------------------------------------------------- |
| Kích thước file  | 1 000 bytes   | Dữ liệu thực tế của file                             |
| Kích thước block | 4 096 bytes   | Đơn vị cấp phát của ext3/ext4                        |
| **Slack space**  | 3 096 bytes   | Phần còn lại trong block sau khi lưu 1 000 bytes đầu |

Các thành phần của `Slack Space`

1. File Slack

- Là toàn bộ phần dư của block chưa dùng, tức 3 096 bytes trong ví dụ trên
- Trên ext3/ext4, slack space chính là file slack

2. RAM slack (chủ yếu trong NTFS)

- Được tạo khi hệ thống file điền đầy phần đầu block với dữ liệu file, rồi phần còn lại được điền từ vùng đệm (RAM) trước đó
- Thường chứa dữ liệu ngẫu nhiên, có thể lộ thông tin nhạy cảm đã từng nằm trong RAM

`Slack Space` có ý nghĩa gì trong Forensics

Dữ liệu cũ: Khi bạn xóa, chỉnh sửa, hay ghi đè file, hệ thống file thường chỉ cập nhật metadata và block mới, phần slack space có thể vẫn giữ dữ liệu cũ

Ẩn thông tin: Kẻ xấu có thể giấu thông điệp, flag CTF, hoặc dữ liệu riêng tư trong slack space để “thấy mà không thấy.”

Khôi phục dữ liệu: Điều tra viên có thể dùng công cụ như debugfs, dd, strings, v.v. để trích xuất toàn bộ block và dò tìm dấu vết bên trong slack.

Đầu tiên chúng ta sẽ xem các file/folder của Disk Image

```bash
$ fls suspicious.dd.sda1
d/d 11: lost+found
d/d 2009:       boot
d/d 4017:       tce
r/r 12: suspicious-file.txt
V/V 8033:       $OrphanFiles
```

Thử đọc nội dung file `suspicious-file.txt`

```bash
$ icat suspicious.dd.sda1 12
Nothing to see here! But you may want to look here -->
```

Bây giờ hãy tìm offset chứa chuỗi kia trong Disk Image

```bash
$ strings -a -t x suspicious.dd.sda1 | grep "Nothing to see here! But you may want to look here"
200400 Nothing to see here! But you may want to look here -->
```

Vậy nó ở offset `200400`

Trích xuất dữ liệu ở ngay sau byte này

```bash
$ xxd -s 0x200400 -l 200 suspicious.dd.sda1
00200400: 4e6f 7468 696e 6720 746f 2073 6565 2068  Nothing to see h
00200410: 6572 6521 2042 7574 2079 6f75 206d 6179  ere! But you may
00200420: 2077 616e 7420 746f 206c 6f6f 6b20 6865   want to look he
00200430: 7265 202d 2d3e 0a7d 0031 0039 0033 0037  re -->.}.1.9.3.7
00200440: 0062 0065 0066 0063 005f 0033 003c 005f  .b.e.f.c._.3.<._
00200450: 007c 004c 006d 005f 0031 0031 0031 0074  .|.L.m._.1.1.1.t
00200460: 0035 005f 0033 0062 007b 0046 0054 0043  .5._.3.b.{.F.T.C
00200470: 006f 0063 0069 0070 0000 0000 0000 0000  .o.c.i.p........
00200480: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00200490: 0000 0000 0000 0000 0000 0000 0000 0000  ................
002004a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
002004b0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
002004c0: 0000 0000 0000 0000                      ........
```

Dùng lệnh đọc ngược flag lên

```bash
$ od --skip-bytes=0x200437 --read-bytes=66 suspicious.dd.sda1 --format=c --address-radix=n --width=100 | sed "s/\\\0//g" | tr -d " " | rev
picoCTF{b3_5t111_mL|_<3_cfeb7391}
```