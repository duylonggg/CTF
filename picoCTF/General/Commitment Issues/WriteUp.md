# Write Up

Check log

```bash
$ git log
commit a6dca68e4310585eac3b5c9caf0f75967dfe972c (HEAD -> master)
Author: picoCTF <ops@picoctf.com>
Date:   Sat Mar 9 21:10:06 2024 +0000

    remove sensitive info

commit e720dc26a1a55405fbdf4d338d465335c439fb3e
Author: picoCTF <ops@picoctf.com>
Date:   Sat Mar 9 21:10:06 2024 +0000

    create flag
```

Xem commit 

```bash
$ git show e720dc26a1a55405fbdf4d338d465335c439fb3e:message.txt
picoCTF{s@n1t1z3_7246792d}
```

Flag: picoCTF{s@n1t1z3_7246792d}
