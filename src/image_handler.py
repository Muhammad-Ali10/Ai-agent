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
                r"lh3\.googleusercontent\.com/d/([\w-]+)",
                r"[?&]id=([\w-]+)"):
        m = re.search(pat, link)
        if m:
            return m.group(1)
    return None


# ---- Drive folder ka {image ka naam: file id} index (naam se image dhoondne ke liye) ----
_drive_index = None


def drive_index(refresh=False):
    """
    Drive folder ki saari images ka index: {naam: file_id}.
    Isse user Sheet me sirf image ka NAAM likh/select kar sakta hai -
    poora link copy karne ki zaroorat nahi.
    """
    global _drive_index
    if _drive_index is not None and not refresh:
        return _drive_index

    _drive_index = {}
    if not config.DRIVE_FOLDER_ID:
        return _drive_index
    try:
        from google.oauth2.service_account import Credentials
        from google.auth.transport.requests import AuthorizedSession
        creds = Credentials.from_service_account_file(
            config.GOOGLE_CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        session = AuthorizedSession(creds)
        page = None
        while True:
            params = {
                "q": (f"'{config.DRIVE_FOLDER_ID}' in parents and "
                      "mimeType contains 'image/' and trashed=false"),
                "fields": "files(id,name),nextPageToken",
                "pageSize": 200,
                "orderBy": "name",
            }
            if page:
                params["pageToken"] = page
            r = session.get("https://www.googleapis.com/drive/v3/files",
                            params=params, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            for f in data.get("files", []):
                _drive_index[f["name"]] = f["id"]
            page = data.get("nextPageToken")
            if not page:
                break
    except Exception:
        pass  # Drive na mile to bhi normal URLs chalti rahengi
    return _drive_index


def resolve_name(name):
    """Image ke naam se Drive file id (na mile to None). Extension ke baghair bhi chalta hai."""
    idx = drive_index()
    name = str(name).strip()
    if name in idx:
        return idx[name]
    # extension ke baghair ya thoda alag likha ho to bhi dhoondo
    low = name.lower()
    for n, fid in idx.items():
        if n.lower() == low or n.lower().rsplit(".", 1)[0] == low.rsplit(".", 1)[0]:
            return fid
    return None


def thumbnail_url(file_id, width=400):
    """Google Sheets ke IMAGE() ke liye - yeh format Sheets me reliably dikhta hai."""
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w{width}"


def to_direct_url(link):
    """
    Sheet ke Image_Link ko DIRECT image URL me badlo. 3 shakalein chalti hain:
      1. Drive share-link  -> direct URL
      2. Sirf image ka NAAM -> Drive folder me dhoond ke direct URL (aasan tareeqa)
      3. Normal website URL -> waise hi

    lh3.googleusercontent.com format use karte hain - ye Google ka image CDN hai
    jo Facebook/Instagram ke servers reliably fetch kar lete hain.
    """
    link = str(link).strip()
    fid = _drive_file_id(link)
    if fid:
        return f"https://lh3.googleusercontent.com/d/{fid}"

    # URL nahi hai? Matlab image ka naam hai - Drive folder me dhoondo
    if not link.lower().startswith(("http://", "https://")):
        fid = resolve_name(link)
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

    # Naam diya tha lekin Drive folder me wo image nahi mili
    if not url.lower().startswith(("http://", "https://")):
        names = list(drive_index().keys())[:4]
        return None, (f"Image '{link}' Drive folder me nahi mili. "
                      f"Folder me hain: {', '.join(names)}..." if names
                      else f"Image '{link}' nahi mili aur Drive folder khali/na-milne wala hai")

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
