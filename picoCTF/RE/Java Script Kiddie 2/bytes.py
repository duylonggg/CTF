bytes_list = [252, 127, 185, 254, 13, 114, 103, …, 96, 141, 140]  # dán đầy đủ vào đây
data = bytes(bytes_list)
with open('out2.png', 'wb') as f:
    f.write(data)
