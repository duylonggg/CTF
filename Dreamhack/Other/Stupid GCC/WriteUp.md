# 🧠 \[Write-up] Stupid GCC – Khi GCC “ngáo tối ưu hoá”

## 🗂 Mục lục

1. 📝 [Tổng quan đề bài](#tổng-quan-đề-bài)
2. 🔎 [Phân tích code](#phân-tích-code)
3. ⚠️ [Hiện tượng bất thường](#️-hiện-tượng-bất-thường)
4. 🛠️ [Các mức tối ưu của GCC](#các-mức-tối-ưu-của-gcc)

   * `-O0` (Mặc định)
   * `-O2` & `-O3`
5. 💥 [Undefined Behavior (UB) trong C](#undefined-behavior-ub-trong-c)
6. 🔍 [Điểm gây UB & cách GCC tận dụng](#điểm-gây-ub--cách-gcc-tận-dụng)
7. 🖨️ [Tương tác với `printf()` (Heisenbug)](#tương-tác-với-printf-heisenbug)
8. 🧪 [Demo & kiểm chứng](#demo--kiểm-chứng)
9. 🔒 [Phòng tránh & khắc phục](#phòng-tránh--khắc-phục)
10. 🎯 [Kết luận](#kết-luận)

---

## 📝 Tổng quan đề bài

Challenge **Stupid GCC** (Dreamhack) cung cấp một chương trình C trông rất bình thường, nhưng:

* Khi biên dịch với `gcc -O2` → chương trình **in ra flag**. 🚩
* Khi biên dịch mặc định (`-O0`) hoặc thêm/bớt `printf` → **không in flag**. ❌

Mục tiêu: Hiểu lý do tại sao GCC -O2 tận dụng **Undefined Behavior (UB)** để bypass logic ban đầu.

---

## 🔎 Phân tích code

```c
#include <stdio.h>
#include <stdint.h>

int main() {
    uint8_t v1 = 0;
    int v2 = 0;
    uint16_t v4[10] = {0};

    while (v4[v1] < UINT16_MAX && v1 < 10) {
        v1++;
        printf("v4[%d]: %p\n", v1, &v4[v1]);
        v2 += v1;

        if (v2 > 10000) {
            puts("Flag{test_gcc}");
            return 0;
        }
    }
    return 0;
}
```

* **Logic ban đầu**: với `v1` từ 0 đến 9, tổng `v2 = 1+2+...+9 = 45` → không thể vượt `10000`.

---

## ⚠️ Hiện tượng bất thường

1. **Biên dịch mặc định (`-O0`)**: Không in flag.
2. **Biên dịch `-O2`/`-O3`**: Tự in flag.
3. **Thêm hoặc bỏ `printf()`** trong vòng lặp → Kết quả khác nhau.

Đây là dấu hiệu của **Undefined Behavior** + **tối ưu hoá aggressive**.

---

## 🛠️ Các mức tối ưu của GCC

| Mức `-O`         | Đặc điểm                                                            |
| ---------------- | ------------------------------------------------------------------- |
| `-O0` (mặc định) | Không tối ưu → Dễ debug, code chạy sát source.                      |
| `-O2`            | Tối ưu mạnh dangr trung: `-funroll-loops`, `-funswitch-loops`, etc. |
| `-O3`            | Tối ưu cực mạnh: thêm vectorization, inlining... → Binary lớn hơn.  |

`-O2`/`-O3` bật nhiều pass tận dụng **giả định UB** để loại bỏ check không cần thiết.

---

## 💥 Undefined Behavior (UB) trong C

* **UB**: Hành vi không định nghĩa bởi chuẩn C (C99+), ví dụ:

  * Truy cập mảng vượt biên.
  * Tràn số nguyên có dấu.
  * Dereference NULL pointer.

* **Tác động**: Khi gặp UB, compiler **được phép**:

  * Giả định UB **không xảy ra**.
  * **Loại bỏ** code liên quan.
  * **Tái sắp xếp** lệnh.

→ Cho phép tối ưu hoá mạnh, nhưng rất nguy hiểm nếu code chứa UB.

---

## 🔍 Điểm gây UB & cách GCC tận dụng

```c
while (v4[v1] < UINT16_MAX && v1 < 10) {
    ...
}
```

* Trong C, compiler **tự do** đánh giá vế `A && B` theo bất kỳ thứ tự nào nếu có UB.
* Ở đây, **`v4[v1] < ...`** có thể được đánh giá trước **`v1 < 10`**.
* Khi `v1 >= 10`, **truy cập `v4[v1]`** là **UB** ⇒ GCC giả định **`v1 < 10` luôn đúng** để tránh UB ⇒ **bỏ hẳn** điều kiện `v1 < 10`.

Kết quả:

1. Vòng lặp trở thành vô hạn.
2. `v1` tăng vượt 10.
3. `v2 += v1` nhanh chóng >10000.
4. In flag.

---

## 🖨️ Tương tác với `printf()` (Heisenbug)

* `printf()` là **side-effect** (I/O), compiler không thể tùy tiện loại bỏ hoặc reorder.
* Khi có `printf` trong vòng lặp, GCC **giữ nguyên** thứ tự, không bỏ check `v1 < 10`.
* Do đó, vòng lặp dừng đúng lúc ⇒ **không in flag**.

Đây là hiện tượng **Heisenbug**: Lỗi xuất hiện/biến mất khi thêm debug.

---

## 🚀 Bypass 

Đôi khi bạn cần đọc **flag gốc** hoặc thay đổi quyền của file `/flag.txt`. Dưới đây là hai “mánh” thường dùng:

1. Pipe + `chmod` ngay khi compile

Dùng GCC như một “trình chạy” để cấp quyền cho file flag:

```bash
echo -e '
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <string.h>

int main()
{
    chmod("/flag.txt", 07777);
}' |  gcc -o a.out -x c -
```

- `-x c`: cho phép GCC nhận mã C từ stdin
- `chmod(...)`: syscall thay đổi quyền, cấp quyền `rwx` cho mọi user

2. Ép macro `if` luôn true

Một cách “hack” khác tận dụng preprocessor:

```bash
gcc -D"if(x)=if(1)" a.c
```

Mọi `if(...)` trong `a.c` đều trở thành `if(1)`, buộc chương trình luôn thực thi nhánh in flag

Sau đó bạn sẽ có flag 1 cách kỳ diệu