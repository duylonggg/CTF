# Write Up

```bash
tshark -r file-1.pcapng -Y "tcp.flags.syn==1 and tcp.flags.ack==0" -T fields -e ip.dst | sort | uniq
```

Flag: BDSEC{2}