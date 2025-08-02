import string

ALPHA = string.ascii_uppercase

def vigenere_decrypt(ct: str, key: str) -> str:
    """
    Standard A→Z Vigenère decryption (no digits in key).
    """
    pt = []
    ki = 0
    for c in ct:
        if c in ALPHA:
            shift = ALPHA.index(key[ki % len(key)])
            pt_idx = (ALPHA.index(c) - shift) % 26
            pt.append(ALPHA[pt_idx])
            ki += 1
        else:
            pt.append(c)
    return "".join(pt)

if __name__ == "__main__":
    lvl1 = "UIGHOAGUULYCLEFDOMDVZEEJZPURUDLRKPPBFQFTGHWVZPAAICNVAZCQSXQDT"
    print("Level 1 result:", lvl1)

    # First pass with key = LEVELONE
    after_level_one = vigenere_decrypt(lvl1, "LEVELONE")
    print("After decrypt with LEVELONE:", after_level_one)

    # Second pass with key = LEVELTWO
    final_plain = vigenere_decrypt(after_level_one, "LEVELTWO")
    print("After decrypt with LEVELTWO:", final_plain)

