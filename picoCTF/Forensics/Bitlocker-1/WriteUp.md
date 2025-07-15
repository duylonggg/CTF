# Write Up

---

## Trích xuất hash

```bash
# bitlocker2john -i bitlocker-1.dd > hash.txt

Signature found at 0x3
Version: 8
Invalid version, looking for a signature with valid version...

Signature found at 0x2195000
Version: 2 (Windows 7 or later)

VMK entry found at 0x21950c5

VMK encrypted with Recovery Password found at 0x21950e6
Searching AES-CCM from 0x2195102
Trying offset 0x2195195....
VMK encrypted with AES-CCM!!

VMK entry found at 0x2195241

VMK encrypted with User Password found at 2195262
VMK encrypted with AES-CCM

Signature found at 0x2c1d000
Version: 2 (Windows 7 or later)

VMK entry found at 0x2c1d0c5

VMK entry found at 0x2c1d241

Signature found at 0x373a000
Version: 2 (Windows 7 or later)

VMK entry found at 0x373a0c5

VMK entry found at 0x373a241
```

```bash
# cat hash.txt
Encrypted device bitlocker-1.dd opened, size 100MB
Salt: 2b71884a0ef66f0b9de049a82a39d15b
RP Nonce: 00be8a46ead6da0106000000
RP MAC: a28f1a60db3e3fe4049a821c3aea5e4b
RP VMK: a1957baea68cd29488c0f3f6efcd4689e43f8ba3120a33048b2ef2c9702e298e4c260743126ec8bd29bc6d58

UP Nonce: d04d9c58eed6da010a000000
UP MAC: 68156e51e53f0a01c076a32ba2b2999a
UP VMK: fffce8530fbe5d84b4c19ac71f6c79375b87d40c2d871ed2b7b5559d71ba31b6779c6f41412fd6869442d66d


User Password hash:
$bitlocker$0$16$cb4809fe9628471a411f8380e0f668db$1048576$12$d04d9c58eed6da010a000000$60$68156e51e53f0a01c076a32ba2b2999afffce8530fbe5d84b4c19ac71f6c79375b87d40c2d871ed2b7b5559d71ba31b6779c6f41412fd6869442d66d
Hash type: User Password with MAC verification (slower solution, no false positives)
$bitlocker$1$16$cb4809fe9628471a411f8380e0f668db$1048576$12$d04d9c58eed6da010a000000$60$68156e51e53f0a01c076a32ba2b2999afffce8530fbe5d84b4c19ac71f6c79375b87d40c2d871ed2b7b5559d71ba31b6779c6f41412fd6869442d66d
Hash type: Recovery Password fast attack
$bitlocker$2$16$2b71884a0ef66f0b9de049a82a39d15b$1048576$12$00be8a46ead6da0106000000$60$a28f1a60db3e3fe4049a821c3aea5e4ba1957baea68cd29488c0f3f6efcd4689e43f8ba3120a33048b2ef2c9702e298e4c260743126ec8bd29bc6d58
Hash type: Recovery Password with MAC verification (slower solution, no false positives)
$bitlocker$3$16$2b71884a0ef66f0b9de049a82a39d15b$1048576$12$00be8a46ead6da0106000000$60$a28f1a60db3e3fe4049a821c3aea5e4ba1957baea68cd29488c0f3f6efcd4689e43f8ba3120a33048b2ef2c9702e298e4c260743126ec8bd29bc6d58
```

Chọn hash `Recovery Password fast attack`

---

## Giải mã

Tạo 1 file `crackme.txt` để lưu mã hash

```bash
# nano crackme.txt

# cat crackme.txt
$bitlocker$1$16$cb4809fe9628471a411f8380e0f668db$1048576$12$d04d9c58eed6da010a000000$60$68156e51e53f0a01c076a32ba2b2999afffce8530fbe5d84b4c19ac71f6c79375b87d40c2d871ed2b7b5559d71ba31b6779c6f41412fd6869442d66d
```

Crack bằng `john` và `rockyou.txt`

```bash
# john --wordlist=/usr/share/wordlists/rockyou.txt crackme.txt
```

Kiểm tra mật khẩu

```bash
$ john --show crackme.txt
?:jacqueline

1 password hash cracked, 0 left
```

---

## Mount 

```bash
sudo dislocker -V bitlocker-1.dd -u"jacqueline" -- dislocker-mount
sudo mount -o loop,ro dislocker-mount/dislocker-file clear-mount
```

---

## Tìm trong phân vùng

```bash
# ls clear-mount/
'$RECYCLE.BIN'   flag.txt  'System Volume Information'
```

---

## Flag

Flag: picoCTF{us3_b3tt3r_p4ssw0rd5_pl5!_3242adb1}
