import re, pathlib
p = pathlib.Path('warp').read_bytes()
pos = [m.start() for m in re.finditer(b'\x7fELF', p)]
pos.append(len(p))
for i in range(1, len(pos)):
    open(f'inner_{i-1}.elf','wb').write(p[pos[i-1]:pos[i]])
print("done, files:", [f"inner_{i}.elf" for i in range(len(pos)-1)])