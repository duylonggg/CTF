# Write Up

Mở file bằng `HxD` 

Nhận thấy đây là file `PNG` nhưng bị hỏng do có các chunk như `IDHR` hay `IEND`

Sửa những byte đầu bị hỏng

Mở ảnh bằng `stegsolve.jar`

```bash
java -jar stegsolve.jar
```

Chỉnh sửa màu của ảnh thì sẽ thấy flag

Flag: picoCTF{w1z4rdry}
