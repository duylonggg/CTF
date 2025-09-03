# Write Up

## Phân tích

Server Python cho thấy:

Mỗi người chơi được tạo một email ngẫu nhiên dạng:

```python
email = ''.join(random.choice('a-z') for 10) + "@notscript.sorcerer"
```

Người chơi nhập một password (hex), phải là bội số 16 bytes.

Server kiểm tra:

```python
assert b"@script.sorcerer" not in password
assert email.encode() not in password
```

Password được AES-CBC encrypt với key/iv ngẫu nhiên và in ra: encrypted_pass.

Người chơi có thể chọn:

```python
[1] Check for new messages
[2] Get flag
```

Khi chọn 2, server decrypt ciphertext nhập vào, kiểm tra:

```python
if user_email[-16:] != b"@script.sorcerer":
    print("You are not part of ScriptSorcerers!")
    exit(0)
```

Sau đó gọi send_email(user_email) để set has_flag=True nếu email match email của người chơi.

Khi chọn 1, nếu has_flag=True, flag được in ra.

---

## Khai thác

Server dùng AES-CBC mà không authenticate ciphertext, dẫn tới CBC bit-flipping attack:

Plaintext được kiểm tra domain @script.sorcerer ở 16 byte cuối block.

CBC: P_i = AES_DECRYPT(C_i) XOR C_{i-1}

Ta không cần key/iv để thay đổi plaintext block: chỉ cần XOR block ciphertext trước đó với P_orig ^ P_target.

---

## Exploit

Mục tiêu:

Block 2 chứa email: ,your_email,

Block 6 chứa domain: @script.sorcerer

Script exploit thực hiện:

Lấy email ngẫu nhiên từ server:

```python
r.recvuntil(b"Your Email is: ")
email = r.recvline().strip().decode()
```

Chuẩn bị 6-block password giả lập (96 bytes):

Blocks filler: B1..B6

Block 2 (B2) sẽ được flip thành ,email,

Block 6 (B6) sẽ được flip thành "@script.sorcerer"

Gửi password giả lập để server encrypt và trả ciphertext:

```python
r.sendlineafter(b"Enter secure password (in hex): ", P.hex().encode())
C = bytes.fromhex(r.recvline().strip().decode())
C1,C2,C3,C4,C5,C6 = [C[i:i+16] for i in range(0,96,16)]
```

CBC flip để sửa block:

```python
C1p = bxor(C1, bxor(B2, t2))         # chỉnh block 2
C5p = bxor(C5, bxor(B6, dom_ok))      # chỉnh block 6
Cmod = C1p + C2 + C3 + C4 + C5p + C6
```

bxor(a,b) = XOR hai block byte.

Logic: C_{i-1} ^= P_orig ^ P_target để plaintext P_i ra đúng giá trị.

Gửi ciphertext đã flip đến server:

```python
r.sendlineafter(b"Enter your choice: ", b"2")
r.sendlineafter(b"Enter encrypted email (in hex): ", Cmod.hex().encode())
```

Server decrypt → plaintext block 2 = ,email, và block 6 = @script.sorcerer → pass kiểm tra → has_flag=True.

Lấy flag:

```python
r.sendlineafter(b"Enter your choice: ", b"1")
r.recvuntil(b"[2] Get flag\n")
flag = r.recvline(timeout=5).decode().strip()
```

Server gửi email mới → flag hiển thị.

---

## Key point

No key/iv needed: Chỉ dựa vào ciphertext từ server.

Bit flipping: Thay đổi block 2 & 6 để bypass domain check.

CBC mechanics: P_i = DEC(C_i) XOR C_{i-1} → thay đổi C_{i-1} sẽ ảnh hưởng P_i.

---

## Flag

Flag: scriptCTF{CBC_1s_s3cur3_r1ght?_700fda644089}