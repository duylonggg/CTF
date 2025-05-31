# Write-Up

## 1. Challenge Analysis

**Original Description:**
> We have caught signs that the server operated by Dream Company has been hacked. Details are unknown, but the malware penetrated the developer PC through a central server, and as a result, it was determined that login information sensitive to network data was leaked every time the developer PC was logged in. Connect to the PC where the penetration has been completed, analyze the malware, find the file used in the penetration, and find the flag!

---

## 2. Network Tracing

Before tracing traffic, determine the source IP address using:

```bash
$ hostname -I
```

Then use `tcpdump` to monitor outgoing packets:

```bash
$ tcpdump -i any src 10.254.0.106
```

To reduce noise from common or irrelevant services, filter out known ports:

```bash
$ tcpdump -i any src 10.254.0.106 and not dst port 22 and not dst port 53 and not dst port 9447
```

Open a second terminal window and initiate a new SSH login session. The reason is that the challenge states data is leaked when the developer PC logs in — so we want to capture that exact moment.

After logging in, a suspicious packet appears:

```txt
10:04:59.575071 IP 10.254.0.106.50787 > 123.45.67.89.31337: UDP, length 11
```

This packet is sent to `123.45.67.89` on port `31337`.

### Side Note: Port 31337

| Item                     | Details                                                                                                                                                        |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Port Number**          | 31337                                                                                                                                                          |
| **Nickname**             | “eleet” (leet speak for “elite”)                                                                                                                               |
| **Protocol**             | TCP/UDP (usually UDP)                                                                                                                                          |
| **Type**                 | Dynamic/private port (range 10000–65535)                                                                                                                       |
| **Typical Uses**         | Backdoors, remote shells, CTF tools, simulated C2 channels                                                                                                     |
| **Historical Usage**     | - **Back Orifice (1999)**<br>- **NetBus**<br>- Many early 2000s malware used 31337 to hide                                                                     |
| **Why UDP is Used**      | No handshake, can slip past loose firewalls, avoids common TCP scans                                                                                           |
| **Risks**                | Well-known suspicious port, often flagged by IDS/IPS systems                                                                                                   |
| **Detection Methods**    | - `tcpdump -i any udp and dst port 31337`<br>- Analyze binaries for embedded IPs or port 31337<br>- Port scan with `nmap` or `nc -zv <host> 31337`             |
| **CTF Context (e.g., Palm)** | - When a user logs in, the malicious PAM module sends credentials to a C2 server on port 31337                                                              |
| **Mitigation**           | - Block UDP 31337 if unused<br>- Check integrity of PAM modules<br>- Deploy IDS signatures to flag 31337 traffic                                               |

Thus, filtering for this port directly can be an effective shortcut in solving such challenges.

---

## 3. File Discovery

Now that we know the destination IP and port, we can search the file system to find which binary contains this hardcoded IP:

```bash
$ grep '123.45.67.89' -R /lib
```

Result:

```bash
Binary file /lib/x86_64-linux-gnu/security/pam_unix.so matches
```

This indicates the `pam_unix.so` file was modified to exfiltrate data during login sessions.

---

## 4. Binary Analysis

Check if the binary contains any base64-encoded data:

```bash
$ strings /lib/x86_64-linux-gnu/security/pam_unix.so | grep -E 'base64|[A-Za-z0-9+/=]{20,}'
```

One base64 string stands out:

```txt
REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=
```

Decode it:

```bash
$ echo 'REh7c29tZXRoaW5nX2hpZGRlbl9pbnNpZGVfbXlfcGFsbX0=' | base64 -d
```

Output:

```txt
DH{something_hidden_inside_my_palm}
```

---

## 5. Flag

**Flag:** `DH{something_hidden_inside_my_palm}`

---