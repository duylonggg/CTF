from pwn import *

p = process("./dict")
dict_output = p.recvall().decode().rstrip()  # thêm .decode()

encoding_dict = {}
for line in dict_output.split("\n"):
    char, encoding = line.split(": ")
    encoding_dict[encoding] = char

with open("output", "rb") as f:
    data = f.read()
    bin_data = bits_str(data)
    res = ""
    while bin_data:
        for k in encoding_dict:
            if bin_data.startswith(k):
                res += encoding_dict[k]
                bin_data = bin_data[len(k):]
                break   # tránh vòng lặp vô tận
print("Flag:", res)

