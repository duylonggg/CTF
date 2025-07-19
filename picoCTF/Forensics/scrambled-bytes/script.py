from scapy.all import *
import random

# 1. Đọc pcap
pkts = rdpcap('capture.pcapng')
# 2. Chọn các gói UDP với port đích là 56742 (đổi theo challenge)
pkts = [p for p in pkts if UDP in p and p[UDP].dport == 56742]

# 3. Lấy toàn bộ payload bytes (đã theo thứ tự gửi)
data = bytearray(b''.join(p[UDP][Raw].load for p in pkts))

# 4. Gán seed RNG với int(packets[0].time), theo write‑up
seed = int(pkts[0].time)
random.seed(seed)

# 5. Khôi phục thứ tự shuffle
order = list(range(len(data)))
random.shuffle(order)

# 6. Undo XOR: cần giữ đúng tiến trình RNG như khi gửi
#    và bỏ thêm một randrange(65536) mỗi byte như trong script gốc
for i in range(len(data)):
    random.randrange(65536)
    key = random.randrange(256)
    data[i] ^= key

# 7. Undo shuffle: đặt lại vào vị trí ban đầu
out = bytearray(len(data))
for i, pos in enumerate(order):
    out[pos] = data[i]

# 8. Ghi ra file
with open('recovered.png', 'wb') as f:
    f.write(out)

print(f"File đã tạo: recovered.png")

