# Write-Up: endianness-v2 - picoCTF

**Thể loại:** Forensics  
**Mức độ:** Vừa   
**Tác giả:** Hà Duy Long - AT02 - PTIT

---

# Mô tả

Phân tích file 

---

# Các bước thực hiện

1. **Phân tích file**
   Thử hoán vị 2 bytes liên tiếp với nhau thông qua `code.py`

2. **File**
   Kiểm tra file `swap_dwords.bin` thấy nó là định dạng JPEG
   Đổi nó thành file JPRG

   ```bash
   mv swap_dwords.bin recovered.jpg
   ```

   Mở file JPEG 

   ```bash
   xdg-open recovered.jpg
   ```

3. **Flag**
   picoCTF{cert!f1Ed_iNd!4n_s0rrY_3nDian_b039bc14}