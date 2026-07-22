"""
pinterest_auth.py - EK DAFA chalana hai Pinterest se connect karne ke liye.
Chalao:  python src/pinterest_auth.py

Kya hoga:
  1. Browser khulega, Pinterest ka login/allow page
  2. TUM apne Pinterest se login karke "Give access" dabaoge
  3. Tokens KHUD save ho jayenge (credentials/pinterest_token.json me)
  4. Tumhare boards ki list dikhegi - ek board ka ID .env me daalna hai

(Main password kabhi nahi dekhta - tum khud login karte ho browser me.)

Achhi baat: Pinterest REFRESH TOKEN deta hai (~1 saal) - matlab baar baar
login ki zaroorat NAHI, agent khud token taza karta rahega.
"""
import base64
import json
import os
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import config

AUTH_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

_auth_code = {"value": None}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            _auth_code["value"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ho gaya! Ab yeh browser tab band kar do aur terminal dekho.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Code nahi mila. Dubara koshish karo.")

    def log_message(self, *args):
        pass  # chup raho


def save_tokens(token_data):
    """Tokens ko file me save karo (expiry time ke saath)."""
    token_data["expires_at"] = (
        datetime.now() + timedelta(seconds=token_data.get("expires_in", 2592000))
    ).isoformat()
    os.makedirs(os.path.dirname(config.PINTEREST_TOKEN_FILE), exist_ok=True)
    with open(config.PINTEREST_TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"[i] Tokens save hue: {config.PINTEREST_TOKEN_FILE}")


def main():
    if not config.PINTEREST_APP_ID or not config.PINTEREST_APP_SECRET:
        print("[X] Pehle .env me PINTEREST_APP_ID aur PINTEREST_APP_SECRET daalo.")
        return

    # Step 1: login URL banao aur browser me kholo
    params = {
        "response_type": "code",
        "client_id": config.PINTEREST_APP_ID,
        "redirect_uri": config.PINTEREST_REDIRECT_URI,
        "scope": SCOPES,
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("\nBrowser khul raha hai... apne Pinterest se login karke 'Give access' dabao.")
    print("Agar khud na khule to yeh link browser me kholo:\n", url, "\n")
    webbrowser.open(url)

    # Step 2: local server chala kar code pakdo
    server = HTTPServer(("localhost", 8000), _Handler)
    while _auth_code["value"] is None:
        server.handle_request()

    # Step 3: code ko tokens me badlo (Basic auth: app_id:app_secret)
    print("Code mil gaya, tokens le raha hoon...")
    basic = base64.b64encode(
        f"{config.PINTEREST_APP_ID}:{config.PINTEREST_APP_SECRET}".encode()
    ).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": _auth_code["value"],
            "redirect_uri": config.PINTEREST_REDIRECT_URI,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print("[X] Tokens nahi mile:", resp.status_code, resp.text[:300])
        return

    token_data = resp.json()
    save_tokens(token_data)
    print("\n[OK] TOKENS MIL GAYE aur save ho gaye:", config.PINTEREST_TOKEN_FILE)
    print("     (Refresh token ~1 saal chalta hai - baar baar login nahi karna padega)")

    # Step 4: boards ki list dikhao taake user default board choose kare
    access = token_data["access_token"]
    boards = requests.get(
        "https://api.pinterest.com/v5/boards",
        headers={"Authorization": f"Bearer {access}"},
        timeout=30,
    )
    print("\n" + "=" * 55)
    if boards.status_code == 200 and boards.json().get("items"):
        print("TUMHARE BOARDS (ek ka ID .env me PINTEREST_BOARD_ID= me daalo):\n")
        for b in boards.json()["items"]:
            print(f"  Board: {b.get('name', '?'):30s}  ID: {b.get('id')}")
    else:
        print("Koi board nahi mila! Pehle Pinterest pe ek board banao")
        print("(Pinterest.com > apna profile > Boards > Create board)")
        print("Phir yeh script dubara chalao - board ka ID milega.")
    print("=" * 55)


if __name__ == "__main__":
    main()
