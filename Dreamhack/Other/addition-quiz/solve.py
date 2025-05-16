from pwn import *

p = remote('host3.dreamhack.games', 11792)

for i in range(50):
    line = p.recvline().decode().strip()
    print(line)

    num1_str, num2_expr = line.split('+')
    num2_str = num2_expr.split('=')[0] 
    num1, num2 = int(num1_str), int(num2_str)

    p.sendline(str(num1 + num2))

print(p.recvall().decode())

