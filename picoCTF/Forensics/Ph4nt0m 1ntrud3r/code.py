import base64

with open("out.txt", "r") as f:
    lines = [line.strip() for line in f.readlines()]

# Giải mã từng dòng từ hex → bytes → base64 decode
output = b''
for line in lines:
    hex_bytes = bytes.fromhex(line)
    output += base64.b64decode(hex_bytes)

print(output)
