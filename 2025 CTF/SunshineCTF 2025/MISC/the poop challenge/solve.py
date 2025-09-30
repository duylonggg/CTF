s = open("poop_challenge.txt","r",encoding="utf-8").read()
ZW = "\u200b"; P = "💩"

def bits_from_line(line):
    parts = line.split(P)
    between = [p.count(ZW) for p in parts[1:-1]]
    trail   = parts[-1].count(ZW)
    return ''.join(str(b) for b in between + [trail])

lines = s.splitlines()
out = ''.join(chr(int(bits_from_line(line), 2)) for line in lines)
print(out)
