#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, socket, sys, string, collections

HOST = "103.197.184.48"
PORT = 12345
if len(sys.argv) >= 2: HOST = sys.argv[1]
if len(sys.argv) >= 3: PORT = int(sys.argv[2])

# ---------- helpers ----------
def title_case_if_not_numbers(s: str) -> str:
    has_alpha = any(ch.isalpha() for ch in s)
    if not has_alpha:
        return s
    return " ".join(
        (w[:1].upper() + w[1:].lower()) if w else w
        for w in s.split()
    )

def keep_unicode_printable(s: str) -> str:
    return "".join(ch for ch in s if ch.isprintable() or ch in "\r\n\t")

# ---------- Charabia Latin ----------
import re
from typing import List

# danh sách suffix Latin thường gặp (viết thường). Bạn có thể mở rộng.
LATIN_SUFFIXES = ["us","um","ae","it","i","a","e","o"]


def decode_charabia_latin(ciphertext: str) -> str:
    words = ciphertext.split()
    stripped_words = []

    for w in words:
        # chỉ loại bỏ suffix ≥2 ký tự
        for suf in sorted(LATIN_SUFFIXES, key=len, reverse=True):
            if len(suf) > 1 and w.lower().endswith(suf):
                w = w[:-len(suf)]
                break
        stripped_words.append(w)

    # nối lại thành chuỗi và đảo toàn bộ
    reversed_text = " ".join(stripped_words)[::-1]

    # tách từ theo space và viết hoa chữ cái đầu
    final_words = [w.capitalize() for w in reversed_text.split()]
    return " ".join(final_words)

# ---------- Trithemius (progressive Caesar) ----------

ITALIAN_SUFFIXES = [
    "INO", "ELLO", "ETTO", "UCCIO", "ONE", "INA", "INA", "ETTA", "UCCIA", "ONA",
    "NO", "INI", "ELLI", "ETTI", "ONI", "INE", "ELLE", "ETTE", "UCCE", "ONI",
]

def decode_trithemius(ciphertext: str) -> str:
    """
    Giải mã Trithemius nhiều từ.
    - Từ 1: offset +3
    - Từ 2: offset +13 (trừ khi từ 1 giải mã thành 'Rondinello' thì offset +14)
    """
    def shift_char(c, k):
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            return chr((ord(c) - base + k) % 26 + base)
        return c

    def decode_word(word, base_shift):
        res = []
        for i, c in enumerate(word):
            if c.isalpha():
                res.append(shift_char(c, -(base_shift + i)))
            else:
                res.append(c)
        return "".join(res)

    words = ciphertext.split()
    out_words = []

    for w_idx, word in enumerate(words):
        if w_idx == 0:
            decoded = decode_word(word, 3)
            out_words.append(decoded)
        elif w_idx == 1:
            chosen = None
            for base_shift in range(1, 21):
                candidate = decode_word(word, base_shift)
                if any(candidate.upper().endswith(sfx) for sfx in ITALIAN_SUFFIXES):
                    chosen = candidate
                    break
            if chosen is None:  # fallback nếu không khớp
                chosen = decode_word(word, 13)
            out_words.append(chosen)
        else:
            decoded = decode_word(word, 13)
            out_words.append(decoded)

    return " ".join(out_words)


# ---------- NATO phonetic (OTAN) ----------
NATO = {
    "ALFA":"A","ALPHA":"A","BRAVO":"B","CHARLIE":"C","DELTA":"D","ECHO":"E",
    "FOXTROT":"F","GOLF":"G","HOTEL":"H","INDIA":"I","JULIET":"J","JULIETT":"J",
    "KILO":"K","LIMA":"L","MIKE":"M","NOVEMBER":"N","OSCAR":"O","PAPA":"P",
    "QUEBEC":"Q","ROMEO":"R","SIERRA":"S","TANGO":"T","UNIFORM":"U","VICTOR":"V",
    "WHISKEY":"W","XRAY":"X","X-RAY":"X","YANKEE":"Y","ZULU":"Z"
}
def decode_nato(cipher: str) -> str:
    # Giữ ngăn cách từ khi có >=2 spaces hoặc dấu "/"
    parts = re.split(r'(\s+|/+)', cipher)
    words, cur = [], []
    for part in parts:
        # Nếu là phân cách
        if re.fullmatch(r'\s+|/+', part or ''):
            if len(part) >= 2 or '/' in part:  # word break
                if cur:
                    words.append("".join(cur)); cur = []
            # 1 space đơn chỉ là phân cách token trong cùng 1 từ
            continue
        # Là token chữ
        token = re.sub(r'[^A-Za-z\-]', '', part)
        if not token: 
            continue
        ch = NATO.get(token.upper())
        if ch: 
            cur.append(ch)
        # token lạ -> bỏ qua
    if cur:
        words.append("".join(cur))
    ans = " ".join(words) if words else cipher
    return title_case_if_not_numbers(ans)

# ---------- Prime ----------
# 2->A, 3->B, 5->C, ..., 97->Z; 0/1=>space
def sieve(limit=200000):
    n=limit+1; s=[True]*n; s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]: s[i*i:n:i]=[False]*len(range(i*i,n,i))
    return [i for i in range(n) if s[i]]
_PRIMES = sieve()
_POS = {p:i+1 for i,p in enumerate(_PRIMES)}  # prime->index (A=1)
# 2->A, 3->B, 5->C, ..., 97->Z. 0/1 => space
def decode_prime(cipher: str) -> str:
    parts = re.split(r'(\s+|/+)', cipher.strip())
    words, cur = [], []

    for part in parts:
        # Word break nếu >=2 spaces hoặc có '/'
        if re.fullmatch(r'\s+|/+', part or ''):
            if len(part) >= 2 or '/' in part:
                if cur:
                    words.append("".join(cur))
                    cur = []
            continue

        # Trong cùng 1 từ: các số cách nhau 1 space
        for tok in re.findall(r"-?\d+", part):
            v = int(tok)
            if v <= 1:
                cur.append(" ")
            else:
                idx = _POS.get(v)  # _POS: {prime: index} với 2->1 (A), 3->2 (B)...
                if idx and 1 <= idx <= 26:
                    cur.append(chr(64 + idx))  # 1->A, 2->B, ...
                else:
                    cur.append(" ")

    if cur:
        words.append("".join(cur))

    # Gộp space thừa trong từng từ rồi ráp từ
    ans = " ".join(" ".join(w.split()) for w in words).strip()
    return title_case_if_not_numbers(ans)

# ---------- GS8 Braille ----------
# map 6-dot to latin a-z, space
BRAILLE6 = {
    'a':0x01,'b':0x03,'c':0x09,'d':0x19,'e':0x11,'f':0x0B,'g':0x1B,'h':0x13,'i':0x0A,'j':0x1A,
    'k':0x05,'l':0x07,'m':0x0D,'n':0x1D,'o':0x15,'p':0x0F,'q':0x1F,'r':0x17,'s':0x0E,'t':0x1E,
    'u':0x25,'v':0x27,'w':0x3A,'x':0x2D,'y':0x3D,'z':0x35,' ':0x00
}
INV6 = {v:k for k,v in BRAILLE6.items()}
def decode_gs8(cipher: str) -> str:
    out = []
    for ch in cipher:
        code = ord(ch)
        if 0x2800 <= code <= 0x28FF:
            dots8 = code - 0x2800
            cap = bool(dots8 & (1 << 6))     # dot7 => uppercase *ngay ô này*
            dots6 = dots8 & 0x3F             # bỏ dot7/8, về 6-dot
            letter = INV6.get(dots6, ' ')
            if cap:
                letter = letter.upper()
            out.append(letter)
        elif ch.isspace() or ch in string.punctuation:
            out.append(ch)
    return title_case_if_not_numbers("".join(out).strip())

# ---------- Wabun (Japanese Morse)-> romaji (subset đủ dùng) ----------
def normalize_words(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        if i > 0 and ch.isupper():
            # Nếu gặp chữ hoa thì chèn khoảng trắng trước
            out.append(" ")
        out.append(ch)
    text = "".join(out)
    
    # Tách từ ra, viết hoa chữ cái đầu, các chữ còn lại viết thường
    words = [w.capitalize() for w in text.split()]
    return " ".join(words)

WABUN_TABLE_JP = """
ア －－・－－ ナ ・－・ ラ ・・・ 
イ ・－ ニ －・－・ リ －－・ 
ウ ・・－ ヌ ・・・・ ル －・－－・ 
エ －・－－－ ネ －－・－ レ －－－ 
オ ・－・・・ ノ ・・－－ ロ ・－・－ 
カ ・－・・ ハ －・・・ ワ －・－ 
キ －・－・・ ヒ －－・・－ ヲ ・－－－ 
ク ・・・－ フ －－・・ ン ・－・－・ 
ケ －・－－ ヘ ・ 〃 ・・ 
コ －－－－ ホ －・・ 。 ・・－－・ 
サ －・－・－ マ －・・－ ー ・－－・－ 
シ －－・－・ ミ ・・－・－ （ －・－－・－ 
ス －－－・－ ム － ） ・－・・－・ 
セ ・－－－・ メ －・・・－ 
ソ －－－・ モ －・・－・ 
タ －・ ヤ ・－－ 
チ ・・－・ ヰ ・－・・－ 
ツ ・－－・ ユ －・・－－ 
テ ・－・－－ ヱ ・－－・・ 
ト ・・－・・ ヨ －－
"""

# chuyển sang dạng dot/dash và parse (tự động tạo code->kana)
def build_wabun_map(table_text: str):
    t = table_text.replace('・', '.').replace('－','-').strip()
    tokens = t.split()
    mapping = {}
    i = 0
    while i < len(tokens)-1:
        kana = tokens[i]
        code = tokens[i+1]
        mapping[code] = kana
        i += 2
    return mapping

CODE_TO_KANA = build_wabun_map(WABUN_TABLE_JP)

# cơ bản katakana -> romaji (monographs). Mở rộng theo nhu cầu.
KANA_TO_ROMAJI = {
 'ア':'a','イ':'i','ウ':'u','エ':'e','オ':'o',
 'カ':'ka','キ':'ki','ク':'ku','ケ':'ke','コ':'ko',
 'サ':'sa','シ':'shi','ス':'su','セ':'se','ソ':'so',
 'タ':'ta','チ':'chi','ツ':'tsu','テ':'te','ト':'to',
 'ナ':'na','ニ':'ni','ヌ':'nu','ネ':'ne','ノ':'no',
 'ハ':'ha','ヒ':'hi','フ':'fu','ヘ':'he','ホ':'ho',
 'マ':'ma','ミ':'mi','ム':'mu','メ':'me','モ':'mo',
 'ヤ':'ya','ユ':'yu','ヨ':'yo',
 'ラ':'ra','リ':'ri','ル':'ru','レ':'re','ロ':'ro',
 'ワ':'wa','ヲ':'wo','ン':'n','ヰ':'wi','ヱ':'we',
 # punctuation / marks
 '。':'.','、':',','ー':'-', '〃':'DAKUTEN'
}

# chuyển CODE->romaji (với KANA->ROMAJI); những code không phải kana (ví dụ '〃' dakuten) giữ dấu hiệu đặc biệt
CODE_TO_ROMAJI = {}
for code,kana in CODE_TO_KANA.items():
    CODE_TO_ROMAJI[code] = KANA_TO_ROMAJI.get(kana, kana)

# tìm mã dakuten (nếu có) — trong bảng ở trên '〃' được ký hiệu là '..' (thường)
DAKUTEN_CODES = [code for code,kana in CODE_TO_KANA.items() if kana == '〃']
# (nếu rỗng thì bỏ qua)
DAKUTEN_CODES = set(DAKUTEN_CODES)

# áp dakuten lên romaji đơn âm (rất cơ bản): ka->ga, sa->za (shi->ji), ta->da (chi->ji/ dji), ha->ba, hoặc ha+handakuten->pa
def apply_dakuten_to_romaji(base: str) -> str:
    # base là một chuỗi romaji như "ka","shi","tsu",...
    # chuyển đổi cơ bản (không xử lý hoàn hảo mọi trường hợp yōon phức tạp)
    if base.startswith("k"):
        return "g" + base[1:]
    if base.startswith("s"):
        # shi -> ji ; sa -> za ; su->zu
        if base == "shi": return "ji"
        return "z" + base[1:]
    if base.startswith("t"):
        # chi -> dji/ji, tsu -> dzu/zu
        if base == "chi": return "ji"
        if base == "tsu": return "dzu"
        return "d" + base[1:]
    if base.startswith("h"):
        return "b" + base[1:]
    # nếu không match, trả về base (fallback)
    return base


HANDAKUTEN_CODES = [code for code,kana in CODE_TO_KANA.items() if kana == '゜']
HANDAKUTEN_CODES = set(HANDAKUTEN_CODES)

# Thêm vào bảng nếu thiếu:
CODE_TO_KANA[".."]    = "゛"   # dakuten
CODE_TO_KANA["..--."] = "゜"   # handakuten

DAKUTEN_CODES    = {code for code,kana in CODE_TO_KANA.items() if kana in {"〃","゛"}}
HANDAKUTEN_CODES = {code for code,kana in CODE_TO_KANA.items() if kana == "゜"}

# Bảng chuyển cụ thể, xử lý các âm đặc biệt trước (shi/chi/tsu/fu)
_DAKUTEN_ROMAJI = {
    # K → G
    "ka":"ga","ki":"gi","ku":"gu","ke":"ge","ko":"go",
    # S → Z (shi → ji)
    "sa":"za","shi":"ji","su":"zu","se":"ze","so":"zo",
    # T → D (chi/tsu → ji/zu)
    "ta":"da","chi":"ji","tsu":"zu","te":"de","to":"do",
    # H → B (fu → bu)
    "ha":"ba","hi":"bi","fu":"bu","he":"be","ho":"bo",
}
_HANDAKUTEN_ROMAJI = {
    # H → P (fu → pu)
    "ha":"pa","hi":"pi","fu":"pu","he":"pe","ho":"po",
}

def apply_dakuten_to_romaji(base: str) -> str:
    b = base.lower()
    # ưu tiên match dài: shi/chi/tsu/fu
    for k in ("shi","chi","tsu","fu","ka","ki","ku","ke","ko",
              "sa","su","se","so","ta","te","to","ha","hi","he","ho"):
        if b.startswith(k):
            return _DAKUTEN_ROMAJI.get(k, b).replace(k, _DAKUTEN_ROMAJI.get(k, k), 1)
    # fallback thô theo phụ âm đầu
    if b.startswith("k"): return "g"+b[1:]
    if b.startswith("s"): return "z"+b[1:] if b!="shi" else "ji"
    if b.startswith("t"): 
        if b=="chi": return "ji"
        if b=="tsu": return "zu"
        return "d"+b[1:]
    if b[0] in ("h","f"): return "b"+b[1:]
    return b

def apply_handakuten_to_romaji(base: str) -> str:
    b = base.lower()
    # ưu tiên fu
    for k in ("fu","ha","hi","he","ho"):
        if b.startswith(k):
            return _HANDAKUTEN_ROMAJI.get(k, b).replace(k, _HANDAKUTEN_ROMAJI.get(k, k), 1)
    if b[0] in ("h","f"):  # fallback
        return "p"+b[1:]
    return b

def decode_wabun(input_text: str) -> str:
    """
    Gộp trực tiếp: [kana] + [dakuten/handakuten] => romaji đã đổi (vd: FU + .. => BU).
    Latin giữ nguyên (uppercase). Token cách nhau bằng space.
    """
    tokens = input_text.split()
    out = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        # Morse?
        if all(ch in ".-" for ch in tok):
            kana = CODE_TO_KANA.get(tok)
            if kana is None:
                out.append("?")
                i += 1
                continue

            # marker riêng lẻ → bỏ (chỉ có tác dụng khi đứng sau kana)
            if tok in DAKUTEN_CODES or tok in HANDAKUTEN_CODES:
                # không có kana trước đó thì bỏ qua
                i += 1
                continue

            rom = KANA_TO_ROMAJI.get(kana, kana)

            # nhìn trước: nếu kế tiếp là dakuten/handakuten thì gộp luôn
            if i+1 < len(tokens) and all(ch in ".-" for ch in tokens[i+1]):
                nxt = tokens[i+1]
                if nxt in DAKUTEN_CODES:
                    rom = apply_dakuten_to_romaji(rom)
                    i += 1  # nuốt marker
                elif nxt in HANDAKUTEN_CODES:
                    rom = apply_handakuten_to_romaji(rom)
                    i += 1  # nuốt marker

            out.append(rom)

        else:
            # Latin (hoặc token khác) giữ nguyên nhưng uppercase
            out.append(tok)

        i += 1

    result = "".join(out)
    fixed = []
    for j, ch in enumerate(result):
        if j > 0 and ch.isupper() and result[j-1] not in (" ",):
            fixed.append(" ")
        fixed.append(ch)
    return "".join(fixed)




# ---------- Spoon -> Brainfuck -> run ----------
SPOON_MAP = collections.OrderedDict([
    ("00101111", "TERMINATE"),  # optional
    ("00101110", "DUMP"),       # optional
    ("0010110", ","),           # input
    ("001010", "."),            # output
    ("0011", "]"),
    ("00100", "["),
    ("011", "<"),
    ("010", ">"),
    ("000", "-"),
    ("1", "+"),
])
def spoon_to_bf(code: str) -> str:
    bits = re.sub(r"[^01]", "", code)
    i=0; out=[]
    keys = list(SPOON_MAP.keys())
    while i < len(bits):
        matched=False
        for k in keys:  # greedy longest-match
            if bits.startswith(k, i):
                cmd = SPOON_MAP[k]
                if cmd in (".",",","[","]","+","-","<",">"):
                    out.append(cmd)
                # ignore DUMP/TERMINATE silently
                i += len(k); matched=True; break
        if not matched:
            # skip one char if garbage
            i += 1
    return "".join(out)

def run_bf(bf: str, input_data: bytes = b"") -> str:
    tape = [0]*30000; p=0; out=[]; inp=list(input_data)[::-1]
    # precompute bracket jumps ...
    i=0; n=len(bf); steps=0; max_steps=2_000_000
    while i<n and steps < max_steps:
        steps += 1
        ch=bf[i]
        if ch==">": p+=1
        elif ch=="<":
            if p>0: p-=1   # <- không cho p âm
        elif ch=="+": tape[p]=(tape[p]+1)&0xFF
        elif ch=="-": tape[p]=(tape[p]-1)&0xFF
        elif ch==".": out.append(chr(tape[p]))
        elif ch==",": tape[p]=inp.pop() if inp else 0
        elif ch=="[":
            if tape[p]==0: i=jump_fwd[i]
        elif ch=="]":
            if tape[p]!=0: i=jump_back[i]
        i+=1
    return "".join(out)

def decode_spoon(cipher: str) -> str:
    bf = spoon_to_bf(cipher)
    ans = run_bf(bf)
    return title_case_if_not_numbers(ans.strip())

# ---------- Shankar (Slumdog) ----------
# A..Z -> X W Y A Z B C D E F G H I K L M N O P J R S T U V
SHANKAR_SUB = "XWYAZBCDQEFGHIKLMNOPJRSTUV"
def decode_shankar(cipher: str) -> str:
    # dùng bảng giải mã ngược theo dCode
    plain_alpha="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    table = {c:p for c,p in zip(SHANKAR_SUB, plain_alpha)}
    out=[]
    for ch in cipher.upper():
        if ch.isalpha(): out.append(table.get(ch, ch))
        elif ch.isspace(): out.append(" ")
    return title_case_if_not_numbers("".join(out).strip())

# ---------- Bibi-binaire ----------
# 16 âm: HO,HA,HE,HI, BO,BA,BE,BI, KO,KA,KE,KI, DO,DA,DE,DI  (0..F)
BIBI = ["HO","HA","HE","HI","BO","BA","BE","BI","KO","KA","KE","KI","DO","DA","DE","DI"]
BIBI_MAP = {s:i for i,s in enumerate(BIBI)}
def decode_bibi(cipher: str) -> str:
    toks = re.findall(r"[A-Za-z]+", cipher.upper())
    # ghép đôi kí tự để thành âm (vd BI-DA-HO)
    syll=[]
    for t in toks:
        # t có thể đã là âm hợp lệ (2 ký)
        if t in BIBI_MAP: syll.append(t); continue
        # else cắt 2-chars
        for i in range(0, len(t), 2):
            chunk = t[i:i+2]
            if chunk in BIBI_MAP: syll.append(chunk)
    # thành HEX rồi sang dec chuỗi (trả số – không Title Case)
    hexd = "".join("0123456789ABCDEF"[BIBI_MAP[s]] for s in syll)
    # Nếu chỉ là 1 số, in ra dạng thập phân; nếu là chuỗi nhiều số (cách bởi space), giữ HEX
    if hexd:
        try:
            val = int(hexd, 16)
            return str(val)
        except Exception:
            return hexd
    return cipher

# ---------- Dispatcher ----------
def solve_one(hint: str, cipher: str) -> str:
    h = hint.strip().lower()

    # map alias theo hint
    if "charabia" in h or "mirror" in h and "latin" in h:
        return decode_charabia_latin(cipher)

    if ("trith" in h or "trithème" in h or "trithemius" in h
        or ("cascade" in h and ("three" in h or "threes" in h))):
        return decode_trithemius(cipher)

    if "otan" in h or "nato" in h:
        return decode_nato(cipher)

    if ("prime" in h) or ("nguyên tố" in h) or ("indivisible" in h):
        return decode_prime(cipher)

    if "gs8" in h or "braille" in h:
        return decode_gs8(cipher)

    # --- Wabun / Japanese Morse ---
    if ("wabun" in h) or ("japanese" in h and "morse" in h) or ("morse" in h and "japanese" in h) or ("accent" in h and "japanese" in h):
        return decode_wabun(cipher)

    if "spoon" in h:
        return decode_spoon(cipher)

    if ("shankar" in h or "slumdog" in h
    or ("eastern" in h and ("abc" in h or "abcs" in h or "alphabet" in h))):
        return decode_shankar(cipher)

    if "bibi" in h or "boby" in h or ("pair" in h and ("tone" in h or "alternating" in h)):
        return decode_bibi(cipher)

    # Nếu cipher toàn số/khoảng trắng/slash/dấu +-, thử prime trước
    if re.fullmatch(r"[0-9\s/+\-]+", cipher.strip()):
        ansp = decode_prime(cipher)
        if any(ch.isalpha() for ch in ansp):
            return ansp

    # fallback: thử dần vài cách phổ biến
    for fn in (decode_charabia_latin, decode_trithemius, decode_nato, decode_prime, decode_gs8):
        try:
            ans = fn(cipher)
            if ans and ans.strip(): return ans
        except Exception: pass
    return cipher.strip()

# ---------- NC loop ----------
def receive_flag(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, port))
    buf = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    finally:
        s.close()

    text = buf.decode(errors="ignore")
    # tìm flag dạng flag{...}
    m = re.search(r"flag\{.*?\}", text, flags=re.I)
    if m:
        return m.group(0)
    return text.strip()


def run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(60)
    s.connect((HOST, PORT))
    buf = b""
    log_all = []   # tích lũy mọi thứ server gửi (đã decode)
    rounds = 0
    try:
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break  # server đóng
                buf += chunk
            except socket.timeout:
                # timeout đọc: thử check flag trong những gì đã có
                pass

            text = keep_unicode_printable(buf.decode(errors="ignore"))
            if text:
                log_all.append(text)

            # bắt flag ngay khi thấy
            joined = "".join(log_all)
            mflag = re.search(r"PTITCTF\{[^}\r\n]*\}", joined, flags=re.I)
            if mflag:
                print("FLAG:", mflag.group(0))
                break

            # xử lý hint/cipher gần nhất
            hint_match = re.findall(r"hint:\s*(.+)", text, flags=re.I)
            ciph_match = re.findall(r"cipher:\s*(.+)", text, flags=re.I)

            if hint_match and ciph_match:
                hint = hint_match[-1].strip()
                cipher = ciph_match[-1].rstrip()
                ans = solve_one(hint, cipher)
                print(f"[hint] {hint}")
                print(f"[cipher] {cipher}")
                print(f"[answer] {ans}")
                s.sendall((ans + "\n").encode())
                rounds += 1
                buf = b""  # clear buffer vòng hiện tại để chờ vòng sau

        # sau khi socket đóng, check lại toàn bộ log
        joined = "".join(log_all)
        mflag = re.search(r"PTITCTF\{[^}\r\n]*\}", joined, flags=re.I)
        if mflag:
            print("FLAG:", mflag.group(0))
        else:
            # in phần cuối log để tham khảo
            tail = joined[-1000:]
            print("Server output (tail):", tail if tail else "(empty)")
    finally:
        s.close()
    print(f"Done {rounds} rounds.")

if __name__ == "__main__":
    run()
