# Write Up

Phân tích gói tin bằng `wireshark`

```bash
$ wireshark capture.flag.pcap
```

Chúng ta sẽ `Follow TCP Stream` để xem thông tin được gửi đi là gì

Thấy thông tin như sau

```txt
Hey, how do you decrypt this file again?
You're serious?
Yeah, I'm serious
*sigh* openssl des3 -d -salt -in file.des3 -out file.txt -k supersecretpassword123
Ok, great, thanks.
Let's use Discord next time, it's more secure.
C'mon, no one knows we use this program like this!
Whatever.
Hey.
Yeah?
Could you transfer the file to me again?
Oh great. Ok, over 9002?
Yeah, listening.
Sent it
Got it.
You're unbelievable
```

Họ dùng lệnh giải mã là 

> openssl des3 -d -salt -in file.des3 -out file.txt -k supersecretpassword123

Và họ chuyển lại file thông qua port `9002`

Lọc những gói tin ở port `9002`

```bash
tcp.port == 9002
```

Tiếp tục `Follow TCP Stream` ta sẽ thấy nội dung gói tin được truyền đi

Lưu dưới dạng `raw` với tên là `file.des3`

Chạy lệnh giải mã trên sẽ lấy được flag

picoCTF{nc_73115_411_0ee7267a}
