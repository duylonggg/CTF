# Write Up

Kiểm tra file

```bash
$ file whitepages.txt
whitepages.txt: Unicode text, UTF-8 text, with very long lines (1376), with no line terminators
```

Thấy dòng rất dài 

Thử kiểm tra byte của file

```bash
$ cat whitepages.txt | head -c 200 | hexdump -C
00000000  e2 80 83 e2 80 83 e2 80  83 e2 80 83 20 e2 80 83  |............ ...|
00000010  20 e2 80 83 e2 80 83 e2  80 83 e2 80 83 e2 80 83  | ...............|
00000020  20 e2 80 83 e2 80 83 20  e2 80 83 e2 80 83 e2 80  | ...... ........|
00000030  83 e2 80 83 20 e2 80 83  e2 80 83 20 e2 80 83 20  |.... ...... ... |
00000040  20 20 e2 80 83 e2 80 83  e2 80 83 e2 80 83 e2 80  |  ..............|
00000050  83 20 20 e2 80 83 20 e2  80 83 e2 80 83 20 e2 80  |.  ... ...... ..|
00000060  83 20 20 e2 80 83 e2 80  83 e2 80 83 20 20 e2 80  |.  .........  ..|
00000070  83 20 20 e2 80 83 20 20  20 20 e2 80 83 20 e2 80  |.  ...    ... ..|
00000080  83 e2 80 83 e2 80 83 e2  80 83 20 20 e2 80 83 20  |..........  ... |
00000090  e2 80 83 20 e2 80 83 20  e2 80 83 e2 80 83 e2 80  |... ... ........|
000000a0  83 20 e2 80 83 e2 80 83  e2 80 83 20 20 e2 80 83  |. .........  ...|
000000b0  e2 80 83 e2 80 83 e2 80  83 e2 80 83 20 e2 80 83  |............ ...|
000000c0  20 e2 80 83 e2 80 83 e2                           | .......|
000000c8
```

Ta nhận thấy đây là dạng `EM Space` do byte `e2 80 83` 

Dùng `script.py` để giải mã

```python
def convertSpacesToBinary():
    with open('whitepages.txt', 'rb') as f:
        result = f.read()
    result = result.replace(b'\xe2\x80\x83', b'0')  # Unicode EM SPACE -> 0
    result = result.replace(b'\x20', b'1')  # ASCII Space -> 1
    result = result.decode()
    return result

def convertFromBinaryToASCII(binaryValues):
    binary_int = int(binaryValues, 2)
    byte_number = (binary_int.bit_length() + 7) // 8
    binary_array = binary_int.to_bytes(byte_number, "big")
    ascii_text = binary_array.decode('ascii')
    print(ascii_text)

convertFromBinaryToASCII(convertSpacesToBinary())
```

Chạy `script.py`

```bash
$ python3 script.py

                picoCTF

                SEE PUBLIC RECORDS & BACKGROUND REPORT
                5000 Forbes Ave, Pittsburgh, PA 15213
                picoCTF{not_all_spaces_are_created_equal_c54f27cd05c2189f8147cc6f5deb2e56}

```
