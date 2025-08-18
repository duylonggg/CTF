# Write Up

## Script

```python
def decode_extended(s):
    out = []
    for ch in s:
        cp = ord(ch)
        # chuẩn Mahjong gốc 0x1F000..0x1F02F
        if 0x1F000 <= cp <= 0x1F02F:
            out.append(hex(cp))
        # extended B 0x1F030..1F09F
        elif 0x1F030 <= cp <= 0x1F09F:
            out.append(f"Ext-{hex(cp)}")
        # extended khác
        elif 0x1F060 <= cp <= 0x1F0AF:
            out.append(f"EB-{hex(cp)}")
        else:
            out.append("?")
    return " ".join(out)

# Test với dãy bạn gửi
s = "🁳🁣🁲🁩🁰🁴🁃🁔🁆🁻🀳🁭🀰🁪🀱🁟🀳🁮🁣🀰🁤🀱🁮🁧🁟🀱🁳🁟🁷🀳🀱🁲🁤🁟🀴🁮🁤🁟🁦🁵🁮🀡🀱🁥🀴🀶🁤🁽"
print(decode_extended(s))
```

```python
tiles = [
0x1f073,0x1f063,0x1f072,0x1f069,0x1f070,0x1f074,
0x1f043,0x1f054,0x1f046,0x1f07b,0x1f033,0x1f06d,
0x1f030,0x1f06a,0x1f031,0x1f05f,0x1f033,0x1f06e,
0x1f063,0x1f030,0x1f064,0x1f031,0x1f06e,0x1f067,
0x1f05f,0x1f031,0x1f073,0x1f05f,0x1f077,0x1f033,
0x1f031,0x1f072,0x1f064,0x1f05f,0x1f034,0x1f06e,
0x1f064,0x1f05f,0x1f066,0x1f075,0x1f06e,0x1f021,
0x1f031,0x1f065,0x1f034,0x1f036,0x1f064,0x1f07d
]

out = ""
for cp in tiles:
    y = cp & 0xFF  # lấy byte cuối
    # map cơ bản 0x30..0x39 = 0-9, 0x3A.. = chữ
    if 0x30 <= y <= 0x39:
        out += str(y-0x30)
    elif 0x3A <= y <= 0x5A:
        out += chr(y)   # hoặc chr(y-0x37) nếu muốn hex
    elif y == 0x5F:  # dấu gạch dưới
        out += "_"
    else:
        out += f"[{hex(y)}]"

print(out)
```

---

## Flag

Flag: scriptCTF{3m0j1_3nc0d1ng_1s_w31rd_4nd_fun!1e46d}