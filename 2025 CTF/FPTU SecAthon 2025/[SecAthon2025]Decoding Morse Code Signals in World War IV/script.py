import string

def vigenere_decrypt_with_digits(ct, key):
    A = string.ascii_uppercase
    pt = []
    ki = 0
    for c in ct:
        if c in A:
            # determine shift
            k = key[ki % len(key)]
            if k.isalpha():
                shift = A.index(k)
            else:
                shift = int(k)
            # decrypt
            idx = (A.index(c) - shift) % 26
            pt.append(A[idx])
            ki += 1
        else:
            pt.append(c)
    return "".join(pt)

ct = "YBEZOMJEUVACNJJWMEDHCOETBPWWYWJJKBSLFAHTIMAOXHAMLMNFCZEVWQOVT"
lvl1 = vigenere_decrypt_with_digits(ct, "ETYSAMDKAK2025")
print("Level 1 result:", lvl1)

