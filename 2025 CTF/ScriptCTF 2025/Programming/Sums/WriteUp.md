# Write Up

## Script

```python
from pwn import *

p = remote("play.scriptsorcerers.xyz", 10430)


# Sinh ra mảng nums có n = 123456 số ngẫu nhiên trong khoảng [0, 696969].
# In toàn bộ mảng nums ra stdout (dòng đầu tiên).
# Sinh ra tiếp n truy vấn (l, r) và cũng in ra lần lượt (mỗi dòng 2 số).
# Ghép thành big_input = nums + queries rồi đưa vào chương trình ./solve.
# Kết quả ./solve phải in ra n dòng, mỗi dòng là tổng a[l..r].
# Sau đó server yêu cầu client (mình) nhập vào lại y chang các kết quả đó.
# Nếu giống thì in flag.
# Có time limit 10s.

# Đọc toàn bộ mảng nums
nums = list(map(int, p.recvline().decode().strip().split()))

n = len(nums)
prefix = [0] * (n+1)
for i in range(1, n+1):
    prefix[i] = prefix[i-1] + nums[i-1]

ans = []
for _ in range(n):
    l, r = map(int, p.recvline().decode().strip().split())
    ans.append(str(prefix[r+1] - prefix[l]))

p.sendline("\n".join(ans).encode())

print(p.recvall().decode())
```

---

## Flag

Flag: scriptCTF{1_w4n7_m0r3_5um5_68f0633c7c53}