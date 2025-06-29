# Write-up: Wireshark twoo twooo two twoo... (picoCTF 2021)

**Challenge**: Wireshark twoo twooo two twoo...
**Category**: Forensics
**Points**: 100
**File provided**: shark2.pcapng

---

## Mục tiêu

Phân tích file .pcapng bằng Wireshark để tìm ra flag thật sự. Challenge này có nhiều flag giả nhằm đánh lạc hướng, vì vậy cần phân tích cẩn thận.

---

## Bước 1: Khảo sát sơ bộ

Dùng lệnh:

```bash
strings shark2.pcapng | grep picoCTF
```

Sẽ thấy hàng trăm flag dạng `picoCTF{...}`. Tuy nhiên, thử submit sẽ thấy tất cả đều sai – đó là các flag giả.

---

## Bước 2: Phân tích trong Wireshark

Mở file trong Wireshark:

```bash
wireshark shark2.pcapng
```

Dùng bộ lọc:

```plaintext
dns
```

Phát hiện một số DNS query đến các subdomain kỳ lạ như:

```
cGljb0NURntkbnNfM3hmMWxfZnR3X2RlYWRiZWVmfQ==.reddshrimpandherring.com
```

Đây là chuỗi Base64 ẩn trong phần subdomain.

---

## Vì sao là DNS?

Flag được ẩn trong các DNS request vì:

* DNS cho phép đặt dữ liệu tùy ý trong tên miền (subdomain).
* Hacker thường dùng kỹ thuật này để gửi dữ liệu ra ngoài mà không bị phát hiện (gọi là DNS Data Exfiltration).
* Challenge này mô phỏng đúng kỹ thuật đó: chia nhỏ flag, encode base64 rồi gửi qua DNS query.

---

## Bước 3: Lọc đúng IP và ghép chuỗi

Dùng filter trong Wireshark:

```plaintext
dns and ip.dst == 18.217.1.57
```

Chỉ IP này chứa các DNS query có dữ liệu base64 thật. Ghép lại phần subdomain của các request theo thứ tự sẽ được chuỗi:

```
cGljb0NURntkbnNfM3hmMWxfZnR3X2RlYWRiZWVmfQ==
```

---

## Bước 4: Giải mã

```bash
echo "cGljb0NURntkbnNfM3hmMWxfZnR3X2RlYWRiZWVmfQ==" | base64 -d
```

Kết quả:

```
picoCTF{dns_3xf1l_ftw_deadbeef}
```

---

## Flag

```
picoCTF{dns_3xf1l_ftw_deadbeef}
```

---

## Kết luận

Challenge này đánh lạc hướng bằng hàng trăm flag giả trong HTTP. Flag thật được gửi qua DNS – mô phỏng một kiểu tấn công rất thực tế: DNS exfiltration. Đây là một bài rất hay để luyện kỹ năng phân tích mạng và tìm dữ liệu bị ẩn một cách tinh vi.

---

## Công cụ sử dụng

| Công cụ        | Mục đích                      |
| -------------- | ----------------------------- |
| Wireshark      | Phân tích .pcapng             |
| Display Filter | Lọc DNS và IP đích            |
| base64         | Giải mã chuỗi                 |
| strings        | Liệt kê nhanh flag trong file |
