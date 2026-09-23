r"""
Kaunsi images abhi TAZA hain (Sheet me pehle se use nahi huin)?
Chalao:  python tools\stock.py

Ye batata hai ke naya plan kitna lamba ban sakta hai.
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import google_sheet  # noqa: E402

pages = json.load(open(os.path.join(HERE, "site_pages.json"), encoding="utf-8"))

# Sheet me jo images pehle se hain (chahe posted hon ya pending)
used = {str(p.get("Image_Link", "")).strip()
        for p in google_sheet.get_all_posts() if str(p.get("Image_Link", "")).strip()}
print(f"Sheet me {len(used)} images pehle se use ho chuki hain\n")

DAY, THEME, EVENT = [], [], []
EVENT_SLUGS = {"buongiorno-ferragosto", "buongiorno-halloween",
               "buongiorno-festa-dei-nonni", "buongiorno-mamma",
               "buongiorno-autunno", "buongiorno-inverno"}

for slug, v in pages.items():
    free = [u for u in v["images"] if u not in used]
    row = (slug, len(v["images"]), len(free))
    (DAY if v["weekday"] is not None else EVENT if slug in EVENT_SLUGS else THEME).append(row)

def show(title, rows):
    print("=" * 58)
    print(f"  {title}")
    print("=" * 58)
    print(f"  {'page':38s} {'kul':>4s} {'taza':>5s}")
    for slug, tot, free in sorted(rows, key=lambda x: -x[2]):
        warn = "  <-- khatam!" if free == 0 else ("  <-- kam" if free < 6 else "")
        print(f"  {slug:38s} {tot:4d} {free:5d}{warn}")
    print(f"  {'TOTAL':38s} {sum(r[1] for r in rows):4d} {sum(r[2] for r in rows):5d}\n")

show("DIN WALE PAGES", DAY)
show("EVENT / MAUSAM PAGES", EVENT)
show("THEME PAGES", THEME)

day_free = sum(r[2] for r in DAY)
other_free = sum(r[2] for r in THEME) + sum(r[2] for r in EVENT)
print("=" * 58)
print(f"  TAZA images: din wale {day_free} | baqi {other_free} | kul {day_free + other_free}")

# Din wale pages hi hadd banate hain (roz 2 chahiye - FB + IG)
print("\n  Har din ke hisab se kitne HAFTE chal sakte hain:")
NAMES = {0: "Lunedi", 1: "Martedi", 2: "Mercoledi", 3: "Giovedi",
         4: "Venerdi", 5: "Sabato", 6: "Domenica"}
weeks = []
for slug, tot, free in DAY:
    wd = pages[slug]["weekday"]
    w = free // 2          # roz 2 (FB + IG)
    weeks.append(w)
    print(f"    {NAMES[wd]:10s}: {free:3d} taza -> {w:2d} hafte")
print(f"\n  => Sabse kam wala hi hadd hai: {min(weeks)} hafte "
      f"(agar roz 2 din-wali posts rakhein)")
