"""
pinterest_poster.py - Pinterest pe pin banane ka kaam (official API v5 se).
Image ko hum khud download karke base64 me DIRECT upload karte hain
(link nahi bhejte - L12 protection).

Token auto-refresh: access token ~30 din chalta hai, refresh token ~1 saal.
Agent khud taza karta rahega - user ko kuch nahi karna (L2 ka Pinterest hal).
"""
import base64
import json
import os
from datetime import datetime, timedelta  # noqa: F401
import requests
import config
import image_handler

API_BASE = config.PINTEREST_API_BASE  # sandbox ya production (config me tay hota hai)
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"  # token hamesha production se


def _load_tokens():
    """Save kiye hue tokens file se parho."""
    if not os.path.exists(config.PINTEREST_TOKEN_FILE):
        return None
    with open(config.PINTEREST_TOKEN_FILE) as f:
        return json.load(f)


def _save_tokens(token_data):
    token_data["expires_at"] = (
        datetime.now() + timedelta(seconds=token_data.get("expires_in", 2592000))
    ).isoformat()
    os.makedirs(os.path.dirname(config.PINTEREST_TOKEN_FILE), exist_ok=True)
    with open(config.PINTEREST_TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)


def _refresh_access_token(tokens):
    """
    Refresh token se naya access token lo (user ko login nahi karna padta).
    Return: (naye tokens ya None, error)
    """
    refresh = tokens.get("refresh_token")
    if not refresh:
        return None, "Refresh token nahi hai - python src/pinterest_auth.py dubara chalao"
    basic = base64.b64encode(
        f"{config.PINTEREST_APP_ID}:{config.PINTEREST_APP_SECRET}".encode()
    ).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "refresh_token", "refresh_token": refresh},
        timeout=30,
    )
    if resp.status_code != 200:
        return None, (f"Token refresh fail ({resp.status_code}) - "
                      "python src/pinterest_auth.py dubara chalao")
    new_tokens = resp.json()
    # Kuch responses me refresh_token dubara nahi aata - purana rakh lo
    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = refresh
    _save_tokens(new_tokens)
    return new_tokens, ""


def _get_access_token():
    """
    Zinda access token do - expire ho chuka ho to khud refresh karo.
    Sandbox mode me alag token (.env se) - wo refresh nahi hota.
    Return: (token ya None, error)
    """
    if config.PINTEREST_SANDBOX:
        if not config.PINTEREST_SANDBOX_TOKEN:
            return None, ("SANDBOX mode on hai lekin PINTEREST_SANDBOX_TOKEN .env me nahi. "
                          "developers.pinterest.com > app > Generate token > Sandbox")
        return config.PINTEREST_SANDBOX_TOKEN, ""

    tokens = _load_tokens()
    if not tokens:
        return None, "Pinterest tokens nahi mile - pehle: python src/pinterest_auth.py"

    # Expiry check (1 din ka margin rakhte hain)
    expires_at = tokens.get("expires_at", "")
    try:
        if datetime.fromisoformat(expires_at) < datetime.now() + timedelta(days=1):
            tokens, err = _refresh_access_token(tokens)
            if err:
                return None, err
    except ValueError:
        pass  # expiry parse na ho to token try karke dekhenge

    return tokens["access_token"], ""


BOARDS_CACHE_FILE = config._path("data/boards.json")


def _save_boards_cache(boards):
    """Boards ki list file me save karo (sandbox me kaam aati hai - L28)."""
    try:
        os.makedirs(os.path.dirname(BOARDS_CACHE_FILE), exist_ok=True)
        with open(BOARDS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(boards, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # cache save na ho to koi baat nahi


def _load_boards_cache():
    try:
        with open(BOARDS_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def list_boards():
    """
    Tumhare saare boards ki list lo.

    Sandbox ka masla (L28): sandbox /boards hamesha KHALI list deta hai
    (halanke account me 39 boards hain) - to wahan cache use karte hain,
    jo production se aati hai.

    Return: (list of {id, name}, error)
    """
    token, err = _get_access_token()
    if err:
        return [], err

    # Sandbox: production wali saved list use karo
    if config.PINTEREST_SANDBOX:
        cached = _load_boards_cache()
        if cached:
            return cached, ""
        return [], ("Sandbox me boards ki list nahi milti. Pehle production se "
                    "list lo: .env me PINTEREST_SANDBOX=false karke "
                    "'python src/list_boards.py' chalao, phir wapas true kar do")

    boards = []
    bookmark = None
    try:
        while True:  # Pinterest pages me deta hai - sab le lo
            params = {"page_size": 100}
            if bookmark:
                params["bookmark"] = bookmark
            resp = requests.get(
                f"{API_BASE}/boards",
                headers={"Authorization": f"Bearer {token}"},
                params=params, timeout=30,
            )
            if resp.status_code != 200:
                return [], f"Boards nahi mile: {resp.status_code} {resp.text[:150]}"
            data = resp.json()
            for b in data.get("items", []):
                boards.append({"id": b.get("id"), "name": b.get("name", "")})
            bookmark = data.get("bookmark")
            if not bookmark:
                break
        _save_boards_cache(boards)  # sandbox ke liye save kar lo
        return boards, ""
    except requests.RequestException as e:
        return [], f"Boards laane me masla: {e}"


# Board naam -> ID ki cache (har run me ek dafa API se aati hai)
_boards_cache = None


def resolve_board(board_name):
    """
    Sheet me likhe board ke NAAM se uska ID nikalo (user ko ID yaad nahi rakhni).
    Khali ho to .env wala default board.
    Return: (board_id, error)
    """
    global _boards_cache
    board_name = str(board_name).strip()

    # Khali - default board use karo
    if not board_name:
        if config.PINTEREST_BOARD_ID:
            return str(config.PINTEREST_BOARD_ID), ""
        return None, "Board khali hai aur .env me PINTEREST_BOARD_ID bhi nahi hai"

    # Number likha hai? Seedha ID maan lo
    if board_name.isdigit():
        return board_name, ""

    # Naam se dhoondo
    if _boards_cache is None:
        boards, err = list_boards()
        if err:
            return None, err
        _boards_cache = boards

    # Pehle bilkul same naam (case ignore karke)
    for b in _boards_cache:
        if b["name"].strip().lower() == board_name.lower():
            return b["id"], ""

    # Phir "shuru me match" (Sheet me naam chhota likha ho to bhi chale)
    matches = [b for b in _boards_cache if b["name"].strip().lower().startswith(board_name.lower())]
    if len(matches) == 1:
        return matches[0]["id"], ""
    if len(matches) > 1:
        names = ", ".join(m["name"] for m in matches[:4])
        return None, f"Board '{board_name}' se kai boards match hue ({names}) - pura naam likho"

    available = ", ".join(b["name"] for b in _boards_cache[:6])
    return None, f"Board '{board_name}' nahi mila. Tumhare boards: {available}..."


def check_token():
    """
    Token zinda hai? (L13 protection)
    Return: (ok: bool, message: str)
    """
    token, err = _get_access_token()
    if err:
        return False, err
    resp = requests.get(
        f"{API_BASE}/user_account",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if resp.status_code == 200:
        return True, "Token theek hai"
    if resp.status_code == 401:
        # Ek dafa refresh try karo
        tokens = _load_tokens()
        tokens, rerr = _refresh_access_token(tokens)
        if rerr:
            return False, f"Pinterest token DEAD hai - {rerr}"
        return True, "Token refresh ho gaya"
    return False, f"Pinterest check fail: {resp.status_code} {resp.text[:150]}"


def post(title, content, hashtags="", link="", image_link="", board=""):
    """
    Pinterest pe ek pin banata hai (image ZAROORI hai).
    board = Sheet ka Board column (naam) - khali ho to .env wala default.
    Return: (success: bool, message: str, post_url: str)
    """
    if not image_link:
        return False, "Pinterest pe image ke bina pin nahi banti", ""

    # Board ka ID nikalo (naam se) - yeh TEST MODE me bhi hota hai taake
    # ghalat board ka naam pehle hi pakda jaye
    board_id, board_err = resolve_board(board)
    if board_err:
        return False, board_err, ""

    # Description = content + hashtags
    description_parts = [p for p in [content, hashtags] if p]
    description = "\n\n".join(description_parts)

    # Image pehle download + check (TEST MODE me bhi - taake masla pehle pakda jaye)
    image_bytes, img_err = image_handler.download_image(image_link)
    if img_err:
        return False, f"Image ka masla: {img_err}", ""

    # TEST MODE: sirf dikhao, asli pin mat banao
    if config.TEST_MODE:
        print("\n--- [TEST MODE] Pinterest pe yeh pin banta (asli nahi bana) ---")
        print(f"Board: {board or '(default)'}  ->  ID: {board_id}")
        print(f"Title: {title}")
        print(description)
        if link:
            print(f"Link: {link}")
        print(f"[image OK: {len(image_bytes)//1024} KB]")
        print("--- end ---\n")
        return True, "TEST MODE - pin nahi bana (dry-run)", ""

    # Asli pin
    token, err = _get_access_token()
    if err:
        return False, err, ""

    body = {
        "board_id": str(board_id),
        "title": title or "",
        "description": description,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode(),
        },
    }
    if link:
        body["link"] = link

    try:
        resp = requests.post(
            f"{API_BASE}/pins",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=60,
        )
        if resp.status_code in (200, 201):
            pin_id = resp.json().get("id", "")
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else ""
            return True, "Pinterest pe pin ban gaya", pin_url

        # 4xx = hamari ghalti (permission/content) - retry se theek NAHI hoga.
        # Sirf 429 (bohot tez chal rahe ho) retry ke qabil hai.
        tag = "PERMANENT" if 400 <= resp.status_code < 500 and resp.status_code != 429 else ""
        return False, f"{tag} Pinterest error {resp.status_code}: {resp.text[:200]}".strip(), ""
    except requests.RequestException as e:
        return False, f"Pinterest exception: {e}", ""
