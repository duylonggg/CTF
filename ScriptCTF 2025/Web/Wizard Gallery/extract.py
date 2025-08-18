#!/usr/bin/env python3
# extract_png_text.py
# Usage: python3 extract_png_text.py processed.png

import sys, struct, zlib

def read_u32(f):
    b = f.read(4)
    if len(b) < 4:
        return None
    return struct.unpack(">I", b)[0]

def parse_png(path):
    with open(path, "rb") as f:
        sig = f.read(8)
        if sig != b'\x89PNG\r\n\x1a\n':
            raise SystemExit("Not a PNG")
        while True:
            length = read_u32(f)
            if length is None:
                break
            ctype = f.read(4)
            if len(ctype) < 4:
                break
            data = f.read(length)
            crc = f.read(4)
            t = ctype.decode('ascii', errors='ignore')
            if t in ('tEXt','zTXt','iTXt'):
                print("="*60)
                print("Chunk:", t)
                try:
                    if t == 'tEXt':
                        # format: keyword\0text
                        key, text = data.split(b'\x00',1)
                        print("keyword:", key.decode('latin1'))
                        print("text:\n", text.decode('latin1', errors='replace'))
                    elif t == 'zTXt':
                        # format: keyword\0compression(1)\x00? then compressed data
                        key, rest = data.split(b'\x00',1)
                        comp_method = rest[0]
                        comp_data = rest[1:]
                        try:
                            txt = zlib.decompress(comp_data).decode('latin1', errors='replace')
                        except Exception as e:
                            txt = f"<zlib decompression failed: {e}>"
                        print("keyword:", key.decode('latin1'))
                        print("compression method:", comp_method)
                        print("text:\n", txt)
                    elif t == 'iTXt':
                        # format: keyword\0comp_flag(1)comp_method(1)language\0translated\0text
                        # parse stepwise
                        keyword, rest = data.split(b'\x00',1)
                        if len(rest) < 2:
                            print("<iTXt parse error>")
                            continue
                        comp_flag = rest[0]
                        comp_method = rest[1]
                        rest2 = rest[2:]
                        try:
                            language, rest3 = rest2.split(b'\x00',1)
                            translated, text = rest3.split(b'\x00',1)
                        except ValueError:
                            # fallback: try safer splits
                            parts = rest2.split(b'\x00')
                            if len(parts) >= 3:
                                language = parts[0]
                                translated = parts[1]
                                text = b'\x00'.join(parts[2:])
                            else:
                                language = b''
                                translated = b''
                                text = rest2
                        if comp_flag == 1:
                            try:
                                text = zlib.decompress(text)
                            except Exception as e:
                                print("<iTXt zlib decompress failed>", e)
                        print("keyword:", keyword.decode('latin1'))
                        print("language:", language.decode('latin1', errors='replace'))
                        print("translated:", translated.decode('utf-8', errors='replace'))
                        print("text:\n", text.decode('utf-8', errors='replace'))
                except Exception as e:
                    print("<error parsing chunk>", e)
        print("="*60)
        print("Done.")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_png_text.py processed.png")
        sys.exit(1)
    parse_png(sys.argv[1])
