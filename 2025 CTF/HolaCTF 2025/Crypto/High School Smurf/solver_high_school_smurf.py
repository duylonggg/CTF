# High School Smurf — solver scaffold
# See README in the header of this file (docstring below) for how to use.

"""
Usage
=====
1) Run the remote instance once. Copy the printed 3 lines (each: x, y, dx, dy)
   and the printed final point (Ex, Ey). Keep the same instance while solving.
2) `pip install z3-solver sympy`
3) Run: `python3 solver_high_school_smurf.py`, paste the numbers when prompted.
4) It will first try an exact integer solve with Z3 using polynomial equal-distance
   constraints (works surprisingly well). If that fails, it uses a numerical fallback.

Theory
======
Let L1, L2, L3 be the three fixed lines:
  Li(t) = (xi + dxi * t, yi + dyi * t).
The server picks secret 32-bit ints (i, j, k), forms P1=L1(i), P2=L2(j), P3=L3(k),
and prints one excenter of triangle ΔP1P2P3:
  For some choice among the three excenters,
    E = (-a*P1 + b*P2 + c*P3)/(-a+b+c), etc., where
      a = |P2P3|, b = |P1P3|, c = |P1P2|.
Key property: an incenter/excenter E is equidistant from all three (or their
extensions) sides. If d(X, AB) denotes the perpendicular distance from X to
the line through A,B, then:
  d(E, P1P2) = d(E, P1P3) = d(E, P2P3).
Squaring and clearing denominators yields two polynomial equations in i,j,k:
  (cross(E-P1, P2-P1))^2 * |P3-P1|^2 = (cross(E-P1, P3-P1))^2 * |P2-P1|^2
  (cross(E-P1, P2-P1))^2 * |P3-P2|^2 = (cross(E-P2, P3-P2))^2 * |P2-P1|^2
These, combined with 0 <= i,j,k < 2^32, are strong enough for Z3 in practice.

If Z3 fails (rare), the fallback tries numerical solving with SymPy's `nsolve`
for [Ex, Ey] plus one of the equal-distance equations, random restarts, and then
rounds to the nearest integers and re-verifies.
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
import sys, math, random

try:
    from z3 import Int, Real, Solver, sat
    Z3_OK = True
except Exception:
    Z3_OK = False

from fractions import Fraction
import sympy as sp

@dataclass
class Line:
    x: sp.Number
    y: sp.Number
    dx: sp.Number
    dy: sp.Number

@dataclass
class Instance:
    lines: List[Line]
    E: Tuple[sp.Number, sp.Number]  # excenter (x,y) printed by server

def parse_decimal(s: str) -> sp.Number:
    try:
        return sp.nsimplify(s, rational=True)
    except Exception:
        return sp.N(s)

def read_instance_from_stdin() -> Instance:
    print("Paste the 3 lines as 4 comma-separated decimals per line: x, y, dx, dy")
    lines: List[Line] = []
    for idx in range(3):
        raw = input(f"Line {idx+1} (x, y, dx, dy): ").strip()
        parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
        if len(parts) != 4:
            print("✖ Expected exactly 4 numbers. Try again.", file=sys.stderr)
            sys.exit(1)
        x, y, dx, dy = [parse_decimal(p) for p in parts]
        lines.append(Line(x, y, dx, dy))

    rawE = input("Excenter point printed (Ex, Ey): ").strip()
    parts = [p.strip() for p in rawE.replace(",", " ").split() if p.strip()]
    if len(parts) != 2:
        print("✖ Expected exactly 2 numbers for Ex, Ey.", file=sys.stderr)
        sys.exit(1)
    Ex, Ey = [parse_decimal(p) for p in parts]
    return Instance(lines=lines, E=(Ex, Ey))

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
    P2 = (L2.x + L2.dx*J, L2.y + L2.dy*J)
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
        rmod = random.choice([16,32,64,128,256,512,1024])
        s.add((var % rmod) == random.randrange(0, rmod))
    if s.check() != sat:
        return None
    m = s.model()
    return (int(str(m[I])), int(str(m[J])), int(str(m[K])))

def recompute_and_check(i,j,k, inst: Instance) -> float:
    I,J,K = sp.Integer(i), sp.Integer(j), sp.Integer(k)
    best = 1e100
    for which in [0,1,2]:
        ex, ey = excenter_xy_sym(I,J,K, inst.lines, which)
        err = float(abs(sp.N(ex - inst.E[0], 60)) + abs(sp.N(ey - inst.E[1], 60)))
        best = min(best, err)
    return best

def main():
    print("=== High School Smurf — solver ===")
    inst = read_instance_from_stdin()

    sol = z3_solve(inst)
    if sol:
        i,j,k = sol
        err = recompute_and_check(i,j,k, inst)
        print(f"[Z3] candidate (i,j,k) = {sol} | repro error = {err:.3e}")
        if err < 1e-6:
            print("[✓] Verified. Submit these indices.")
            return
        else:
            print("[!] Z3 candidate didn't verify. Try rerunning or adjust random hints.")

    print("[*] Numeric fallback (SymPy nsolve)")
    I,J,K = sp.symbols('I J K')
    best = (None, 1e100)
    for which in [0,1,2]:
        ex_sym, ey_sym = excenter_xy_sym(I,J,K, inst.lines, which)
        eq1, _ = equal_distance_polys(I,J,K, inst.lines, inst.E[0], inst.E[1])
        # try multiple random starts
        for _try in range(16):
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
                print(f"  candidate {best[0]}  err={best[1]:.3e}")
                if err < 1e-6:
                    print("[✓] Verified. Submit these indices.")
                    return

    if best[0]:
        print(f"[?] Best candidate found: {best[0]} (repro error={best[1]:.3e})")
    else:
        print("✖ No solution found. Re-run with Z3 installed or increase restarts.")

if __name__ == "__main__":
    main()
