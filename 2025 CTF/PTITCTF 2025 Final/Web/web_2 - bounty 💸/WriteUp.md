# Write Up

Bài này khai thác “tính khí thất thường” của JavaScript khi so sánh bằng lỏng (`==`), ép kiểu ngầm, `parseInt`, `NaN`, `-0`, và cách các object/array chuyển sang chuỗi.

Nhiệm vụ đặt ra: tìm đúng input cho từng stage dựa trên chuỗi biểu thức kỳ dị mà đề bài đưa ra. Đi hết hành trình, ta sẽ mở được cánh cửa cuối cùng để lấy flag.

---

## Kiến thức nền cần nhớ nhanh

---

- Ưu tiên toán tử: **Unary**: `!`, `+` (ép kiểu số) có độ ưu tiên cao nhất sau đó mới tới toán tử `+` (nhị phân, cộng hoặc ghép chuỗi) rồi mới tới `[...]` (indexing / truy cập phần tử chuỗi, mảng).

- Quy tắc toán tử `+` nhị phân: Nếu một vế (sau khi ép kiểu ToPrimitive) là **string**, thì `+` trở thành **nối chuỗi**. Nếu cả hai đều là số (hoặc ép được về số), thì `+` là phép **cộng số học**.

- ToPrimitive cho Array và Object
    -   `[].toString()` ⇒ `""` (chuỗi rỗng, vì mảng rỗng khi join không có phần tử nào).
    -   `({}).toString()` ⇒ `"[object Object]"` (theo `Object.prototype.toString`).

- Một số ví dụ ép kiểu số
    -   `+[]` ⇒ `0`
    -   `!0` ⇒ `true`
    -   `+true` ⇒ `1`

- Indexing trên chuỗi
    -   `"abc"[0]` ⇒ `"a"`
    -   Chỉ số bắt đầu từ `0`.

---

## Stage 0 / 4

![alt text](image-1.png)

**Biểu thức:**

``` js
(![]+[])[+[]] + ([][[]]+[])[+!+[]] + ({}+[])[+!+[]+!+[]] == input
```

### Giải mã

**Phần 1: `(![]+[])[+[]]`**

- `![]`: `[]` là `truthy` (giá trị khi ép sang kiểu `boolean` sẽ trở thành `true`) ⇒ `![] = false` 

- `(![]+[])`: `[] = ""` (chuỗi rỗng). Khi một vế là chuỗi, + là nối chuỗi: `false + "" = "false"`.

- `[+[]]`: `+[] ⇒ 0`. Lấy ký tự thứ `0` của **`"false"`** là **'f'**.

> ⇒ Chuỗi trên = `(false)[0]` nghĩa là lấy ký tự thứ `0` của `"false"` là **'f'**.

**Phần 2: `([][[]]+[])[+!+[]]`**

- `[][[]]`: `[]` là mảng rỗng, `[[]]` là mảng có 1 phần tử là `[]`. Khi dùng làm **key** truy cập thuộc tính (**obj[key]**), **key** bị ép sang chuỗi: `[[]].toString()`, phần tử duy nhất là `[]`, mà `[].toString() = ""` ⇒ toàn bộ thành `""`. Vậy `[][[]] ≡ [][""]`. Array không có thuộc tính khóa rỗng "" ⇒ `undefined`

- `[][[]]+[]`: `[] = ""` ⇒ `undefined + "" = "undefined"`

- `[+!+[]]`: `+[] ⇒ 0`, `!0 ⇒ true`, `+true ⇒ 1`

> ⇒ Chuỗi trên = `(undefined)[1]` nghĩa là lấy ký tự thứ `1` của `"undefined"` là **'n'**.

**Phần 3: `({}+[])[+!+[]+!+[]]`**

- `({}+[])`: Dấu ngoặc bắt buộc để `{}` được hiểu là object literal (không bị parse như block rỗng). `{}` khi ToPrimitive → `"[object Object]"`. `[] → ""` nên `({}+[]) ⇒ "[object Object]"`.

- `+!+[]+!+[]`: `+[] ⇒ 0 → !0 ⇒ true → +true ⇒ 1`. Biểu thức là `1 + (!+[])`, do `!+[] = !0 = true`. Cộng số với **boolean** ⇒ `true` ép số thành `1` ⇒ `1 + 1 = 2`

> ⇒ Ký tự thứ 2 (0-based) của `"[object Object]"`: là **'b'**.

👉 **Input:** `fnb`

---

## Stage 1 / 4

![alt text](image-2.png)

**Biểu thức:**

``` js
typeof a == 'number' && a !== NaN && (a - 1 < a) == false
```

với `a = parseInt(input)`

### Giải mã

- `typeof a == 'number'`: `parseInt(...)` luôn trả về kiểu number trong JS: hoặc là một số hữu hạn, hoặc là `NaN`. Vì vậy vế này luôn đúng cho mọi kết quả của `parseInt`

- `a !== NaN` luôn `true`, kể cả khi `a` thực sự là `NaN` (Muốn kiểm tra `NaN` đúng cách phải dùng `Number.isNaN(a)`)

- `(a - 1 < a) == false`, với số hữu hạn bình thường, `a - 1 < a` luôn `true`, Với `±Infinity` biểu thức luôn đúng Nhưng `parseInt` không thể tạo ra `±Infinity`, với `NaN` thì `a - 1` là `NaN`, mọi so sánh với `NaN` (<, >, <=, >=) đều `false` ⇒ biểu thức đúng

> ⇒ Do đó, điều kiện toàn bộ chỉ thỏa khi `a` là `NaN`.

👉 **Input:** `abc` (hay bất kỳ chuỗi chữ nào).

---

## Stage 2 / 4

![alt text](image-3.png)

**Biểu thức:**

``` js
Object.is(0, a) == false && Math.abs(1 / a) > 1
```

với `a = parseInt(input)`

### Giải mã

-   `Math.abs(1/a) > 1` ⇒ với số nguyên thì chỉ xảy ra khi `|a| < 1` ⇒ `a` phải là `0` hoặc `-0` (`NaN` loại vì `1/NaN` là `NaN`, so sánh cho ra `false`).
-   `Object.is(0, a) == false` ⇒ chỉ `-0` thỏa `(Object.is(0, -0)` là `false`.

> → Cần `a = -0`.

👉 **Input:** `-0`

---

## Stage 3 / 4

![alt text](image-4.png)

**Biểu thức:**

``` js
[] == input && ![[]] == input
```

### Giải mã

-   `[] == ""` → true.
-   `![[]]` = `false`, nếu một vế là boolean, đổi boolean sang number `false ⇒ 0`. So sánh thành `0 == ""`, khi so sánh number với string, chuỗi được đổi sang number: `Number("") ⇒ 0`. So sánh `0 == 0 ⇒ true`

👉 **Input:** chuỗi rỗng `""` (để trống).

---

## Flag

Đi hết bốn cánh cửa, trang web trả về flag:

![alt text](image-5.png)

Flag: `PTITCTF{Js_iS_The_best_BAD!!!}`