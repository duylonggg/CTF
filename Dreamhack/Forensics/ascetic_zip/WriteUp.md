# 🧠 Challenge: Ascetic Zip (Forensics)

---

## 📂 Mô tả:

Challenge cung cấp một file ảnh `flag.jpg`. Nhiệm vụ của bạn là trích xuất thông tin ẩn chứa trong ảnh để lấy được flag.

---

## 🔧 Kiến thức liên quan

| Kỹ thuật                              | Giải thích                                                        |
| ------------------------------------- | ----------------------------------------------------------------- |
| **Steganography**                     | Giấu dữ liệu trong ảnh (thường qua LSB hoặc metadata)             |
| **Zip Cracking (password protected)** | Crack file `.zip` bảo vệ bằng mật khẩu (dùng `zip2john` + `john`) |
| **EXIF Data**                         | Dữ liệu metadata ảnh JPEG (ngày, phần mềm tạo, comment, v.v.)     |

---

## 🛠️ Công cụ sử dụng

| Công cụ             | Chức năng                            | Mảng                          |
| ------------------- | ------------------------------------ | ----------------------------- |
| `binwalk`           | Trích xuất dữ liệu ẩn trong file ảnh | Forensics – Steganography     |
| `zip2john` + `john` | Crack mật khẩu file ZIP              | Forensics – Password Cracking |
| `unzip`             | Giải nén file                        | Hệ thống                      |

---

## 🪜 Các bước thực hiện

---

### 🖼️ B1 – Phân tích ảnh flag.jpg

```bash
$ binwalk flag.jpg

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             JPEG image data, JFIF standard 1.01
4609          0x1201          Zip archive data, encrypted at least v2.0 to extract, compressed size: 33, uncompressed size: 19, name: flag.txt
4770          0x12A2          End of Zip archive, footer length: 22
```

→ Có file ẩn tại offset `4609 = 0x1201`

---

### 📤 B2 – Trích xuất dữ liệu ẩn

```bash
$ binwalk -e flag.jpg

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
4609          0x1201          Zip archive data, encrypted at least v2.0 to extract, compressed size: 33, uncompressed size: 19, name: flag.txt

WARNING: One or more files failed to extract: either no utility was found or it's unimplemented

$ ls _flag.jpg.extracted/
1201.zip
```

---

### 🔐 B3 – Crack mật khẩu file ZIP

File `.zip` này được bảo vệ bằng password

```bash
$ unzip _flag.jpg.extracted/1201.zip
Archive:  _flag.jpg.extracted/1201.zip
[_flag.jpg.extracted/1201.zip] flag.txt password:
```

Dùng `zip2john` để tạo hash

```bash
$ zip2john _flag.jpg.extracted/1201.zip > hash.txt
ver 2.0 1201.zip/flag.txt PKZIP Encr: TS_chk, cmplen=33, decmplen=19, crc=F06B93DC ts=4E58 cs=4e58 type=8
```

Rồi dùng `john` để brute-force với từ điển `rockyou.txt`

```bash
$ john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Note: Passwords longer than 21 [worst case UTF-8] to 63 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
ascetic          (1201.zip/flag.txt)
1g 0:00:00:01 DONE (2025-08-07 17:37) 0.8772g/s 8752Kp/s 8752Kc/s 8752KC/s ashhopper_1..arwajz
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Ta sẽ có password là `ascetic`

```bash
$ john --show hash.txt
1201.zip/flag.txt:ascetic:flag.txt:1201.zip::_flag.jpg.extracted/1201.zip

1 password hash cracked, 0 left
```

---

### 📂 B4 – Giải nén file ZIP

Giai nén file `.zip`

```bash
$ unzip _flag.jpg.extracted/1201.zip
Archive:  _flag.jpg.extracted/1201.zip
[_flag.jpg.extracted/1201.zip] flag.txt password:
  inflating: flag.txt
error: invalid zip file with overlapped components (possible zip bomb)
```

---

## Flag

Flag: DH{My_n@me_h@#NAMM}