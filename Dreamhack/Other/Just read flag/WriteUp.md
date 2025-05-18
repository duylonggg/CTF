# Write Up

## 1. **SSH**

Để SSH được vào máy chủ chúng ta cần chuyển file key là `dreamhack_invitational_welcome` về dạng `rw`

```bash
# Tạo thư mục tạm trong Linux home
mkdir -p ~/temp_key

# Copy file key từ ổ D: (Windows) vào thư mục này
cp "/mnt/d/Documents/CTF/Dreamhack/Other/Just read flag/dreamhack_invitational_welcome" ~/temp_key/

# Vào thư mục đó
cd ~/temp_key

# Đặt quyền đúng
chmod 600 dreamhack_invitational_welcome

# Thử SSH lại
ssh -i dreamhack_invitational_welcome -p 11146 dream@host3.dreamhack.games
```

## 2. **Đọc file**

Trong máy chủ chúng ta sẽ sử dụng lệnh `ls -l` để kiểm tra xem có bao nhiêu file:

```bash
localhost% ls -l
total 4
-rw-r----- 1 root dream 45 May  3  2024 flag_welcome
```

Thấy file này bị giới hạn quyền, không thể sử dụng lệnh như `cat` để đọc.

Chúng ta sẽ bypass bằng cách dùng Python để mở file lên và đọc:

```bash
python3 -c 'print(open("flag_welcome", "rb").read())'
```

## 4. **Flag**

DH{A cat walks across the frozen Han River.}
