r"""
Site ka poora naqsha + har page ki images.
Chalao:  python tools\crawl_site.py

Natija: tools\site_pages.json  (plan banane ke liye isi ka istemal hota hai)

AHEM: site rate-limit karti hai - is liye AARAM SE (2 workers, gap ke saath).
Tez chalao to "sab links toote hain" jaisa jhoota natija milta hai.
"""
import io
import json
import os
import re
import sys
import time

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "https://buongiornoimg.it"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_pages.json")
SKIP_IMG = ("buongiorno.it_", "cropped-", "logo", "favicon")
SKIP_PAGE = ("contattaci", "privacy", "cookie", "chi-siamo", "termini")

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (compatible; BuongiornoPlanner/1.0)"})


def get(url, tries=2):
    for i in range(tries):
        try:
            r = S.get(url, timeout=30)
            return r.status_code, r.text
        except Exception as e:
            if i == tries - 1:
                return "ERR", str(e)
            time.sleep(3)


# ---------- 1. Sitemap se saare pages ----------
print("Sitemap parh raha hoon...")
pages = set()
code, body = get(f"{BASE}/sitemap_index.xml")
subs = re.findall(r"<loc>([^<]+\.xml)</loc>", body or "") if code == 200 else []
for s in subs:
    time.sleep(1.2)
    c, b = get(s)
    if c == 200:
        pages.update(re.findall(r"<loc>([^<]+)</loc>", b))
pages = sorted(u for u in pages if not u.endswith(".xml"))

slugs = []
for u in pages:
    slug = u.replace(BASE, "").strip("/")
    if slug and not any(k in slug for k in SKIP_PAGE):
        slugs.append(slug)
print(f"  {len(slugs)} content pages mile\n")

# ---------- 2. Har page ki images ----------
# Din ke naam -> python weekday (0=Monday)
DAY_OF = {"buon-lunedi": 0, "buon-martedi": 1, "buon-mercoledi": 2, "buon-giovedi": 3,
          "buon-venerdi": 4, "buon-sabato": 5, "buona-domenica": 6}

result = {}
for i, slug in enumerate(slugs, 1):
    url = f"{BASE}/{slug}/"
    code, html = get(url)
    if code != 200:
        print(f"  [{code}] {slug}")
        time.sleep(1.5)
        continue

    m = re.search(r'property=["\']og:title["\'][^>]*content=["\']([^"\']+)', html)
    title = m.group(1) if m else slug

    raw = re.findall(
        r"https://buongiornoimg\.it/wp-content/uploads/[^\"'\s\\)]+?\.(?:webp|jpg|jpeg|png)", html)
    seen, imgs = set(), []
    for u in raw:
        u = re.sub(r"-\d+x\d+(?=\.\w+$)", "", u)     # thumbnail -> asli
        if u in seen or any(s in u.rsplit("/", 1)[-1] for s in SKIP_IMG):
            continue
        seen.add(u)
        imgs.append(u)

    result[slug] = {"url": url, "title": title,
                    "weekday": DAY_OF.get(slug), "images": imgs}
    print(f"  [{i:2d}/{len(slugs)}] {slug:46s} {len(imgs):3d} images")
    time.sleep(1.5)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

total = sum(len(v["images"]) for v in result.values())
day_n = sum(len(v["images"]) for v in result.values() if v["weekday"] is not None)
print(f"\n  PAGES : {len(result)}")
print(f"  IMAGES: {total}  (din wale: {day_n} | baqi: {total - day_n})")
print(f"  -> {OUT}")
