# Write Up

## 1. **IDA**

Sử dụng `IDA` để mở file `chall`.

Chúng ta sẽ thấy hàm kiểm tra điều kiện với một số điểm đáng lưu ý sau:

```c
get_rand_num(&v6);
printf("Random number: %#x\n", v6);

printf("Input? ");
__isoc99_scanf("%d", &v7);

snprintf(s, 9uLL, "%08x", v6 ^ v7);
for ( i = 0; i <= 7; ++i )
    s1[i] = s[7 - i];
printf("Result: %s\n", s1);

if ( !strcmp(s1, "a0b4c1d7") )
{
    puts("Congrats!");
    puts((const char *)buf);
}
```

## 2. **Phân tích**

Ban đầu nó sẽ sinh ra 1 số ngẫu nhiên và lưu vào `v6`.

Tiếp đến chúng ta phải nhập vào 1 số và lưu vào `v7`.

Xâu `s = v6 ^ v7`.

Sau đó chúng ta đảo ngược xâu `s` và lưu vào `s1`.

Rồi so sánh `s1` với `a0b4c1d7`.

Tổng quát sẽ là như sau:

```txt
v6 = random_number
v7 = input_number
s = v6 ^ v7
reverse_s = a0b4c1d7 --> Congrats
```

Ngắn gọn lại thì việc chúng ta cần làm sẽ đơn giản chỉ là:

```txt
# Tóm tắt
v6 ^ v7 = 0x7d1c4b0a

# Vậy chúng ta đơn giản là XOR xâu đảo ngược với số ngẫu nhiên
v7 = v6 ^ 0x7d1c4b0a
```

## 3. **Flag**

DH{cc0017076ad93f32c8aaa21bea38af5588d95d2cdc9cf48760381cc84df4668e}
