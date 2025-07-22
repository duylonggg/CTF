# Write Up

```bash
Specialer$ echo /home/ctf-player/*
/home/ctf-player/abra /home/ctf-player/ala /home/ctf-player/sim

Specialer$ echo /home/ctf-player/abra/*
/home/ctf-player/abra/cadabra.txt /home/ctf-player/abra/cadaniel.txt
Specialer$ echo /home/ctf-player/ala/*
/home/ctf-player/ala/kazam.txt /home/ctf-player/ala/mode.txt
Specialer$ echo /home/ctf-player/sim/*
/home/ctf-player/sim/city.txt /home/ctf-player/sim/salabim.txt

Specialer$ for f in /home/ctf-player/*/*.txt; do
>   echo "=== $f ==="
>   echo $(<"$f")
> done
=== /home/ctf-player/abra/cadabra.txt ===
Nothing up my sleeve!
=== /home/ctf-player/abra/cadaniel.txt ===
Yes, I did it! I really did it! I'm a true wizard!
=== /home/ctf-player/ala/kazam.txt ===
return 0 picoCTF{y0u_d0n7_4ppr3c1473_wh47_w3r3_d01ng_h3r3_38f5cc78}
=== /home/ctf-player/ala/mode.txt ===
Yummy! Ice cream!
=== /home/ctf-player/sim/city.txt ===
05ed181c-4aa0-4d4a-8505-2fe6ca9097d3
=== /home/ctf-player/sim/salabim.txt ===
#He was so kind, such a gentleman tied to the oceanside#
```
