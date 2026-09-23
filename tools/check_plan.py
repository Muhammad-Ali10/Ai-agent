r"""
Naye plan ki poori jaanch - Sheet me daalne se PEHLE.
Chalao:  python tools\check_plan.py
         python tools\check_plan.py --images    (image links bhi check karo, slow)
"""
import io
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import config, validator, google_sheet, main as agent  # noqa: E402

plan = json.load(open(os.path.join(HERE, "new_plan.json"), encoding="utf-8"))
print(f"Plan me {len(plan)} posts\n")
fails = 0

# 1) Agent ka apna validator
bad = [(i, validator.validate_post(p)) for i, p in enumerate(plan, 2)]
bad = [(i, v) for i, v in bad if v]
print(f"1. VALIDATOR     : {'SAB PASS' if not bad else str(len(bad)) + ' me masla'}")
for i, v in bad[:4]:
    print(f"     row {i}: {v[0][:66]}")
fails += len(bad)

# 2) Date/Time
bad_dt, per_day = [], defaultdict(Counter)
for i, p in enumerate(plan, 2):
    dt, err = agent.parse_schedule(p)
    if err:
        bad_dt.append((i, err))
    else:
        per_day[dt.date()][p["Platform"]] += 1
print(f"2. DATE/TIME     : {'SAB THEEK' if not bad_dt else str(len(bad_dt)) + ' kharab'}")
fails += len(bad_dt)

# 3) Daily limits
over = [(d, pf, n) for d, c in per_day.items() for pf, n in c.items()
        if n > config.DAILY_LIMITS.get(pf, 0)]
print(f"3. LIMITS        : {'SAB THEEK' if not over else str(over[:3])}")
fails += len(over)

# 4) DIN ke naam sahi din pe? (sabse ahem)
DAYS = {"lunedì": 0, "martedì": 1, "mercoledì": 2, "giovedì": 3,
        "venerdì": 4, "sabato": 5, "domenica": 6}
mism = []
for i, p in enumerate(plan, 2):
    t = p["Title"].lower()
    for w, wd in DAYS.items():
        if t.startswith(f"buon {w}") or t.startswith(f"buona {w}"):
            dt, _ = agent.parse_schedule(p)
            if dt and dt.date().weekday() != wd:
                mism.append((i, p["Date"], w))
            break
print(f"4. DIN KE NAAM   : {'0 ghalat' if not mism else str(len(mism)) + ' GHALAT'}")
for i, d, w in mism[:4]:
    print(f"     row {i}: {d} pe '{w}'")
fails += len(mism)

# 5) Event sahi tareekh pe?
print("5. EVENTS        :")
for name, lo, hi in (("Halloween", "2026-10-25", "2026-10-31"),
                     ("Festa dei Nonni", "2026-09-30", "2026-10-02")):
    ds = sorted({p["Date"] for p in plan if name.lower() in p["Title"].lower()})
    ok = ds and ds[0] >= lo and ds[-1] <= hi
    print(f"     {name:16s}: {len(ds)} din {ds[0] if ds else '-'}..{ds[-1] if ds else '-'}"
          f"  {'OK' if ok else 'GALAT WINDOW'}")
    fails += (not ok)

# 6) Content ki quality
issues = Counter()
for p in plan:
    cat, _, desc = p["Title"].partition(" — ")
    if not desc:
        issues["sirf category (filename me manzar nahi tha)"] += 1
        continue
    dl = desc.lower()
    if re.search(r"\b(allalba|allaperto|dallalto|damore|darancia|dacqua|dellaria)\b", dl):
        issues["apostrophe missing"] += 1
    if re.search(r"gemini|removebg|[a-z0-9]{14,}", dl):
        issues["kachra filename"] += 1
    if dl.split()[0] in ("gatti", "cani", "ombrello", "originale", "originali",
                         "terrace", "foto", "di", "del", "da"):
        issues["bhadda shuru"] += 1
    if re.search(r"\bcaffe\b", desc):
        issues["accent missing (caffe)"] += 1
    # "scritta Buongiorno" (image pe likha hua), "buongiorno lo stesso",
    # "buongiorno dal letto" - ye matlab wale hain, masla nahi.
    if ("buongiorno" in dl
            and not re.search(r"(scritta|un|una|il|la|tenero|dolce)\s+buongiorno", dl)
            and not re.search(r"buongiorno\s+(lo stesso|dal|da|anche)", dl)):
        issues["'buongiorno' dohra"] += 1
print("6. CONTENT       :")
real = {k: v for k, v in issues.items() if "sirf category" not in k}
print(f"     masle: {sum(real.values())}" + ("" if not real else f"  {dict(real)}"))
print(f"     (sirf-category wale: {issues['sirf category (filename me manzar nahi tha)']}"
      f" - ye theek hai, caption saaf banta hai)")
fails += sum(real.values())

# 7) Lambai + variety + duplicates
mx = max(len(p["Content"]) + len(p["Hashtags"]) for p in plan)
print(f"7. LAMBAI        : max {mx} chars (IG limit 2200) {'OK' if mx < 2200 else 'ZYADA'}")
dup = [k for k, v in Counter(p["Content"] for p in plan).items() if v > 1]
imgs = [p["Image_Link"] for p in plan]
print(f"8. DUPLICATE     : content {len(dup)} | images {len(imgs) - len(set(imgs))}")
fails += len(dup) + (len(imgs) - len(set(imgs)))

# 9) Sheet ki purani images se overlap
used = {str(p.get("Image_Link", "")).strip() for p in google_sheet.get_all_posts()}
ov = set(imgs) & used
print(f"9. PURANI SE OVERLAP: {len(ov)}  (0 hona chahiye)")
fails += len(ov)

print("\n" + "=" * 56)
print(f"  {'SAB THEEK - Sheet me daal sakte hain' if not fails else str(fails) + ' MASLE HAIN'}")
print("=" * 56)

# 10) Images (optional - slow, site rate-limit karti hai)
if "--images" in sys.argv:
    import requests
    S = requests.Session()
    S.headers.update({"User-Agent": "Mozilla/5.0"})
    urls = sorted(set(imgs))
    print(f"\n10. IMAGES check ({len(urls)} links, aaram se)...")
    broken = []
    for n, u in enumerate(urls, 1):
        try:
            r = S.get(u, timeout=25, stream=True)
            code = r.status_code
            r.close()
        except Exception as e:
            code = "ERR:" + type(e).__name__
        if code != 200:
            broken.append((u, code))
        if n % 50 == 0:
            print(f"      {n}/{len(urls)} ...")
        time.sleep(0.7)
    print(f"    OK: {len(urls) - len(broken)}/{len(urls)}")
    for u, c in broken[:12]:
        print(f"      [{c}] ...{u[-62:]}")
