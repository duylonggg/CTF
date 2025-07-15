# Write Up

Đầu tiên chúng ta sẽ sửa header

```txt
89 50 4E 47 0D 0A 1A 0A
‰PNG....
```

Tiếp đó là chunk `IHDR` bị lỗi

```txt
00 00 00 0D 49 48 44 52
....IHDR
```

Sau đó thử kiểm tra lại bằng `pngcheck`

```bash
$ pngcheck mystery.png
zlib warning:  different version (expected 1.2.13, using 1.3.1)

mystery.png  CRC error in chunk pHYs (computed 38d82c82, expected 495224f0)
ERROR: mystery.png
```

Kiểm tra chunk `pHYs`

Nhận thấy CRC đã đúng nhưng file cứ báo sai -> xóa luôn chunk `pHYs`

Ngay sau chunk `pHYs` là chunk `IDAT` nhưng đã bị lỗi mất tên chunk -> sửa thành `IDAT`

Tiếp tục kiểm tra bằng `pngcheck`

```bash
$ pngcheck -v mystery.png
zlib warning:  different version (expected 1.2.13, using 1.3.1)

File: mystery.png (202919 bytes)
  chunk IHDR at offset 0x0000c, length 13
    1642 x 1095 image, 24-bit RGB, non-interlaced
  chunk sRGB at offset 0x00025, length 1
    rendering intent = perceptual
  chunk gAMA at offset 0x00032, length 4: 0.45455
:  invalid chunk length (too large)
ERRORS DETECTED in mystery.png
```

Báo lỗi file quá lớn, chúng ta hãy cùng quay lại check chunk `IDAT`

Thấy phần length là `AA AA FF A5` quá lớn

Hãy tìm đến chunk tiếp theo

Ta thấy chunk `IDAT` tiếp theo nằm ở offset `0xFFF6`

Chunk `IDAT` ta đang xét nằm ở offset `0x45`

Ta tính toán ra được length phải là `0xFFA5`

Vậy phải sửa lenght thành `00 00 FF A5`

Check lại file

```bash
$ pngcheck -v mystery.png
zlib warning:  different version (expected 1.2.13, using 1.3.1)

File: mystery.png (202919 bytes)
  chunk IHDR at offset 0x0000c, length 13
    1642 x 1095 image, 24-bit RGB, non-interlaced
  chunk sRGB at offset 0x00025, length 1
    rendering intent = perceptual
  chunk gAMA at offset 0x00032, length 4: 0.45455
  chunk IDAT at offset 0x00042, length 65445
    zlib: deflated, 32K window, fast compression
  chunk IDAT at offset 0x0fff3, length 65524
  chunk IDAT at offset 0x1fff3, length 65524
  chunk IDAT at offset 0x2fff3, length 6304
  chunk IEND at offset 0x3189f, length 0
No errors detected in mystery.png (8 chunks, 96.3% compression).
```

Mở file lên và thấy flag
