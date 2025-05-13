def rol(byte, n):
    return ((byte << n) & 0xFF) | (byte >> (8 - n))

def reverse_rol(byte, n):
    return ((byte >> n) & 0xFF) | ((byte & ((1 << n) - 1)) << (8 - n))

def recover_a1():
    byte_140003000 = [0x52, 0xDF, 0xB3, 0x60, 0xF1, 0x8B, 0x1C, 0xB5, 0x57, 0xD1,
                      0x9F, 0x38, 0x4B, 0x29, 0xD9, 0x26, 0x7F, 0xC9, 0xA3, 0xE9,
                      0x53, 0x18, 0x4F, 0xB8, 0x6A, 0xCB, 0x87, 0x58, 0x5B, 0x39,
                      0x1E, 0x0]
    a1 = []
    for i in range(31):
        value = byte_140003000[i]
        recovered_byte = reverse_rol(value ^ i, i & 7)
        a1.append(recovered_byte)
    
    return bytes(a1)

# In ra kết quả
a1_value = recover_a1()
print(a1_value)

