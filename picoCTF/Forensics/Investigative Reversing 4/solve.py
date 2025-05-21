import sys
import os

def extract_from_file(path, start_flag_index):
    """
    Đọc một file *_cp.bmp, bỏ qua 2019 byte đầu, rồi trên 50 vòng j=0..49:
      - nếu j % 5 == 0: nhúng 8 bit -> 1 byte flag
      - ngược lại: bỏ qua 1 byte
    Trả về (list_of_bytes, next_flag_index)
    """
    with open(path, 'rb') as f:
        data = f.read()

    idx = 2019 
    flag_bytes = []
    flag_index = start_flag_index

    for j in range(50):
        if j % 5 == 0:
            c = 0
            for bit_pos in range(8):
                bit = data[idx] & 1
                c |= (bit << bit_pos)
                idx += 1
            flag_bytes.append(c)
            flag_index += 1
        else:
            idx += 1

    return flag_bytes, flag_index


def main():
    files = [f"Item{n:02}_cp.bmp" for n in range(5, 0, -1)]
    all_flag = []
    flag_idx = 0

    for fn in files:
        if not os.path.exists(fn):
            print(f"[ERROR] File not found: {fn}")
            sys.exit(1)
        part, flag_idx = extract_from_file(fn, flag_idx)
        all_flag.extend(part)

    flag_bytes = bytes(all_flag)
    flag = flag_bytes.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
    print("Recovered flag:", flag)


if __name__ == "__main__":
    main()
