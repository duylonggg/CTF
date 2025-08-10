# Write Up

## Set up 

```bash
pactl load-module module-null-sink sink_name=virtual-cable
```

Mở `pavucontrol`

```bash
pavucontrol
```

Đảm bảo trong `Output Devices` có `Null Output`

![alt text](image.png)

Mở `qsstv`

```bash
qsstv
```

Chọn `Options` -> `Configuration` -> `Sound` -> `Pulse Audio`

![alt text](image-1.png)

---

## Chạy file

```bash
paplay -d virtual-cable scream.wav
```

![alt text](image-2.png)

---

## Flag

Flag: starpwn{CelestiForge_Playhouse_Zhul}