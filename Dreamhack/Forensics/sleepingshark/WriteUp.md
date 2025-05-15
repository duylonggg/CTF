# 🛠️ Write Up

## 1. **Install Required Tools**

Use the following commands to install the necessary tools on a Linux system:

```bash
sudo apt update
sudo apt install wireshark tshark pyshark python3-pip
pip3 install pyshark
```

---

## 2. **Opening a PCAP File with Wireshark**

To open a `.pcap` file in Wireshark:

```bash
wireshark dump.pcap
```

---

## 3. **Understanding the Payload**

Click on any HTTP packet, and examine the request:

```http
POST /?q=SELECT%20IF%28ASCII%28SUBSTRING%28%28SELECT%20flag%20FROM%20s3cr3t%20LIMIT%201%29%2C35%2C1%29%29%3D156%2C%20SLEEP%283%29%2C%200%29 HTTP/1.1\\r\\n
```

This query is using **Time-Based SQL Injection**:

- If the 35th character of the `flag` equals ASCII 156, the server sleeps for 3 seconds.
- By checking which requests cause a 3-second delay, we can infer the correct character at that position.

---

## 4. **Add Delta Time Column in Wireshark**

To identify delayed packets:
  
1. Right-click on any column title.
2. Select `Column Preferences`.
3. Click the [+] icon to add a new column.
4. Set:
   - **Title**: `Delta time`
   - **Field Type**: `Custom`
   - **Field Name**: `frame.time_delta_displayed`
5. Click `OK`

You’ll now be able to spot packets with ~3-second delays — these contain correct character guesses.

---

## 5. **Python Script for Automated Extraction**

Use this script to automate detection and flag reconstruction:

```python
import pyshark
import re

pcap_file = 'dump.pcap'
cap = pyshark.FileCapture(pcap_file, display_filter='http')

http_requests = {}
flag_chars = {}

print("HTTP 200 OK packets with delay >= 3.0 seconds:\\n")

def extract_position_and_ascii(uri):
    percent_indices = [m.start() for m in re.finditer(r'%..', uri)]
    if len(percent_indices) >= 16:
        try:
            pos_start = percent_indices[11] + 3
            ascii_start = percent_indices[15] + 3

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
                print(f'Delta: {delta:.6f}s\\nRequest URI: {uri}')

                pos, ascii_val = extract_position_and_ascii(uri)
                if pos is not None and ascii_val is not None:
                    char = chr(ascii_val)
                    flag_chars[pos] = char
                    print(f' -> Found flag[{pos}] = {char}\\n')

    except AttributeError:
        continue

flag = ''.join(flag_chars[i] for i in sorted(flag_chars))
print(f'\\n✅ Recovered flag: {flag}')
```

---

## 6. **Final Flag**

After running the script and analyzing the packets:

```txt
GoN{T1mE_B4s3d_5QL_Inj3c7i0n_wI7h_Pc4p}
```