# Write Up

## Binwalk

```bash
$ binwalk stick.img

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
404992        0x62E00         gzip compressed data, has original file name: "flag.txt", from Unix, last modified: 2025-07-17 22:27:22
```

---

## Extract

```bash
$ binwalk -e stick.img

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
404992        0x62E00         gzip compressed data, has original file name: "flag.txt", from Unix, last modified: 2025-07-17 22:27:22
```

---

## Get Flag

```bash
$ cat _stick.img.extracted/flag.txt
scriptCTF{1_l0v3_m461c_7r1ck5}
```

Flag: scriptCTF{1_l0v3_m461c_7r1ck5}