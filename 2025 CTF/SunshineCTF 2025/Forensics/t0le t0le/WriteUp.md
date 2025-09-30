# Write-up: t0le t0le (SunshineCTF 2025)

## Mô tả thử thách

> Our CCDC business guy made a really weird inject. He's just obsessed with that damn cat... there's nothing hiding in there, right?

---

## Kiểm tra file docx

Đầu tiên mình sẽ sử dụng lệnh `file` để kiểm tra file `docx`

```bash
$ file Team_5_-_Inject_72725.docx 
Team_5_-_Inject_72725.docx: Microsoft Word 2007+
```

Nhận thấy đây là file `Docx: Microsoft Word 2007+` bình thường

Tiếp tục kiểm tra xem có file ẩn bên trong không với `binwalk`

```bash
$ binwalk Team_5_-_Inject_72725.docx 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             Zip archive data, at least v2.0 to extract, compressed size: 417, uncompressed size: 1954, name: [Content_Types].xml
986           0x3DA           Zip archive data, at least v2.0 to extract, compressed size: 239, uncompressed size: 590, name: _rels/.rels
1786          0x6FA           Zip archive data, at least v2.0 to extract, compressed size: 5204, uncompressed size: 36844, name: word/document.xml
7037          0x1B7D          Zip archive data, at least v2.0 to extract, compressed size: 367, uncompressed size: 2153, name: word/_rels/document.xml.rels
7726          0x1E2E          Zip archive data, at least v2.0 to extract, compressed size: 738, uncompressed size: 3196, name: word/footnotes.xml
8512          0x2140          Zip archive data, at least v2.0 to extract, compressed size: 737, uncompressed size: 3190, name: word/endnotes.xml
9296          0x2450          Zip archive data, at least v2.0 to extract, compressed size: 1699, uncompressed size: 6400, name: word/header1.xml
11041         0x2B21          Zip archive data, at least v2.0 to extract, compressed size: 186, uncompressed size: 290, name: word/_rels/header1.xml.rels
11284         0x2C14          Zip archive data, at least v1.0 to extract, compressed size: 37089, uncompressed size: 37089, name: word/media/image1.png
48424         0xBD28          Zip archive data, at least v1.0 to extract, compressed size: 125657, uncompressed size: 125657, name: word/media/image2.png
174132        0x2A834         Zip archive data, at least v1.0 to extract, compressed size: 278306, uncompressed size: 278306, name: word/media/image3.png
452489        0x6E789         Zip archive data, at least v1.0 to extract, compressed size: 152042, uncompressed size: 152042, name: word/media/image4.png
604582        0x939A6         Zip archive data, at least v2.0 to extract, compressed size: 896, uncompressed size: 11180, name: word/media/image5.emf
605529        0x93D59         Zip archive data, at least v2.0 to extract, compressed size: 602, uncompressed size: 3072, name: word/embeddings/oleObject1.bin
606191        0x93FEF         Zip archive data, at least v1.0 to extract, compressed size: 6779, uncompressed size: 6779, name: word/media/image6.jpeg
613022        0x95A9E         Zip archive data, at least v1.0 to extract, compressed size: 11124, uncompressed size: 11124, name: word/media/image7.jpeg
624198        0x98646         Zip archive data, at least v2.0 to extract, compressed size: 1836, uncompressed size: 8717, name: word/theme/theme1.xml
626085        0x98DA5         Zip archive data, at least v2.0 to extract, compressed size: 1169, uncompressed size: 3604, name: word/settings.xml
627301        0x99265         Zip archive data, at least v2.0 to extract, compressed size: 4315, uncompressed size: 44594, name: word/styles.xml
631661        0x9A36D         Zip archive data, at least v2.0 to extract, compressed size: 376, uncompressed size: 1083, name: word/webSettings.xml
632087        0x9A517         Zip archive data, at least v2.0 to extract, compressed size: 515, uncompressed size: 1749, name: word/fontTable.xml
632650        0x9A74A         Zip archive data, at least v2.0 to extract, compressed size: 358, uncompressed size: 727, name: docProps/core.xml
633319        0x9A9E7         Zip archive data, at least v2.0 to extract, compressed size: 374, uncompressed size: 715, name: docProps/app.xml
635517        0x9B27D         End of Zip archive, footer length: 22
```

Nhận thấy có rất nhiều file nén bên trong file `docx` này

Gần như tất cả các file đều là định dạng `rels`, `xml`, `jpeg`, `png`. Duy nhất có file đáng nghi với định dạng `bin` → `word/embeddings/oleObject1.bin`

Bây giờ mình sẽ extract hết ra hoặc có thể extract mỗi file đó để tiếp tục kiểm tra

```bash
# Extract toàn bộ 
$ binwalk -e Team_5_-_Inject_72725.docx 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             Zip archive data, at least v2.0 to extract, compressed size: 417, uncompressed size: 1954, name: [Content_Types].xml
986           0x3DA           Zip archive data, at least v2.0 to extract, compressed size: 239, uncompressed size: 590, name: _rels/.rels
1786          0x6FA           Zip archive data, at least v2.0 to extract, compressed size: 5204, uncompressed size: 36844, name: word/document.xml
7037          0x1B7D          Zip archive data, at least v2.0 to extract, compressed size: 367, uncompressed size: 2153, name: word/_rels/document.xml.rels
7726          0x1E2E          Zip archive data, at least v2.0 to extract, compressed size: 738, uncompressed size: 3196, name: word/footnotes.xml
8512          0x2140          Zip archive data, at least v2.0 to extract, compressed size: 737, uncompressed size: 3190, name: word/endnotes.xml
9296          0x2450          Zip archive data, at least v2.0 to extract, compressed size: 1699, uncompressed size: 6400, name: word/header1.xml
11041         0x2B21          Zip archive data, at least v2.0 to extract, compressed size: 186, uncompressed size: 290, name: word/_rels/header1.xml.rels
11284         0x2C14          Zip archive data, at least v1.0 to extract, compressed size: 37089, uncompressed size: 37089, name: word/media/image1.png
48424         0xBD28          Zip archive data, at least v1.0 to extract, compressed size: 125657, uncompressed size: 125657, name: word/media/image2.png
174132        0x2A834         Zip archive data, at least v1.0 to extract, compressed size: 278306, uncompressed size: 278306, name: word/media/image3.png
452489        0x6E789         Zip archive data, at least v1.0 to extract, compressed size: 152042, uncompressed size: 152042, name: word/media/image4.png
604582        0x939A6         Zip archive data, at least v2.0 to extract, compressed size: 896, uncompressed size: 11180, name: word/media/image5.emf
605529        0x93D59         Zip archive data, at least v2.0 to extract, compressed size: 602, uncompressed size: 3072, name: word/embeddings/oleObject1.bin
606191        0x93FEF         Zip archive data, at least v1.0 to extract, compressed size: 6779, uncompressed size: 6779, name: word/media/image6.jpeg
613022        0x95A9E         Zip archive data, at least v1.0 to extract, compressed size: 11124, uncompressed size: 11124, name: word/media/image7.jpeg
624198        0x98646         Zip archive data, at least v2.0 to extract, compressed size: 1836, uncompressed size: 8717, name: word/theme/theme1.xml
626085        0x98DA5         Zip archive data, at least v2.0 to extract, compressed size: 1169, uncompressed size: 3604, name: word/settings.xml
627301        0x99265         Zip archive data, at least v2.0 to extract, compressed size: 4315, uncompressed size: 44594, name: word/styles.xml
631661        0x9A36D         Zip archive data, at least v2.0 to extract, compressed size: 376, uncompressed size: 1083, name: word/webSettings.xml
632087        0x9A517         Zip archive data, at least v2.0 to extract, compressed size: 515, uncompressed size: 1749, name: word/fontTable.xml
632650        0x9A74A         Zip archive data, at least v2.0 to extract, compressed size: 358, uncompressed size: 727, name: docProps/core.xml
633319        0x9A9E7         Zip archive data, at least v2.0 to extract, compressed size: 374, uncompressed size: 715, name: docProps/app.xml

WARNING: One or more files failed to extract: either no utility was found or it's unimplemented

# Extract mỗi file bin 
$ unzip -p "Team_5_-_Inject_72725.docx" "word/embeddings/oleObject1.bin" > oleObject1.bin
```

---

## Phân tích

Mình sẽ phân tích file `oleObject1.bin` bằng `strings` để xem nó có chứa những chuỗi nào đáng nghi không

```bash
$ strings oleObject1.bin 
OLE Package
Package
C:\Users\ardy\Downloads\vro
C:\Users\ardy\AppData\Local\Temp\{016E985C-CACE-4FD5-BE62-7088A89D6E7F}\{07D47D53-4E54-46B2-9C7A-31322E56717A}\vro
Zmhhe2cweXJfZzB5cl96bF9vM3kwaTNxIX0=
```

Nhận thấy nó có một đoạn mã base64

```bash
$ echo 'Zmhhe2cweXJfZzB5cl96bF9vM3kwaTNxIX0=' | base64 -d
fha{g0yr_g0yr_zl_o3y0i3q!}
```

Quan sát có thể thấy Flag đã bị mã hóa, sử dụng [kt.gy](https://kt.gy/) để giải mã

---

## Flag

**Flag:** `sun{t0le_t0le_my_b3l0v3d!}`
