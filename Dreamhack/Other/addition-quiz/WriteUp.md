# Write Up

## 1. **Phân tích chall.c**

```c
for (int i = 0; i < 50; i++){
    alarm(1);
    num1 = rand() % 10000;
    num2 = rand() % 10000;
    printf("%d+%d=?\n", num1, num2);
    scanf("%d", &inpt);

    if(inpt != num1 + num2){
        printf("Wrong...\n");
        return 0;
    }
} 
```

Ta nhận thấy yêu cầu của bài là gọi ra 2 số ngẫu nhiên num1 và num2, chúng ta cần nhập vào tổng của 2 số đó với thời gian là dưới 1 giây.

Với thiên tài tính nhẩm thì giải chay bài này cũng được.

Nhưng tôi bị ngu nên sẽ làm 1 con code tự động hóa để tính.

---

## 2. **Script**

Chúng ta sẽ sử dụng thư viện `pwn` của Python để kết nối đến server và tự động gửi đáp án.

```python
from pwn import *

p = remote('host3.dreamhack.games', 11792)

for i in range(50):
    line = p.recvline().decode().strip()

    num1_str, num2_expr = line.split('+')
    num2_str = num2_expr.split('=')[0] 
    num1, num2 = int(num1_str), int(num2_str)

    p.sendline(str(num1 + num2))

print(p.recvall().decode())
```

---

## 3. **Flag**

DH{0472d70efbc7fee1de726614d534661e0858541bf26ab992a408de549518ccaf}