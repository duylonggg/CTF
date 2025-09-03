import zlib
import re

pdf_file = "challenge.pdf"

with open(pdf_file, "rb") as f:
    data = f.read()

# Tìm tất cả object có stream và FlateDecode
pattern = re.compile(rb'(\d+ \d+ obj.*?<<.*?/Filter/FlateDecode.*?>>.*?stream(.*?)endstream)', re.S)

matches = pattern.findall(data)

print(f"Đã tìm thấy {len(matches)} stream FlateDecode.\n")

for i, (full_obj, stream_content) in enumerate(matches, 1):
    # Lấy phần dữ liệu giữa 'stream' và 'endstream'
    stream_data = stream_content.strip(b"\r\n")

    try:
        text = zlib.decompress(stream_data).decode("utf-8", errors="ignore")
    except Exception as e:
        text = f"[!] Không thể giải nén: {e}"

    print(f"--- Stream #{i} ---\n{text}\n")
