#!/usr/bin/env python3
import sys, re, time, random, math, asyncio, threading
from dataclasses import dataclass
from typing import List, Tuple, Optional

import sympy as sp

try:
    from z3 import Int, Real, Solver, sat
    Z3_OK = True
except Exception:
    Z3_OK = False

try:
    import websocket  # websocket-client
except Exception:
    websocket = None

@dataclass
class Line:
    x: sp.Number
    y: sp.Number
    dx: sp.Number
    dy: sp.Number

@dataclass
class Instance:
    lines: List[Line]
    E: Tuple[sp.Number, sp.Number]

def parse_numbers_blob(text: str) -> List[str]:
    # Capture high-precision decimals, possibly with leading minus, dots.
    # Avoid grabbing integers from words like (i j k) by requiring a dot in them.
    # But the server prints with many decimals, so this is fine.
    # Still, allow for integer-like digits too, in case dx/dy are integers; be robust.
    pat = r'[-+]?\d+(?:\.\d+)?'
    return re.findall(pat, text)

def nsimplify_list(vals: List[str]) -> List[sp.Number]:
    out = []
    for v in vals:
        try:
            out.append(sp.nsimplify(v, rational=True))
        except Exception:
            out.append(sp.N(v))
    return out

def excenter_xy_sym(I, J, K, Ls: List[Line], which: int):
    L1, L2, L3 = Ls
    P1 = (L1.x + L1.dx*I, L1.y + L1.dy*I)
    P2 = (L2.x + L2.dx*J, L2.y + L2.dy*J)
    P3 = (L3.x + L3.dx*K, L3.y + L3.dy*K)
    def L2_sq(A,B):
        return (A[0]-B[0])**2 + (A[1]-B[1])**2
    a = sp.sqrt(L2_sq(P2,P3))
    b = sp.sqrt(L2_sq(P1,P3))
    c = sp.sqrt(L2_sq(P1,P2))
    if which == 0:
        den = (-a + b + c)
        ex = (-a*P1[0] + b*P2[0] + c*P3[0]) / den
        ey = (-a*P1[1] + b*P2[1] + c*P3[1]) / den
    elif which == 1:
        den = (a - b + c)
        ex = ( a*P1[0] - b*P2[0] + c*P3[0]) / den
        ey = ( a*P1[1] - b*P2[1] + c*P3[1]) / den
    else:
        den = (a + b - c)
        ex = ( a*P1[0] + b*P2[0] - c*P3[0]) / den
        ey = ( a*P1[1] + b*P2[1] - c*P3[1]) / den
    return sp.simplify(ex), sp.simplify(ey)

def cross(u, v):
    return u[0]*v[1] - u[1]*v[0]

def equal_distance_polys(I,J,K, Ls: List[Line], Ex, Ey):
    L1, L2, L3 = Ls
    P1 = (L1.x + L1.dx*I, L1.y + L1.dy*I)
    P2 = (L2.x + L2.dx*J, L2.y + L2.dy*K*0 + L2.dy*J)  # keep symbols distinct; ensure J used
    P3 = (L3.x + L3.dx*K, L3.y + L3.dy*K)
    E = (Ex, Ey)
    s12 = (P2[0]-P1[0], P2[1]-P1[1])
    s13 = (P3[0]-P1[0], P3[1]-P1[1])
    s23 = (P3[0]-P2[0], P3[1]-P2[1])
    t1E = (E[0]-P1[0], E[1]-P1[1])
    t2E = (E[0]-P2[0], E[1]-P2[1])
    eq1 = sp.expand(cross(t1E, s12)**2 * (s13[0]**2 + s13[1]**2) - cross(t1E, s13)**2 * (s12[0]**2 + s12[1]**2))
    eq2 = sp.expand(cross(t1E, s12)**2 * (s23[0]**2 + s23[1]**2) - cross(t2E, s23)**2 * (s12[0]**2 + s12[1]**2))
    return eq1, eq2

def recompute_and_check(i,j,k, inst: Instance) -> float:
    I,J,K = sp.Integer(i), sp.Integer(j), sp.Integer(k)
    best = 1e100
    for which in [0,1,2]:
        ex, ey = excenter_xy_sym(I,J,K, inst.lines, which)
        err = float(abs(sp.N(ex - inst.E[0], 50)) + abs(sp.N(ey - inst.E[1], 50)))
        best = min(best, err)
    return best

def z3_solve(inst: Instance) -> Optional[Tuple[int,int,int]]:
    if not Z3_OK:
        return None
    I, J, K = Int('I'), Int('J'), Int('K')
    Ex, Ey = inst.E
    ExR, EyR = Real('ExR'), Real('EyR')
    s = Solver()
    s.add(I >= 0, J >= 0, K >= 0, I < 2**32, J < 2**32, K < 2**32)
    s.add(ExR == float(Ex), EyR == float(Ey))
    Isp, Jsp, Ksp = sp.symbols('I J K', integer=True)
    eq1_sp, eq2_sp = equal_distance_polys(Isp, Jsp, Ksp, inst.lines, Ex, Ey)
    from sympy.core import numbers
    def sympy_to_z3(e):
        if isinstance(e, numbers.Integer):
            return int(e)
        if isinstance(e, numbers.Rational):
            return float(e)
        if isinstance(e, numbers.Float):
            return float(e)
        if e == Isp: return I
        if e == Jsp: return J
        if e == Ksp: return K
        op = e.func
        args = [sympy_to_z3(a) for a in e.args]
        if op == sp.Add:
            r = args[0]
            for a in args[1:]: r = r + a
            return r
        if op == sp.Mul:
            r = args[0]
            for a in args[1:]: r = r * a
            return r
        if op == sp.Pow:
            base, exp = args
            return base ** int(float(exp))
        if op == sp.Sub:
            return args[0] - args[1]
        if op == sp.Neg:
            return -args[0]
        raise ValueError(f"Unsupported op {op}")
    eq1_z3 = sympy_to_z3(eq1_sp)
    eq2_z3 = sympy_to_z3(eq2_sp)
    s.add(eq1_z3 == 0, eq2_z3 == 0)
    # helpful random congruence hints
    for var in [I,J,K]:
        rmod = random.choice([32,64,128,256,512,1024])
        s.add((var % rmod) == random.randrange(0, rmod))
    if s.check() != sat:
        return None
    m = s.model()
    return (int(str(m[I])), int(str(m[J])), int(str(m[K])))

def numeric_fallback(inst: Instance) -> Optional[Tuple[int,int,int]]:
    I,J,K = sp.symbols('I J K')
    best = (None, 1e100)
    for which in [0,1,2]:
        ex_sym, ey_sym = excenter_xy_sym(I,J,K, inst.lines, which)
        eq1, _ = equal_distance_polys(I,J,K, inst.lines, inst.E[0], inst.E[1])
        for _try in range(12):
            guess = [random.uniform(0, 1e6), random.uniform(0, 1e6), random.uniform(0, 1e6)]
            try:
                soln = sp.nsolve([ex_sym - inst.E[0], ey_sym - inst.E[1], eq1],
                                 [I,J,K], guess, tol=1e-28, maxsteps=200)
            except Exception:
                continue
            i,j,k = [int(round(float(v))) for v in soln]
            if not (0 <= i < 2**32 and 0 <= j < 2**32 and 0 <= k < 2**32):
                continue
            err = recompute_and_check(i,j,k, inst)
            if err < best[1]:
                best = ((i,j,k), err)
                if err < 1e-6:
                    return best[0]
    return best[0]

def solve_instance(lines_vals: List[sp.Number], E_vals: List[sp.Number]) -> Tuple[int,int,int]:
    lines = [Line(*lines_vals[i*4:(i+1)*4]) for i in range(3)]
    inst = Instance(lines=lines, E=(E_vals[0], E_vals[1]))
    # try z3 then numeric
    sol = z3_solve(inst)
    if sol:
        i,j,k = sol
        err = recompute_and_check(i,j,k, inst)
        if err < 1e-6:
            return sol
    sol = numeric_fallback(inst)
    if sol:
        return sol
    raise RuntimeError("Failed to solve instance quickly.")

def main():
    if websocket is None:
        print("Please: pip install websocket-client")
        sys.exit(1)
    if len(sys.argv) != 2:
        print("Usage: python3 autopwn_high_school_smurf.py 'wss://.../proxy/...'\n"
              "Tip: ensure you have z3-solver and sympy installed for speed.")
        sys.exit(1)
    url = sys.argv[1]

    ws = websocket.WebSocket()
    ws.connect(url, timeout=10)  # proxy should accept without extra headers

    # Read until we think we captured all printed numbers.
    # Then compute and send the answer "i j k".
    buff = ""
    t0 = time.time()
    while True:
        try:
            chunk = ws.recv()
        except Exception as e:
            break
        if isinstance(chunk, (bytes, bytearray)):
            try:
                chunk = chunk.decode('utf-8', 'ignore')
            except Exception:
                chunk = ''
        buff += chunk
        # Heuristic: stop when prompt appears or enough numbers are seen
        if "Can you guess" in buff or len(parse_numbers_blob(buff)) >= 14:
            break

    nums = parse_numbers_blob(buff)
    if len(nums) < 14:
        print("Received text:\n", buff)
        raise SystemExit("Not enough numbers captured.")

    vals = nsimplify_list(nums)
    lines_vals = vals[:12]
    E_vals = vals[12:14]

    print("[*] Parsed parameters:")
    for i in range(3):
        x,y,dx,dy = lines_vals[i*4:(i+1)*4]
        print(f"  L{i+1}: x={x}, y={y}, dx={dx}, dy={dy}")
    print(f"  Excenter: Ex={E_vals[0]}, Ey={E_vals[1]}")

    print("[*] Solving...")
    i,j,k = solve_instance(lines_vals, E_vals)
    print(f"[+] Solution (i j k) = {i} {j} {k}")

    ws.send(f"{i} {j} {k}\n")
    # Read final response
    try:
        time.sleep(0.2)
        out = ws.recv()
        if isinstance(out, (bytes, bytearray)):
            out = out.decode('utf-8', 'ignore')
        print(out)
    except Exception:
        pass

if __name__ == "__main__":
    main()
