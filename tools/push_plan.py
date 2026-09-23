r"""
Naya plan Google Sheet me daalo - MEHFOOZ tareeqe se.
Chalao:  python tools\push_plan.py            (pehle dikhata hai, kuch likhta nahi)
         python tools\push_plan.py --yes      (asal me likh deta hai)

⚠️ 1 Aug 2026 KA SABAK:
Purani rows ka Status wapas 'pending' kar diya tha -> cloud agent ne wo posts
DOBARA kar di (kuch Instagram pe 4-4 dafa). Is liye ye script:
  * posted / failed / expired rows ko HAATH NAHI LAGATA
  * naya plan unke NEECHE add karta hai (overwrite nahi)
"""
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import google_sheet  # noqa: E402

plan = json.load(open(os.path.join(HERE, "new_plan.json"), encoding="utf-8"))
sheet = google_sheet._connect()
hdr = [h.strip() for h in sheet.row_values(1)]

rows = google_sheet.get_all_posts()
live = [p for p in rows if str(p.get("Platform", "")).strip()]
st = Counter(str(p.get("Status", "")).strip().lower() or "(khali)" for p in live)
last_row = max((p["_row_number"] for p in live), default=1)

# Purani images - overlap na ho
used = {str(p.get("Image_Link", "")).strip() for p in live if str(p.get("Image_Link", "")).strip()}
overlap = {p["Image_Link"] for p in plan} & used

print("=" * 60)
print("  SHEET KA HAAL ABHI")
print("=" * 60)
print(f"  posts        : {len(live)}   (aakhri row: {last_row})")
print(f"  status       : {dict(st)}")
print(f"\n  NAYA PLAN    : {len(plan)} posts")
print(f"  Image overlap: {len(overlap)}  {'THEEK' if not overlap else '<-- MASLA!'}")
print(f"  Likha jayega : row {last_row + 1} se row {last_row + len(plan)}")
print(f"  Purani {len(live)} rows: CHHERI NAHI JAYENGI")

if overlap:
    print("\n  [X] Ruk gaya - kuch images pehle se Sheet me hain.")
    sys.exit(1)

if "--yes" not in sys.argv:
    print("\n  (dry-run) Asal me likhne ke liye:  python tools\\push_plan.py --yes")
    sys.exit(0)

# ---- Likho: sirf NAYI rows, purani chhue baghair ----
out = [[d.get(h, "") for h in hdr] for d in plan]
end = chr(64 + len(hdr))
rng = f"A{last_row + 1}:{end}{last_row + len(out)}"
sheet.update(values=out, range_name=rng, value_input_option="USER_ENTERED")
print(f"\n  [OK] {len(out)} rows likh diye ({rng})")

# ---- Confirm ----
live2 = [p for p in google_sheet.get_all_posts() if str(p.get("Platform", "")).strip()]
st2 = Counter(str(p.get("Status", "")).strip().lower() or "(khali)" for p in live2)
print(f"  Sheet me ab {len(live2)} posts | status: {dict(st2)}")
