# Write Up

## 1. Phát hiện các giao dịch lạ

Mở file poisoned_ledger.json, ta thấy chỉ có một vài block chứa trường op_return thay vì data. Đó chính là nơi ta sẽ tìm payload:

```json
...
  {
    "block": 101,
    "transactions": [
      { "txid": "tx10101",
        "op_return": [0,6,17,7,1,57,0,14,114,1]
      }
    ]
  },
...
  {
    "block": 108,
    "transactions": [
      { "txid": "tx10801",
        "op_return": [9,29,1,10,3,11,44,29,6,55]
      }
    ]
  },
...
  {
    "block": 117,
    "transactions": [
      { "txid": "tx11701",
        "op_return": [47,18,29,115,119,29,4,55,44,44,27,63]
      }
    ]
  },
...
```

## 2. Xác định phép giải mã

Phát hiện “tác giả” đã dùng phép XOR mỗi byte với giá trị 66 (chữ ‘B’ trong ASCII):

```txt
plain_byte = cipher_byte XOR 66
```

Mục tiêu là giải ra chuỗi ký tự rõ ràng.

## 3. Script

```python
#!/usr/bin/env python3
import json
import sys

def main(path):
    # 1. Load JSON blockchain
    with open(path, 'r', encoding='utf-8') as f:
        ledger = json.load(f)

    # 2. Thu thập tất cả op_return
    payload = []
    for block in ledger.get('chain', []):
        for tx in block.get('transactions', []):
            if 'op_return' in tx:
                payload.extend(tx['op_return'])

    # 3. Giải mã XOR với 66
    decoded = ''.join(chr(b ^ 66) for b in payload)

    print("Recovered Flag:", decoded)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} poisoned_ledger.json")
        sys.exit(1)
    main(sys.argv[1])
```

## 4. Flag

BDSEC{BL0CK_CHAIn_DumP_15_FunnY}