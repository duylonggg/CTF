#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zoo_dns2zip.py
Extract hex-leaked data from DNS queries in a PCAP, recover a ZIP starting at PK\x03\x04,
then unzip (with a manual fallback if the central directory is missing).
Usage:
    python3 zoo_dns2zip.py /path/to/zoo.pcap out_dir
Requires:
    pip install scapy
"""
import sys, os, re, io, struct, zlib, binascii
from datetime import datetime

# Scapy imports (install with: pip install scapy)
from scapy.all import rdpcap, DNS, DNSQR

HEX_RE = re.compile(r'^[0-9a-fA-F]{2,}$')

def extract_hex_from_dns_qname(qname: bytes) -> str:
    """
    Given a DNS qname bytes (e.g. b'504b0304.deadbeef.example.com.'),
    return concatenated hex labels ('504b0304deadbeef'), preserving order.
    """
    if not qname:
        return ""
    try:
        s = qname.decode('ascii', 'ignore').strip('.')
    except Exception:
        s = str(qname)
    hex_parts = []
    for label in s.split('.'):
        lab = ''.join(ch for ch in label if ch in '0123456789abcdefABCDEF')
        if lab and len(lab) >= 2 and len(lab) % 2 == 0 and HEX_RE.match(lab):
            hex_parts.append(lab)
    return ''.join(hex_parts)

def collect_hex_stream_from_pcap(pcap_path: str) -> bytes:
    """
    Iterate PCAP, collect hex fragments from DNS queries in timestamp order,
    hex-decode and return the concatenated bytes.
    """
    pkts = rdpcap(pcap_path)
    fragments = []
    for p in pkts:
        if p.haslayer(DNS) and p[DNS].qd is not None and isinstance(p[DNS].qd, DNSQR):
            hex_str = extract_hex_from_dns_qname(p[DNS].qd.qname)
            if hex_str:
                fragments.append(hex_str)
    if not fragments:
        return b""
    hex_all = ''.join(fragments)
    # If odd length, drop last nibble
    if len(hex_all) % 2 == 1:
        hex_all = hex_all[:-1]
    try:
        return bytes.fromhex(hex_all)
    except binascii.Error:
        # Fallback: filter any non-hex (shouldn't happen because we filter above)
        filtered = ''.join(ch for ch in hex_all if ch in '0123456789abcdefABCDEF')
        if len(filtered) % 2 == 1:
            filtered = filtered[:-1]
        return bytes.fromhex(filtered)

def write_zip_slice(buf: bytes, out_zip_path: str) -> bytes:
    """
    Find first 'PK\\x03\\x04' in buf, write the slice [idx:] to out_zip_path.
    Return the written slice.
    """
    sig = b'PK\x03\x04'
    idx = buf.find(sig)
    if idx == -1:
        raise RuntimeError("Could not find 'PK\\x03\\x04' signature in reconstructed stream.")
    slice_bytes = buf[idx:]
    with open(out_zip_path, 'wb') as f:
        f.write(slice_bytes)
    return slice_bytes

def try_zipfile_extract(zip_bytes: bytes, out_dir: str) -> bool:
    """
    Try Python's zipfile first. Returns True on success, False on failure.
    """
    import zipfile
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(out_dir)
        return True
    except Exception as e:
        print(f"[zipfile] Failed to extract with central directory: {e}")
        return False

def extract_from_local_headers(zip_bytes: bytes, out_dir: str) -> None:
    """
    Minimal manual extractor that walks Local File Headers starting at PK\\x03\\x04
    and writes each file. Handles deflate (method=8) and store (method=0).
    Does NOT rely on the central directory.
    """
    os.makedirs(out_dir, exist_ok=True)
    data = memoryview(zip_bytes)
    pos = 0
    sig_lfh = 0x04034B50  # PK\x03\x04
    count = 0

    while pos + 30 <= len(data):
        sig = struct.unpack_from('<I', data, pos)[0]
        if sig != sig_lfh:
            # scan forward for the next possible local header
            nxt = bytes(data[pos:]).find(b'PK\x03\x04')
            if nxt == -1:
                break
            pos += nxt
            continue

        # Parse local header
        # struct:
        # signature         4  (0x04034b50)
        # ver_needed        2
        # gp_flag           2
        # comp_method       2
        # mtime             2
        # mdate             2
        # crc32             4
        # comp_size         4
        # uncomp_size       4
        # fname_len         2
        # extra_len         2
        if pos + 30 > len(data):
            break
        (_sig, ver_needed, gp_flag, comp_method, mtime, mdate,
         crc32, comp_size, uncomp_size, fname_len, extra_len) = struct.unpack_from('<IHHHHHIIIHH', data, pos)

        hdr_end = pos + 30
        name_start = hdr_end
        name_end = name_start + fname_len
        extra_end = name_end + extra_len
        if extra_end > len(data):
            break

        fname_bytes = bytes(data[name_start:name_end])
        try:
            fname = fname_bytes.decode('utf-8')
        except UnicodeDecodeError:
            fname = fname_bytes.decode('cp437', errors='replace')

        data_start = extra_end

        # If sizes are zero and data-descriptor is used (bit 3), we need to find the next header
        use_dd = bool(gp_flag & 0x0008)
        if comp_size == 0 or use_dd:
            # Fallback: Locate next local header to bound the file data
            next_off = bytes(data[data_start:]).find(b'PK\x03\x04')
            if next_off == -1:
                data_end = len(data)
            else:
                data_end = data_start + next_off
            comp_block = bytes(data[data_start:data_end])
        else:
            data_end = data_start + comp_size
            if data_end > len(data):
                comp_block = bytes(data[data_start:])
            else:
                comp_block = bytes(data[data_start:data_end])

        # Decompress / store
        out_path = os.path.join(out_dir, fname)
        os.makedirs(os.path.dirname(out_path) or out_dir, exist_ok=True)

        if comp_method == 0:  # stored
            payload = comp_block
        elif comp_method == 8:  # deflate
            try:
                payload = zlib.decompress(comp_block, -zlib.MAX_WBITS)
            except zlib.error:
                # try with zlib header
                payload = zlib.decompress(comp_block)
        else:
            # unsupported method; just dump compressed data with .compressed suffix
            out_path += ".compressed"
            payload = comp_block

        with open(out_path, 'wb') as f:
            f.write(payload)
        count += 1
        print(f"[LFH] Extracted: {fname} ({len(payload)} bytes)")

        # Advance to next header (either via known comp_size or by seeking next PK)
        if comp_size and not use_dd:
            pos = data_end
        else:
            # already set data_end using next header search
            pos = data_end

    print(f"[LFH] Done. Extracted {count} file(s) to: {out_dir}")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("Example:\n  python3 zoo_dns2zip.py zoo.pcap out_dir")
        sys.exit(1)

    pcap_path = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    print(f"[+] Reading PCAP: {pcap_path}")
    stream = collect_hex_stream_from_pcap(pcap_path)
    if not stream:
        print("[-] No hex fragments found in DNS qnames. Aborting.")
        sys.exit(2)

    # Save raw concatenation for auditing
    raw_path = os.path.join(out_dir, "dns_hex_concat.bin")
    with open(raw_path, "wb") as f:
        f.write(stream)
    print(f"[+] Wrote concatenated DNS hex stream: {raw_path} ({len(stream)} bytes)")

    # Carve PK zip
    zip_path = os.path.join(out_dir, "carved.zip")
    try:
        zip_bytes = write_zip_slice(stream, zip_path)
    except RuntimeError as e:
        print(f"[-] {e}")
        sys.exit(3)

    print(f"[+] Carved ZIP slice written: {zip_path} ({len(zip_bytes)} bytes)")

    # Try extraction via zipfile, then fallback to local-header parsing
    extracted_dir = os.path.join(out_dir, "unzipped")
    os.makedirs(extracted_dir, exist_ok=True)

    ok = try_zipfile_extract(zip_bytes, extracted_dir)
    if ok:
        print(f"[+] Extracted with zipfile to: {extracted_dir}")
    else:
        print("[*] Falling back to Local File Header parsing...")
        extract_from_local_headers(zip_bytes, extracted_dir)

    print("[+] Done.")

if __name__ == "__main__":
    main()
