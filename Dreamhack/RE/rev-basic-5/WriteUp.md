# Write Up

## 1. **IDA**

Dùng `IDA` để đọc file `chall5.exe`

Tìm hàm kiểm tra xâu nhập vào.

```c
__int64 __fastcall sub_140001000(__int64 a1)
{
  int i; // [rsp+0h] [rbp-18h]

  for ( i = 0; (unsigned __int64)i < 0x18; ++i )
  {
    if ( *(unsigned __int8 *)(a1 + i + 1) + *(unsigned __int8 *)(a1 + i) != byte_140003000[i] )
      return 0i64;
  }
  return 1i64;
}
```

## 2. **Script**

```python
data = [
    0xAD, 0xD8, 0xCB, 0xCB, 0x9D, 0x97, 0xCB, 0xC4, 0x92,
    0xA1, 0xD2, 0xD7, 0xD2, 0xD6, 0xA8, 0xA5, 0xDC, 0xC7,
    0xAD, 0xA3, 0xA1, 0x98, 0x4C, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00
]

flag = None

for first in range(256):
    arr = [first]
    valid = True

    for i in range(len(data)):
        next_bytes = data[i] - arr[-1]

        if (0 <= next_bytes <= 255):
            arr.append(next_bytes)
        else:
            valid = False
            break

    if valid:
        flag = arr
        print(''.join(chr(c) for c in flag))
        break
```

## 3. **Flag**

DH{All_l1fe_3nds_w1th_NULL}
