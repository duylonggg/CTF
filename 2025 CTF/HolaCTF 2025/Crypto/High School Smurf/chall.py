import secrets
from sympy import Float, Point, Triangle, simplify
import signal
import sys
import time

FLAG = "HOLACTF{REDACTED}"
P = 2025

class Line:
    def __init__(self):
        self.x = self._r()
        self.y = self._r()
        self.dx = self._r()
        self.dy = self._r()

    def at(self, t):
        return Point(self.x + self.dx * t, self.y + self.dy * t, evaluate=False)

    def _r(self):
        return -1 + 2 * Float(secrets.randbits(P), P) / (1 << P)
    
def timeout_handler(signum, frame):
    print("Timeout")
    sys.exit(1)

def run():
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(25)
        
        start_time = time.time()
        
        lines = [Line() for _ in range(3)]
        for L in lines:
            print(f'{L.x}, {L.y}, {L.dx}, {L.dy}')
        i, j, k = [secrets.randbits(32) for _ in range(3)]
        tri = Triangle(*[L.at(n) for L, n in zip(lines, [i, j, k])])
        s, v = tri.sides, tri.vertices
        a, b, c = s[1].length, s[2].length, s[0].length
        x, y = [v[i].x for i in range(3)], [v[i].y for i in range(3)]
        exc = {
            s[0]: Point(simplify((-a*x[0]+b*x[1]+c*x[2])/(-a+b+c)), simplify((-a*y[0]+b*y[1]+c*y[2])/(-a+b+c))),
            s[1]: Point(simplify((a*x[0]-b*x[1]+c*x[2])/(a-b+c)), simplify((a*y[0]-b*y[1]+c*y[2])/(a-b+c))),
            s[2]: Point(simplify((a*x[0]+b*x[1]-c*x[2])/(a+b-c)), simplify((a*y[0]+b*y[1]-c*y[2])/(a+b-c)))
        }
        pt = exc[secrets.choice(s)]
        print(f'{Float(pt.x, P)}, {Float(pt.y, P)}')
        print("Can you guess the indices of the lines? (i j k)")

        if time.time() - start_time <= 25.0:
            if [int(n) for n in input().split()] == [i, j, k]:
                print(f"Congratulations! Here is your flag: {FLAG}")
            else:
                print("Wrong, try harder next time!")
        else:
            print("Timeout")
            
        signal.alarm(0)
        
    except Exception as e:
        print("Wrong, try harder next time!")
        sys.exit(1)

if __name__ == "__main__":
    run()