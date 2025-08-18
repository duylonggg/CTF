# Write Up

## Script

```python
@app.route('/developer')
def developer():
    cookie = request.cookies.get("developer_secret_cookie")
    correct = open('./static/uploads/secrets/secret_cookie.txt').read()
    if correct == '':
        c = open('./static/uploads/secrets/secret_cookie.txt','w')
        c.write(sha256(os.urandom(16)).hexdigest())
        c.close()
    correct = open('./static/uploads/secrets/secret_cookie.txt').read()
    if cookie == correct:
        c = open('./static/uploads/secrets/secret_cookie.txt','w')
        c.write(sha256(os.urandom(16)).hexdigest())
        c.close()
        return f"Welcome! There is currently 1 unread message: {open('flag.txt').read()}"
    else:
        return "You are not a developer!"
```

---

## Get cookies

Vào URL `/developer` để nó chạy lấy `developer_secret_cookies`

Sau đó truy cập vào URL `/static/uploads/secrets/secret_cookie.txt` lấy cookies

`F12` chỉnh sửa cookies và truy cập lại URL `/developer`

---

## Flag

Flag: scriptCTF{my_c00k135_4r3_n0t_s4f3!_5209fd673c8a}