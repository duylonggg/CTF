# Write Up

## 1. **IDA**

Dùng `IDA` để mở `chall3.exe` và tìm đến hàm so sánh xâu `input`

Tìm thấy 1 hàm so sánh tên là `sub140001000`:

```cpp
__int64 __fastcall sub_140001000(__int64 a1)
{
  int i; // [rsp+0h] [rbp-18h]

  for ( i = 0; (unsigned __int64)i < 0x18; ++i )
  {
    if ( byte_140003000[i] != (i ^ *(unsigned __int8 *)(a1 + i)) + 2 * i )
      return 0i64;
  }
  return 1i64;
}
```

Ta thử tìm đến `byte_140003000` xem nó lưu những giá trị gì.

```txt
.data:0000000140003000 byte_140003000  db 49h, 60h, 67h, 74h, 63h, 67h, 42h, 66h, 80h, 78h, 2 dup(69h)
.data:0000000140003000                                         ; DATA XREF: sub_140001000+28↑o
.data:0000000140003000                 db 7Bh, 99h, 6Dh, 88h, 68h, 94h, 9Fh, 8Dh, 4Dh, 0A5h, 9Dh
.data:0000000140003000                 db 45h, 8 dup(0)
```

Đã có đủ thông tin, hãy viết 1 hàm dịch ngược để lấy password.

## 2. **Script**

```python
data = [
    0x49, 0x60, 0x67, 0x74, 0x63, 0x67, 0x42, 0x66,
    0x80, 0x78, 0x69, 0x69, 0x7B, 0x99, 0x6D, 0x88,
    0x68, 0x94, 0x9F, 0x8D, 0x4D, 0xA5, 0x9D, 0x45
]

flag = ''
for i in range(len(data)):
    x = (data[i] - 2 * i) ^ i
    flag += chr(x)

print("Flag:", flag)
```

## 3. **Flag**


DH{I_am_X0_xo_Xor_eXcit1ng}
