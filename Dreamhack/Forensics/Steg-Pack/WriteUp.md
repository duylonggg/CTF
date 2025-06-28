# Write Up

Đây là 1 bài dạng Steganoraphy

Thử xem có file nào ẩn tron file ảnh không

```bash
$ binwalk flag.png

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 1187 x 490, 8-bit/color RGBA, non-interlaced
91            0x5B            Zlib compressed data, compressed
18048         0x4680          Zip archive data, at least v2.0 to extract, name: App Data/
18087         0x46A7          Zip archive data, at least v2.0 to extract, name: Application Data/
18134         0x46D6          Zip archive data, at least v2.0 to extract, name: Download/
18173         0x46FD          Zip archive data, at least v2.0 to extract, name: E-mail/
18210         0x4722          Zip archive data, at least v2.0 to extract, name: Music/
18246         0x4746          Zip archive data, at least v2.0 to extract, name: Pictures/
18285         0x476D          Zip archive data, at least v2.0 to extract, compressed size: 9918, uncompressed size: 11779, name: Pictures/flag.PNG
28250         0x6E5A          Zip archive data, at least v2.0 to extract, name: Video/
28286         0x6E7E          Zip archive data, at least v2.0 to extract, name: Video/GNS3/
29156         0x71E4          End of Zip archive, footer length: 22
```

extract toàn bộ file ra 

Thấy 1 file ảnh trong Picture

Flag: DH{Picture_iN_fl@g?}
