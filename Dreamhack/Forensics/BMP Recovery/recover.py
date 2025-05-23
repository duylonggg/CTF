with open('flag.bmp.broken', 'rb') as f:
    data = bytearray(f.read())

total_bytes = 14309622  
header_size = 54  
info_header_size = 40
bitplane_value = 1
bytes_per_pixel = 3 

image_data_size = total_bytes - header_size

num_pixels = image_data_size // bytes_per_pixel

data[0x0] = 0x42
data[0x1] = 0x4D
data[0x2:0x6] = total_bytes.to_bytes(4, byteorder='little')     
data[0xA:0xE] = header_size.to_bytes(4, byteorder='little')
data[0xE:0x12] = info_header_size.to_bytes(4, byteorder='little')     
data[0x1A:0x1C] = bitplane_value.to_bytes(2, byteorder='little')     
data[0x22:0x26] = image_data_size.to_bytes(4, byteorder='little')       


for width in range(1, int(num_pixels**0.5) + 1):
    if num_pixels % width == 0:
        height = num_pixels // width
        data[0x12:0x16] = width.to_bytes(4, byteorder='little')
        data[0x16:0x1A] = height.to_bytes(4, byteorder='little')
        with open(f'flag_{width}.bmp', 'wb') as f:
            f.write(data)
        data[0x12:0x16] = height.to_bytes(4, byteorder='little')
        data[0x16:0x1A] = width.to_bytes(4, byteorder='little')
        with open(f'flag_{height}.bmp', 'wb') as f:
            f.write(data)
