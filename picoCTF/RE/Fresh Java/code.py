import re

# Mở file chứa Java code
with open("KeygenMe.java") as f:
    data = f.read()

# Tìm tất cả các dòng kiểm tra ký tự
matches = re.findall(r'string\.charAt\((\d+)\) != \'(.)\'', data)

# Tạo một list với 34 ký tự rỗng
key = [''] * 34

# Điền đúng ký tự vào đúng vị trí
for pos, char in matches:
    key[int(pos)] = char

# In ra flag
print("Key:", ''.join(key))

