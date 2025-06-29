# Writeup Torrent Analyze

---

## Tổng quan bài tập
Mục tiêu của challenge Torrent Analyze là xác định tên file `.iso` được tải về qua BitTorrent trên mạng công ty. Traffic được lưu trong file `torrent.pcap`. Flag có định dạng `picoCTF{<tên_file.iso>}`.

---

## Tại sao không dùng protocol **bittorrent**?
- Dissectors `bittorrent` trong Wireshark chủ yếu xử lý **truyền dữ liệu** (chunks/pieces) qua TCP.
- Khi client đã biết **info_hash**, nó kết nối tới peer và trao đổi những đoạn dữ liệu nhị phân (piece).
- Payload TCP **không chứa** metadata như tên file, chỉ là dữ liệu thô.
- Filter `bittorrent` hoặc `tcp contains ".iso"` **không** tìm thấy tên file.

---

## Giới thiệu **BT-DHT** (BitTorrent Distributed Hash Table)
- **BT-DHT** hoạt động qua **UDP** (thường cổng 6881) để tìm kiếm peer phân tán.
- Gồm các RPC messages như:
  - `get_peers`: hỏi peer chia sẻ torrent
  - `announce_peer`: thông báo client đang có torrent
  - `find_node`: tìm node gần ID mục tiêu
- Quan trọng: các message DHT mang trường **`info_hash`** — hash SHA‑1 của dictionary `info` trong file `.torrent`.

### Các trường chính trong BT-DHT
- **info_hash**  
  - SHA‑1 của phần `info` trong torrent  
  - Xác định duy nhất torrent, gián tiếp chứa tên file
- **token**  
  - Mã ủy quyền tạm thời để announce peer
- **nodes**  
  - Danh sách node ở dạng `<node_id><IP><port>` trong phản hồi `find_node`
- **port**  
  - Cổng mà client lắng nghe kết nối torrent

---

## Hướng dẫn chi tiết từng bước

1. **Mở `torrent.pcap` bằng Wireshark.**  
   - Đảm bảo có traffic UDP cổng 6881.

2. **Bật dissector BT-DHT.**  
   - Vào **Analyze → Enabled Protocols...**  
   - Tìm và bật **BT-DHT (BitTorrent DHT Protocol)**.

3. **Lọc các DHT RPC chứa `info_hash`.**  
   ```text
   bt-dht.bencoded.string contains info_hash
   ```

4. **Xác định message `announce_peer` hoặc `get_peers` từ client.**  
   - Ghi lại giá trị **info_hash**, ví dụ:  
     ```
     e2467cbf021192c241367b892230dc1e05c0580e
     ```

5. **Tra cứu info_hash trên trang torrent.**  
   - Dùng Google hoặc các trang như `linuxtracker.org`, `torrentproject`,...  
   - Tìm hash `e2467cbf021192c241367b892230dc1e05c0580e`  
   - Kết quả: file torrent có tên  
     ```
     ubuntu-19.10-desktop-amd64.iso
     ```

6. **Tạo flag.**  
   ```
   picoCTF{ubuntu-19.10-desktop-amd64.iso}
   ```

---

## Ghi chú thêm
- **Bencode vs. DHT**: Metadata trong `.torrent` dùng bencode, DHT chỉ chứa `info_hash`, không chứa danh sách file.
- **Rủi ro bảo mật**: DHT công khai `info_hash`, cho phép kẻ ăn cắp passively xác định và tải torrent.
- **Công cụ thay thế**:  
  - **NetworkMiner** có thể tự động trích xuất DHT messages.  
  - **tshark** với filter `-Y "bt-dht.bencoded.string contains info_hash"` để script hóa.
