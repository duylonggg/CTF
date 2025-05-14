import struct

# Read the raw file
with open('/mnt/d/Documents/CTF_Lab/picoCTF/Forensics/endianness-v2/challengefile', 'rb') as f:
    data = f.read()

def swap_pairs(data):
    """Swap every pair of bytes"""
    swapped = bytearray()
    for i in range(0, len(data), 2):
        pair = data[i:i+2]
        if len(pair) == 2:
            swapped += pair[::-1]
        else:
            swapped += pair
    return bytes(swapped)

def swap_dwords(data):
    """Within each 4-byte word, reverse byte order"""
    swapped = bytearray()
    for i in range(0, len(data), 4):
        dword = data[i:i+4]
        if len(dword) == 4:
            swapped += dword[::-1]
        else:
            swapped += dword
    return bytes(swapped)

# Generate transformed versions
outputs = {
    'identity': data,
    'swap_pairs': swap_pairs(data),
    'swap_dwords': swap_dwords(data)
}

# Print out the first 16 bytes of each for inspection
for name, d in outputs.items():
    sample = d[:16]
    print(f"{name}: {' '.join(f'{b:02X}' for b in sample)}")

# Save to disk for further manual inspection
for name, d in outputs.items():
    open(f"./{name}.bin", 'wb').write(d)

