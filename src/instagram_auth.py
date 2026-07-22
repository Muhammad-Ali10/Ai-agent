"""
instagram_auth.py - EK DAFA chalana hai Instagram se connect karne ke liye.
Chalao:  python src/instagram_auth.py

Yeh "Instagram Login" tareeqa use karta hai - Facebook Page ki ZAROORAT NAHI.
Seedha Instagram se connect hota hai.

Kya hoga:
  1. Browser khulega, Instagram ka authorization page
  2. TUM apne Instagram (business) se login karke "Allow" dabaoge
  3. Token + user ID KHUD .env me save ho jayenge

Zaroori (pehle .env me hon):
  INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET (app dashboard > Instagram > business login)
  INSTAGRAM_REDIRECT_URI (dashboard me jo set kiya, wahi)
"""
import json
import os
import re
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import config

AUTH_URL = "https://www.instagram.com/oauth/authorize"
TOKEN_URL = "https://api.instagram.com/oauth/access_token"
LONG_TOKEN_URL = "https://graph.instagram.com/access_token"
SCOPES = "instagram_business_basic,instagram_business_content_publish"

_auth_code = {"value": None}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            _auth_code["value"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ho gaya! Yeh tab band karke terminal dekho.")
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass


def _update_env(updates):
    env_path = config._path(".env")
    with open(env_path, encoding="utf-8") as f:
        lines = f.readlines()
    done = set()
    for i, line in enumerate(lines):
        m = re.match(r"^(\w+)=", line)
        if m and m.group(1) in updates:
            lines[i] = f"{m.group(1)}={updates[m.group(1)]}\n"
            done.add(m.group(1))
    for k, v in updates.items():
        if k not in done:
            lines.append(f"{k}={v}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    if not (config.INSTAGRAM_APP_ID and config.INSTAGRAM_APP_SECRET):
        print("[X] Pehle .env me INSTAGRAM_APP_ID aur INSTAGRAM_APP_SECRET daalo.")
        print("    (App dashboard > Instagram > API setup with Instagram business login)")
        return

    # Step 1: authorization URL
    params = {
        "client_id": config.INSTAGRAM_APP_ID,
        "redirect_uri": config.INSTAGRAM_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("\nBrowser khul raha hai... apne Instagram (business) se login karke 'Allow' dabao.")
    print("Agar khud na khule to yeh link kholo:\n", url, "\n")
    webbrowser.open(url)

    # Step 2: code pakdo (localhost server). HTTPS redirect ho to browser page load
    # nahi hoga - us surat me user address bar se 'code' copy karke paste kar de.
    print("Login ke baad browser wapas is app pe aayega (code milega).")
    print("Agar page load na ho (https localhost), to browser ke address bar se")
    print("poora URL copy karke yahan paste karo (usme code= hota hai):\n")

    code = None
    try:
        server = HTTPServer(("localhost", 8000), _Handler)
        server.timeout = 120
        while _auth_code["value"] is None:
            server.handle_request()
            break
        code = _auth_code["value"]
    except OSError:
        pass

    if not code:
        pasted = input("Redirect URL ya code yahan paste karo: ").strip()
        if "code=" in pasted:
            code = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query).get("code", [""])[0]
            code = code.split("#")[0]  # instagram kabhi #_ jodta hai
        else:
            code = pasted
    if not code:
        print("[X] Code nahi mila. Dubara koshish karo.")
        return

    # Step 3: code -> short-lived token (+ user_id)
    print("\nCode mil gaya, token le raha hoon...")
    r = requests.post(TOKEN_URL, data={
        "client_id": config.INSTAGRAM_APP_ID,
        "client_secret": config.INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": config.INSTAGRAM_REDIRECT_URI,
        "code": code,
    }, timeout=30)
    if r.status_code != 200:
        print("[X] Token nahi mila:", r.text[:300])
        return
    data = r.json()
    short_token = data["access_token"]
    user_id = str(data.get("user_id", ""))

    # Step 4: short -> long-lived token (60 din, refresh ho sakta hai)
    r2 = requests.get(LONG_TOKEN_URL, params={
        "grant_type": "ig_exchange_token",
        "client_secret": config.INSTAGRAM_APP_SECRET,
        "access_token": short_token,
    }, timeout=30)
    long_token = r2.json().get("access_token", short_token) if r2.status_code == 200 else short_token

    # user_id confirm karo (kabhi token response me nahi hota)
    if not user_id:
        me = requests.get("https://graph.instagram.com/me",
                          params={"fields": "user_id,username", "access_token": long_token},
                          timeout=30).json()
        user_id = str(me.get("user_id") or me.get("id", ""))

    os.makedirs(os.path.dirname(config.INSTAGRAM_TOKEN_FILE), exist_ok=True)
    with open(config.INSTAGRAM_TOKEN_FILE, "w") as f:
        json.dump({"access_token": long_token, "user_id": user_id}, f, indent=2)
    _update_env({"INSTAGRAM_LOGIN_TOKEN": long_token, "INSTAGRAM_USER_ID": user_id})

    print("\n" + "=" * 55)
    print("[OK] INSTAGRAM CONNECT HO GAYA!")
    print(f"     User ID: {user_id}")
    print("     Token .env me save ho gaya (60 din, refresh hota rahega)")
    print("=" * 55)


if __name__ == "__main__":
    main()
