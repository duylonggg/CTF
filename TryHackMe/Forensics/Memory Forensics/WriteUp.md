# Write Up

## Task 2

Ban đầu chúng ta cứ xem info file cái cho chắc

```bash
$ vol2 -f /data/Snapshot6_1609157562389.vmem imageinfo
Volatility Foundation Volatility Framework 2.6.1
INFO    : volatility.debug    : Determining profile based on KDBG search...
          Suggested Profile(s) : Win7SP1x64, Win7SP0x64, Win2008R2SP0x64, Win2008R2SP1x64_24000, Win2008R2SP1x64_23418, Win2008R2SP1x64, Win7SP1x64_24000, Win7SP1x64_23418
                     AS Layer1 : WindowsAMD64PagedMemory (Kernel AS)
                     AS Layer2 : FileAddressSpace (/data/Snapshot6_1609157562389.vmem)
                      PAE type : No PAE
                           DTB : 0x187000L
                          KDBG : 0xf80002c4a0a0L
          Number of Processors : 1
     Image Type (Service Pack) : 1
                KPCR for CPU 0 : 0xfffff80002c4bd00L
             KUSER_SHARED_DATA : 0xfffff78000000000L
           Image date and time : 2020-12-27 06:20:05 UTC+0000
     Image local date and time : 2020-12-26 22:20:05 -0800
```

Trích xuất mật khẩu

```bash
$ vol2 -f /data/Snapshot6_1609157562389.vmem --profile=Win7SP1x64 hashdump
Volatility Foundation Volatility Framework 2.6.1
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
John:1001:aad3b435b51404eeaad3b435b51404ee:47fbd6536d7868c873d5ea455f2fc0c9:::
HomeGroupUser$:1002:aad3b435b51404eeaad3b435b51404ee:91c34c06b7988e216c3bfeb9530cabfb:::
```

Giải mã mật khẩu theo `john`

```bash
$ john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (NT [MD4 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=8
Note: Passwords longer than 27 rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
charmander999    (John)
1g 0:00:00:00 DONE (2025-07-01 23:37) 2.041g/s 18736Kp/s 18736Kc/s 18736KC/s charmed12345..charmainylovessteve
Use the "--show --format=NT" options to display all of the cracked passwords reliably
Session completed.
```

Mật khẩu là : charmander999

---

## Task 3

Truy cập vào `Reigistry Key` để xem trường `Shutdown Time`

```bash
$ vol2 -f /data/Snapshot19_1609159453792.vmem --profile=Win7SP1x64 printkey -K "ControlSet001\Control\Windows"
Volatility Foundation Volatility Framework 2.6.1
Legend: (S) = Stable   (V) = Volatile

----------------------------
Registry: \REGISTRY\MACHINE\SYSTEM
Key name: Windows (S)
Last updated: 2020-12-27 22:50:12 UTC+0000

Subkeys:

Values:
REG_DWORD     ErrorMode       : (S) 0
REG_EXPAND_SZ Directory       : (S) %SystemRoot%
REG_DWORD     NoInteractiveServices : (S) 0
REG_EXPAND_SZ SystemDirectory : (S) %SystemRoot%\system32
REG_DWORD     ShellErrorMode  : (S) 1
REG_DWORD     CSDVersion      : (S) 256
REG_DWORD     CSDReleaseType  : (S) 0
REG_DWORD     CSDBuildNumber  : (S) 17514
REG_DWORD     ComponentizedBuild : (S) 1
REG_BINARY    ShutdownTime    : (S)
0x00000000  d2 e3 50 a2 a2 dc d6 01         
```

Giải mã thời gian

```bash
>>> print(0x01d6dca2a250e3d2)
132535830120031186
>>> (132535830120031186 - 116444736000000000) // 10000000
1609109412
>>> print(datetime.utcfromtimestamp(1609109412))
2020-12-27 22:50:12
>>>
```

Xem các lệnh trong `cmd`

```bash
$ vol2 -f /data/Snapshot19_1609159453792.vmem --profile=Win7SP1x64 consoles
Volatility Foundation Volatility Framework 2.6.1
**************************************************
ConsoleProcess: conhost.exe Pid: 2488
Console: 0xffa66200 CommandHistorySize: 50
HistoryBufferCount: 1 HistoryBufferMax: 4
OriginalTitle: %SystemRoot%\System32\cmd.exe
Title: Administrator: C:\Windows\System32\cmd.exe
AttachedProcess: cmd.exe Pid: 1920 Handle: 0x60
----
CommandHistory: 0x21e9c0 Application: cmd.exe Flags: Allocated, Reset
CommandCount: 7 LastAdded: 6 LastDisplayed: 6
FirstCommand: 0 CommandCountMax: 50
ProcessHandle: 0x60
Cmd #0 at 0x1fe3a0: cd /
Cmd #1 at 0x1f78b0: echo THM{You_found_me} > test.txt
Cmd #2 at 0x21dcf0: cls
Cmd #3 at 0x1fe3c0: cd /Users
Cmd #4 at 0x1fe3e0: cd /John
Cmd #5 at 0x21db30: dir
Cmd #6 at 0x1fe400: cd John
----
Screen 0x200f70 X:80 Y:300
Dump:

C:\>cd /Users

C:\Users>cd /John
The system cannot find the path specified.

C:\Users>dir
 Volume in drive C has no label.
 Volume Serial Number is 1602-421F

 Directory of C:\Users

12/27/2020  02:20 AM    <DIR>          .
12/27/2020  02:20 AM    <DIR>          ..
12/27/2020  02:21 AM    <DIR>          John
04/12/2011  08:45 AM    <DIR>          Public
               0 File(s)              0 bytes
               4 Dir(s)  54,565,433,344 bytes free

C:\Users>cd John

C:\Users\John>
```

---

## Task 4

Dùng plugins `truecryptpassphrase`

```bash
$ vol2 -f /data/Snapshot14_1609164553061.vmem --profile=Win7SP1x64 truecryptpassphrase
Volatility Foundation Volatility Framework 2.6.1
Found at 0xfffff8800512bee4 length 11: forgetmenot
```