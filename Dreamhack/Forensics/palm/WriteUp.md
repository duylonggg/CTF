# Write Up

## 1. Phân tích đề bài

Đề bài:

```txt
Tiếng Anh:
We have caught signs that the server operated by Dream Company has been hacked. Details are unknown, but the malware penetrated the developer PC through a central server, and as a result, it was determined that login information sensitive to network data was leaked every time the developer PC was logged in. Connect to the PC where the penetration has been completed, analyze the malware, find the file used in the penetration, and find the flag!

Tiếng Việt:
Chúng tôi đã phát hiện ra dấu hiệu cho thấy máy chủ do Dream Company vận hành đã bị tấn công. Chi tiết chưa được biết, nhưng phần mềm độc hại đã xâm nhập vào PC của nhà phát triển thông qua một máy chủ trung tâm và kết quả là thông tin đăng nhập nhạy cảm với dữ liệu mạng đã bị rò rỉ mỗi khi PC của nhà phát triển đăng nhập. Kết nối với PC nơi quá trình xâm nhập đã hoàn tất, phân tích phần mềm độc hại, tìm tệp được sử dụng trong quá trình xâm nhập và tìm cờ!
```

Anh em hãy để ý là khi PC của nhà phát triển đăng nhập, dữ liệu bị rò rỉ

Vậy nên chúng ta sẽ cần phải phân tích xem có gói tin nào bịtruyền ra ngoài mà đến một IP lạ hay không

---

## 2. Truy vết

Trước khi truy vết anh em cần biết địa chỉ IP nguồn hoặc đích

Lệnh tìm địa chỉ IP nguồn

```bash
$ hostname -I
```

Lệnh truy vết

```bash
$ tcpdump -i any src 10.254.0.106
```

Lệnh này sẽ giúp anh em tìm các gói tin được gửi đi với IP nguồn là `10.254.0.106` 

Vì các gói tin được gửi đi rất nhiều và liên tục nên chúng ta sẽ phải lọc bớt đi

```bash
$ tcpdump -i any src 10.254.0.106 and not dst port 22 and not dst port 53 and not dst port 9447
```

Ở đây tôi sẽ bỏ những cái port linh tinh mà cá gói tin cứ gửi lại đi 

Bây giờ anh em sẽ mở cửa sổ terminal thứ 2 và ssh lại

Lý do cho việc này là vì đề bài nói rằng khi đăng nhập vào PC, dữ liệu sẽ bị đánh cắp

Tức là tại thời điểm đăng nhập, sẽ có 1 gói tin lạ được truyền đi đến 1 địa chỉ IP lạ

Mà khi anh em đăng nhập vào cho đến khoảng thời gian chạy `tcpdump` thì gói tin đã bị trôi mất rất lâu rồi nên cần 1 cửa sổ terminal thứ 2 để đăng nhập thử lại

Sau khi ssh xong thì anh em sẽ thấy 1 gói tin lạ như sau

```txt
10:04:59.575071 IP 10.254.0.106.50787 > 123.45.67.89.31337: UDP, length 11
```

Nó gửi đến IP `123.45.67.89` với port là `31337`

Khác với nguồn mà các gói tin khác được truyền đi, có thể của anh em sẽ khác còn của tôi là `dynamic-ip-adsl.viettel.vn.52159`

Nói thêm 1 kiến thức ngoài

```txt
| Mục                                                  | Thông tin chi tiết                                                                                                                                                                                                                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Số port**                                          | 31337                                                                                                                                                                                                                                                                   |
| **Tên gọi thân mật**                                 | “eleet” (leet speak của chữ “elite”)                                                                                                                                                                                                                                    |
| **Protocol**                                         | TCP/UDP (phổ biến hơn là UDP)                                                                                                                                                                                                                                           |
| **Well-known / Registered / Dynamic**                | Dynamic/private port (10000–65535)                                                                                                                                                                                                                                      |
| **Mục đích sử dụng thông thường**                    | - Backdoor / Remote shell <br> - Tiện ích CTF / PoC malware <br> - Kênh điều khiển C2 (Command & Control) giả lập                                                                                                                                                       |
| **Lịch sử nổi bật**                                  | - **Back Orifice (1999)**: một trong những backdoor đầu tiên của nhóm Cult of the Dead Cow (cOw). <br> - **NetBus**: cũng từng sử dụng port lạ (mặc định 12345 nhưng nhiều varients chuyển sang 31337). <br> - Nhiều mã exploit thời kỳ 2000s dùng port này để ẩn mình. |
| **Ưu điểm khi dùng UDP**                             | - Không cần handshake, dễ “lẻn” qua firewall nếu firewall không kiểm soát chặt UDP. <br> - Tránh bị phát hiện qua các công cụ quét TCP phổ thông.                                                                                                                       |
| **Nhược điểm / Rủi ro**                              | - Vì port này quá nổi tiếng, nếu firewall hoặc IDS/IPS (Intrusion Detection) đã cài signature thì traffic 31337 sẽ bị cảnh báo ngay. <br> - Dễ bị an ninh mạng “để ý” ngay từ tên port (nhiều admin chặn sẵn).                                                         |
| **Ví dụ malware/backdoor nổi tiếng dùng port 31337** | - **Back Orifice**: mặc định đặt port UDP 31337 để quản trị từ xa. <br> - **Cbypass**: nhiều biến thể của trojan đánh cắp mật khẩu từng sử dụng port 31337. <br> - Một số shellcode PoC dùng ransome port 31337 để “minh họa”.                                          |
| **Biểu hiện trong CTF (như bài Palm)**               | - Khi có user login (qua PAM) → malware gắn vào `pam_unix.so` sẽ gửi payload (username/password) tới IP C2 tại port UDP 31337. <br> - Thử thách đòi bạn dùng `tcpdump` hoặc Wireshark để phát hiện dòng `> …:31337`.                                                    |
| **Cách phát hiện / phát hiện nhanh**                 | - Dùng `tcpdump -i any udp and dst port 31337` để bắt traffic. <br> - Kiểm tra file nhị phân (ví dụ `pam_unix.so`), tìm kiếm chuỗi “31337” hoặc IP đích. <br> - Dùng `nmap` hoặc `nc -zv <host> 31337` để quét xem có service đang “listen”.                            |
| **Cách khắc phục**                                   | - **Block port 31337** trên firewall (udp/31337) nếu không có nhu cầu. <br> - Kiểm tra các module PAM bị sửa đổi (như `/lib/x86_64-linux-gnu/security/pam_unix.so`). <br> - Sử dụng IDS/IPS signature có sẵn để phát hiện traffic 31337.                                |
```

Như anh em đã đọc thì đây là 1 port khá nổi cho việc ăn cắp thông tin, nên chúng ta cũng có thể lọc riêng port này cho đỡ rối theo lệnh trong bảng

---

## 3. Tìm kiếm

Sau khi đã xác định được IP và port lạ, chúng ta hãy tìm kiếm xem nó được ẩn giấu trong file thực thi nào

```bash
$  grep '123.45.67.89' -R /lib
Binary file /lib/x86_64-linux-gnu/security/pam_unix.so matches
```

Xác định được file thực thi khi ssh và IP đích được thêm trong file để gửi dữ liệu khi ssh

---

## 4. Phân tích file

Tìm xem trong file có mã `base64` nào không

```bash
$ strings /lib/x86_64-linux-gnu/security/pam_unix.so | grep -E 'base64|[A-Za-z0-9+/=]{20,}'
_ITM_deregisterTMCloneTable
_ITM_registerTMCloneTable
/home/aaaa/pam/libpam/.libs
REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=No password supplied
/etc/security/opasswd
/etc/security/nopasswd
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789./
./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

Giải mã đoạn mã `base64` vừa tìm được

```bash
$ echo 'REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=' | base64 -d
```

---

## 5. Flag

DH{something_hidden_inside_my_palm}
