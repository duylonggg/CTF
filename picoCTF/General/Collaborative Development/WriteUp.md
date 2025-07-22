# Write Up

```bash
$ git branch -a
  feature/part-1
  feature/part-2
  feature/part-3
* main

$ git show feature/part-1:flag.py
print("Printing the flag...")
print("picoCTF{t3@mw0rk_", end='')

$ git show feature/part-2:flag.py
print("Printing the flag...")
print("m@k3s_th3_dr3@m_", end='')

$ git show feature/part-3:flag.py
print("Printing the flag...")
print("w0rk_4c24302f}")
```

Flag: picoCTF{t3@mw0rk_m@k3s_th3_dr3@m_w0rk_4c24302f}
