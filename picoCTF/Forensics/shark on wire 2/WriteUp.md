# Write Up

## Phân tích

Ban đầu tôi đã thử `Follow Stream` của hết các giao thức TCP, UDP đến cả ICMPv6 hay ICMPv4 nhưng vẫn không có gì

Vậy thì chứng tỏ nó phải giấu tin ở đâu đó

---

## Điều tra

Khi nhìn vào port đích là 22, nhận thấy port nguồn không cố định, lúc thi 5112, 5097,...

Vậy chứng tỏ port chính là nơi giấu Flag và rất có thể lấy port - 5000 sẽ ra ký tự ở bảng mã ASCII

---

## Scipt

```python
from scapy.all import *

# Đọc file pcap
packets = rdpcap("capture.pcap")

flag = ""

for pkt in packets:
    if pkt.haslayer(UDP):
        udp = pkt[UDP]
        # Kiểm tra port đích là 22 (theo writeup)
        if udp.dport == 22:
            char_code = udp.sport - 5000
            if 0 <= char_code < 128:
                flag += chr(char_code)

print("Extracted flag:", flag)
```

---

## Flag

picoCTF{p1LLf3r3d_data_v1a_st3g0}