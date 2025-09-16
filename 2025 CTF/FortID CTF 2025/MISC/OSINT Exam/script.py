#!/usr/bin/env python3
# submit_q6.py
from pwn import remote, context
import argparse, os, sys, time

ANS_1 = "Luxembourg House of Financial Technology Petra Krizan"
ANS_2 = "2 Staverton Road Oxford OX2 6XJ United Kingdom"
ANS_3 = "Koturaska 51 10000 Zagreb Croatia"
ANS_4 = "Manchester 00:53:04 00:49:12"
ANS_5 = "Kopacka solidarnosti 3"
ANS_6 = "Concurrency, Security, and Puzzles"

def drain(sock, seconds=1.5):
    t_end = time.time() + seconds
    out = b""
    while time.time() < t_end:
        try:
            chunk = sock.recv(timeout=0.2)
            if not chunk:
                break
            out += chunk
        except EOFError:
            break
    if out:
        sys.stdout.buffer.write(out); sys.stdout.flush()

def send_answers(sock, answers, gap=0.30):
    for a in answers:
        sock.sendline(a.encode())
        time.sleep(gap)

def main():
    parser = argparse.ArgumentParser(description="Auto-submit OSINT answers; Q6 có thể điền ngay trong file.")
    parser.add_argument("--host", default="0.cloud.chals.io")
    parser.add_argument("--port", type=int, default=27689)
    parser.add_argument("--q6", default=os.getenv("Q6"), help='Override tiêu đề sách cho Q6 (ưu tiên hơn ANS_6)')
    parser.add_argument("--gap", type=float, default=0.30, help="Delay giữa các câu trả lời (s)")
    parser.add_argument("--log", default="warn", help="pwntools log level (debug/info/warn/error)")
    args = parser.parse_args()

    q6 = args.q6 if (args.q6 and args.q6.strip()) else ANS_6

    if not q6 or not q6.strip():
        print('Chưa có Câu 6. Điền trực tiếp vào file: ANS_6 = "Tựa sách" '
              'hoặc chạy: python3 submit_q6.py --q6 "Tựa sách" (hay export Q6="Tựa sách")',
              file=sys.stderr)
        sys.exit(2)

    context.log_level = args.log
    io = remote(args.host, args.port)

    # Hút banner/prompt đầu
    drain(io, seconds=1.5)

    # Gửi Q1–Q6
    answers = [ANS_1, ANS_2, ANS_3, ANS_4, ANS_5, q6]
    send_answers(io, answers, gap=args.gap)

    # Đọc kết quả/flag
    drain(io, seconds=3.0)
    io.interactive()

if __name__ == "__main__":
    main()
