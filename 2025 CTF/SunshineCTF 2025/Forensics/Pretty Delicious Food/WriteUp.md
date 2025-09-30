# Write‑up: Pretty Delicious Food (SunshineCTF 2025)

## Mô tả thử thách

> This cake is out of this world! :DDDDDDD
> omnomonmonmonmonm
> ...
> something else is out of place too.
> Note: This is not a steganography challenge

---

## Kiểm tra file PDF

Xử dụng lệnh `file` để xem định dạng của file PDF

```bash
$ file prettydeliciouscakes.pdf 
prettydeliciouscakes.pdf: PDF document, version 1.4, 2 page(s)
```

Đây chỉ là 1 file PDF bình thường, tiếp tục kiểm tra xem có file nhúng bên trong không bằng `binwalk`

```bash
$ binwalk prettydeliciouscakes.pdf 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PDF document, version: "1.4"
1500          0x5DC           Zlib compressed data, default compression
1630          0x65E           Zlib compressed data, default compression
2259          0x8D3           Zlib compressed data, default compression
2016258       0x1EC402        Zlib compressed data, default compression
2016664       0x1EC598        Zlib compressed data, default compression
4380767       0x42D85F        Zlib compressed data, default compression
4381068       0x42D98C        Zlib compressed data, default compression
4381993       0x42DD29        Zlib compressed data, default compression
```

Nhận thấy cũng không có gì khi chỉ là những file nén mặc định của nó

Tiếp tục sẽ kiểm tra metadata của ảnh bằng `exiftool`

```bash
$ exiftool prettydeliciouscakes.pdf 
ExifTool Version Number         : 13.25
File Name                       : prettydeliciouscakes.pdf
Directory                       : .
File Size                       : 4.4 MB
File Modification Date/Time     : 2025:09:27 21:20:48+07:00
File Access Date/Time           : 2025:09:29 19:46:37+07:00
File Inode Change Date/Time     : 2025:09:27 21:22:36+07:00
File Permissions                : -rwxrwxrwx
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.4
Linearized                      : No
Producer                        : Skia/PDF m142 Google Docs Renderer
Title                           : prettycakes
Language                        : en
Tagged PDF                      : Yes
Page Count                      : 2
```

Nhận thấy các thông số cũng không có gì đặc biệt và thể hiện rằng đây là file PDF bình thường

Tiếp tục sẽ quét nhanh những từ khóa nghi vấn với `pdfid`

```bash
$ pdfid prettydeliciouscakes.pdf 
PDFiD 0.2.10 prettydeliciouscakes.pdf
 PDF Header: %PDF-1.4
 obj                   32
 endobj                32
 stream                 8
 endstream              8
 xref                   1
 trailer                1
 startxref              1
 /Page                  2
 /Encrypt               0
 /ObjStm                0
 /JS                    0
 /JavaScript            0
 /AA                    0
 /OpenAction            0
 /AcroForm              0
 /JBIG2Decode           0
 /RichMedia             0
 /Launch                0
 /EmbeddedFile          1
 /XFA                   0
 /Colors > 2^24         0
```

Nhận thấy nó xuất hiện những từ khóa như `/EmbeddedFile`

Bây giờ mình sẽ liệt kê ra tất cả các file đính kém và extract ra với `pdfdetach`

```bash
$ pdfdetach -list prettydeliciouscakes.pdf  
1 embedded files
1: payload.txt

$ pdfdetach -saveall prettydeliciouscakes.pdf
```

Quan sát thấy nó có một file nhúng là `payload.txt` với nội dung như sau

```txt
const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';
```

---

## Phân tích

Đến bước này thì khá là dễ rồi khi mình chỉ cần phân tích đoạn mã trong `payload.txt` thôi

```bash
$ echo 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==' | base64 -d
sun{p33p_d1s_fl@g_y0!}
```

---

## Flag

**Flag:** `sun{p33p_d1s_fl@g_y0!}`
