mystery   = b"CF{An1_9a47141}`"
mystery2  = bytes([0x85, 0x73])
mystery3  = b"icT0tha_"

flag = [None] * 25

flag[1] = mystery3[0]
flag[0] = mystery2[0] - 0x15
flag[2] = mystery3[1]
flag[3] = mystery2[1] - 4

flag[5] = mystery3[2]
flag[4] = mystery[0]

for i in range(1, 5):
    flag[5 + i] = mystery[i]

for i in range(3, 8):
    flag[7 + i] = mystery3[i]

for i in range(5, 15):
    flag[10 + i] = mystery[i]

print(''.join([chr(c) for c in flag if c is not None]))
