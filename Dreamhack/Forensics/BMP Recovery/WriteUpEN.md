## Write Up

## 1. **Analysis**

Let's examine the `chal.py` file:

```Bash
$ cat chal.py
with open('flag.bmp', 'rb') as f:
    data = bytearray(f.read())

data[:0x1C] = b'\x00' * 0x1C
data[0x22:0x36] = b'\x00' * 0x14

with open('flag.bmp.broken', 'wb') as f:
    f.write(data)
From this, we can see that chal.py opens flag.bmp, reads its data as a byte array, and then zeroes out specific ranges:

data[:0x1C] = b'\0x00 * 0x1C clears data from 0x00 to 0x1B.
data[0x22:0x36] = b'\x00' * 0x14 clears data from 0x22 to 0x35.
```

Our task is to restore these zeroed-out bytes.

---

## 2. **Restoration**

To restore the bytes of a `.bmp` file, we first need to understand its structure, starting with the Bitmap file header:

```txt
Offset  | Size      | Field                 | Description                                                               |
----------------------------------------------------------------------------------------------------------------------- |
0x00    | 2 bytes   | Signature             | Must be BM (0x42 0x4D) for a standard BMP.                                |
0x02    | 4 bytes   | File size             | The total size of the BMP file in bytes.                                  |
0x06    | 2 bytes   | Reserved1             | Usually 0.                                                                |
0x08    | 2 bytes   | Reserved2             | Usually 0.                                                                |
0x0A    | 4 bytes   | Pixel data offset     | Offset to the beginning of the pixel data (usually 54 if no color table). |
0x0E    | 4 bytes   | DIB Header size       | Size of the DIB header (usually 40 bytes - BITMAPINFOHEADER).             |
0x12    | 4 bytes   | Width                 | Image width in pixels.                                                    |
0x16    | 4 bytes   | Height                | Image height in pixels.                                                   |
0x1A    | 2 bytes   | Planes                | Number of color planes (always 1).                                        |
0x1C    | 2 bytes   | Bits per pixel        | Number of bits per pixel (24 = RGB, 32 = RGBA, etc.).                     |
0x1E    | 4 bytes   | Compression           | Compression method (0 = none).                                            |
0x22    | 4 bytes   | Image size            | Size of the pixel data (can be 0 if uncompressed).                        |
0x26    | 4 bytes   | X pixels per meter    | Horizontal resolution.                                                    |
0x2A    | 4 bytes   | Y pixels per meter    | Vertical resolution.                                                      |
0x2E    | 4 bytes   | Total colors          | Number of colors used (0 if all colors are used).                         |
0x32    | 4 bytes   | Important colors      | Number of important colors (0 = all).                                     |
```

After identifying the offsets of the fields within the first 54 bytes, we can start populating some of them:

```txt
| Offset | Kích thước | Trường               | Dữ liệu              |
| ------ | ---------- | -------------------- | ---------------------|
| 0x00   | 2 bytes    | `Signature`          | 0x42 0x4D            | 
| 0x02   | 4 bytes    | `File size`          | 0xF6 0x58 0xDA 0x00  |   
| 0x06   | 2 bytes    | `Reserved1`          | 0x00 0x00            |
| 0x08   | 2 bytes    | `Reserved2`          | 0x00 0x00            |
| 0x0A   | 4 bytes    | `Pixel data offset`  | 0x36 0x00 0x00 0x00  |
| 0x0E   | 4 bytes    | `DIB Header size`    | 0x28 0x00 0x00 0x00  |
| 0x12   | 4 bytes    | `Width`              |                      | 
| 0x16   | 4 bytes    | `Height`             |                      |
| 0x1A   | 2 bytes    | `Planes`             | 0x01 0x00            | 
| 0x1C   | 2 bytes    | `Bits per pixel`     | 0x18 0x00            |
| 0x1E   | 4 bytes    | `Compression`        | 0x00 0x00 0x00 0x00  | 
| 0x22   | 4 bytes    | `Image size`         | 0x00 0x00 0x00 0x00  | 
| 0x26   | 4 bytes    | `X pixels per meter` | 0x13 0x0B 0x00 0x00  | 
| 0x2A   | 4 bytes    | `Y pixels per meter` | 0x13 0x0B 0x00 0x00  | 
| 0x2E   | 4 bytes    | `Total colors`       | 0x00 0x00 0x00 0x00  | 
| 0x32   | 4 bytes    | `Important colors`   | 0x00 0x00 0x00 0x00  | 
```

We've filled in most of the fields. Only Width and Height are still unknown.

---

## 3. **Calculation**

The Image size field can be 0 if the image is uncompressed, or it can be calculated as total_bytes - header_size. It won't affect the solution.

However, to calculate Width and Height, we can use the following formula:

$$
\text{Image Size} = \left\lfloor \frac{\text{Bits Per Pixel} \times \text{Image Width}}{32} \right\rfloor \times 4 \times \text{Image Height}
$$

We already have Image size and Bits Per Pixel. We'll need to determine Image Width and Image Height. We can brute-force these values.

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