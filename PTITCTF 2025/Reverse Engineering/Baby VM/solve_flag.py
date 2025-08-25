# solve_flag_v2.py
import re, sys, pathlib

KEY = b"virtualmachine"  # sha256 = da985b0995...ee55f

# ---- đọc file decompile để lấy mảng `data` ----
src_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "chall_src.py")
txt = src_path.read_text(encoding="utf-8", errors="ignore")

m = re.search(r"\bdata\s*=\s*\[(.*?)\]", txt, re.S)
if not m:
    raise SystemExit("Không tìm thấy mảng `data = [...]` trong file nguồn.")
nums = list(map(int, re.findall(r"-?\d+", m.group(1))))

# XOR giải mã bytecode
for i in range(len(nums)):
    nums[i] ^= KEY[i % len(KEY)]

# ---- VM opcodes (từ chall.py) ----
PUSH_IMM,PUSH_R1,PUSH_R2 = 161,162,163
POP_R1,POP_R2            = 177,178
ADD_R1,ADD_R2            = 81, 82
SUB_R1,SUB_R2            = 97, 98
XOR_R1,XOR_R2            = 113,114
MUL_R1,MUL_R2            = 129,130
CMP_EQ,NOP               = 144,105

def run_segment(start_ip, c):
    # Đã qua POP_R1 nên reg1 = c, stack cục bộ rỗng
    r1 = c
    r2 = 0
    st = []
    ip = start_ip
    while ip < len(nums):
        op = nums[ip]; ip += 1
        if op == PUSH_IMM:
            v = nums[ip]; ip += 1; st.append(v)
        elif op == PUSH_R1: st.append(r1)
        elif op == PUSH_R2: st.append(r2)
        elif op == POP_R1:  # nghĩa là block kế (ký tự tiếp theo) -> quay lại
            return None, ip-1, False
        elif op == POP_R2:  r2 = st.pop()
        elif op == ADD_R1:  r1 += st.pop()
        elif op == ADD_R2:  r2 += st.pop()
        elif op == SUB_R1:  r1 -= st.pop()
        elif op == SUB_R2:  r2 -= st.pop()
        elif op == XOR_R1:  r1 ^= st.pop()
        elif op == XOR_R2:  r2 ^= st.pop()
        elif op == MUL_R1:  r1 *= st.pop()
        elif op == MUL_R2:  r2 *= st.pop()
        elif op == CMP_EQ:  return (r1 == r2), ip, True
        elif op == NOP:     pass
        else:               return None, ip, False
    return None, ip, False

def solve():
    ip = 0
    out_rev = []
    while ip < len(nums):
        if nums[ip] == POP_R1:
            ip += 1  # chạy từ sau POP_R1
            found = False
            # thử ASCII in được trước, rồi đến 0..255
            for c in list(range(32,127)) + list(range(256)):
                ok, endip, got = run_segment(ip, c)
                if got and ok:
                    out_rev.append(c)
                    ip = endip
                    found = True
                    break
                if not got:
                    break
            if not found:
                raise SystemExit(f"Unsolved at ip={ip}")
        else:
            ip += 1
    out_rev.reverse()
    return "".join(map(chr, out_rev))

flag = solve()
print(flag)
