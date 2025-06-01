# Write Up

Bắt các gói tin bằng `wireshark`

```bash
wireshark wpa-ing_out.pcap
```

Chúng ta được cung cấp file `.pcap` chứa dữ liệu mạng WiFi (802.11 wireless)

Mật khẩu được sử dụng có thể bị lộ do truyền qua mạng không an toàn

Hint: dùng `rockyou.txt` để giải mã

Đầu tiên chúng ta sẽ filter để tìm kiếm gói `WPA handshake` trong traffic

Chúng ta sẽ lấy ra địa chỉ MAC: `00:5f:67:4f:6a:1a`

Sau khi có địa chỉ MAC thì cần tải file wordlist phổ biến là `rockyou.txt` về để tiến hành brute-force

```bash
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
sudo mkdir -p /usr/share/wordlists/
sudo mv rockyou.txt /usr/share/wordlists/
export ROCKYOU=/usr/share/wordlists/rockyou.txt
source ~/.bashrc
```

Sau đó chạy `Aircrack-ng` để tìm ra mật khẩu

```bash
aircrack-ng -w $ROCKYOU -b 00:5f:67:4f:6a:1a wpa-ing_out.pcap
```

Flag: picoCTF{mickeymouse}
