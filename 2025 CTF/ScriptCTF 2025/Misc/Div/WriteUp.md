# Write Up

## Đọc

Anh em sẽ thấy có dòng kiểm tra logic sau

```python
fl_num = decimal.Decimal(num)
div = secret / fl_num

if div == 0:
    print(open('flag.txt').read().strip())
else:
    print('Try again...')
```

Để `div == 0` thì chỉ có chia cho vô cùng và vô cùng trong module `decimal` của Python là `Infinity`

## Lấy Flag

```bash
$ nc play.scriptsorcerers.xyz 10101
Enter a number: Infinity
scriptCTF{70_1nf1n17y_4nd_b3y0nd_19a0c3c4c3c4}
```

## Flag

Flag: scriptCTF{70_1nf1n17y_4nd_b3y0nd_19a0c3c4c3c4}