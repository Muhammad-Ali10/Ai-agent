"""
facebook_poster.py - Facebook PAGE pe post karne ka kaam (Meta Graph API se).
Image + text post. Personal profile pe nahi - sirf Page pe (Meta ka rule).

Token: Page Access Token (long-lived ~60 din). L13 protection: health check hai.
Image: hum URL bhejte hain (Facebook khud fetch karta hai) - lekin pehle apni taraf
       se download+check kar lete hain (L5/L12) taake dead/private link pakda jaye.
"""
import re
import requests
import config
import image_handler
import token_store

GRAPH = "https://graph.facebook.com/v21.0"
_URL_RE = re.compile(r"https?://[^\s]+")


def find_link(content, post_link):
    """
    Link card ke liye URL dhoondo:
      1. Post_Link column (agar bhara ho)
      2. warna Content me jo pehla URL mile
    Return: URL ya None
    """
    if str(post_link).strip():
        return str(post_link).strip()
    m = _URL_RE.search(str(content or ""))
    return m.group(0).rstrip(".,;)\"'") if m else None


def _fb_token():
    """FB token: pehle Sheet (Tokens tab) se, warna .env se. Badalna aasan ho jata hai."""
    try:
        t = token_store.get("FACEBOOK_ACCESS_TOKEN")
        if t:
            return t
    except Exception:
        pass
    return config.FACEBOOK_ACCESS_TOKEN


def check_token():
    """
    Page token zinda hai? (L13)
    Return: (ok, message)
    """
    if not _fb_token() or not config.FACEBOOK_PAGE_ID:
        return False, "Facebook token/Page ID nahi hai (.env me daalo - SETUP_GUIDE_PHASE4.md)"
    try:
        r = requests.get(
            f"{GRAPH}/{config.FACEBOOK_PAGE_ID}",
            params={"fields": "name", "access_token": _fb_token()},
            timeout=30,
        )
        if r.status_code == 200:
            return True, f"Token theek hai (Page: {r.json().get('name', '?')})"
        if r.status_code in (400, 401):
            return False, ("Facebook token DEAD/EXPIRE hai (60 din baad hota hai, "
                           "ya password badla) - naya Page token banao")
        return False, f"Facebook token check fail: {r.status_code} {r.text[:150]}"
    except requests.RequestException as e:
        return False, f"Facebook se raabta nahi (internet?): {e}"


def post(title, content, hashtags="", link="", image_link="", board=""):
    """
    Facebook Page pe post banata hai.
    Return: (success, message, post_url)
    """
    # Text tayyar karo
    parts = [p for p in [content, hashtags] if p]
    if link:
        parts.append(link)
    message = "\n\n".join(parts)

    token = _fb_token()
    page_id = config.FACEBOOK_PAGE_ID
    if not token or not page_id:
        return False, "Facebook token/Page ID missing (.env)", ""

    # LINK CARD ka faisla: URL mile aur setting on ho to card banega
    # (card pe click = website khulti hai - traffic ke liye behtar)
    card_link = find_link(content, link) if config.FACEBOOK_LINK_CARDS else None

    # Image ho to pehle apni taraf se check (dead/private link pakdo - L5/L12)
    # Link card me image page ke og:image se aati hai, isliye tab check ki zaroorat nahi
    image_url = None
    img_bytes = b""
    if image_link and not card_link:
        img_bytes, img_err = image_handler.download_image(image_link)
        if img_err:
            return False, f"Image ka masla: {img_err}", ""
        # FB ko direct-download URL bhejenge (Drive links convert ho jate hain)
        image_url = image_handler.to_direct_url(image_link)

    # TEST MODE
    if config.TEST_MODE:
        print("\n--- [TEST MODE] Facebook Page pe yeh post hota (asli nahi) ---")
        print(f"Type: {'LINK CARD -> ' + card_link if card_link else 'PHOTO POST'}")
        print(message)
        if image_url:
            print(f"[image OK - {len(img_bytes)//1024} KB]")
        print("--- end ---\n")
        return True, "TEST MODE - post nahi hua (dry-run)", ""

    try:
        if card_link:
            # Link card: /feed endpoint - FB khud page se image/title uthata hai
            r = requests.post(
                f"{GRAPH}/{page_id}/feed",
                data={"message": message, "link": card_link, "access_token": token},
                timeout=60,
            )
        elif image_url:
            # Photo post: /photos endpoint
            r = requests.post(
                f"{GRAPH}/{page_id}/photos",
                data={"url": image_url, "caption": message, "access_token": token},
                timeout=60,
            )
        else:
            # Text-only post: /feed endpoint
            r = requests.post(
                f"{GRAPH}/{page_id}/feed",
                data={"message": message, "access_token": token},
                timeout=60,
            )
        if r.status_code == 200:
            data = r.json()
            post_id = data.get("post_id") or data.get("id", "")
            post_url = f"https://www.facebook.com/{post_id}" if post_id else ""
            return True, "Facebook pe post ho gaya", post_url
        tag = "PERMANENT" if 400 <= r.status_code < 500 and r.status_code != 429 else ""
        return False, f"{tag} Facebook error {r.status_code}: {r.text[:200]}".strip(), ""
    except requests.RequestException as e:
        return False, f"Facebook exception: {e}", ""
