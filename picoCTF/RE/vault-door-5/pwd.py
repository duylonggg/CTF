import base64
import urllib.parse

expected = (
    "JTYzJTMwJTZlJTc2JTMzJTcyJTc0JTMxJTZlJTY3JTVm"
    "JTY2JTcyJTMwJTZkJTVmJTYyJTYxJTM1JTY1JTVmJTM2"
    "JTM0JTVmJTY1JTMzJTMxJTM1JTMyJTYyJTY2JTM0"
)

# 1. Base64 decode
decoded_base64 = base64.b64decode(expected).decode()

# 2. URL decode
password = urllib.parse.unquote(decoded_base64)

print("Recovered password:", password)

