"""
image_handler.py - Images ka saara kaam (L12, L16 protection).

Kyun zaroori: Google Drive ka "share link" seedha image nahi hota - platform
ko wo link dein to post fail hoti hai. Isliye hum image ko KHUD download
karke seedha platform pe UPLOAD karte hain (link kabhi nahi bhejte).

Kaam:
  1. Drive share-link ko direct-download link me badalna
  2. Image download karna
  3. Check karna ke asli image hai (kharab/dead link pakadna - L5)
  4. Format/size theek karna (JPEG/PNG, max 8MB - L16)
"""
import io
import re
import requests
from PIL import Image
import config


def _drive_file_id(link):
    """Google Drive link me se file ID nikalo (kai formats)."""
    for pat in (r"drive\.google\.com/file/d/([\w-]+)",
                r"drive\.google\.com/open\?id=([\w-]+)",
                r"drive\.google\.com/uc\?(?:export=\w+&)?id=([\w-]+)",
                r"[?&]id=([\w-]+)"):
        m = re.search(pat, link)
        if m:
            return m.group(1)
    return None


def to_direct_url(link):
    """
    Google Drive share-link ko DIRECT image URL me badlo.
    lh3.googleusercontent.com format use karte hain - ye Google ka image CDN hai
    jo Facebook/Instagram ke servers reliably fetch kar lete hain
    (uc?export=download se behtar - wo bade files pe HTML page deta hai).
    """
    link = str(link).strip()
    fid = _drive_file_id(link)
    if fid:
        return f"https://lh3.googleusercontent.com/d/{fid}"
    return link  # normal link (website/CDN) - waise hi rehne do


def download_image(link):
    """
    Image download karke bytes return karo.
    Return: (image_bytes, error_message) - error ho to bytes None.
    Har masla saaf urdu-style message me batate hain (Sheet ke Error column ke liye).
    """
    url = to_direct_url(link)
    try:
        resp = requests.get(url, timeout=30)
    except requests.RequestException as e:
        return None, f"Image link nahi khula: {e}"

    if resp.status_code != 200:
        return None, f"Image link ne {resp.status_code} diya (link dead ya private hai?)"

    # Drive private file ho to HTML page milta hai, image nahi - yeh L12 ka check hai
    ctype = resp.headers.get("Content-Type", "")
    if "text/html" in ctype:
        return None, ("Link se image nahi mili (HTML mila) - Drive file private hai? "
                      "File pe right-click > Share > 'Anyone with the link' karo")

    data = resp.content

    # Asli image hai? (kharab file pakadna)
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        return None, "File download hui lekin image nahi hai (format kharab)"

    # Format check: JPEG/PNG chalega, baaki JPEG me convert (L16)
    if img.format not in ("JPEG", "PNG"):
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=90)
        data = buf.getvalue()

    # Size check: bohot badi ho to compress (L16)
    if len(data) > config.MAX_IMAGE_MB * 1024 * 1024:
        img = Image.open(io.BytesIO(data))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=75)
        data = buf.getvalue()
        if len(data) > config.MAX_IMAGE_MB * 1024 * 1024:
            return None, f"Image bohot badi hai ({len(data)//1024//1024}MB) - chhoti image use karo"

    return data, ""
