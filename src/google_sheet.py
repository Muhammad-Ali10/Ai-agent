"""
google_sheet.py - Google Sheet ko parhne aur usme Status likhne ka kaam.

L14 protection: columns ko NAAM se dhoondte hain (number se nahi) -
agar kisi ne column ka naam badal diya ya hata diya to agent RUK jata hai,
ghalat jagah kabhi nahi likhta.
"""
import gspread
from google.oauth2.service_account import Credentials
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Yeh columns Sheet me zaroor hone chahiye (naam bilkul aise hi)
REQUIRED_COLUMNS = [
    "Platform", "Account", "Board", "Date", "Time", "Title", "Content",
    "Image_Link", "Hashtags", "Post_Link", "Late_Policy",
    "Status", "Posted_At", "Post_URL", "Error",
]

_ss_cache = None
_sheet_cache = None
_headers_cache = None


def _spreadsheet():
    """Poori spreadsheet (saare tabs) - ek dafa connect, phir reuse."""
    global _ss_cache
    if _ss_cache is None:
        creds = Credentials.from_service_account_file(
            config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        client = gspread.authorize(creds)
        _ss_cache = client.open_by_key(config.GOOGLE_SHEET_ID)
    return _ss_cache


def _connect():
    """Posts wala tab (pehla tab)."""
    global _sheet_cache
    if _sheet_cache is None:
        _sheet_cache = _spreadsheet().sheet1
    return _sheet_cache


def _headers():
    """Pehli row (column ke naam) parho, cache karo."""
    global _headers_cache
    if _headers_cache is None:
        _headers_cache = [h.strip() for h in _connect().row_values(1)]
    return _headers_cache


def verify_structure():
    """
    Sheet ka structure check karo. Koi zaroori column missing/renamed ho to
    error list return karo - agent aage NAHI barhega (L14).
    """
    found = _headers()
    missing = [c for c in REQUIRED_COLUMNS if c not in found]
    if missing:
        return [f"Sheet me yeh columns nahi mile (naam badla ya delete hua?): {', '.join(missing)}"]
    return []


def _col_number(name):
    """Column ke naam se uska number nikalo (A=1, B=2...)."""
    return _headers().index(name) + 1


def get_all_posts():
    """
    Saari rows parho. Har row ek dictionary banti hai jisme
    column ka naam key hoti hai (Platform, Date, Content, etc.)
    Row number bhi saath rakhte hain taake baad me usi row me Status likh saken.
    """
    sheet = _connect()
    records = sheet.get_all_records()  # list of dicts (header-name -> value)
    posts = []
    for i, row in enumerate(records):
        row["_row_number"] = i + 2  # +2 kyunke row 1 header hai, aur gsheet 1 se start
        posts.append(row)
    return posts


def update_status(row_number, status, posted_at="", post_url="", error=""):
    """Ek row ke agent-columns update karo - column NAAM se dhoond ke (L14 safe)."""
    sheet = _connect()
    sheet.update_cell(row_number, _col_number("Status"), status)
    if posted_at:
        sheet.update_cell(row_number, _col_number("Posted_At"), posted_at)
    if post_url:
        sheet.update_cell(row_number, _col_number("Post_URL"), post_url)
    if error:
        sheet.update_cell(row_number, _col_number("Error"), error)


def count_posted_today(posts, platform, today_str):
    """
    Aaj is platform pe kitni posts ho chuki hain? (Sheet ke record se ginti -
    taake agent restart ho to bhi daily limit sahi rahe.)
    """
    count = 0
    for p in posts:
        if (str(p.get("Platform", "")).strip() == platform
                and str(p.get("Status", "")).strip().lower() == "posted"
                and str(p.get("Posted_At", "")).startswith(today_str)):
            count += 1
    return count


# ============ REPORTS TAB (Phase 2) ============

REPORT_HEADERS = ["Date", "Total", "Posted", "Failed", "Details", "Last_Run"]


def _reports_tab():
    """Reports tab lo - na ho to bana do."""
    ss = _spreadsheet()
    try:
        return ss.worksheet(config.REPORTS_TAB)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=config.REPORTS_TAB, rows=500, cols=6)
        ws.append_row(REPORT_HEADERS)
        return ws


def write_daily_report(today_str, total, posted, failed, details, run_time):
    """
    Aaj ki summary Reports tab me likho.

    Cloud din me kai dafa chalta hai, is liye ginti JODTE hain (overwrite nahi) -
    warna report sirf aakhri run ki ginti dikhati hai, poore din ki nahi.
    """
    try:
        ws = _reports_tab()
        dates = ws.col_values(1)  # Date column
        if today_str in dates:
            row_num = dates.index(today_str) + 1
            old = ws.row_values(row_num)

            def num(i):
                try:
                    return int(str(old[i]).strip())
                except (IndexError, ValueError):
                    return 0

            total += num(1)
            posted += num(2)
            failed += num(3)
            details = f"Posted: {posted}, Failed: {failed} (din bhar ka)"
            ws.update(values=[[today_str, total, posted, failed, details, run_time]],
                      range_name=f"A{row_num}:F{row_num}")
        else:
            ws.append_row([today_str, total, posted, failed, details, run_time])
        return True, ""
    except Exception as e:
        return False, f"Report likhne me masla: {e}"
