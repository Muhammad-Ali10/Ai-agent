"""
token_store.py - Tokens ko Google Sheet ki "Tokens" tab me rakhta hai.

Kyun zaroori: Cloud (GitHub Actions) har run pe naya (stateless) hota hai -
agar Instagram token refresh ho to wo kahin save hona chahiye, warna agli
run purana token use karegi. Secret update karna mushkil hai, isliye token
Sheet me rakhte hain (agent khud parh/likh sakta hai).

Sheet private hai (sirf tum + service account), isliye yahan token rakhna safe hai.
"""
import google_sheet
import gspread

TAB = "Tokens"
_cache = None


def _ws():
    ss = google_sheet._spreadsheet()
    try:
        return ss.worksheet(TAB)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=TAB, rows=50, cols=3)
        ws.append_row(["Key", "Value", "Updated"])
        return ws


def _load():
    global _cache
    if _cache is None:
        _cache = {}
        try:
            for row in _ws().get_all_records():
                k = str(row.get("Key", "")).strip()
                if k:
                    _cache[k] = {"value": str(row.get("Value", "")),
                                 "updated": str(row.get("Updated", ""))}
        except Exception:
            _cache = {}
    return _cache


def get(key):
    """Token ki value (ya None)."""
    return _load().get(key, {}).get("value") or None


def get_updated(key):
    """Token kab update hua (YYYY-MM-DD ya None)."""
    return _load().get(key, {}).get("updated") or None


def set(key, value, updated=""):
    """Token save/update karo (Tokens tab me)."""
    ws = _ws()
    keys = ws.col_values(1)
    row_vals = [key, value, updated]
    if key in keys:
        r = keys.index(key) + 1
        ws.update(values=[row_vals], range_name=f"A{r}:C{r}")
    else:
        ws.append_row(row_vals)
    _load()[key] = {"value": value, "updated": updated}
