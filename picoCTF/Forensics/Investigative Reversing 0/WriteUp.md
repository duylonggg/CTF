# Write Up

## 1. **Phân tích file .png**

Chúng ta nhận được 1 file `binary` và 1 file `.png`.

Hãy cùng thử phân tích file `.png` trước.

```bash
$ pngcheck mystery.png
zlib warning:  different version (expected 1.2.13, using 1.3)

mystery.png  additional data after IEND chunk
ERROR: mystery.png
```

Chúng ta nhận thấy nó có cảnh báo sau chunk `IEND` có xuất hiện thêm một đoạn data lạ

## 2. **Hxd**

Sử dụng `HxD` để xem data của file `.png`

Nhận thấy đoạn dữ liệu lạ sau chunk `IEND` như sau:

```txt
# Hex-view
70 69 63 6F 43 54 4B 80 6B 35 7A 73 69 64 36 71 5F 33 64 36 35 39 66 35 37 7D

# ASCII 
picoCTK€k5zsid6q_3d659f57}
```

## 3. **Ghidra**

Sử dụng `Ghidra` để đọc file `binary`

Nhận thấy nó thêm dữ liệu vào file `.png` như sau:

```c
fputc((int)local_38[0],__stream_00);
fputc((int)local_38[1],__stream_00);
fputc((int)local_38[2],__stream_00);
fputc((int)local_38[3],__stream_00);
fputc((int)local_34,__stream_00);
fputc((int)local_33,__stream_00);
for (local_54 = 6; local_54 < 0xf; local_54 = local_54 + 1) {
    fputc((int)(char)(local_38[local_54] + '\x05'),__stream_00);
}
fputc((int)(char)(local_29 + -3),__stream_00);
for (local_50 = 0x10; local_50 < 0x1a; local_50 = local_50 + 1) {
    fputc((int)local_38[local_50],__stream_00);
}
```

Rõ ràng hơn thì sẽ là như sau:

```txt
| Index | Byte (hex)                    | ASCII             | Hành động                 |
| ----- | ----------------------------- | ----------------- | ------------------------- |
| 0–5   | 70 69 63 6F 43 54             | picoCT            | Giữ nguyên                |
| 6–14  | 4B 80 6B 35 7A 73 69 64 36    | K € k 5 z s i d 6 | -5 mỗi byte               |
| 15    | 71                            | q                 | +3 (đã bị -3)  → +3 → t   |
| 16–25 | 5F 33 64 36 35 39 66 35 37 7D | `_3d659f57}`      | Giữ nguyên                |
```

## 4. **Script**

```python
# 26 byte hex từ mystery.png
data = bytes.fromhex("70 69 63 6F 43 54 4B 80 6B 35 7A 73 69 64 36 71 5F 33 64 36 35 39 66 35 37 7D")

original = bytearray()

# Byte 0–5: giữ nguyên
original.extend(data[0:6])

# Byte 6–14: trừ 5
for i in range(6, 15):
    original.append((data[i] - 5) % 256)

# Byte 15: cộng lại 3
original.append((data[15] + 3) % 256)

# Byte 16–25: giữ nguyên
original.extend(data[16:26])

# In flag
print("Flag:")
print(original.decode())
```

## 5. **Flag**

picoCTF{f0und_1t_3d659f57}
