# Write-Up: Mob psycho - picoCTF

**Thể loại:** Forensics  
**Mức độ:** Khó  
**Tác giả:** Hà Duy Long - AT02 - PTIT

---

# Mô tả

Phân tích file .apk

---

# Các bước thực hiện

1. **Giải nén file apk**
   ```bash
   unzip mobpsycho.apk
   ```

2. **Tìm kiếm**
   ```bash
   strings * | grep flag
   ```

   Bạn sẽ tìm được 1 file `flag.txt` nằm trong folder `res/color/flag.txt`
    Đọc dữ liệu trong file `flag.txt`
    ```bash
    cat res/color/flag.txt
    ```

3. **Flag**
   picoCTF{ax8mC0RU6ve_NX85l4ax8mCl_85dbd215}