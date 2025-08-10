# Write Up

`tshark`

```bash
┌──(kali㉿kali)-[/mnt/d/Documents/CTF/BDSecCTF/BDSec CTF 2025/Ports]
└─$ tshark -r file-1.pcapng -Y "ip.src==192.168.1.5 and tcp.flags.syn==1 and tcp.flags.ack==1" -T fields -e tcp.srcport | sort -n | uniq
22
80
7426

┌──(kali㉿kali)-[/mnt/d/Documents/CTF/BDSecCTF/BDSec CTF 2025/Ports]
└─$ tshark -r file-1.pcapng -Y "ip.src==192.168.1.5 and tcp.flags.syn==1 and tcp.flags.ack==1" -T fields -e tcp.srcport | sort -n | uniq | wc -l
3
```

Flag: BDSEC{3}
