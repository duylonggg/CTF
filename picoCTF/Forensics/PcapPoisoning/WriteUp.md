# Write-Up: PcapPoisoning - picoCTF

**Thể loại:** Forensics  
**Mức độ:** Vừa   
**Tác giả:** Hà Duy Long - AT02 - PTIT

---

# Mô tả

Phân tích file .pcap 

---

# Các bước thực hiện

1. **Dùng wireshark đọc file .pcap**
   ```bash
   wireshark trace.pcap
   ```

2. **Lọc dữ liệu trong các gói tin bằng filter**
   ```
   frame contains "picoCTF{"
   ```

3. **Flag**
   picoCTF{P64P_4N4L7S1S_SU55355FUL_fc4e803f}