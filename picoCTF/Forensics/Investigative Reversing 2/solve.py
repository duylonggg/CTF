def extract_flag(encoded_file_path):
    with open(encoded_file_path, "rb") as f:
        f.read(2000)  # bỏ qua phần đầu

        result = []
        for _ in range(50):
            value = 0
            for bit_index in range(8):
                byte = f.read(1)[0]
                lsb = byte & 1
                value |= (lsb << bit_index) 
            result.append((value + 5) & 0xFF) 

        return bytes(result).decode(errors="ignore")

flag = extract_flag("encoded.bmp")
print("Flag:", flag)
