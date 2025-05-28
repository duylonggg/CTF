# Write Up

## 1. Phân tích file

Chúng ta sẽ thử phân tích file `.E01` bằng lệnh `ewwfinfo`

```bash
$ ewfinfo CorruptedDiskImage.E01
ewfinfo 20140814

Acquiry information
        Case number:
        Description:            untitled
        Examiner name:
        Evidence number:
        Notes:
        Acquisition date:       Sun Mar 31 13:10:51 2024
        System date:            Sun Mar 31 13:10:51 2024
        Operating system used:  Win 201x
        Software version used:  ADI4.7.1.2
        Password:               N/A

EWF information
        File format:            FTK Imager
        Sectors per chunk:      64
        Compression method:     deflate
        Compression level:      no compression

Media information
        Media type:             fixed disk
        Is physical:            no
        Bytes per sector:       512
        Number of sectors:      444416
        Media size:             217 MiB (227540992 bytes)

Digest hash information
        MD5:                    9d10c8709009799b8fba23d47c37dc05
        SHA1:                   d58822075487d541b90ebbe3d4d051d4f942a31f
```

Chuyển file `.E01` thành dạng `raw` hoặc `dd`

```bash
$ ewfexport CorruptedDiskImage.E01
```

Kiểm tra file `raw`

```bash
$ file CorruptedDiskImage.raw
CorruptedDiskImage.raw: data
```

Nhận thấy đây chỉ là 1 file data

Vây rất có khả năng file đã bị hỏng

---

## 2. Chỉnh sửa 

Mở file `CorruptedDiskImage.raw` bằng `HxD`

Chúng ta sẽ nhận thấy sector đầu của file toàn ký tự lạ

Thông thường sector cuối cùng sẽ lưu bản sao để phục hồi file

Chúng ta kéo xuống dưới và thấy magicbyte là `EB 52 90 4E 54 46 53` tức `ëR.NTFS`

1 dạng hệ thống file

Ta copy chúng và dán lên phần đầu

---

## 3. Mở file

```bash
$ fls -o 0 CorruptedDiskImage.raw
r/r 4-128-1:    $AttrDef
r/r 8-128-2:    $BadClus
r/r 8-128-1:    $BadClus:$Bad
r/r 6-128-4:    $Bitmap
r/r 7-128-1:    $Boot
d/d 11-144-4:   $Extend
r/r 2-128-1:    $LogFile
r/r 0-128-6:    $MFT
r/r 1-128-1:    $MFTMirr
r/r 9-128-8:    $Secure:$SDS
r/r 9-144-11:   $Secure:$SDH
r/r 9-144-5:    $Secure:$SII
r/r 10-128-1:   $UpCase
r/r 10-128-4:   $UpCase:$Info
r/r 3-128-3:    $Volume
r/r 38-128-3:   DO_NOT_READ_THIS.png
r/r 39-128-1:   keyFile
d/d 36-144-1:   System Volume Information
V/V 256:        $OrphanFiles
```

Chúng ta thấy 2 file là `DO_NOT_READ_THIS.png` và `keyFile`

Lưu 2 file này về

```bash
$ icat -o 0 CorruptedDiskImage.raw 38 > DO_NOT_READ_THIS.png
$ icat -o 0 CorruptedDiskImage.raw 39 > keyFile
```

Mở file ảnh lên thì thấy flag là file `keyfile` được mã hóa bằng mã hóa sha256

Vậy chúng ta sẽ giải mã

```bash
$ sha256sum keyFile
e71e2b1230fd090aebd3a347310acac611e0161684fb4b7703135b6cc91bb7ac  keyFile
```

---

## 4. Flag

DH{e71e2b1230fd090aebd3a347310acac611e0161684fb4b7703135b6cc91bb7ac}
