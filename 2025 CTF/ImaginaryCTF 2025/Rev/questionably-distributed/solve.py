# worker.py — 64 luồng “cày” ALU qua TCP
import sys, socket, re, threading

HOST = "127.0.0.1"
if len(sys.argv) < 2:
    print("Usage: python worker.py <PORT> [NWORKERS]")
    sys.exit(1)
PORT = int(sys.argv[1])
NWORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 64

pat = re.compile(r'(-?\d+)\s+(-?\d+)\s*(\^|\+|<<|>>|&|\||-|/|\*)')

def eval_op(a,b,op):
    if   op=='+':  return a+b
    elif op=='-':  return a-b
    elif op=='*':  return a*b
    elif op=='/':  return a//b    # chia nguyên
    elif op=='^':  return a^b
    elif op=='&':  return a&b
    elif op=='|':  return a|b
    elif op=='<<': return a<<b
    elif op=='>>': return a>>b
    else: raise ValueError(op)

def worker():
    s = socket.create_connection((HOST, PORT))
    f = s.makefile('r', encoding='utf-8', errors='ignore')
    while True:
        line = f.readline()
        if not line:
            break
        if 'ictf{' in line:
            print("[FLAG]", line.strip())
            break
        m = pat.search(line)
        if m:
            a,b,op = m.groups()
            ans = str(eval_op(int(a), int(b), op))
            s.sendall((ans+"\n").encode())

threads = [threading.Thread(target=worker, daemon=True) for _ in range(NWORKERS)]
for t in threads: t.start()
for t in threads: t.join()
