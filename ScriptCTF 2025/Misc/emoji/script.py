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