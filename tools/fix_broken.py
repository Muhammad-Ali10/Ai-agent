r"""
Sheet ki jin `pending` rows ka Image_Link toota hua (404) hai, unhe kisi
TAZA image se badal do - caption bhi naye page/filename ke hisab se dobara.

Chalao:  python tools\fix_broken.py "url1" "url2" ...          (sirf dikhata hai)
         python tools\fix_broken.py --yes "url1" "url2" ...    (theek karta hai)

Pehle usi page ki image dhoondta hai; na mile to kisi doosre page ki
(aisi surat me caption us naye page ka ban jata hai).
Jo rows post ho chuki hain unhe HAATH NAHI LAGATA.
"""
import io
import json
import os
import sys
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import compose  # noqa: E402
import google_sheet  # noqa: E402

bad = {a for a in sys.argv[1:] if a.startswith("http")}
apply = "--yes" in sys.argv
clear = "--clear" in sys.argv      # koi mauzoo image na ho to row khali kar do
if not bad:
    print(r"Istemal: python tools\fix_broken.py [--yes] [--clear] <toota-url> ...")
    print(r"  --clear = jis row ke liye koi mauzoo image na mile, wo row khali")
    sys.exit(1)

pages = json.load(open(os.path.join(HERE, "site_pages.json"), encoding="utf-8"))
rows = google_sheet.get_all_posts()
used = {str(p.get("Image_Link", "")).strip() for p in rows}
by_url = {v["url"]: slug for slug, v in pages.items()}

# Tyohar wale pages replacement ke liye theek nahi - ghalat waqt pe chale
# jayenge (Ferragosto 15 August ka hai, Estate garmi ka).
SKIP_PAGES = {"buongiorno-ferragosto", "buongiorno-estate", "buongiorno-halloween",
              "buongiorno-festa-dei-nonni"}
# Mausam ka page sirf apne mahine me chalega (November me Autunno theek hai)
SEASON = {10: "buongiorno-autunno", 11: "buongiorno-autunno", 12: "buongiorno-inverno"}


def real(u):
    """Placeholder URLs me tareekh ka folder nahi hota - wo asal me 404 hote hain."""
    return "/uploads/20" in u and u not in bad


# Kuch images kai pages pe hoti hain - Autunno page pe bhi garmi ki tasveerein
# pari hain ("Buongiorno-estate-Positano"). Unhe November me lagana ghalat hai,
# is liye filename ka mausam bhi check karte hain.
SEASON_WORDS = {"estate": (6, 7, 8, 9), "estivo": (6, 7, 8, 9),
                "ferragosto": (8,), "inverno": (12, 1, 2), "natale": (12,),
                "autunno": (9, 10, 11), "halloween": (10,)}


def fits_month(u, month):
    name = u.rsplit("/", 1)[-1].lower()
    for word, months in SEASON_WORDS.items():
        if word in name and month not in months:
            return False
    return True


def spare(slug, month=None):
    return next((u for u in pages[slug]["images"]
                 if u not in used and real(u)
                 and (month is None or fits_month(u, month))), None)


targets = []
for p in rows:
    if str(p.get("Image_Link", "")).strip() not in bad:
        continue
    st = str(p.get("Status", "")).strip().lower()
    if st != "pending":
        print(f"  Row {p['_row_number']}: status '{st}' - chhod diya")
        continue
    targets.append(p)

print(f"\n{len(targets)} rows badalni hain\n")
updates = []
for p in targets:
    row_no = p["_row_number"]
    slug = by_url.get(str(p.get("Post_Link", "")).strip())

    # 1) usi page se, warna 2) kisi doosre theme page se (jis pe sabse zyada bachi hain)
    try:
        row_month_0 = date.fromisoformat(str(p.get("Date"))[:10]).month
    except Exception:
        row_month_0 = None

    new_slug, new_img = None, None
    if slug:
        new_img = spare(slug, row_month_0)
        new_slug = slug if new_img else None
    if not new_img:
        # AHEM: doosre DIN ka page nahi lena! Monday ki row me "Buona Domenica"
        # chala jaye to bilkul ghalat lagega. Sirf theme pages, ya wahi din ka
        # page jo us tareekh se milta ho.
        row_wd = row_month = None
        try:
            dt = date.fromisoformat(str(p.get("Date"))[:10])
            row_wd, row_month = dt.weekday(), dt.month
        except Exception:
            pass
        season_ok = SEASON.get(row_month)

        def ok(s):
            wd = pages[s]["weekday"]
            if s in SKIP_PAGES or s == slug:
                return False
            if s in SEASON.values():            # mausam ka page
                return s == season_ok
            return wd is None or wd == row_wd

        cands = sorted((s for s in pages if ok(s)),
                       key=lambda s: -sum(1 for u in pages[s]["images"]
                                          if u not in used and real(u)
                                          and fits_month(u, row_month)))
        for s in cands:
            new_img = spare(s, row_month)
            if new_img:
                new_slug = s
                break
    if not new_img:
        if clear:
            updates.append((row_no, None))     # row khali kar denge
            print(f"  Row {row_no} | {p.get('Date')} {p.get('Time')} "
                  f"{p.get('Platform')}  -> KHALI ki jayegi (koi mauzoo image nahi)")
        else:
            print(f"  Row {row_no}: koi taza image nahi bachi - skip")
        continue

    used.add(new_img)
    is_day = pages[new_slug]["weekday"] is not None
    fresh = compose.make(new_slug, new_img, str(p.get("Platform")).strip(),
                         pages[new_slug]["url"], is_day)
    updates.append((row_no, fresh))
    note = "" if new_slug == slug else "  (page badal gaya)"
    print(f"  Row {row_no} | {p.get('Date')} {p.get('Time')} {p.get('Platform')}{note}")
    print(f"     purana: {str(p.get('Title'))[:58]}")
    print(f"     naya  : {fresh['Title'][:58]}")
    print(f"     image : {new_img.rsplit('/', 1)[-1][:58]}")

if not apply:
    print("\n  (dry-run) Theek karne ke liye --yes lagao")
    sys.exit(0)

sheet = google_sheet._connect()
hdr = [h.strip() for h in sheet.row_values(1)]


def col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


cells = []
end = col(len(hdr))
for row_no, fresh in updates:
    if fresh is None:
        # poori row khali - agent aisi row ko dekhta hi nahi
        cells.append({"range": f"A{row_no}:{end}{row_no}", "values": [[""] * len(hdr)]})
        continue
    # Sirf content wale columns - Status/Posted_At/Post_URL chhurte nahi
    for f in ("Platform", "Account", "Title", "Content", "Image_Link",
              "Hashtags", "Post_Link"):
        if f in hdr:
            cells.append({"range": f"{col(hdr.index(f) + 1)}{row_no}",
                          "values": [[fresh[f]]]})
sheet.batch_update(cells, value_input_option="USER_ENTERED")
fixed = sum(1 for _, f in updates if f)
print(f"\n  [OK] {fixed} rows badli, {len(updates) - fixed} khali ki")
