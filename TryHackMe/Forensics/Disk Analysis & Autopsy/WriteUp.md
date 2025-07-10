# Write Up

---

## 1. What is the MD5 hash of the E01 image?

![alt text](image.png)

MD5 hash: 3f08c518adb3b5c1359849657a9b2079

---

## 2. What is the computer account name?

![alt text](image-3.png)

Name: DESKTOP-0R59DJ3

---

## 3. List all the user accounts. (alphabetical order)

![alt text](image-1.png)

List: H4S4N,joshwa,keshav,sandhya,shreya,sivapriya,srini,suba

---

## 4. Who was the last user to log into the computer?

![alt text](image-2.png)

User: sivapriya

---

## 5. What was the IP address of the computer?

`vol3` -> `Program File (x86)` -> `Look@LAN` -> `irunin.ini`

![alt text](image-4.png)

IP: 192.168.130.216

---

## 6. What was the MAC address of the computer? (XX-XX-XX-XX-XX-XX)

![alt text](image-8.png)

MAC: 08-00-27-2c-c4-b9

---

## 7. What is the name of the network card on this computer?

![alt text](image-9.png)

Network card: Intel(R) PRO/1000 MT Desktop Adapter

---

## 8. What is the name of the network monitoring tool?

![alt text](image-7.png)

Tool: Look@LAN

---

## 9. A user bookmarked a Google Maps location. What are the coordinates of the location?

![alt text](image-5.png)

Location: 12°52'23.0"N 80°13'25.0"E

---

## 10. A user has his full name printed on his desktop wallpaper. What is the user's full name?

`User` -> `Username` -> `AppData` -> `Roaming` -> `Microsoft` -> `Windows` -> `Thmemes`

![alt text](image-6.png)

Name: Anto Joshwa

---

## 11. A user had a file on her desktop. It had a flag but she changed the flag using PowerShell. What was the first flag?

`User` -> `Username` -> `AppData` -> `Roaming` -> `Windows` -> `PowerShell`

![alt text](image-10.png)

Flag: flag{HarleyQuinnForQueen}

---

## 12. The same user found an exploit to escalate privileges on the computer. What was the message to the device owner?

![alt text](image-11.png)

Flag: Flag{I-hacked-you}

---

## 13. 2 hack tools focused on passwords were found in the system. What are the names of these tools? (alphabetical order)

`Data Sources` > `HASAN2.E01` > `Vol3` > `Program Data` > `Microsoft` > `Windows Defender` > `Scans` > `History` > `Service` > `DetectionHistory` > `02`

![alt text](image-12.png)

Tools: Lazagne,Mimikatz

---

## 14. There is a YARA file on the computer. Inspect the file. What is the name of the author?

Tìm theo đuôi file `.yar`

![alt text](image-13.png)

Extracted về máy

![alt text](image-14.png)

Author: Benjamin DELPY (gentilkiwi)

---

## 15. One of the users wanted to exploit a domain controller with an MS-NRPC based exploit. What is the filename of the archive that you found? 

![alt text](image-15.png)

Name: 2.2.0 20200918 Zerologon encrypted.zip