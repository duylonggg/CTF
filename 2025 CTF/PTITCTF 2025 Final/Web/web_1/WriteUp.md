# Write Up

## Phân tích

![alt text](image.png)

`Đăng ký` tài khoản mới và `Đăng nhập`

---

## Path Traversal

Mình sẽ thử kỹ thuật cơ bản là Path Traversal xem sao

`/robots.txt`

![alt text](image-2.png)

`/etc/passwd`

![alt text](image-3.png)

`/uploads`

![alt text](image-4.png)

`/uploads/flag.txt`

![alt text](image-5.png)

Sau một hồi mày mò với những file cơ bản và hàng tá dạng obfuscaste URL thì cuối cùng mình cũng mò ra `/uploads/flag.txt` chứa flag

---

## Flag

Flag: `PTITCTF{Ph4r_Deseri4liz4tion_he_he_he}`