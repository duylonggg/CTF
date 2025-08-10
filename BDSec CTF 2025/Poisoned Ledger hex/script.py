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

