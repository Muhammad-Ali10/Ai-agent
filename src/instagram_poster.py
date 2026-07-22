"""
instagram_poster.py - Instagram pe post (Plan B: "Instagram Login" - FB Page ki zaroorat NAHI).

Instagram ka tareeqa 2-step (graph.instagram.com):
  1. "Container" banao (image URL + caption)
  2. Container ko "publish" karo

ZAROORI: IG ko PUBLIC image URL chahiye (base64 nahi). Image ka link accessible
hona chahiye - hum pehle download karke check karte hain (L5/L12).

Token: Instagram Login token (60 din, refresh hota hai). L13: health check.
Connect karne ke liye ek dafa: python src/instagram_auth.py
"""
import time
import requests
import config
import image_handler

GRAPH = "https://graph.instagram.com"


def check_token():
    """IG token zinda hai? (L13). Return: (ok, message)"""
    if not config.INSTAGRAM_LOGIN_TOKEN or not config.INSTAGRAM_USER_ID:
        return False, "Instagram connect nahi hua - chalao: python src/instagram_auth.py"
    try:
        r = requests.get(
            f"{GRAPH}/{config.INSTAGRAM_USER_ID}",
            params={"fields": "username", "access_token": config.INSTAGRAM_LOGIN_TOKEN},
            timeout=30,
        )
        if r.status_code == 200:
            return True, f"Token theek hai (IG: @{r.json().get('username', '?')})"
        if r.status_code in (400, 401):
            return False, ("Instagram token DEAD/EXPIRE hai (60 din baad) - "
                           "python src/instagram_auth.py dubara chalao")
        return False, f"Instagram token check fail: {r.status_code} {r.text[:150]}"
    except requests.RequestException as e:
        return False, f"Instagram se raabta nahi (internet?): {e}"


def post(title, content, hashtags="", link="", image_link="", board=""):
    """
    Instagram pe post banata hai (image ZAROORI - IG bina image ke post nahi karta).
    Return: (success, message, post_url)
    """
    if not image_link:
        return False, "Instagram pe image ke bina post nahi hota", ""

    # Caption = content + hashtags (IG pe link click-able nahi hota)
    parts = [p for p in [content, hashtags] if p]
    caption = "\n\n".join(parts)

    token = config.INSTAGRAM_LOGIN_TOKEN
    ig_id = config.INSTAGRAM_USER_ID
    if not token or not ig_id:
        return False, "Instagram connect nahi hua (python src/instagram_auth.py)", ""

    # Image check (dead/private link pehle pakdo - L5/L12)
    img_bytes, img_err = image_handler.download_image(image_link)
    if img_err:
        return False, f"Image ka masla: {img_err}", ""
    image_url = image_handler.to_direct_url(image_link)

    # TEST MODE
    if config.TEST_MODE:
        print("\n--- [TEST MODE] Instagram pe yeh post hota (asli nahi) ---")
        print(caption)
        print(f"[image OK - {len(img_bytes)//1024} KB | URL: {image_url[:50]}...]")
        print("--- end ---\n")
        return True, "TEST MODE - post nahi hua (dry-run)", ""

    try:
        # Step 1: container banao
        r1 = requests.post(
            f"{GRAPH}/{ig_id}/media",
            data={"image_url": image_url, "caption": caption, "access_token": token},
            timeout=60,
        )
        if r1.status_code != 200:
            tag = "PERMANENT" if 400 <= r1.status_code < 500 and r1.status_code != 429 else ""
            return False, f"{tag} IG container fail {r1.status_code}: {r1.text[:200]}".strip(), ""
        container_id = r1.json()["id"]

        # IG ko image process karne ka thoda waqt do
        time.sleep(5)

        # Step 2: publish
        r2 = requests.post(
            f"{GRAPH}/{ig_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=60,
        )
        if r2.status_code == 200:
            media_id = r2.json().get("id", "")
            # permalink lo (post ka asli link)
            perma = ""
            try:
                pr = requests.get(f"{GRAPH}/{media_id}",
                                  params={"fields": "permalink", "access_token": token}, timeout=30)
                if pr.status_code == 200:
                    perma = pr.json().get("permalink", "")
            except requests.RequestException:
                pass
            return True, "Instagram pe post ho gaya", perma
        tag = "PERMANENT" if 400 <= r2.status_code < 500 and r2.status_code != 429 else ""
        return False, f"{tag} IG publish fail {r2.status_code}: {r2.text[:200]}".strip(), ""
    except requests.RequestException as e:
        return False, f"Instagram exception: {e}", ""
