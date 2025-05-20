import pyshark
import re

# File PCAP cần đọc
pcap_file = 'dump.pcap'

# Lọc các gói HTTP
cap = pyshark.FileCapture(pcap_file, display_filter='http')

# Lưu request URI theo stream
http_requests = {}
flag_chars = {}

print("Các gói HTTP 200 OK có delay >= 3.0 giây:\n")

def extract_position_and_ascii(uri):
    # Tìm tất cả vị trí xuất hiện của '%'
    percent_indices = [m.start() for m in re.finditer(r'%..', uri)]
    if len(percent_indices) >= 16:
        try:
            # Lấy chuỗi 3 ký tự sau % thứ 12 và % thứ 16
            pos_start = percent_indices[11] + 3
            ascii_start = percent_indices[15] + 3

            # Lấy tiếp vài ký tự số sau đó (tối đa 3 để tránh sai sót)
            pos = ''
            while pos_start < len(uri) and uri[pos_start].isdigit():
                pos += uri[pos_start]
                pos_start += 1

            ascii_val = ''
            while ascii_start < len(uri) and uri[ascii_start].isdigit():
                ascii_val += uri[ascii_start]
                ascii_start += 1

            return int(pos), int(ascii_val)
        except:
            return None, None
    return None, None

for pkt in cap:
    try:
        stream_id = pkt.tcp.stream
        if 'request_method' in pkt.http.field_names:
            uri = pkt.http.get('request_full_uri', '')
            http_requests[stream_id] = uri

        if 'response_code' in pkt.http.field_names and pkt.http.response_code == '200':
            delta = float(pkt.tcp.time_delta)
            if delta >= 3.0:
                uri = http_requests.get(stream_id, '[Unknown URI]')
                print(f'Delta: {delta:.6f}s\nRequest URI: {uri}')

                pos, ascii_val = extract_position_and_ascii(uri)
                if pos is not None and ascii_val is not None:
                    char = chr(ascii_val)
                    flag_chars[pos] = char
                    print(f' -> Found flag[{pos}] = {char}\n')

    except AttributeError:
        continue

# Ghép flag
flag = ''.join(flag_chars[i] for i in sorted(flag_chars))
print(f'\n✅ Flag khôi phục được: {flag}')
