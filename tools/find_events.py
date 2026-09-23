r"""
Site ke kaunse pages kisi TAREEKH/EVENT se jude hain?
Chalao:  python tools\find_events.py

Page ke naam, title aur image filenames me Italian tareekhein dhoondta hai
(jaise "31 ottobre", "2 ottobre") - is se pata chalta hai ke kaunsa page
kis din ke liye hai.
"""
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
pages = json.load(open(os.path.join(HERE, "site_pages.json"), encoding="utf-8"))

MONTHS = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5,
          "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10,
          "novembre": 11, "dicembre": 12}
MONTH_NAME = {v: k for k, v in MONTHS.items()}

# Jo events hum jaante hain (Italy ke)
KNOWN = {
    "ferragosto": ("15 agosto", "Ferragosto"),
    "halloween": ("31 ottobre", "Halloween"),
    "festa-dei-nonni": ("2 ottobre", "Festa dei Nonni"),
    "mamma": ("2nd Sunday of May", "Festa della Mamma"),
    "papa": ("19 marzo", "Festa del Papà"),
    "natale": ("25 dicembre", "Natale"),
    "capodanno": ("1 gennaio", "Capodanno"),
    "pasqua": ("Easter", "Pasqua"),
    "san-valentino": ("14 febbraio", "San Valentino"),
    "epifania": ("6 gennaio", "Epifania"),
    "autunno": ("22 set - 21 dic", "Autunno (mausam)"),
    "inverno": ("21 dic - 20 mar", "Inverno (mausam)"),
    "estate": ("21 giu - 22 set", "Estate (mausam)"),
    "primavera": ("20 mar - 21 giu", "Primavera (mausam)"),
}

print("=" * 66)
print("  SITE KE EVENT / TAREEKH WALE PAGES")
print("=" * 66)

event_pages, plain = [], []
for slug, v in pages.items():
    blob = (slug + " " + v["title"] + " " +
            " ".join(u.rsplit("/", 1)[-1] for u in v["images"])).lower()

    # filenames/title me "31 ottobre" jaisi tareekh
    found = Counter()
    for m in re.finditer(r"\b(\d{1,2})[-\s](" + "|".join(MONTHS) + r")\b", blob):
        found[f"{int(m.group(1))} {m.group(2)}"] += 1

    # jaana-pehchana event?
    known = next(((d, n) for k, (d, n) in KNOWN.items() if k in slug), None)

    if known or found:
        event_pages.append((slug, known, found, len(v["images"])))
    else:
        plain.append((slug, len(v["images"])))

for slug, known, found, n in sorted(event_pages, key=lambda x: (x[1] is None, x[0])):
    label = known[1] if known else "?"
    when = known[0] if known else ""
    print(f"\n  {slug}  ({n} images)")
    print(f"     event : {label}   {('-> ' + when) if when else ''}")
    if found:
        top = ", ".join(f"{k} ({c}x)" for k, c in found.most_common(3))
        print(f"     images me tareekh: {top}")

print("\n" + "=" * 66)
print("  BAQI PAGES (kisi tareekh se nahi jude - kabhi bhi chal sakte)")
print("=" * 66)
for slug, n in sorted(plain, key=lambda x: -x[1]):
    print(f"  {slug:46s} {n:3d} images")

# Oct-Dec 2026 ke Italian events - kaunse cover ho sakte, kaunse nahi
print("\n" + "=" * 66)
print("  OCT-DEC 2026 KE ITALIAN EVENTS - page hai ya nahi?")
print("=" * 66)
CAL = [
    ("2026-10-02", "Festa dei Nonni", "festa-dei-nonni"),
    ("2026-10-04", "San Francesco (patrono d'Italia)", None),
    ("2026-10-31", "Halloween", "halloween"),
    ("2026-11-01", "Ognissanti", None),
    ("2026-11-02", "Commemorazione dei defunti", None),
    ("2026-11-11", "San Martino", None),
    ("2026-12-08", "Immacolata Concezione", None),
    ("2026-12-25", "Natale", "natale"),
    ("2026-12-26", "Santo Stefano", None),
    ("2026-12-31", "San Silvestro", None),
    ("2027-01-01", "Capodanno", "capodanno"),
    ("2027-01-06", "Epifania / Befana", "epifania"),
]
for d, name, key in CAL:
    hit = next((s for s in pages if key and key in s), None) if key else None
    n = len(pages[hit]["images"]) if hit else 0
    mark = f"HAI ({n} images)" if hit else "page NAHI hai"
    print(f"  {d}  {name:34s} {mark}")
