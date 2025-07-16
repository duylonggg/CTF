# Write Up

## Phân tích

Ta tìm vào phần `text`, thấy file log có nội dung sau:

```txt
[08:12] <yone786> Ok, let me give you the keys for the light.
[08:12] <avidreader13> I’m ready.
[08:15] <yone786> First it’s steghide.
[08:15] <yone786> Use password: akalibardzyratrundle
[08:16] <avidreader13> Huh, is that a different language?
[08:18] <yone786> Not really, don’t worry about it.
[08:18] <yone786> The next is the encryption. Use openssl, AES, cbc.
[08:19] <yone786> salt=0f3fa17eeacd53a9 key=58593a7522257f2a95cce9a68886ff78546784ad7db4473dbd91aecd9eefd508 iv=7a12fd4dc1898efcd997a1b9496e7591
[08:19] <avidreader13> Damn! Ever heard of passphrases?
[08:19] <yone786> Don’t trust em. I seed my crypto keys with uuids.
[08:20] <avidreader13> Ok, I get it, you’re paranoid.
[08:20] <avidreader13> But I have no idea if that would work.
[08:21] <yone786> Haha, I’m not paranoid. I know you’re not a good hacker dude.
[08:21] <avidreader13> Is there a better way?
[08:22] * yone786 yawns.
[08:24] <yone786> You’re ok at hacking. I’m good at writing code and using it
[08:24] <avidreader13> What language are you writing in?
[08:26] <yone786> C
[08:26] <avidreader13> Oh, I see.
[08:26] <yone786> I’m glad you like it. I’m sure you wouldn’t understand half of what I was doing.
[08:28] <avidreader13> I understand enough, but I do wish you wouldn’t take so much time with it.
[08:28] <yone786> Sorry. Well, I wish you could learn some things.
[08:29] <avidreader13> But it’s an incredible amount of time you spend on it.
[08:29] <yone786> Haha, don’t take it like that.


------------------------------METADATA------------------------------
```

Nhận thấy nó có sử dụng `steghide` và `openssl`, chúng ta sẽ đi theo 2 hướng này

Đầu tiên là `steghide`, tools này chỉ dùng được cho những file ảnh như `.jpg`, `.bmp` hay `.png`

Từ đó tìm vào `Images`, thấy có 4 file `.bmp`, ta extected nó về máy

Thử `steghide` với từng file một

```bash
$ steghide extract -sf 1.bmp -p akalibardzyratrundle
wrote extracted data to "les-mis.txt.enc".

$ steghide extract -sf 2.bmp -p akalibardzyratrundle
wrote extracted data to "dracula.txt.enc".

$ steghide extract -sf 3.bmp -p akalibardzyratrundle
wrote extracted data to "frankenstein.txt.enc".

$ steghide extract -sf 7.bmp -p akalibardzyratrundle
steghide: could not extract any data with that passphrase!
```

Vậy là có 3 file chứa dữ liệu ẩn, hãy đi vào từng file

Chúng chính là những file mã hóa AES-CBC nên hãy dùng dòng lệnh trên để giải mã từng file

```bash
$ openssl enc -aes-256-cbc -d \
  -K 58593a7522257f2a95cce9a68886ff78546784ad7db4473dbd91aecd9eefd508 \
  -iv 7a12fd4dc1898efcd997a1b9496e7591 \
  -in dracula.txt.enc -out dracula.txt

$ openssl enc -aes-256-cbc -d \
  -K 58593a7522257f2a95cce9a68886ff78546784ad7db4473dbd91aecd9eefd508 \
  -iv 7a12fd4dc1898efcd997a1b9496e7591 \
  -in frankenstein.txt.enc -out frankenstein.txt

$ openssl enc -aes-256-cbc -d \
  -K 58593a7522257f2a95cce9a68886ff78546784ad7db4473dbd91aecd9eefd508 \
  -iv 7a12fd4dc1898efcd997a1b9496e7591 \
  -in les-mis.txt.enc -out les-mis.txt
```

Có vẻ như không có manh mối gì mấy

Tiếp tục tiếp kiếm file log và thấy 1 file có nội dung như sau

```txt
I keep forgetting this, but it starts like: yasuoaatrox...
```

Có vẻ như đấy sẽ là password cho file `7.bmp`

Ở đây chúng ta sẽ phải brute-force mật khẩu

Đầu tiên chúng ta cần 1 file các tướng LoL đã

```txt
Aatrox
Ahri
Akali
Akshan
Alistar
Amumu
Anivia
Annie
Aphelios
Ashe
Aurelion Sol
Azir
Bard
Bel'Veth
Blitzcrank
Brand
Braum
Caitlyn
Camille
Cassiopeia
Cho'Gath
Corki
Darius
Diana
Dr. Mundo
Draven
Ekko
Elise
Evelynn
Ezreal
Fiddlesticks
Fiora
Fizz
Galio
Gangplank
Garen
Gnar
Gragas
Graves
Gwen
Hecarim
Heimerdinger
Illaoi
Irelia
Ivern
Janna
Jarvan IV
Jax
Jayce
Jhin
Jinx
Kai'Sa
Kalista
Karma
Karthus
Kassadin
Katarina
Kayle
Kayn
Kennen
Kha'Zix
Kindred
Kled
Kog'Maw
K'Sante
LeBlanc
Lee Sin
Leona
Lillia
Lissandra
Lucian
Lulu
Lux
Malphite
Malzahar
Maokai
Master Yi
Milio
Miss Fortune
Mordekaiser
Morgana
Nami
Nasus
Nautilus
Neeko
Nidalee
Nilah
Nocturne
Nunu & Willump
Olaf
Orianna
Ornn
Pantheon
Poppy
Pyke
Qiyana
Quinn
Rakan
Rammus
Rek'Sai
Rell
Renata Glasc
Renekton
Rengar
Riven
Rumble
Ryze
Samira
Sejuani
Senna
Seraphine
Sett
Shaco
Shen
Shyvana
Singed
Sion
Sivir
Skarner
Sona
Soraka
Swain
Sylas
Syndra
Tahm Kench
Taliyah
Talon
Taric
Teemo
Thresh
Tristana
Trundle
Tryndamere
Twisted Fate
Twitch
Udyr
Urgot
Varus
Vayne
Veigar
Vel'Koz
Vex
Vi
Viego
Viktor
Vladimir
Volibear
Warwick
Wukong
Xayah
Xerath
Xin Zhao
Yasuo
Yone
Yorick
Yuumi
Zac
Zed
Zeri
Ziggs
Zilean
Zoe
Zyra
```

Tiếp theo sẽ là tạo script sinh ra mật khẩu

```python
with open('lol_champs.txt') as f:
    lines = f.read().splitlines()

with open("lol_wordlist.txt", "a") as g:
    for x in lines:
        for y in lines:
            pw = ("yasuoaatrox"+x+y+"\n").lower()
            g.write(pw)
```

Bây giờ chúng ta đã có file `lol_wordlist.txt` chứa mật khẩu

Brute-force thôi

```python
import subprocess

def dict_attack(wordlist):
    for x in wordlist:
        try:
            subprocess.check_output(["steghide", "extract", 
                                     "-sf", "7.bmp", "-p", x], 
                                     stderr=subprocess.DEVNULL)
            return x
        except subprocess.CalledProcessError:
            pass
    return 0

if __name__ == "__main__":
    with open('lol_wordlist.txt') as f:
        lines = f.read().splitlines()

    passphrase = dict_attack(lines)
    
    if passphrase:
        print("Success! Passphrase is " + passphrase)
    else:
        print("Sorry, no cigar.")
```

Chạy file `brute_force.py`

```bash
$ python3 brute_force.py
Success! Passphrase is yasuoaatroxashecassiopeia
```

OK đã có pasword thì sẽ dùng được `steghide` cho `7.bmp`

Giải mã bằng `steghide` xong thì sẽ có file `ledger.1.txt.enc`

Thử giải mã tiếp bằng `openssl`

```bash
$ openssl enc -d -aes256 -in ledger.1.txt.enc -out ledger.1.txt \
-S 0f3fa17eeacd53a9 \
-K 58593a7522257f2a95cce9a68886ff78546784ad7db4473dbd91aecd9eefd508 \
-iv 7a12fd4dc1898efcd997a1b9496e7591
bad decrypt
40C7F338177F0000:error:1C800064:Provider routines:ossl_cipher_unpadblock:bad decrypt:../providers/implementations/ciphers/ciphercommon_block.c:107:
```

Có vẻ là còn nhiều thứ ẩn giấu nữa

Đoạn này thì tôi đọc Write Up do mò kim đáy bể lâu quá

Thì đoạn này người ta sẽ tìm trong `Slack Space`, phần này tôi đã nói rồi, `Slack Space` có thể chứa file đã xóa nên có thể dữ liệu đã được ấn giấu trong đó

Chúng ta tìm được file `1.txt-slack` chứa nội dung như sau

```txt

1.txt-
slack 01010010100.01001001000100.01001010000100.00101010010101.01000100100100.00100100000100.01000100000101.01000100001010.00000100000001.00001001010000.00000100010010.01000100010010.01001001001000.10001001000101.01001001010000.00001001000100.01001001010001.00000100000010.01000100010000.00001001001000.10000100010100.01000000010100.01001010000010.00101001010000.00001010101000.10000100100100.00101001000100.01000100010100.01001001010001.00000100010010.01000100010000.00001001000101.01000100010010.01000100010001.00000100001000.10001001000101.01001001001010.00000100010100.01000100000100.01000100010001.00000100000001.00000100001010.00000100010001.00001001000100.01000100000001.00000100001010.00000100001000.10000100000001.00000100010010.01001001001010.00000100000100.01000100010001.00000100001000.10001001010000.00001001010000.00000100000101.01001001000100.01000100010010.01000100010010.01001001000100.01000100010010.01000100000101.01001001000100.01001001001010.00000100010100.01000100010001.00000100000100.01000100000100.01000100000010.01000100010001.00001001000101.01000100010010.01000100000010.01001001010001.00001001001010.00001001001000.10000100000100.01001001000101.01001001000101.01000100010010.01001001010000.00000100010010.01001001001000.10001001000100.01000100010010.01000100010001.00000100000101.01000100010000.00001001001010.00001001000100.01000000010100.01001001010101.01001010100010.00100100100100.00100100010100.01000100000001.00000100010010.01000100001000.10000100001010.00000100010010.01001001010000.00000100001000.10000100010010.01001001010001.00001001001000.10000100010010.01001001001010.00001001000101.01000100000010.01001001001000.10000100001010.00001001000100.01000100001000.10000100010000.00001001010001.00000100000010.01000100010010.01001001010001.00000100000001.00001001010001.00001001010000.00001001000101.01000100000010.01000100000010.01000100010100.01001001010001.00000000010100.010
```

Trong `x-log` ta thấy `browsing-history.log` có nội dung

```txt
www.google.com
https://www.google.com/search?q=number+encodings&source=hp&ei=WeC9Y77KJ_iwqtsP0sGu6A0&iflsig=AK50M_UAAAAAY73uaRxDkbHRUH8jn4OVhOgM8riUqvVI&ved=0ahUKEwj-2r_EgL78AhV4mGoFHdKgC90Q4dUDCAk&uact=5&oq=number+encodings&gs_lcp=Cgdnd3Mtd2l6EAMyBggAEBYQHjIFCAAQhgMyBQgAEIYDMgUIABCGAzIFCAAQhgM6DgguEIAEELEDEIMBENQCOgsIABCABBCxAxCDAToRCC4QgAQQsQMQgwEQxwEQ0QM6CAgAELEDEIMBOgsILhCABBCxAxCDAToFCAAQgAQ6CAgAEIAEELEDOggILhCABBDUAjoHCAAQgAQQCjoHCC4QgAQQClAAWI0VYPAXaABwAHgDgAHDA4gB-iKSAQkwLjMuNS40LjOYAQCgAQE&sclient=gws-wiz
https://en.wikipedia.org/wiki/Church_encoding
https://cs.lmu.edu/~ray/notes/numenc/
https://www.wikiwand.com/en/Golden_ratio_base
```

Thấy người này tìm kiếm tỉ lệ vàng (chắc thế) nên tôi tìm thử

Nhận được 1 bảng như sau

```txt
Decimal	Powers of φ		Base φ
1	φ0			1     
2	φ1 + φ−2		10.01  
3	φ2 + φ−2		100.01  
4	φ2 + φ0 + φ−2		101.01  
5	φ3 + φ−1 + φ−4		1000.1001
6	φ3 + φ1 + φ−4		1010.0001
7	φ4 + φ−4		10000.0001
8	φ4 + φ0 + φ−4		10001.0001
9	φ4 + φ1 + φ−2 + φ−4	10010.0101
10	φ4 + φ2 + φ−2 + φ−4	10100.0101
```

Vậy đây chính là tỉ lệ 

script giải mã

```python 
from math import ceil
from scipy.constants import golden

def phinary_to_decimal(phigit):
    integer, fraction = phigit.split(".")
    integer = integer[::-1] #reverse integer string

    number = 0

    for i, x in enumerate(integer):
        if x == "1":
            number = number + golden ** (i)
    for i, x in enumerate(fraction):
        if x == "1":
            number = number + golden ** -(i+1)
    
    return number

if __name__ == "__main__":
    with open("phi_enc.txt") as f:
        string = f.read()
        string = string.rstrip("\n")
    
    #Split string every 15th character
    phigits = [string[i: i + 15] for i in range(0, len(string), 15)]
    
    decoded_phi = []

    for phigit in phigits:
        decoded_phi.append(ceil(phinary_to_decimal(phigit)))

    print(''.join(map(chr,decoded_phi)))
```

Mỗi `phi` sẽ có độ dài 15 ký tự `000000000.00000` 

Ví dụ: "100.01" → φ² + φ⁻²

Vậy nên code trên sẽ giải mã từng `phidigit` theo cách đó, bên phải dấu "." sẽ tăng dần theo số dương, bên trái sẽ giảm dần theo số âm

Chạy file giải mã

```bash
$ python3 phi_decoder.py
salt=2350e88cbeaf16c9
key=a9f86b874bd927057a05408d274ee3a88a83ad972217b81fdc2bb8e8ca8736da
iv=908458e48fc8db1c5a46f18f0feb119f
```

Vậy là đã có key mới cho `openssl`

Chạy `openssl`

```bash
$ openssl enc -d -aes256 -in ledger.1.txt.enc -out ledger.1.txt \
-S 2350e88cbeaf16c9 \
-K a9f86b874bd927057a05408d274ee3a88a83ad972217b81fdc2bb8e8ca8736da \
-iv 908458e48fc8db1c5a46f18f0feb119f \
| cat ledger.1.txt
avidreader13                                                 PAID
    Les Mis, Dracula, Frankenstein, Swiss Family
    Robinson, Don Quixote, A Tale of Two Cities

513u7h                                                       PAID
    Don Quixote

masterOfSp1n                                                 PAID
    Swiss Family Robinson, A Tale of Two Cities

AwolCoyote                                                   PAID
    Les Mis, Dracula

picoCTF                                                    UNPAID
    picoCTF{f473_53413d_40405b89}
```

Flag: picoCTF{f473_53413d_40405b89}
