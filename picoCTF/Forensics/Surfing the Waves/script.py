from scipy.io import wavfile
rate, data = wavfile.read("main.wav")

# 1) Gom buckets qua 2 chữ số đầu
buckets = [int(str(x)[:2]) for x in data]

# 2) Tạo danh sách 16 mức và sắp xếp
levels = sorted(set(buckets))

# 3) Ánh xạ bucket → hex digit
hex_digits = [hex(levels.index(b))[2:] for b in buckets]

# 4) Decode thành flag
flag = bytearray.fromhex("".join(hex_digits)).decode()
print(flag)
