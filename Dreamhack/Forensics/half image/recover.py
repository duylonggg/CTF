from PIL import Image
from io import BytesIO

# 1. Đọc toàn bộ file corrupted
with open('flag.png', 'rb') as f:
    data = f.read()

# 2. Tìm vị trí kết thúc chunk IEND
#    IEND chunk format: 4-byte length (0x00 00 00 00) + b'IEND' + 4-byte CRC
iend_pos = data.find(b'\x00\x00\x00\x00IEND')
if iend_pos == -1:
    raise ValueError("Không tìm thấy chunk IEND trong flag.png")
iend_end = iend_pos + 8  # 4-byte length + 4-byte 'IEND'
iend_end += 4            # + 4-byte CRC

# 3. Tách phần PNG (left) và phần raw RGB (right)
png_bytes = data[:iend_end]
rgb_bytes = data[iend_end:]

# 4. Mở ảnh left từ bytes
left_img = Image.open(BytesIO(png_bytes))
w_left, h = left_img.size

# 5. Kích thước nửa phải (width phải = width trái = w_left)
w_right = w_left

# 6. Kiểm tra độ dài rgb_bytes có khớp w_right*h*3 không
expected_len = w_right * h * 3
if len(rgb_bytes) != expected_len:
    raise ValueError(f"Dữ liệu RGB sai kích thước: có {len(rgb_bytes)} bytes, nhưng cần {expected_len}")

# 7. Tạo ảnh right từ raw RGB
right_img = Image.frombytes('RGB', (w_right, h), rgb_bytes)

# 8. Kết hợp hai nửa
full = Image.new('RGB', (w_left + w_right, h))
full.paste(left_img,  (0, 0))
full.paste(right_img, (w_left, 0))

# 9. Lưu kết quả
left_img.save('recovered_left.png')
right_img.save('recovered_right.png')
full.save('recovered_full.png')

print("Đã khôi phục:\n - recovered_left.png\n - recovered_right.png\n - recovered_full.png")

