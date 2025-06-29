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

