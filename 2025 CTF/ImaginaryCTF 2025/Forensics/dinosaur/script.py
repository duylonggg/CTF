#!/usr/bin/env python3
import base64, zlib, itertools
from collections import Counter

F = "STEGosaurus.txt"
BLOCK = 49
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def pick_char(tok: str) -> str:
    return tok[3] if tok.startswith("roo") and len(tok) > 3 else tok[0]

def load_blocks():
    toks = open(F, encoding="utf-8").read().split()
    assert len(toks) % BLOCK == 0
    G = [toks[i:i+BLOCK] for i in range(0, len(toks), BLOCK)]
    return G

def to_stream(blocks):
    chars = []
    for g in blocks:
        chars.extend(pick_char(t) for t in g)
    s = "".join(ch for ch in chars if ch in B64)
    # base64 -> XOR 0xF2
    data = base64.b64decode(s + "="*((-len(s))%4), validate=False)
    return bytes(b ^ 0xF2 for b in data)

def try_decompress(x):
    try:
        out = zlib.decompress(x)     # zlib with header (wbits=+15)
        return out
    except Exception:
        return None

def rotate(g, k):
    k %= len(g)
    return g[k:]+g[:k]

def strategies_for_group(g):
    c = Counter(g)
    dom_tok, dom_cnt = c.most_common(1)[0]
    # Một số hoán vị/offset “hợp lý”
    yield g
    yield list(reversed(g))
    # non-roo trước rồi roo
    yield [t for t in g if not t.startswith("roo")] + [t for t in g if t.startswith("roo")]
    # roo trước rồi non-roo
    yield [t for t in g if t.startswith("roo")] + [t for t in g if not t.startswith("roo")]
    # rotate theo các offset suy đoán
    candidates = set()
    candidates.add(BLOCK - dom_cnt)                       # số phần tử khác “filler”
    candidates.add(sum(1 for t in g if t.startswith("roo")))
    candidates.add(c["imagine"])
    candidates.add(c["harold"])
    for k in candidates:
        yield rotate(g, k)

def product_limited(all_groups, limit_per_group=2):
    """
    Để không nổ search space, mỗi group chỉ lấy N phương án đầu,
    và ghép theo từng “dải” groups (chunk) để check dần.
    """
    picks = [list(itertools.islice(strategies_for_group(g), limit_per_group)) for g in all_groups]
    for choice in itertools.product(*picks):
        yield list(choice)

def scan_for_flag(x):
    i = x.find(b"ictf{")
    if i == -1:
        return None
    j = x.find(b"}", i+5)
    if j == -1:
        return None
    return x[i:j+1].decode(errors="ignore")

def main():
    blocks = load_blocks()

    # sanity: sau XOR phải mở đầu bằng 0x78 0xDA (zlib)
    raw = to_stream(blocks)
    if not (len(raw) >= 2 and raw[0] == 0x78 and raw[1] in (0xDA, 0x9C)):
        print("[!] Lấy ký tự/base64/XOR chưa đúng (không thấy zlib header). Kiểm tra lại.")
        print(raw[:16].hex())
        return

    # thử theo “làn” 8 block một để giảm tổ hợp, rồi ghép dần
    CHUNK = 8
    cur = []
    for idx in range(0, len(blocks), CHUNK):
        part = blocks[idx:idx+CHUNK]
        best = None
        for cand in product_limited(part, limit_per_group=3):
            trial = cur + cand + blocks[idx+CHUNK:]
            x = to_stream(trial)
            # thử decompress ngay khi có hy vọng
            out = try_decompress(x)
            if out:
                flag = scan_for_flag(out)
                if flag:
                    print(flag)
                    return
                # chưa thấy flag, nhưng giữ cấu hình này vì đã decompress được
                best = cand
                break
        # nếu chưa decompress được chunk này, nới limit một chút
        if best is None:
            for cand in product_limited(part, limit_per_group=5):
                x = to_stream(cur + cand + blocks[idx+CHUNK:])
                out = try_decompress(x)
                if out:
                    flag = scan_for_flag(out)
                    if flag:
                        print(flag)
                        return
                    best = cand
                    break
        if best is None:
            # fallback: chọn phương án “ít xấu nhất” (đẩy vòng theo số non-filler)
            best = [rotate(g, BLOCK - Counter(g).most_common(1)[0][1]) for g in part]
        cur += best

    # Nếu đi hết mà chưa thấy: in thử vài byte đầu sau decompress để bạn kiểm tra tay
    x = to_stream(cur)
    out = try_decompress(x)
    if out:
        print("[i] giải nén OK nhưng chưa thấy flag, dump vài dòng để bạn grep:")
        print(out[:200])
    else:
        print("[!] Vẫn chưa đúng trật tự trong block 49. Tăng limit_per_group và CHUNK rồi chạy lại.")

if __name__ == "__main__":
    main()
