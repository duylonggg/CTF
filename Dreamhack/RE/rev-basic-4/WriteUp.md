# Write Up 

## 1. **IDA**

Sử dụng `IDA` để đọc file `char4.exe`

Tìm đến hàm kiểm tra chuỗi nhập vào.

```c
__int64 __fastcall sub_140001000(__int64 a1)
{
  int i; // [rsp+0h] [rbp-18h]

  for ( i = 0; (unsigned __int64)i < 0x1C; ++i )
  {
    if ( ((unsigned __int8)(16 * *(_BYTE *)(a1 + i)) | ((int)*(unsigned __int8 *)(a1 + i) >> 4)) != byte_140003000[i] )
      return 0i64;
  }
  return 1i64;
}
```

Ta nhận thấy nó sẽ kiểm tra như sau:

```txt
(a[i] * 16) --> giữ lại 8 bit đầu OR (a[i] >> 4)
```

Vậy ý tưởng của chúng ta sẽ là brute-force dò hết 256 ký tự xem cái nào thỏa mãn cho từng phần tử của mảng `byte_140003000`

## 2. **Script**

```python
data = [
    0x24, 0x27, 0x13, 0xC6, 0xC6, 0x13, 0x16, 0xE6, 0x47, 0xF5,
    0x26, 0x96, 0x47, 0xF5, 0x46, 0x27, 0x13, 0x26, 0x26, 0xC6,
    0x56, 0xF5, 0xC3, 0xC3, 0xF5, 0xE3, 0xE3
]

flag = ''
for i in range(len(data)):
    for val in range(256):
        check = ((val << 4) & 0xFF) | (val >> 4)
        if check == data[i]:
            flag += chr(val)
            break

print("Flag:", flag)
```

## 3. **Flag**

DH{Br1ll1ant_bit_dr1bble_<<_>>}
