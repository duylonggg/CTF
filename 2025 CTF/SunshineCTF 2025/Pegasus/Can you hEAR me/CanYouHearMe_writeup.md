
# SunshineCTF 2025 — *Can you hEAR me?* (Reversing / Emulation)

**Điểm:** 479  
**Tác giả:** kcolley  
**Flag:** `sun{d0_n0t_fEAR_th1s_c4t3g0ry}`

---

## 1) Mô tả ngắn
Một vệ tinh chạy CPU **RAD‑EAR‑3** có cơ chế “băng chương trình” (cartridge) như jukebox. Trong số các cartridge có một cái nhãn “**hello**”. Nhiệm vụ: chạy được chương trình và lấy **serial number** của bo mạch (cũng chính là flag).

Ban tổ chức cung cấp bộ giả lập **PEGASUS v3** kèm runtime EAR và file ảnh máy: `CanYouHearMe.peg`.

---

## 2) Tài liệu & file được cấp
- `CanYouHearMe.peg` — ảnh máy PEGASUS cần chạy.
- `runpeg` — trình chạy PEGASUS v3.
- `libear.so`, `libeardbg.so` — thư viện runtime cho kiến trúc EAR/EAR‑3.
- `EAR_EAR_v3.md` — mô tả kiến trúc EAR v3.
- `PEGASUS.md` — mô tả định dạng PEGASUS và cách chạy.

> Cú pháp chạy: `runpeg <file.peg> [--debug] [--verbose] [--trace]`

---

## 3) Ý tưởng lời giải (TL;DR)
Chạy `CanYouHearMe.peg` trên giả lập với **`--verbose`** để log mọi thao tác I/O. Chương trình bên trong ghi từng byte ký tự ra **cổng 0** (kiểu UART) bằng lệnh **WRB**. Gom các ký tự đó lại sẽ được:

```
Board serial number: sun{d0_n0t_fEAR_th1s_c4t3g0ry}
```

---

## 4) Thiết lập môi trường
```bash
# 1) Cho phép thực thi
chmod +x runpeg

# 2) Đặt biến môi trường để trình chạy thấy các .so đi kèm
export LD_LIBRARY_PATH="$PWD"
```

> Nếu chạy trên hệ Linux khác thư mục, đảm bảo `runpeg`, `libear.so`, `libeardbg.so` nằm cùng thư mục hoặc đã thêm vào `LD_LIBRARY_PATH`.

---

## 5) Chạy và bắt log I/O
### Cách 1 — xem trực tiếp
```bash
LD_LIBRARY_PATH=. ./runpeg CanYouHearMe.peg --verbose
```
Bạn sẽ thấy nhiều dòng tương tự:
```
[IO] WRB port=0 value=0x42 'B'
[IO] WRB port=0 value=0x6f 'o'
[IO] WRB port=0 value=0x61 'a'
[IO] WRB port=0 value=0x72 'r'
[IO] WRB port=0 value=0x64 'd'
...
[IO] WRB port=0 value=0x7d '}'
[IO] WRB port=0 value=0x0a '\n'
```
Ghép lại các ký tự `'...'` sẽ thành chuỗi output cuối.

### Cách 2 — trích xuất tự động
Dùng `awk` để ráp các ký tự từ log `--verbose` thành một dòng hoàn chỉnh:

```bash
LD_LIBRARY_PATH=. ./runpeg CanYouHearMe.peg --verbose   | awk 'match($0, /'(.)'/, m) && /WRB .*port=0/ {printf "%s", m[1]} END{print ""}'
```

Kết quả in ra:
```
Board serial number: sun{d0_n0t_fEAR_th1s_c4t3g0ry}
```

> *Giải thích one‑liner:* `awk` tìm mẫu `'X'` (ký tự nằm giữa hai dấu nháy đơn) trên các dòng có `WRB ... port=0` rồi `printf` nối lại.

---

## 6) Vì sao làm vậy?
- Theo convention của runtime EAR/PEGASUS trong challenge, **port 0** là kênh ký tự “console/UART”.  
- Cờ không được in ra console “thường” mà được **ghi I/O từng byte**. Bật `--verbose` cho phép thấy các thao tác I/O như `WRB` (write byte).  
- Cartridge “**hello**” bên trong ảnh `.peg` chính là chương trình in serial. Việc “chọn cartridge” đã được ảnh máy làm sẵn; ta chỉ cần chạy đúng môi trường.

Nếu muốn soi sâu hơn, có thể dùng `--trace` hoặc `--debug` (và thư viện `libeardbg.so`) để xem luồng lệnh ở cấp thanh ghi/PC; tuy nhiên không cần thiết để lấy flag.

---

## 7) Kết quả
- **Serial / Flag:** `sun{d0_n0t_fEAR_th1s_c4t3g0ry}`

---

## 8) Notes & Pitfall
- Nếu không set `LD_LIBRARY_PATH=.`, `runpeg` có thể lỗi do không tìm thấy `libear.so`/`libeardbg.so`.
- Một số shell sẽ “nuốt” dấu nháy của `awk`. Nếu gặp lỗi, chạy trong Bash chuẩn hoặc đổi `'` thành ký tự `'` với escaping phù hợp.
- Trên hệ thống không có `awk`, có thể dùng Python parse log tương tự:
```python
import re, sys
out = []
for line in sys.stdin:
    if "WRB" in line and "port=0" in line:
        m = re.search(r"'(.)'", line)
        if m: out.append(m.group(1))
print("".join(out))
```
Rồi pipe:  
`LD_LIBRARY_PATH=. ./runpeg CanYouHearMe.peg --verbose | python3 parse.py`

---

## 9) Tóm tắt
1. Chuẩn bị: `chmod +x runpeg && export LD_LIBRARY_PATH=.`  
2. Chạy: `./runpeg CanYouHearMe.peg --verbose`  
3. Ghép ký tự từ các dòng `WRB port=0` ⇒ thu được serial/flag.

Chúc bạn “nghe” PEGASUS rõ như vũ trụ yên lặng 🛰️👂
