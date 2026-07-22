"""
demo_for_review.py - Pinterest Standard Access ke REVIEW VIDEO ke liye.
Chalao:  python src/demo_for_review.py

Yeh script wo SAB kuch ek hi run me dikhati hai jo Pinterest ke reviewers
maangte hain (warna video reject ho jati hai):

  1. OAuth consent screen  - user apna Pinterest se "Give access" dabata hai
  2. Token exchange        - code se access token banta hai (screen pe dikhta hai)
  3. Authenticated API call - token se asli API calls (user_account + boards)
  4. Pin creation          - pin banti hai (write action)

SAB EK RECORDING ME - yehi Pinterest ki shart hai.

CHALANE SE PEHLE:
  - Purani token file hata do (warna OAuth flow nahi dikhega):
      del credentials\\pinterest_token.json
  - Screen recording shuru karo, phir yeh script chalao
"""
import base64
import json
import os
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

import config
import image_handler
import pinterest_auth

PROD_BASE = "https://api.pinterest.com/v5"
SANDBOX_BASE = "https://api-sandbox.pinterest.com/v5"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

_auth_code = {"value": None}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            _auth_code["value"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this tab.")
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass


def step(n, title):
    print()
    print("=" * 62)
    print(f"  STEP {n}: {title}")
    print("=" * 62)
    time.sleep(1)  # reviewer ko parhne ka waqt


def main():
    print("\n" + "#" * 62)
    print("#  PINTEREST API DEMO - Social Poster (App ID: "
          f"{config.PINTEREST_APP_ID})")
    print("#  Personal tool: posts scheduled pins from my own Google Sheet")
    print("#  to my own Pinterest boards.")
    print("#" * 62)
    time.sleep(2)

    # Purani token file ho to warning
    if os.path.exists(config.PINTEREST_TOKEN_FILE):
        print("\n[!] Purani token file mojood hai. Reviewers poora OAuth flow")
        print("    dekhna chahte hain - pehle yeh file delete karo:")
        print(f"    {config.PINTEREST_TOKEN_FILE}")
        print("\n    Phir recording shuru karke yeh script dubara chalao.")
        return

    # ---------- STEP 1: OAuth consent ----------
    step(1, "OAuth 2.0 - User Authorization (consent screen)")
    params = {
        "response_type": "code",
        "client_id": config.PINTEREST_APP_ID,
        "redirect_uri": config.PINTEREST_REDIRECT_URI,
        "scope": SCOPES,
    }
    auth_url = f"https://www.pinterest.com/oauth/?{urllib.parse.urlencode(params)}"
    print("Requested scopes:", SCOPES)
    print("\nOpening Pinterest authorization page in browser...")
    print("(The user reviews the permissions and clicks 'Give access')\n")
    print(auth_url)
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8000), _Handler)
    while _auth_code["value"] is None:
        server.handle_request()
    code = _auth_code["value"]
    print(f"\n[OK] Authorization code received: {code[:12]}...{code[-4:]}")

    # ---------- STEP 2: Token exchange ----------
    step(2, "Token Exchange (authorization code -> access token)")
    print(f"POST {TOKEN_URL}")
    print("grant_type=authorization_code\n")
    basic = base64.b64encode(
        f"{config.PINTEREST_APP_ID}:{config.PINTEREST_APP_SECRET}".encode()
    ).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": code,
              "redirect_uri": config.PINTEREST_REDIRECT_URI},
        timeout=30,
    )
    print("Response status:", resp.status_code)
    if resp.status_code != 200:
        print("[X] Token exchange failed:", resp.text[:300])
        return
    tokens = resp.json()
    access = tokens["access_token"]
    print(f"[OK] Access token received:  {access[:16]}...{access[-6:]}")
    print(f"[OK] Refresh token received: {'yes' if tokens.get('refresh_token') else 'no'}")
    print(f"[OK] Expires in: {tokens.get('expires_in')} seconds")
    pinterest_auth.save_tokens(dict(tokens))
    time.sleep(2)

    # ---------- STEP 3: Authenticated API call ----------
    step(3, "Authenticated API Call - GET /user_account (production)")
    h = {"Authorization": f"Bearer {access}"}
    r = requests.get(f"{PROD_BASE}/user_account", headers=h, timeout=30)
    print(f"GET {PROD_BASE}/user_account")
    print("Response status:", r.status_code)
    if r.status_code == 200:
        d = r.json()
        print(json.dumps({"username": d.get("username"),
                          "account_type": d.get("account_type"),
                          "board_count": d.get("board_count")},
                         indent=2, ensure_ascii=False))
    time.sleep(2)

    step(4, "Authenticated API Call - GET /boards (production)")
    r = requests.get(f"{PROD_BASE}/boards", headers=h,
                     params={"page_size": 5}, timeout=30)
    print(f"GET {PROD_BASE}/boards?page_size=5")
    print("Response status:", r.status_code)
    boards = r.json().get("items", []) if r.status_code == 200 else []
    for b in boards[:5]:
        print(f"   - {b.get('name')}  (id: {b.get('id')})")
    time.sleep(2)

    # ---------- STEP 5: Pin creation (core write action) ----------
    step(5, "Core API Action - POST /pins (create a Pin)")
    board_id = boards[0]["id"] if boards else config.PINTEREST_BOARD_ID
    board_name = boards[0]["name"] if boards else "(default board)"
    if not board_id:
        print("[X] No board found - create a board on Pinterest first.")
        return

    print("Downloading the image the app will upload...")
    img, err = image_handler.download_image("https://picsum.photos/600/900")
    if err:
        print("[X] Image error:", err)
        return
    print(f"[OK] Image ready: {len(img)//1024} KB\n")

    body = {
        "board_id": board_id,
        "title": "Buongiorno - scheduled by Social Poster",
        "description": "This Pin was created automatically by my app "
                       "from a row in my Google Sheet.",
        "media_source": {"source_type": "image_base64",
                         "content_type": "image/jpeg",
                         "data": base64.b64encode(img).decode()},
    }
    print(f"Target board: {board_name} (id: {board_id})")
    print(f"POST {SANDBOX_BASE}/pins")
    print("(Trial access cannot write to production, so this demo uses the")
    print(" API Sandbox as instructed by the API error message.)\n")

    r = requests.post(f"{SANDBOX_BASE}/pins",
                      headers={"Authorization": f"Bearer {config.PINTEREST_SANDBOX_TOKEN}",
                               "Content-Type": "application/json"},
                      json=body, timeout=60)
    print("Response status:", r.status_code)
    if r.status_code in (200, 201):
        pin = r.json()
        print(json.dumps({"id": pin.get("id"), "board_id": pin.get("board_id"),
                          "title": pin.get("title"),
                          "created_at": pin.get("created_at")},
                         indent=2, ensure_ascii=False))
        print(f"\n[OK] Pin created successfully: id {pin.get('id')}")
    else:
        print("[X] Pin creation failed:", r.text[:300])

    print("\n" + "#" * 62)
    print("#  DEMO COMPLETE")
    print("#  OAuth consent -> token exchange -> authenticated calls -> Pin")
    print("#" * 62 + "\n")


if __name__ == "__main__":
    main()
