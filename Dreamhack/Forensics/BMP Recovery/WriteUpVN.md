# Write Up

## 1. **Phân tích**

Chúng ta hãy thử mở file `chal.py` xem nó có gì

```bash
$ cat chal.py
with open('flag.bmp', 'rb') as f:
    data = bytearray(f.read())

data[:0x1C] = b'\x00' * 0x1C
data[0x22:0x36] = b'\x00' * 0x14

with open('flag.bmp.broken', 'wb') as f:
    f.write(data)
```

Chúng ta có thể thấy rằng file `chal.py` sẽ mở file `flag.bmp`

Sau đó đọc và lưu dữ liệu file `flag.bmp` dưới dạng các byte

`data[:0x1C] = b'\0x00 * 0x1C` --> Xóa dữ liệu từ `0x00` đến `0x1B`

`data[0x22:0x36] = b'\x00' * 0x14` --> Xóa dữ liệu từ `0x22` đến `0x35`

Vậy bây giờ việc chúng ta cần làm là khôi phục lại các byte bị xóa

---

## 2. **Khôi phục**

Để khôi phục các byte của file `.bmp` thì đầu tiên chúng ta cần tìm hiểu về dạng file này trước

Chúng ta sẽ đến với phần đầu tiên: **Bitmap file header**

```txt
| Offset | Kích thước | Trường               | Mô tả                                                              |
| ------ | ---------- | -------------------- | ------------------------------------------------------------------ |
| 0x00   | 2 bytes    | `Signature`          | Phải là `BM` (0x42 0x4D) nếu là BMP chuẩn                          |
| 0x02   | 4 bytes    | `File size`          | Kích thước toàn bộ file BMP (tính bằng byte)                       |
| 0x06   | 2 bytes    | `Reserved1`          | Thường là 0                                                        |
| 0x08   | 2 bytes    | `Reserved2`          | Thường là 0                                                        |
| 0x0A   | 4 bytes    | `Pixel data offset`  | Offset bắt đầu vùng ảnh pixel (thường là 54 nếu không có bảng màu) |
| 0x0E   | 4 bytes    | `DIB Header size`    | Kích thước DIB header (thường là 40 byte - BITMAPINFOHEADER)       |
| 0x12   | 4 bytes    | `Width`              | Chiều rộng ảnh (pixel)                                             |
| 0x16   | 4 bytes    | `Height`             | Chiều cao ảnh (pixel)                                              |
| 0x1A   | 2 bytes    | `Planes`             | Số mặt phẳng màu (luôn là 1)                                       |
| 0x1C   | 2 bytes    | `Bits per pixel`     | Số bit trên mỗi pixel (24 = RGB, 32 = RGBA, v.v.)                  |
| 0x1E   | 4 bytes    | `Compression`        | Phương pháp nén (0 = none)                                         |
| 0x22   | 4 bytes    | `Image size`         | Kích thước vùng pixel (có thể là 0 nếu không nén)                  |
| 0x26   | 4 bytes    | `X pixels per meter` | Độ phân giải ngang                                                 |
| 0x2A   | 4 bytes    | `Y pixels per meter` | Độ phân giải dọc                                                   |
| 0x2E   | 4 bytes    | `Total colors`       | Số màu dùng (0 nếu tất cả màu được dùng)                           |
| 0x32   | 4 bytes    | `Important colors`   | Số màu quan trọng (0 = tất cả)                                     |
```

Sau khi xác định offset của các trường trong 54 byte đầu tiên thì chúng ta tiến hành điền giá trị 1 số trường nhất định vào

```txt
| Offset | Kích thước | Trường               | Dữ liệu              | Cách tính                                             |
| ------ | ---------- | -------------------- | ---------------------------------------------------------------------------- |
| 0x00   | 2 bytes    | `Signature`          | 0x42 0x4D            | Mặc định theo mã ASCII của 'BM'                       |
| 0x02   | 4 bytes    | `File size`          | 0xF6 0x58 0xDA 0x00  | Sử dụng lệnh ls -l flag.bmp.broken để xem kích thước  |     
| 0x06   | 2 bytes    | `Reserved1`          | 0x00 0x00            | Thường là 0                                           |
| 0x08   | 2 bytes    | `Reserved2`          | 0x00 0x00            | Thường là 0                                           |
| 0x0A   | 4 bytes    | `Pixel data offset`  | 0x36 0x00 0x00 0x00  | Thường là 54                                          |
| 0x0E   | 4 bytes    | `DIB Header size`    | 0x28 0x00 0x00 0x00  | Thường là 40                                          |
| 0x12   | 4 bytes    | `Width`              |                      | Chưa có dữ liệu                                       |
| 0x16   | 4 bytes    | `Height`             |                      | Chưa có dữ liệu                                       |
| 0x1A   | 2 bytes    | `Planes`             | 0x01 0x00            | Luôn là 1                                             |
| 0x1C   | 2 bytes    | `Bits per pixel`     | 0x18 0x00            | Đề cho                                                |
| 0x1E   | 4 bytes    | `Compression`        | 0x00 0x00 0x00 0x00  | Bằng 0 do không nén                                   |
| 0x22   | 4 bytes    | `Image size`         | 0x00 0x00 0x00 0x00  | Bằng 0 do không nén                                   |
| 0x26   | 4 bytes    | `X pixels per meter` | 0x13 0x0B 0x00 0x00  | 72 DPI, chuẩn mặc định                                |
| 0x2A   | 4 bytes    | `Y pixels per meter` | 0x13 0x0B 0x00 0x00  | 72 DPI, chuẩn mặc định                                |
| 0x2E   | 4 bytes    | `Total colors`       | 0x00 0x00 0x00 0x00  | Thường là 0                                           |
| 0x32   | 4 bytes    | `Important colors`   | 0x00 0x00 0x00 0x00  | Thường là 0                                           |
```

Ok vậy là chúng ta đã điền được gần hết

Chỉ còn có trường `width` và `height` là chưa có dữ liệu để điền

---

## 3. **Tính toán**

Thực ra trường `Image size` anh em để 0 hay tính nó theo công thức là `image_data_size = total_bytes - header_size` cũng được, nó sẽ không ảnh hưởng đến kết quả bài toán

Nhưng để phục vụ việc tính `width` và `height` thì tôi sẽ để cho anh em công thức như trên

$$
\text{Image Size} = \left\lfloor \frac{\text{Bits Per Pixel} \times \text{Image Width}}{32} \right\rfloor \times 4 \times \text{Image Height}
$$

Chúng ta đã có các giá trị cho sẵn là `Image size` và `Bits Per Pixel`

Vậy sẽ chỉ cần tính `Image Width` và `Image Height`

Chúng ta sẽ đơn giản là brute force vì tôi không nghĩ ra cách hay hơn

---

## 4. **Script**

```python
with open('flag.bmp.broken', 'rb') as f:
    data = bytearray(f.read())

total_bytes = 14309622  
header_size = 54  
info_header_size = 40
bitplane_value = 1
bytes_per_pixel = 3 

image_data_size = total_bytes - header_size

num_pixels = image_data_size // bytes_per_pixel

data[0x0] = 0x42
data[0x1] = 0x4D
data[0x2:0x6] = total_bytes.to_bytes(4, byteorder='little')     
data[0xA:0xE] = header_size.to_bytes(4, byteorder='little')
data[0xE:0x12] = info_header_size.to_bytes(4, byteorder='little')     
data[0x1A:0x1C] = bitplane_value.to_bytes(2, byteorder='little')     
data[0x22:0x26] = image_data_size.to_bytes(4, byteorder='little')       


for width in range(1, int(num_pixels**0.5) + 1):
    if num_pixels % width == 0:
        height = num_pixels // width
        data[0x12:0x16] = width.to_bytes(4, byteorder='little')
        data[0x16:0x1A] = height.to_bytes(4, byteorder='little')
        with open(f'flag_{width}.bmp', 'wb') as f:
            f.write(data)
        data[0x12:0x16] = height.to_bytes(4, byteorder='little')
        data[0x16:0x1A] = width.to_bytes(4, byteorder='little')
        with open(f'flag_{height}.bmp', 'wb') as f:
            f.write(data)
```

---

## 5. **Flag**

DH{c08ad9e275928481fe5aabac2a34b6573bf8dc7f8fb15d8b7120e069160a2c2f}