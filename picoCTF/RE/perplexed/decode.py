def extract_constant_data():
    import math
    # Các hằng số (số nguyên 64-bit)
    v3 = 0x617B2375F81EA7E1
    v4_0 = 0xD269DF5B5AFC9DB9
    v4_plus7 = 0xF467EDF4ED1BFED2
    # Giả sử v4[1] và v4[2] chưa khởi tạo, nên ta coi chúng là 0 (8 byte mỗi phần tử)
    v4_1 = 0
    v4_2 = 0

    # Sắp xếp dữ liệu trong bộ nhớ theo thứ tự:
    # + v3: 8 byte
    # + v4[0]: 8 byte
    # + v4[1]: 8 byte
    # + v4[2]: 8 byte   => Tổng cộng 32 byte.
    block = bytearray()
    block += v3.to_bytes(8, 'little')
    block += v4_0.to_bytes(8, 'little')
    block += v4_1.to_bytes(8, 'little')
    block += v4_2.to_bytes(8, 'little')
    # Ghi đè 8 byte bắt đầu từ offset (v4 + 7) 
    # v4 nằm ở offset 8, nên offset ghi đè = 8 + 7 = 15
    v4_plus7_bytes = v4_plus7.to_bytes(8, 'little')
    block[15:15+8] = v4_plus7_bytes
    # Lấy 27 byte đầu của block (dữ liệu mẫu được dùng trong hàm check)
    data = block[0:27]
    return data

def extract_flag_from_data(data, flag_length=27):
    # Tổng số bit cần dùng: 27 ký tự x 7 bit = 189 bit.
    # Đọc bitstream từ data: đọc từng byte từ bit 7 (MSB) tới bit 0
    bitstream = []
    for byte in data:
        for i in range(8):
            # Lấy bit theo thứ tự từ MSB đến LSB:
            bit = (byte >> (7 - i)) & 1
            bitstream.append(bit)
    # Nếu bitstream có nhiều hơn 189 bit, ta chỉ lấy 189 bit đầu.
    bitstream = bitstream[:flag_length * 7]
    
    # Chia bitstream thành các nhóm 7 bit liên tiếp
    flag_chars = []
    for i in range(flag_length):
        bits = bitstream[i*7:(i+1)*7]
        # Ghép các bit (bit[0] là bit có trọng số cao nhất)
        val = 0
        for b in bits:
            val = (val << 1) | b
        flag_chars.append(val)
    # Giả sử flag được mã hóa dưới dạng ASCII
    flag = ''.join(chr(c) for c in flag_chars)
    return flag

if __name__ == '__main__':
    data = extract_constant_data()
    flag = extract_flag_from_data(data)
    print("Flag giải được:", flag)
