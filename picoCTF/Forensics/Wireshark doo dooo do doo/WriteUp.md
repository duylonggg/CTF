# Write Up

Phân tích gói tin `.pcapng`

```bash
$ wireshark shark1.pcapng
```

Chúng ta sẽ Follow TCP Stream bất kỳ

Sau đó điều chỉnh `stream` từ 0 đến hết

Tại `stream=5` ta thấy 1 chuỗi

```txt
Gur synt vf cvpbPGS{c33xno00_1_f33_h_qrnqorrs}
```

Đây là mã hóa `ROT13`

Giải mã 

Flag: picoCTF{p33kab00_1_s33_u_deadbeef}
