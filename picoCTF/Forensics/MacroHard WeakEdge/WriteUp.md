# Write Up

Chúng ta copy phải gốc sang 1 file khác, để đề phòng nghịch hỏng thôi

```bash
cp Forensics\ is\ fun.pptm challenge.pptm
```

Sau đó unzip file `.pptm`

```bash
mv challenge.pptm challenge.zip
unzip challenge.zip -d challenge_extract
```

Bây giờ chúng ta sẽ thử `list` ra xem có những file nào

Bỏ qua những file/folder không quan trọng nhé anh em

```bash
ls -laR | grep -viE '.xml|.ref|drw|.pptm'
```

Nhận thấy có 1 file `hidden`

```txt
./challenge_extract/ppt/slideMasters:
total 16
-rwxrwxrwx 1 longhd longhd    99 Oct 23  2020 hidden
```

Truy cập vào và đọc nội dung file

```bash
$ cat hidden
Z m x h Z z o g c G l j b 0 N U R n t E M W R f d V 9 r b j B 3 X 3 B w d H N f c l 9 6 M X A 1 f Q
```

Giải mã

```bash
$ cat hidden | tr -d " " | base64 -d
flag: picoCTF{D1d_u_kn0w_ppts_r_z1p5}base64: invalid input
```

Flag: picoCTF{D1d_u_kn0w_ppts_r_z1p5}
