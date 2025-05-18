# Write Up

Đọc file HTML:

```html
<h1>EUg5MJAyYJ9fYJ5iMKqio29iVK1VL2WlnTM0o3AyL2Elq3q3qlRu</h1>
<h2>Rail Fence → Base64 → ROT13</h2>
<h3>Have Fun</h3>
```

Vậy chúng ta sẽ giải mã ngược lại từng bước 1:

```python
import codecs
import base64

rot13_decoded = codecs.decode("EUg5MJAyYJ9fYJ5iMKqio29iVK1VL2WlnTM0o3AyL2Elq3q3qlRu", 'rot_13')
decoded = base64.b64decode(rot13_decoded)
print(decoded.decode(errors="ignore"))
```

Sau đó lên web `https://tools.dreamhack.games/cyberchef`
Tìm kiếm `Rail Fence Cipher Decode`

Flag: DH{cyberchef-tools-encoderwwowowowo!!!}
