#!/usr/bin/env python3
import socket, os, binascii, argparse

BS = 16
PROMPT = b'input cipher (hex): '

def pkcs7_pad(b: bytes) -> bytes:
    pad = BS - (len(b) % BS)
    return b + bytes([pad]) * pad

class Service:
    def __init__(self, host, port, timeout=5.0):
        self.host, self.port, self.timeout = host, port, timeout
        self.s = None
    def connect(self):
        self.s = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._recv_until_prompt()
    def close(self):
        if self.s:
            try: 
                self.s.sendall(b'exit\n')
            except Exception:
                pass
            try: self.s.close()
            finally: self.s = None
    def _recv_until_prompt(self) -> bytes:
        data = b''
        while True:
            chunk = self.s.recv(4096)
            if not chunk:
                break
            data += chunk
            if PROMPT in data:
                break
        return data
    def query(self, payload_bytes: bytes) -> bytes:
        # gửi 1 dòng hex, nhận về thông báo + prompt kế tiếp
        line = binascii.hexlify(payload_bytes) + b'\n'
        self.s.sendall(line)
        return self._recv_until_prompt()

def oracle_valid(resp: bytes) -> bool:
    # padding hợp lệ nếu KHÔNG có "invalid padding"
    return (b'invalid padding' not in resp)

def find_intermediate(svc, target_c: bytes) -> bytes:
    BS = 16
    I = bytearray(BS)
    prev = bytearray(os.urandom(BS))
    for padlen in range(1, BS+1):
        idx = BS - padlen
        # set đuôi về pad hiện tại
        for j in range(idx+1, BS):
            prev[j] = I[j] ^ padlen

        found = False
        for g in range(256):
            prev[idx] = g
            resp = svc.query(bytes(prev) + target_c)
            if b'invalid padding' not in resp:
                # XÁC NHẬN: chỉ làm khi còn byte 'an toàn' ở trước vùng pad
                if idx > 0:
                    prev[idx-1] ^= 1        # flip 1 byte trước vùng pad
                    resp2 = svc.query(bytes(prev) + target_c)
                    prev[idx-1] ^= 1
                    if b'invalid padding' in resp2:
                        continue  # xác nhận hỏng → thử g khác
                I[idx] = g ^ padlen
                found = True
                break
        if not found:
            raise RuntimeError(f"Không tìm được byte tại vị trí {idx} (pad={padlen})")
    return bytes(I)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host"); ap.add_argument("port", type=int)
    ap.add_argument("--payload", default='{"command":"print(flag)"}')
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()

    # Chuẩn bị plaintext 2 khối
    P = pkcs7_pad(args.payload.encode())
    if len(P) > 32:
        raise SystemExit("Payload quá dài; hãy giữ ≤25 byte để vừa 2 khối.")
    P1, P2 = P[:16], P[16:]

    svc = Service(args.host, args.port, args.timeout)
    svc.connect()

    # Oracle encrypt “ngược”: chọn C2 ngẫu nhiên → tìm I2 → C1 = I2 ⊕ P2
    C2 = os.urandom(16)
    I2 = find_intermediate(svc, C2)
    C1 = bytes(a ^ b for a, b in zip(I2, P2))

    # Tìm I1 từ C1 → IV = I1 ⊕ P1
    I1 = find_intermediate(svc, C1)
    IV = bytes(a ^ b for a, b in zip(I1, P1))

    full = IV + C1 + C2
    print("[+] Cipher (hex):", binascii.hexlify(full).decode())

    # Gửi phát cuối: sẽ in flag rồi trả về prompt
    resp = svc.query(full)
    print(resp.decode(errors="ignore"))

    svc.close()

if __name__ == "__main__":
    main()
