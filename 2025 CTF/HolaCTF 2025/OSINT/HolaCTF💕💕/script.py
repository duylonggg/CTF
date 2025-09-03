def vig_dec(s, key):
    r, i = [], 0
    for ch in s:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[i % len(key)].lower()) - 97
            r.append(chr((ord(ch) - base - k) % 26 + base))
            i += 1
        else:
            r.append(ch)
    return ''.join(r)

cipher = "#ohepu://pbd.wysvtlyox.cqf/u/KTylGddAuMn/"
print(vig_dec(cipher, "holactf"))
# -> #https://www.instagram.com/p/DFnlEkyTgBn/
