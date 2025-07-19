# Write Up

## Set up

Đầu tiên chúng ta cần chuyển private key `OpenSSH` sang dạng `PEM`

```bash
ssh-keygen -p -f picopico.key -m PEM -N "" 
```

Sau đó mở `wireshark`

```bash
wireshark capture.pcap
```

Bây giờ chúng ta sẽ config để hiển thị được những file được mã hóa bằng `OpenSSH` qua giao thức `TLS`

Vào `Edit` → `Preferences` → `Protocols` → `TLS`

Trong `RSA keys list` bấm `Edit`, thêm dấu `+`

Điền

| IP Address    | Port | Protocol | Key File                          |
|---------------|------|----------|-----------------------------------|
| `172.31.22.220` | `57567`  | `http`     | `/tmp/picopico.key`           |

Sau đó chúng ta sẽ thấy những giao thức `http` ẩn được hiện ra

---

## Tìm flag

Có thể dùng `tshark` để lấy hết data thô về

```bash
$ tshark \
  -o tls.desegment_ssl_records:TRUE \
  -o tls.desegment_ssl_application_data:TRUE \
  -o tls.keys_list:"0.0.0.0,443,http,/full/path/to/picopico.key" \
  -r capture.pcap \
  -Y http \
  -V > decrypted_http.txt
```

Sau đó tìm flag

```bash
$ cat decrypted_http.txt | grep pico
Pico-Flag: picoCTF{nongshim.shrimp.crackers}\r\n
Pico-Flag: picoCTF{nongshim.shrimp.crackers}\r\n
```

Flag: picoCTF{nongshim.shrimp.crackers}