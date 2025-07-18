# Write Up

Anh em đọc về time-based attack để biết thêm nhé

Dạng này đã xuất hiện nhiều rồi nhưng chúng ta hay làm ở dạng phòng thủ, điển hình là những bài đọc lag truy vấn SQL nếu đúng thì sleep 1 giây chẳng hạn

Bài này chúng ta cũng sẽ khai thác như vậy, thử từng số cho đến khi đúng hết

```bash
#!/bin/bash
for i in {0..9}; do
  pin="${i}0000000"
  echo $pin
  time ./pin_checker <<< "$pin"
done
```

PIN: 48390513

Flag: picoCTF{t1m1ng_4tt4ck_914c5ec3}
