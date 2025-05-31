
# Write Up

## 1. Phân tích đề bài

**Tiếng Anh**:
> We have caught signs that the server operated by Dream Company has been hacked. Details are unknown, but the malware penetrated the developer PC through a central server, and as a result, it was determined that login information sensitive to network data was leaked every time the developer PC was logged in. Connect to the PC where the penetration has been completed, analyze the malware, find the file used in the penetration, and find the flag!

**Tiếng Việt**:
> Chúng tôi đã phát hiện dấu hiệu cho thấy máy chủ của Dream Company đã bị tấn công. Dù chưa rõ chi tiết, phần mềm độc hại đã xâm nhập vào máy tính của nhà phát triển thông qua một máy chủ trung tâm. Kết quả là thông tin đăng nhập nhạy cảm đã bị rò rỉ mỗi khi nhà phát triển đăng nhập. Hãy kết nối với máy tính đã bị xâm nhập, phân tích phần mềm độc hại, tìm tệp được sử dụng trong quá trình xâm nhập và tìm cờ!

Điểm đáng lưu ý: **dữ liệu bị rò rỉ ngay khi PC của nhà phát triển được đăng nhập**.

Do đó, ta cần kiểm tra xem có gói tin nào được gửi ra ngoài đến địa chỉ IP lạ hay không.

---

## 2. Truy vết

### Bước 1: Lấy địa chỉ IP của máy

```bash
$ hostname -I
```

### Bước 2: Theo dõi các gói tin gửi ra ngoài từ IP đó

```bash
$ tcpdump -i any src 10.254.0.106
```

Vì quá nhiều gói tin có thể gây nhiễu, hãy loại bỏ các port không liên quan:

```bash
$ tcpdump -i any src 10.254.0.106 and not dst port 22 and not dst port 53 and not dst port 9447
```

### Bước 3: Đăng nhập lại bằng một terminal khác

Theo đề bài, dữ liệu bị rò rỉ **ngay khi đăng nhập**, do đó cần mở một terminal khác và SSH vào để bắt được gói tin trong thời gian thực.

Sau khi đăng nhập lại, sẽ thấy một gói tin bất thường:

```text
10:04:59.575071 IP 10.254.0.106.50787 > 123.45.67.89.31337: UDP, length 11
```

→ IP đích: `123.45.67.89`, Port: `31337`

Port 31337 là port nổi tiếng từng được dùng cho backdoor. Bảng dưới đây cung cấp thêm thông tin:

| Mục                                      | Thông tin chi tiết |
|-----------------------------------------|---------------------|
| **Số port**                              | 31337 |
| **Tên gọi**                              | “eleet” (leet speak của “elite”) |
| **Protocol**                             | TCP/UDP (UDP phổ biến hơn) |
| **Loại port**                            | Dynamic/private (10000–65535) |
| **Mục đích phổ biến**                    | - Backdoor / Remote shell<br>- Malware / PoC CTF<br>- Kênh C2 (Command & Control) |
| **Lịch sử đáng chú ý**                   | - **Back Orifice** (1999): của nhóm Cult of the Dead Cow<br>- **NetBus**: cũng sử dụng port lạ<br>- Một số shellcode PoC cũng dùng port này |
| **Ưu điểm khi dùng UDP**                 | - Không cần bắt tay (handshake)<br>- Dễ lẻn qua firewall nếu không kiểm tra chặt UDP |
| **Nhược điểm / Rủi ro**                  | - Port quá nổi → dễ bị firewall phát hiện<br>- Nhiều IDS/IPS đã có signature cho port này |
| **Dấu hiệu trong CTF**                   | - Khi login (qua PAM) → module bị sửa gửi thông tin tới IP lạ qua UDP 31337 |
| **Cách phát hiện nhanh**                 | - `tcpdump -i any udp and dst port 31337`<br>- Dò trong file nhị phân `pam_unix.so`<br>- Dùng `nmap` hoặc `nc` kiểm tra |
| **Cách khắc phục**                       | - Block UDP port 31337<br>- Kiểm tra file PAM trong `/lib/.../security`<br>- Dùng IDS/IPS có chữ ký tương ứng |

---

## 3. Tìm kiếm file chứa địa chỉ IP lạ

```bash
$ grep '123.45.67.89' -R /lib
```

Kết quả:

```bash
Binary file /lib/x86_64-linux-gnu/security/pam_unix.so matches
```

→ Xác định được module `pam_unix.so` đã bị chỉnh sửa để gửi dữ liệu về IP lạ.

---

## 4. Phân tích file thực thi

Tìm chuỗi `base64` trong file thực thi:

```bash
$ strings /lib/x86_64-linux-gnu/security/pam_unix.so | grep -E 'base64|[A-Za-z0-9+/=]{20,}'
```

Tìm được chuỗi:

```text
REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=
```

Giải mã:

```bash
$ echo 'REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=' | base64 -d
```

---

## 5. Flag

```
DH{something_hidden_inside_my_palm}
```
