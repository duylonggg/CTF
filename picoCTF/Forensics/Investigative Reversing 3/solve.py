import sys

def extract_flag(encoded_path):
    with open(encoded_path, 'rb') as f:
        data = f.read()

    idx = 723

    flag_bytes = []
    for j in range(100):
        if j % 2 == 1:
            idx += 1
        else:
            c = 0
            for bit_pos in range(8):
                bit = data[idx] & 1
                c |= (bit << bit_pos)
                idx += 1
            flag_bytes.append(c)

    flag = bytes(flag_bytes).split(b'\x00',1)[0]  
    try:
        return flag.decode('utf-8', errors='replace')
    except:
        return flag

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} encoded.bmp")
        sys.exit(1)

    flag = extract_flag(sys.argv[1])
    print("Recovered flag:", flag)
