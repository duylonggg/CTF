from PIL import Image
import os

# Cài đặt số mảnh muốn cắt (ví dụ: 10 mảnh)
NUM_SLICES = 10

# Mở ảnh gốc
img = Image.open("concat_v.png")
width, height = img.size

# Tính chiều cao mỗi mảnh
slice_height = height // NUM_SLICES
if height % NUM_SLICES != 0:
    slice_height += 1  # Đảm bảo bao hết ảnh nếu không chia hết

# Cắt và lưu từng mảnh trong thư mục hiện tại
for i in range(NUM_SLICES):
    y0 = i * slice_height
    y1 = min((i + 1) * slice_height, height)
    if y0 >= height:
        break
    cropped = img.crop((0, y0, width, y1))
    out_name = f"slice_{i:02d}.png"
    cropped.save(out_name)
    print(f"Saved {out_name} (y0={y0}, y1={y1})")

