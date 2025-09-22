# PEMPEM 🔪 (PTIT CTF 2025)

![alt text](image.png)

## Mục tiêu

Khôi phục **khóa riêng RSA** từ phần thông tin còn sót lại trong `private.pem`, sau đó dùng khóa này để giải mã bản mã trong `ciphertext.txt` và lấy được flag

---

## Phân tích

Trước tiên, ta cần phân tích phần còn lại của `private.pem`. Đây là một khóa riêng RSA dạng PEM (PEM = Base64 của cấu trúc DER ASN.1). Mở tệp cho thấy nội dung Base64 bị cắt cụt (không đầy đủ). Ta tiến hành:

- Giải mã Base64 phần còn lại để thu được chuỗi byte DER
- Phân tích cấu trúc DER: Theo chuẩn PKCS#1, khóa riêng RSA bao gồm một SEQUENCE chứa 9 số nguyên (INTEGER) lần lượt là: `version`, `n` (modulus), `e` (public exponent), `d` (private exponent), `p` (prime1), `q` (prime2), `dP` (exponent1 = d mod (p-1)), `dQ` (exponent2 = d mod (q-1)), `qInv` (coefficient = q^(-1) mod p)

Do khóa đã hỏng nên có thể các trường đầu bị mất, nhưng dựa vào thứ tự, phần cuối của tệp còn lại có khả năng chính là các trường prime2 (`q`) và exponent1 (`dP`) (và có thể một phần của exponent2). Thật vậy, sau khi giải mã Base64:

- Ta nhận thấy xuất hiện 2 số nguyên lớn (ASN.1 INTEGER) liên tiếp với độ dài xấp xỉ bằng một nửa độ dài modulus. Điều này phù hợp với kích thước của prime2 q (~2048 bit) và exponent1 dP (~2048 bit)
- Kiểm tra thêm: `q` thường là số nguyên tố 2048-bit, `dP = d mod (p-1)` cũng có độ lớn tương đương p. Phần DER cho thấy hai số này có độ dài 257 byte (có byte 0x00 đầu do số dương MSB=1) – điều khẳng định đây có thể là q và dP

Như vậy, ta trích xuất được:

- q – giá trị số nguyên tố thứ hai của khóa RSA
- dP = d mod (p-1) – giá trị mũ riêng lẻ cho modulo p

---

## ý tưởng khai thác

Biết được q và dP, ta có thể tìm p dựa trên tính chất của RSA:

Vì $dP = d \bmod (p-1)$, nên tồn tại một số nguyên $k$ sao cho:

```txt
d≡dP(mod(p−1))⟹d=dP+k(p−1)
```

Ta cũng có công thức $e \cdot d \equiv 1 \pmod{\phi(n)}$, trong đó $\phi(n)=(p-1)(q-1)$. Đặc biệt, $e \cdot d \equiv 1 \pmod{(p-1)}$ và $e \cdot d \equiv 1 \pmod{(q-1)}$. Xét modulo $p-1$:

```txt
e⋅d≡1(mod(p−1))
```

Thay $d = dP + k(p-1)$ vào, ta được:

```txt
e⋅dP+ke(p−1)≡1(mod(p−1))⟹e⋅dP≡1(mod(p−1))
```

Do đó:

$(p-1)$ là ước của $(e \cdot dP - 1)$. Nói cách khác, $e \cdot dP - 1 = h \cdot (p-1)$ với một số nguyên $h$ nào đó

Bài toán giờ quy về: Tính $K = e \cdot dP - 1$. Số $K$ này sẽ chia hết cho $p-1$. Nếu ta phân tích thừa số (factor) được $K$, thì một trong các thừa số của $K$ cộng 1 sẽ bằng $p$. Cụ thể, ta tìm một ước số $u$ của $K$ sao cho $u + 1$ là số nguyên tố có độ dài bit phù hợp (~2048 bit) – đó chính là ứng viên cho $p$. Thử lần lượt các thừa số (đặc biệt các thừa số lớn) của $K$ để tìm ra $p$

> **Lưu ý** 
> Trong thực tế, $K$ rất lớn (cỡ 2064 bit). Tuy nhiên, do cấu trúc CRT, $p-1$ thường có các ước số nhỏ từ $e$ hoặc các giá trị liên quan. Ta có thể chia thử (trial division) $K$ cho các số nguyên tố nhỏ và vừa để tách các thừa số nhỏ. Khi loại bỏ hết các thừa số nhỏ, nếu phần còn lại của $K$ (gọi là $K'$) cộng 1 là số nguyên tố lớn, nhiều khả năng đó chính là $p$. (Đây chính là cách tiếp cận trong bài: “chia thử để tìm $p = K/h + 1$ là số nguyên tố”, tức là tìm ước $h$ sao cho $K/h + 1$ prime)

---

## Tính toán khóa riêng

### Bước 1: Tìm $p$ từ $dP$ và $q$

- Từ `private.pem` phân tích, ta thu được:
  - $q$ (một số nguyên ~2048 bit)
  - $dP$ (một số nguyên ~2048 bit)
- Giả sử (đoán) $e = 65537$ (0x10001, một giá trị công khai thường dùng). Thật ra nếu đề bài không cho $e$, ta có thể ngầm định 65537 vì rất phổ biến
- Tính $K = e \cdot dP - 1$
- Thực hiện trial division trên $K$: Chia $K$ lần lượt cho các prime nhỏ. Kết quả tìm được một loạt thừa số nhỏ như: 2, 3, 13, 19, 23, 1789, 12347,... (các giá trị này có thể khác nhau tùy trường hợp cụ thể). Giả sử tập hợp các thừa số nhỏ tìm được là $S$
- Chia hết các thừa số đó, ta thu được phần còn lại $K'$ (rất lớn, cỡ >2000 bit). Kiểm tra $K' + 1$:
  - Nếu $K' + 1$ là số nguyên tố lớn ~2048 bit, thì $p = K' + 1$
  - (Nếu chưa phải, có thể cần tìm tiếp thừa số của $K'$ bằng cách khác, nhưng trong bài này giả sử $K' + 1$ đã là prime)
- Kết quả thu được $p$ (prime1) – số nguyên tố thứ nhất của khóa RSA

### Bước 2: Khôi phục các tham số khóa riêng khác

- Tính $n = p \times q$ (modulus)
- Tính $\phi(n) = (p-1)(q-1)$
- Tính $d$ – exponent riêng đầy đủ: đây là nghịch đảo modulo của $e$ mod $\phi(n)$. Ta dùng thuật toán Euclid mở rộng hoặc hàm thư viện để tìm $d$ thỏa mãn $d \cdot e \equiv 1 \pmod{\phi(n)}$
- Bây giờ đã có $(n, e, d, p, q)$. Ta cũng có thể tính lại $dQ = d \bmod (q-1)$ và $qInv = q^{-1} \bmod p$ để hoàn thiện đủ thông tin khóa RSA (điều này không bắt buộc để giải mã nhưng kiểm tra cho nhất quán)

---

## Giải mã ciphertext

Sau khi có khóa riêng đầy đủ, việc giải mã bản mã RSA trở nên đơn giản. Bản mã `ciphertext.txt` cho dưới dạng một số nguyên lớn (rất dài). Gọi số này là $C$. Flag được mã hóa có thể ở dạng plaintext ASCII hoặc chuỗi byte.

Ta giải mã bằng cách tính:

```txt
M=C^d mod n
```

Trong đó $d$ là khóa riêng vừa tìm được. Kết quả $M$ là bản rõ (plaintext) dưới dạng số nguyên. Đổi $M$ ra chuỗi byte (theo big-endian) sẽ thu được thông điệp gốc

Tùy thuộc vào cách mã hóa, có thể cần loại bỏ padding PKCS#1: Trong RSA, nếu plaintext được padding theo PKCS#1 v1.5, chuỗi byte của $M$ sẽ bắt đầu bằng byte `0x00 0x02`, tiếp theo là các byte padding ngẫu nhiên, một byte `0x00` phân tách, rồi đến dữ liệu thật. Khi đó ta bỏ phần padding trước byte `0x00` thứ hai để lấy dữ liệu thông điệp. Nếu plaintext không padding (ví dụ chỉ chuyển thẳng flag thành số), thì trực tiếp chuyển $M$ thành chuỗi ký tự

---

## Script

```python
from math import gcd

# Đọc và giải mã Base64 từ private.pem (phần còn lại)
import base64
pem_data = open("private.pem", "rb").read()
# Lấy phần Base64 (bỏ header và footer nếu có)
b64_data = pem_data.strip().split(b'\n')
b64_data = b"".join([line for line in b64_data if b'-----' not in line])
der_bytes = base64.b64decode(b64_data)

# Tìm các offset có thể chứa q và dP trong DER (dựa trên độ dài)
# Giả sử đã xác định offset hoặc dùng ASN1 parser,
# ở đây minh họa việc cắt thủ công:
q_bytes = der_bytes[14:271]    # đoạn byte tương ứng q (257 bytes bao gồm 0x00 đầu)
dP_bytes = der_bytes[276:533]  # đoạn byte tương ứng dP (257 bytes bao gồm 0x00 đầu)

# Chuyển sang số nguyên
q = int.from_bytes(q_bytes, byteorder='big')
dP = int.from_bytes(dP_bytes, byteorder='big')

# Đặt e = 65537
e = 65537

# Tính K = e * dP - 1
K = e * dP - 1

# Trial division trên K để tìm thừa số nhỏ
factors = []
temp = K
for prime in [2,3,5,7,11,13,17,19,23,29]:
    while temp % prime == 0:
        factors.append(prime)
        temp //= prime
# (Tiếp tục thử với các prime nhỏ hơn một ngưỡng nào đó,
#  ở đây chỉ minh họa một vài prime đầu tiên)

print("Small factors found:", factors)

# Sau khi loại bỏ thừa số nhỏ, phần còn lại temp có thể là p-1 (hoặc chứa p-1)
remaining = temp
p = None
# Kiểm tra nếu remaining+1 là prime (phương pháp đơn giản: test chia vài prime nhỏ, hoặc Miller-Rabin)
def is_probably_prime(n, k=10):
    # Miller-Rabin kiểm tra tính nguyên tố xác suất
    if n < 2: 
        return False
    # thử các prime nhỏ trước
    small_primes = [2,3,5,7,11,13,17,19,23]
    for pr in small_primes:
        if n % pr == 0:
            return n == pr
    # phân tích n-1 = 2^s * r
    r, s = n-1, 0
    while r % 2 == 0:
        s += 1
        r //= 2
    import random
    for _ in range(k):
        a = random.randrange(2, n-1)
        x = pow(a, r, n)
        if x == 1 or x == n-1:
            continue
        for _ in range(s-1):
            x = pow(x, 2, n)
            if x == n-1:
                break
        else:
            return False
    return True

if is_probably_prime(remaining + 1):
    p = remaining + 1
    print("Found p:", p)
else:
    # Nếu chưa prime, có thể cần factor tiếp (sử dụng tool ECM, etc.)
    # ... (phần này tùy trường hợp, bài này giả sử remaining+1 là prime)
    pass

# Tính các tham số khóa RSA khác
n = p * q
phi = (p - 1) * (q - 1)
# Tính d (modular inverse của e mod phi)
# Python 3.8+ có pow với đối số -1 để tìm nghịch đảo mod
d = pow(e, -1, phi)
print("Recovered d (private exponent):", d)

# Giải mã ciphertext
with open("ciphertext.txt", "r") as f:
    C = int(f.read().strip())   # ciphertext dưới dạng số

M = pow(C, d, n)                # giải mã M = C^d mod n
# Chuyển M thành bytes (độ dài bằng kích thước modulus)
plaintext_bytes = M.to_bytes((n.bit_length()+7)//8, 'big')

# Nếu có padding PKCS#1, tìm vị trí 0x00 phân cách
if plaintext_bytes[0] == 0 and plaintext_bytes[1] == 2:
    # Tìm byte 0 thứ hai
    sep_index = plaintext_bytes.find(b'\x00', 2)
    message = plaintext_bytes[sep_index+1:]
else:
    # Không padding, loại bỏ các byte 0 đầu (nếu có)
    message = plaintext_bytes.lstrip(b'\x00')

print("Decrypted message bytes:", message)
print("Decrypted message (ASCII):", message.decode('utf-8', errors='ignore'))
```

---

## Flag

Flag: `PTITCTF{Pr1v4t3_K3y_G3n3r4t10n_1s_Fun!}`