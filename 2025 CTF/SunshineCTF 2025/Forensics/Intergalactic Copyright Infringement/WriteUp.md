# Write‑up: Intergalactic Copyright Infringement (SunshineCTF 2025)

## Mô tả thử thách

> NASA received a notification from their ISP that it appeared that some copyrighted files were transferred to and from the ISS (Guess astronauts need movies too). We weren't able to recover the all of the files, but we were able to capture some traffic from the final download before the user signed off. If you can help recover the file that was downloaded perhaps you can shed some light on what they were doing?

---

## Phân tích lưu lượng mạng

Tệp `evidence.pcapng` chứa rất nhiều gói dữ liệu, tuy nhiên sau khi quan sát bằng Wireshark hoặc dùng script Python đơn giản, có thể thấy chỉ có hai kết nối BitTorrent. Các gói handshake của BitTorrent đều chứa chuỗi "BitTorrent protocol" cùng với một thông số `info_hash` 20 byte (mã băm SHA‑1 của torrent). Cả hai kết nối đều có chung `info_hash`, vì vậy đây là một torrent duy nhất.

Mỗi gói BitTorrent sau handshake gửi các mảnh (piece) dữ liệu có kích thước 16 KiB. Bằng cách nối tất cả dữ liệu mảnh theo đúng thứ tự chỉ số, chúng ta thu được một tệp dung lượng khoảng 5,5 MB. Khi kiểm tra chữ ký tệp bằng lệnh file, tệp đó được nhận diện là PDF (PDF document, version 1.6, 484 pages).

Script

```python
import argparse
import ipaddress
import struct
from collections import defaultdict, OrderedDict

EPB_TYPE = 0x00000006

def read_u32_le(b, off):
    return struct.unpack_from("<I", b, off)[0]

def parse_pcapng_epb_packets(pcap_bytes):
    off = 0
    n_packets = 0
    while off + 8 <= len(pcap_bytes):
        blk_type, blk_len = struct.unpack_from("<II", pcap_bytes, off)
        if blk_len <= 0 or off + blk_len > len(pcap_bytes):
            break
        if blk_type == EPB_TYPE:
            body = pcap_bytes[off + 8 : off + blk_len - 4]
            if len(body) >= 20:
                cap_len = read_u32_le(body, 12)
                pkt = body[20 : 20 + cap_len]
                if len(pkt) == cap_len:
                    n_packets += 1
                    yield pkt
        off += blk_len

def parse_eth_ipv4_tcp(pkt):
    if len(pkt) < 14:
        return None
    eth_type = struct.unpack("!H", pkt[12:14])[0]
    off = 14

    if eth_type == 0x8100:
        if len(pkt) < 18:
            return None
        eth_type = struct.unpack("!H", pkt[16:18])[0]
        off = 18

    if eth_type != 0x0800:
        return None
    if len(pkt) < off + 20:
        return None

    ip = pkt[off:]
    ver_ihl = ip[0]
    version = ver_ihl >> 4
    ihl = (ver_ihl & 0x0F) * 4
    if version != 4 or len(ip) < ihl + 20:
        return None
    total_len = struct.unpack("!H", ip[2:4])[0]
    proto = ip[9]
    src_ip = str(ipaddress.IPv4Address(ip[12:16]))
    dst_ip = str(ipaddress.IPv4Address(ip[16:20]))
    if proto != 6:
        return None

    tcp = ip[ihl:]
    if len(tcp) < 20:
        return None
    src_port, dst_port = struct.unpack("!HH", tcp[0:4])
    data_off = (tcp[12] >> 4) * 4
    if len(tcp) < data_off:
        return None

    ip_payload_len = max(0, total_len - ihl)
    tcp_seg_len = max(0, ip_payload_len - data_off)
    if tcp_seg_len > len(tcp) - data_off:
        tcp_seg_len = len(tcp) - data_off

    tcp_payload = tcp[data_off : data_off + tcp_seg_len]
    return (src_ip, src_port, dst_ip, dst_port, tcp_payload)

def flow_key(src_ip, src_port, dst_ip, dst_port):
    return (src_ip, src_port, dst_ip, dst_port)

def reverse_flow_key(k):
    a, b, c, d = k
    return (c, d, a, b)

def collect_tcp_streams(pcap_bytes):
    streams = defaultdict(bytearray)
    for pkt in parse_pcapng_epb_packets(pcap_bytes):
        parsed = parse_eth_ipv4_tcp(pkt)
        if not parsed:
            continue
        src_ip, src_p, dst_ip, dst_p, pl = parsed
        if not pl:
            continue
        streams[flow_key(src_ip, src_p, dst_ip, dst_p)] += pl
    return streams

BT_PSTR = b"BitTorrent protocol"

def scan_bt_in_stream(buf):
    if isinstance(buf, bytearray):
        buf = bytes(buf)

    i = 0
    n = len(buf)
    while i < n:
        if i + 68 <= n and buf[i] == 19 and buf[i+1:i+20] == b"BitTorrent protocol":
            info_hash = bytes(buf[i+28:i+48])
            peer_id   = bytes(buf[i+48:i+68])
            yield {'type': 'handshake', 'info_hash': info_hash, 'peer_id': peer_id}
            i += 68
            continue

        if i + 4 > n:
            break
        msg_len = int.from_bytes(buf[i:i+4], 'big', signed=False)
        if msg_len == 0:
            i += 4
            continue
        end = i + 4 + msg_len
        if msg_len < 0 or end > n:
            i += 1
            continue

        msg_id = buf[i+4]
        if msg_id == 7:
            if msg_len >= 9:
                index = int.from_bytes(buf[i+5:i+9], 'big')
                begin = int.from_bytes(buf[i+9:i+13], 'big')
                block = bytes(buf[i+13:end])
                yield {'type': 'piece', 'index': index, 'begin': begin, 'block': block}
        i = end

def reconstruct_file_from_pieces(pieces_dict):
    if not pieces_dict:
        return b""

    out = bytearray()
    piece_indices = sorted(pieces_dict.keys())
    max_piece_size = 0

    for idx in piece_indices:
        sub = pieces_dict[idx]
        begins = sorted(sub.keys())
        piece_data = bytearray()
        last_end = 0
        for bgn in begins:
            block = sub[bgn]
            if bgn > last_end:
                piece_data.extend(b"\x00" * (bgn - last_end))
            piece_data.extend(block)
            last_end = bgn + len(block)
        max_piece_size = max(max_piece_size, len(piece_data))
        out.extend(piece_data)

    return bytes(out), max_piece_size, piece_indices[0], piece_indices[-1]

def hexstr(b):
    return b.hex()

def main():
    ap = argparse.ArgumentParser(description="Reconstruct file from BitTorrent pieces inside a PCAPNG")
    ap.add_argument("pcapng", help="Input pcapng file")
    ap.add_argument("-o", "--out", default="reconstructed.bin", help="Output file name")
    ap.add_argument("-v", "--verbose", action="store_true", help="Verbose logs")
    args = ap.parse_args()

    data = open(args.pcapng, "rb").read()
    streams = collect_tcp_streams(data)

    bt_streams = []
    for fk, buf in streams.items():
        if BT_PSTR in buf:
            bt_streams.append((fk, buf))

    if args.verbose:
        print(f"[info] Total TCP streams: {len(streams)}")
        print(f"[info] Streams with BitTorrent handshake: {len(bt_streams)}")
        for fk, _ in bt_streams:
            print("       ", fk, " <-> ", reverse_flow_key(fk))

    pieces = defaultdict(dict)
    info_hashes = set()
    peer_ids = set()
    piece_msgs = 0

    for fk, buf in bt_streams:
        for evt in scan_bt_in_stream(buf):
            if evt['type'] == 'handshake':
                info_hashes.add(evt['info_hash'])
                peer_ids.add(evt['peer_id'])
            elif evt['type'] == 'piece':
                pieces[evt['index']][evt['begin']] = evt['block']
                piece_msgs += 1
        rfk = reverse_flow_key(fk)
        if rfk in streams:
            rbuf = streams[rfk]
            for evt in scan_bt_in_stream(rbuf):
                if evt['type'] == 'handshake':
                    info_hashes.add(evt['info_hash'])
                    peer_ids.add(evt['peer_id'])
                elif evt['type'] == 'piece':
                    pieces[evt['index']][evt['begin']] = evt['block']
                    piece_msgs += 1

    if args.verbose:
        for ih in info_hashes:
            print(f"[bt] info_hash: {hexstr(ih)}")
        for pid in peer_ids:
            print(f"[bt] peer_id: {pid}")

        print(f"[bt] piece messages parsed: {piece_msgs}")
        print(f"[bt] unique piece indices: {len(pieces)}")

    file_bytes, piece_sz_max, pmin, pmax = reconstruct_file_from_pieces(pieces)
    open(args.out, "wb").write(file_bytes)

    print(f"[ok] Wrote: {args.out} ({len(file_bytes):,} bytes)")
    print(f"[ok] piece indices: {pmin}..{pmax} (count={len(pieces)})  max_piece_size={piece_sz_max}")

    if file_bytes.startswith(b"%PDF"):
        print("[hint] Looks like PDF (starts with %PDF)")
        eof_pos = file_bytes.rfind(b"%%EOF")
        if eof_pos != -1:
            print(f"[hint] Found '%%EOF' at offset {eof_pos:,}")

if __name__ == "__main__":
    main()
```

Lệnh

```bash
$ python3 bt_reconstruct.py evidence.pcapng -o reconstructed.bin
[ok] Wrote: reconstructed.bin (5,500,629 bytes)
[ok] piece indices: 0..20 (count=21)  max_piece_size=262144
[hint] Looks like PDF (starts with %PDF)
[hint] Found '%%EOF' at offset 5,500,623
```

---

## Kiểm tra tệp PDF

Đầu tiên, sử dụng `pdfinfo` (Poppler) để xem thông tin meta nhận thấy tệp PDF được tạo bằng LibreOffice 7.3 và không có metadata tùy chỉnh hay JavaScript. Khi mở nội dung, đây là phiên bản Copyright Law of the United States and Related Laws Contained in Title 17 of the United States Code (circular 92), tức là văn bản luật bản quyền Hoa Kỳ. Phần lớn nội dung là văn bản thuần túy, không chứa flag. Điều này gợi ý rằng flag có thể được giấu trong hình ảnh hay các đối tượng khác.

```bash
$ file reconstructed.bin 
reconstructed.bin: PDF document, version 1.6

$ pdfinfo reconstructed.bin 
Creator:         Draw
Producer:        LibreOffice 7.3
CreationDate:    Thu Sep 18 03:04:22 2025 +07
Custom Metadata: no
Metadata Stream: no
Tagged:          no
UserProperties:  no
Suspects:        no
Form:            none
JavaScript:      no
Pages:           484
Encrypted:       no
Page size:       432 x 648 pts
Page rot:        0
File size:       5500629 bytes
Optimized:       no
PDF version:     1.6
```

---

## Trích xuất hình ảnh từ PDF

Poppler cung cấp lệnh `pdfimages` để liệt kê và tách tất cả hình ảnh nhúng trong PDF. Khi chạy `pdfimages -list reconstructed_file.bin`, chỉ có 5 hình ảnh được báo cáo: các nền gradient cho trang bìa và bìa sau, một lớp mặt nạ (smask) và một hình ảnh nhỏ ở trang 2. Dùng `pdfimages -all reconstructed_file.bin <prefix>` để tách chúng ra thành các tệp JPEG/PNG.

```bash
$ pdfimages -list reconstructed.bin 
page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    3803  2636  gray    1   8  jpeg   no         4  0   292   292 3054K  31%
   1     1 image    1276   453  gray    1   8  jpeg   no         5  0   292   292  190K  34%
   2     2 image    1685   297  gray    1   8  jpeg   no         9  0   294   294 79.6K  16%
   2     3 smask    1685   297  gray    1   8  image  no         9  0   294   294 47.6K 9.7%
 484     4 image    3803  2636  gray    1   8  jpeg   no         4  0   292   292 3054K  31%

$ mkdir -p out

$ pdfimages -all reconstructed.bin out/img
```

Sau khi kiểm tra từng tệp hình ảnh, 4 tệp trong số đó chỉ là nền xám không chứa thông tin. Tuy nhiên, tệp `img-003.png` (cùng với `img-002.jpg` là phiên bản màu khác) lại chứa dòng chữ lạ. Khi mở `img-003.png` bằng trình duyệt, có thể nhìn thấy rõ flag:

Trong ảnh, chuỗi chữ màu trắng có dạng:

```txt
sun{4rggg_sp4c3_p1r4cy}
```

Ký tự 4 được dùng để đại diện cho chữ a, 3 đại diện cho e và 1 đại diện cho i. Dịch theo tiếng Anh, chuỗi này đọc là "arggg space piracy" – một cách chơi chữ liên quan tới "pirate" (cướp biển) và khoảng không vũ trụ.

---

## Kết quả

Flag được ẩn trong một hình ảnh nhúng trong tài liệu PDF. Bằng cách tách hình ảnh khỏi file torrent, chúng ta thu được chuỗi flag:

```txt
sun{4rggg_sp4c3_p1r4cy}
```

Sự xuất hiện của flag trong văn bản Copyright Law of the United States là một lời nhắc hài hước rằng, trên ISS, các phi hành gia đã tải xuống một bản sao của luật bản quyền Hoa Kỳ – vốn nằm trong phạm vi public domain – chứ không phải đang vi phạm bản quyền thực sự.

---

## Flag

**Flag:** `sun{4rggg_sp4c3_p1r4cy}`
