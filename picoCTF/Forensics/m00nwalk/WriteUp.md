# Write Up

## Kali-tools

Đây là dạng bài `SSTV`

Chúng ta sẽ cần chuyển từ âm thanh qua dạng hình ảnh

Set up môi trường

```bash
$ pavucontrol
```

Mở control lên và đảm bảo output devices có `Null Output`

Sau đó mở `QSSTV` trên Kali

```bash
$ qsstv
```

Trên `QSSTV` ta mở `Options` chọn `Configuration` -> `Sound` -> `PulseAudio`

Tại màn hình chính chọn `Transmit` -> `Mode` -> `Scottie 1` (Gợi ý)

Tại màn hình chính chọn `Receive` -> `Auto Slant` -> Tích chọn

Cho khởi chạy file `message.wav`

```bash
$ paplay -d virtual-cable message.wav
```

Nhìn hình ảnh được in ra là sẽ thấy flag

---

## Windows tools

Tải phần mềm `RX-SSTV` và `VLC`

Tải cả `VCA` để `RX-SSTV` có thể nghe âm thanh nội bộ

Trong `Control Panel` phần `Sound` anh em sẽ thấy có cái là `Line 1`

Chọn `Line 1` để nghe âm thanh nội bộ

Sau đó mở `VLC` và chọn `Line 1` để chạy file âm thanh nội bộ

Mở `RX-SSTV` chọn Mode là `Scottie 1`

Sau đó Record và chạy file `message.wav` trong `VLC`

Chờ giải mã 

---

## Flag

Flag: picoCTF{beep_boop_im_in_space}
