#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstruct a file from BitTorrent piece messages inside a PCAPNG.
- No external deps (pure Python)
- Handles Ethernet + IPv4 + TCP in EPB blocks
- Collects BitTorrent piece (msg id=7) and reassembles the payload
"""

import argparse
import ipaddress
import struct
from collections import defaultdict, OrderedDict

EPB_TYPE = 0x00000006  # Enhanced Packet Block

def read_u32_le(b, off):
    return struct.unpack_from("<I", b, off)[0]

def parse_pcapng_epb_packets(pcap_bytes):
    """
    Iterate over Enhanced Packet Blocks and yield raw captured packet bytes.
    Returns generator of packet bytes (Layer-2 frames).
    """
    off = 0
    n_packets = 0
    while off + 8 <= len(pcap_bytes):
        blk_type, blk_len = struct.unpack_from("<II", pcap_bytes, off)
        if blk_len <= 0 or off + blk_len > len(pcap_bytes):
            break
        if blk_type == EPB_TYPE:
            body = pcap_bytes[off + 8 : off + blk_len - 4]
            if len(body) >= 20:
                cap_len = read_u32_le(body, 12)  # captured length
                pkt = body[20 : 20 + cap_len]
                if len(pkt) == cap_len:
                    n_packets += 1
                    yield pkt
        off += blk_len
    # print(f"[pcapng] EPB packets parsed: {n_packets}")

def parse_eth_ipv4_tcp(pkt):
    """
    Very small parser: Ethernet (with optional 802.1Q) -> IPv4 -> TCP.
    Return (src_ip, src_port, dst_ip, dst_port, tcp_payload) or None.
    """
    if len(pkt) < 14:
        return None
    eth_type = struct.unpack("!H", pkt[12:14])[0]
    off = 14

    # VLAN tag 802.1Q
    if eth_type == 0x8100:
        if len(pkt) < 18:
            return None
        eth_type = struct.unpack("!H", pkt[16:18])[0]
        off = 18

    if eth_type != 0x0800:  # IPv4 only
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
    if proto != 6:  # TCP
        return None

    tcp = ip[ihl:]
    if len(tcp) < 20:
        return None
    src_port, dst_port = struct.unpack("!HH", tcp[0:4])
    data_off = (tcp[12] >> 4) * 4
    if len(tcp) < data_off:
        return None

    # Prefer IP total_len if sane; else fallback to full capture
    ip_payload_len = max(0, total_len - ihl)
    tcp_seg_len = max(0, ip_payload_len - data_off)
    if tcp_seg_len > len(tcp) - data_off:  # guard if total_len looks wrong
        tcp_seg_len = len(tcp) - data_off

    tcp_payload = tcp[data_off : data_off + tcp_seg_len]
    return (src_ip, src_port, dst_ip, dst_port, tcp_payload)

def flow_key(src_ip, src_port, dst_ip, dst_port):
    return (src_ip, src_port, dst_ip, dst_port)

def reverse_flow_key(k):
    a, b, c, d = k
    return (c, d, a, b)

def collect_tcp_streams(pcap_bytes):
    """
    Concatenate TCP payloads by direction for every 4-tuple flow.
    Returns dict: flow_key -> bytearray
    """
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

# ---------- BitTorrent parsing ----------

BT_PSTR = b"BitTorrent protocol"

def scan_bt_in_stream(buf):
    # NEW: nếu là bytearray thì ép sang bytes để hash/so sánh ổn định
    if isinstance(buf, bytearray):
        buf = bytes(buf)

    i = 0
    n = len(buf)
    while i < n:
        # Handshake: 0x13 + "BitTorrent protocol" + 8 + 20 + 20
        if i + 68 <= n and buf[i] == 19 and buf[i+1:i+20] == b"BitTorrent protocol":
            # NEW: ép lát cắt sang bytes (phòng khi buf là memoryview/bytearray)
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
        if msg_id == 7:  # piece
            if msg_len >= 9:
                index = int.from_bytes(buf[i+5:i+9], 'big')
                begin = int.from_bytes(buf[i+9:i+13], 'big')
                # NEW: ép block sang bytes cho nhất quán
                block = bytes(buf[i+13:end])
                yield {'type': 'piece', 'index': index, 'begin': begin, 'block': block}
        i = end

def reconstruct_file_from_pieces(pieces_dict):
    """
    pieces_dict: dict[index] -> dict[begin] = bytes(block)
    Returns bytes for the full file (pieces concatenated by index, and begin ascending).
    """
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
            # If there is a gap, pad with zeros (rare; usually contiguous 16KiB blocks)
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

    # Find streams that contain BitTorrent handshake
    bt_streams = []
    for fk, buf in streams.items():
        if BT_PSTR in buf:
            bt_streams.append((fk, buf))

    if args.verbose:
        print(f"[info] Total TCP streams: {len(streams)}")
        print(f"[info] Streams with BitTorrent handshake: {len(bt_streams)}")
        for fk, _ in bt_streams:
            print("       ", fk, " <-> ", reverse_flow_key(fk))

    # Parse messages from both directions; collect pieces
    pieces = defaultdict(dict)  # index -> { begin: block }
    info_hashes = set()
    peer_ids = set()
    piece_msgs = 0

    # Also consider the reverse-direction buffer if present
    for fk, buf in bt_streams:
        # forward dir
        for evt in scan_bt_in_stream(buf):
            if evt['type'] == 'handshake':
                info_hashes.add(evt['info_hash'])
                peer_ids.add(evt['peer_id'])
            elif evt['type'] == 'piece':
                pieces[evt['index']][evt['begin']] = evt['block']
                piece_msgs += 1
        # reverse dir (if any)
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

    # Reconstruct
    file_bytes, piece_sz_max, pmin, pmax = reconstruct_file_from_pieces(pieces)
    open(args.out, "wb").write(file_bytes)

    print(f"[ok] Wrote: {args.out} ({len(file_bytes):,} bytes)")
    print(f"[ok] piece indices: {pmin}..{pmax} (count={len(pieces)})  max_piece_size={piece_sz_max}")

    # Heuristics: PDF?
    if file_bytes.startswith(b"%PDF"):
        print("[hint] Looks like PDF (starts with %PDF)")
        eof_pos = file_bytes.rfind(b"%%EOF")
        if eof_pos != -1:
            print(f"[hint] Found '%%EOF' at offset {eof_pos:,}")

if __name__ == "__main__":
    main()
