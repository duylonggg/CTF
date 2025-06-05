# Write Up

## 📝 Chrono

**Category**: Forensics

---

## 🔐 SSH 

```txt
Server: saturn.picoctf.net  
Port: 61797  
Username: picoplayer  
Password: kZx-HVJKu8
```

---

## 🔍 Step-by-Step Solution

🧩 **Step 1: SSH vào máy chủ**

```bash
ssh -p 61797 picoplayer@saturn.picoctf.net
# password: kZx-HVJKu8
```

🧩 **Step 2: Kiểm tra hệ thống cron**

```bash
cat /etc/crontab
```

---

## ✍️ Flag

picoCTF{Sch3DUL7NG_T45K3_L1NUX_5b7059d0}
