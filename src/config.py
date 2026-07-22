"""
config.py - Saari settings aur secret keys yahan load hoti hain (.env file se).
Baaki code isi file se settings maangta hai.
Limits/rules PLAN.md ke mutabiq LOCKED hain.

PLATFORMS: Pinterest, Facebook, Instagram
(LinkedIn user ke kehne pe REMOVED - 14 July 2026 | Twitter/X paid hai isliye kabhi tha hi nahi)
"""
import os
import sys
from dotenv import load_dotenv

# ---- UTF-8 fix (L21) ----
# Windows ka terminal by default Urdu/emoji/accent (è, ì, 🚀) print nahi kar sakta
# aur poora agent CRASH ho jata hai. Yeh usse rokta hai.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass  # kuch environments me stream reconfigure nahi hoti - koi baat nahi

# Project ka root folder (yeh file src/ me hai, to ek qadam upar)
# Isse farq nahi padta ke script kahan se chalao - files hamesha sahi jagah milengi
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _path(relative):
    """Project root se path banao (absolute)."""
    return os.path.join(ROOT, relative)


# .env file load karo (project ke root folder se - chahe kahin se bhi chalao)
load_dotenv(_path(".env"))

# ---- Google Sheet ----
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_FILE = _path(
    os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials/service-account.json")
)
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")  # images wala folder (Gallery ke liye)

# ---- Pinterest ----
PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "")
PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET", "")
PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8000/callback")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID", "")  # default board jahan pins jayengi
PINTEREST_TOKEN_FILE = _path("credentials/pinterest_token.json")  # tokens yahan auto-save

# ---- Pinterest SANDBOX (L26) ----
# Trial access wali app PRODUCTION pe pin nahi bana sakti - Pinterest khud kehta hai
# "use API Sandbox instead". Sandbox = nakli duniya (asli pin nahi banti, sirf test).
# Standard access milne ke baad SANDBOX=false karke asli pins banengi.
PINTEREST_SANDBOX = os.getenv("PINTEREST_SANDBOX", "false").lower() == "true"
# Sandbox ka token developer portal se banta hai (Generate token > Sandbox):
PINTEREST_SANDBOX_TOKEN = os.getenv("PINTEREST_SANDBOX_TOKEN", "")

PINTEREST_API_BASE = (
    "https://api-sandbox.pinterest.com/v5" if PINTEREST_SANDBOX
    else "https://api.pinterest.com/v5"
)

# ---- Facebook ----
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")  # (purana FB-linked tareeqa - ab use nahi)
FB_SHORT_TOKEN = os.getenv("FB_SHORT_TOKEN", "")

# ---- Instagram Login (Plan B - Facebook Page ke baghair) ----
# "Instagram API with Instagram Login" - app dashboard me "Instagram" product ke
# "Business login" settings me milte hain:
INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", "https://localhost:8000/callback")
# Yeh instagram_auth.py khud bhar dega (login ke baad):
INSTAGRAM_LOGIN_TOKEN = os.getenv("INSTAGRAM_LOGIN_TOKEN", "")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "")
INSTAGRAM_TOKEN_FILE = _path("credentials/instagram_token.json")

# ---- Safety ----
# TEST_MODE true ho to asli post nahi hoti, sirf screen pe dikhata hai (dry-run)
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

# ---- Daily limits (PLAN.md me user ke decide kiye hue - ban se bachne ke liye) ----
DAILY_LIMITS = {
    "Pinterest": 10,
    "Facebook": 2,
    "Instagram": 2,
}

# Do posts ke beech kam-az-kam itna gap (minutes) - spam signal se bachao
MIN_GAP_MINUTES = 3

# ---- Content limits (har platform ki apni had - post se PEHLE check hoti hai) ----
CHAR_LIMITS = {
    "Pinterest": {"content": 800, "title": 100, "max_hashtags": 20},
    "Instagram": {"content": 2200, "max_hashtags": 30},
    "Facebook":  {"content": 60000, "max_hashtags": 30},
}

VALID_PLATFORMS = ["Pinterest", "Facebook", "Instagram"]

# ---- Scheduling rules ----
# Itne ghante purani pending post KABHI auto-post nahi hogi (Status = expired)
EXPIRE_HOURS = 24
# Itne minute tak late ho to "thodi late" maana jayega (Late_Policy tab lagti hai)
LATE_GRACE_MINUTES = 30

# ---- Images ----
MAX_IMAGE_MB = 8  # is se badi image auto-compress hogi

# ---- Retry (Phase 2): fail hone pe kitni dafa aur kitne gap se ----
RETRY_COUNT = 3
RETRY_GAP_MINUTES = 5

# ---- Scheduler (Phase 2): har kitne minute baad Sheet check karni hai ----
CHECK_INTERVAL_MINUTES = 5

# ---- Hashtag repeat warning (L19 - shadowban se bachao) ----
# Pichli itni posts me same hashtags hon to warning
HASHTAG_REPEAT_CHECK = 5

# ---- Alerts (Phase 2) ----
ALERT_EMAIL = "muhammadalitahir6232@gmail.com"
# Gmail se alert bhejne ke liye "App Password" chahiye (.env me daalo).
# Khali chhod do to email band rahegi - sirf screen/Sheet pe report milegi.
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "muhammadalitahir6232@gmail.com")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
REPORTS_TAB = "Reports"

# Timezone - Sheet ka har time Pakistan time (PKT) maana jayega
TIMEZONE = "Asia/Karachi"

# ---- Lock file (double-instance protection) ----
LOCK_FILE = _path("data/agent.lock")


def check_setup():
    """
    Shuru me check karta hai ke ZAROORI settings mojood hain ya nahi.
    Sirf Google (Sheet + credentials) zaroori - baaki platforms optional
    (jis platform ki keys nahi, us ki posts skip ho jati hain).
    """
    problems = []
    if not GOOGLE_SHEET_ID:
        problems.append("GOOGLE_SHEET_ID missing hai (.env me daalo)")
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        problems.append(f"Google JSON file nahi mili: {GOOGLE_CREDENTIALS_FILE}")
    return problems
