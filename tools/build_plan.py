r"""
Site ki content se social media plan banata hai.
Chalao:  python tools\build_plan.py

Natija: tools\new_plan.json  (phir `python tools\push_plan.py` se Sheet me)

HAR DIN 4 POSTS:
  08:00 FB  -> us din ka page (Buon Lunedi) - agar us page ki taza image bachi ho
  08:30 IG  -> theme / event page
  09:00 FB  -> theme / event page
  09:30 IG  -> us din ka page - agar image bachi ho

Din wale pages ki images kam hain (Sabato 0, Mercoledi 2), is liye jahan
image na ho wahan theme/event wali post chali jati hai - plan rukta nahi.

EVENTS: apni tareekh ke aas paas theme slots pe qabza kar lete hain.
"""
import io
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
from describe import describe  # noqa: E402
import google_sheet  # noqa: E402

# ------------------------------------------------------------------ settings
START = date(2026, 9, 29)
END = date(2026, 12, 20)        # Natale ka page nahi hai -> 21 Dec se aage baad me
SLOT_TIME = {("Facebook", 1): "8:00 am", ("Instagram", 1): "8:30 am",
             ("Facebook", 2): "9:00 am", ("Instagram", 2): "9:30 am"}

# Har page ka naam + uske apne hashtags
META = {
    "buon-lunedi": ("Buon Lunedì", "#buonlunedì #lunedì"),
    "buon-martedi": ("Buon Martedì", "#buonmartedì #martedì"),
    "buon-mercoledi": ("Buon Mercoledì", "#buonmercoledì #mercoledì"),
    "buon-giovedi": ("Buon Giovedì", "#buongiovedì #giovedì"),
    "buon-venerdi": ("Buon Venerdì", "#buonvenerdì #venerdì"),
    "buon-sabato": ("Buon Sabato", "#buonsabato #buonweekend"),
    "buona-domenica": ("Buona Domenica", "#buonadomenica #domenica"),
    "buongiorno-caffe": ("Buongiorno Caffè", "#buongiornocaffè #caffè"),
    "buongiorno-con-i-fiori": ("Buongiorno con i Fiori", "#buongiornoconifiori #fiori"),
    "buongiorno-amore-mio": ("Buongiorno Amore Mio", "#buongiornoamoremio #amore"),
    "buongiorno-amici": ("Buongiorno Amici", "#buongiornoamici #amici"),
    "buongiorno-estate": ("Buongiorno Estate", "#buongiornoestate #estate"),
    "buongiorno-pioggia": ("Buongiorno Pioggia", "#buongiornopioggia #pioggia"),
    "buongiorno-ferragosto": ("Buongiorno Ferragosto", "#buonferragosto #ferragosto"),
    "immagini-buongiorno": ("Immagini Buongiorno", "#immaginibuongiorno #buongiornoatutti"),
    "100-immagini-buongiorno-gratis-per-whatsapp":
        ("Immagini Buongiorno WhatsApp", "#immaginibuongiorno #whatsapp"),
    "buongiorno-autunno": ("Buongiorno Autunno", "#buongiornoautunno #autunno"),
    "buongiorno-bambini": ("Buongiorno Bambini", "#buongiornobambini #bambini"),
    "buongiorno-cuore": ("Buongiorno Cuore", "#buongiornocuore #cuore"),
    "buongiorno-divertente": ("Buongiorno Divertente", "#buongiornodivertente #sorriso"),
    "buongiorno-festa-dei-nonni": ("Buongiorno Festa dei Nonni", "#festadeinonni #nonni"),
    "buongiorno-gatti": ("Buongiorno Gatti", "#buongiornogatti #gatti"),
    "buongiorno-halloween": ("Buongiorno Halloween", "#halloween #buonhalloween"),
    "buongiorno-in-ritardo": ("Buongiorno in Ritardo", "#buongiornoinritardo #buongiorno"),
    "buongiorno-inedite": ("Buongiorno Inedite", "#immaginibuongiorno #inedite"),
    "buongiorno-inverno": ("Buongiorno Inverno", "#buongiornoinverno #inverno"),
    "buongiorno-mamma": ("Buongiorno Mamma", "#buongiornomamma #mamma"),
    "buongiorno-pietra-bianca": ("Buongiorno Pietra Bianca", "#buongiorno #pietrabianca"),
    "le-ali-del-sorriso-buongiorno": ("Le Ali del Sorriso", "#buongiorno #sorriso"),
    "le-fate-del-sole-buongiorno": ("Le Fate del Sole", "#buongiorno #sole"),
}
IG_EXTRA = ("#goodmorning #italia #buongiornoatutti #sorriso #mattino "
            "#buongiornocosì #frasidelbuongiorno #condividi #gratis #dolcerisveglio")
BASE_TAGS = "#buongiorno #buongiornissimo #buonagiornata #immaginibuongiorno"

# Kuch filenames me koi manzar hota hi nahi ("foto-buongiorno.webp"). Un ke liye
# caption sirf category se banta hai - lekin agar sab ka ek hi text ho to 10-12
# posts bilkul ek jaisi ho jati hain (spam signal). Is liye ye baari baari aate hain.
NO_DESC_FB = [
    "Una nuova immagine di {c} da scaricare e condividere.",
    "Ecco una nuova immagine di {c}, gratis e senza registrazione.",
    "Un nuovo pensiero di {c} per iniziare bene la giornata.",
    "Nuova immagine di {c}: salvala e mandala a chi vuoi bene.",
    "Una bella immagine di {c} da condividere questa mattina.",
    "Un'immagine di {c} per augurare una splendida giornata.",
    "Nuova immagine di {c}, pronta da inviare su WhatsApp.",
    "Un'altra immagine di {c} per il tuo buongiorno di oggi.",
    "Immagine di {c} appena aggiunta: scaricala gratis.",
    "Una dolce immagine di {c} per cominciare la giornata.",
    "Nuova immagine di {c} da mandare a chi ti sta a cuore.",
    "Un'immagine di {c} per regalare un sorriso stamattina.",
]
NO_DESC_IG = [
    "{c} — un pensiero gentile per il tuo risveglio 💛",
    "{c} — da salvare e condividere con chi ami 💛",
    "{c} — per iniziare la giornata con il sorriso 💛",
    "{c} — nuove immagini ogni giorno, sempre gratis 💛",
    "{c} — un augurio speciale per questa mattina 💛",
    "{c} — condividila con chi vuoi bene 💛",
    "{c} — un dolce risveglio per te 💛",
    "{c} — salvala e mandala su WhatsApp 💛",
    "{c} — un buongiorno da regalare 💛",
    "{c} — perché ogni mattina merita un sorriso 💛",
    "{c} — nuova immagine appena aggiunta 💛",
    "{c} — un piccolo pensiero per iniziare 💛",
]
# Har (platform, category) ka apna counter - warna ek hi variant dohra jata hai
_no_desc_n = defaultdict(int)

# EVENTS: (slug, shuru, khatam) - in dino theme slots event page se bharte hain
EVENTS = [
    ("buongiorno-festa-dei-nonni", date(2026, 9, 30), date(2026, 10, 2)),
    ("buongiorno-halloween", date(2026, 10, 25), date(2026, 10, 31)),
]
# MAUSAM: in mahino me theme rotation me zyada aate hain
SEASON = {10: "buongiorno-autunno", 11: "buongiorno-autunno", 12: "buongiorno-inverno"}

# In pages ko aam rotation se bahar rakho (mausam/event ke liye mehfooz)
OUT_OF_ROTATION = {"buongiorno-ferragosto", "buongiorno-estate", "buongiorno-mamma",
                   "buongiorno-halloween", "buongiorno-festa-dei-nonni",
                   "buongiorno-autunno", "buongiorno-inverno"}

# ------------------------------------------------------------------ data
pages = json.load(open(os.path.join(HERE, "site_pages.json"), encoding="utf-8"))
used = {str(p.get("Image_Link", "")).strip()
        for p in google_sheet.get_all_posts() if str(p.get("Image_Link", "")).strip()}
print(f"Sheet me {len(used)} images pehle se use ho chuki hain (wo skip hongi)\n")

# Har page ki TAZA images. Jo image kai pages pe hai use aakhir me rakho.
appears = Counter(u for v in pages.values() for u in v["images"])
stock = {}
for slug, v in pages.items():
    fresh = [u for u in v["images"] if u not in used]
    fresh.sort(key=lambda u: appears[u])      # khaas pehle, aam baad me
    stock[slug] = fresh

DAY_PAGE = {v["weekday"]: s for s, v in pages.items() if v["weekday"] is not None}
THEMES = [s for s in pages if pages[s]["weekday"] is None and s not in OUT_OF_ROTATION]

taken = set()


def take(slug):
    """Us page ki agli taza image (ya None agar khatam)."""
    for u in stock.get(slug, []):
        if u not in taken:
            taken.add(u)
            return u
    return None


# ---- Din wali images ko poore plan me BARABAR phailao ----
# (warna Lunedi ki 46 images October me hi khatam ho jayengi)
day_budget = {}
for wd, slug in DAY_PAGE.items():
    occurrences = sum(1 for i in range((END - START).days + 1)
                      if (START + timedelta(days=i)).weekday() == wd)
    have = len(stock[slug])
    day_budget[wd] = [0] * occurrences
    for k in range(min(have, occurrences * 2)):      # har din max 2
        day_budget[wd][k % occurrences] += 1
seen_wd = Counter()

# ---- Mausam wali images bhi phailao ----
# Warna Autunno ki saari 16 images October me khatam ho jati hain aur
# November me khazaan ki ek bhi post nahi jati.
season_days = defaultdict(list)
for i in range((END - START).days + 1):
    d = START + timedelta(days=i)
    if d.month in SEASON:
        season_days[SEASON[d.month]].append(d)
season_pick = {}
for slug, days_list in season_days.items():
    have = len(stock.get(slug, []))
    n = len(days_list)
    if not n or not have:
        continue
    # Poore mausam me BARABAR phailao (har picked din pe SIRF 1 post - neeche cap)
    if have >= n:
        season_pick[slug] = set(days_list)
    else:
        season_pick[slug] = {days_list[round(k * (n - 1) / (have - 1))]
                             for k in range(have)} if have > 1 else {days_list[0]}


def make(slug, img, platform):
    label, tags = META.get(slug, (slug, "#buongiorno"))
    url = pages[slug]["url"]
    desc = describe(img, label)
    is_day = pages[slug]["weekday"] is not None
    if not desc:
        _no_desc_n[(platform, slug)] += 1
    k = _no_desc_n[(platform, slug)] - 1

    if platform == "Facebook":
        if desc:
            opening = (f"Buongiorno! ☀️ {desc}: una nuova immagine di "
                       f"{label.lower()} da scaricare e condividere.")
        else:
            line = NO_DESC_FB[k % len(NO_DESC_FB)].format(c=label.lower())
            opening = f"Buongiorno! ☀️ {line}"
        content = (f"{opening}\n\n👉 Scaricala gratis qui: {url}\n\n"
                   f"Nuove immagini ogni giorno, senza registrazione. 💛")
        hashtags = f"{BASE_TAGS} {tags}"
    else:
        # DIN wali category khud ek SALAAM hai -> "Buon Venerdì! ☀️ ..."
        if desc:
            opening = (f"{label}! ☀️ {desc} 💛" if is_day
                       else f"Buongiorno! ☀️ {desc} — {label.lower()} 💛")
        elif is_day:
            opening = f"{label}! ☀️ Buona giornata a tutti 💛"
        else:
            opening = "Buongiorno! ☀️ " + NO_DESC_IG[
                k % len(NO_DESC_IG)].format(c=label)
        content = (f"{opening}\n\n🔗 Scarica gratis qui: {url}\n"
                   f"📌 Salva questo post e condividilo con chi ami.")
        hashtags = f"{BASE_TAGS} {tags} {IG_EXTRA}"

    return {
        "Platform": platform,
        "Account": "my_facebook" if platform == "Facebook" else "my_instagram",
        "Board": "", "Title": f"{label} — {desc}" if desc else label,
        "Content": content, "Image_Link": img, "Preview": "", "Hashtags": hashtags,
        "Post_Link": url, "Late_Policy": "post-anyway", "Status": "pending",
        "Posted_At": "", "Post_URL": "", "Error": "",
    }


# ------------------------------------------------------------------ build
plan, theme_i = [], 0
short = defaultdict(int)

for i in range((END - START).days + 1):
    d = START + timedelta(days=i)
    wd = d.weekday()
    day_slug = DAY_PAGE[wd]

    # aaj kitni din-wali posts mil sakti hain (budget ke mutabiq)
    quota = day_budget[wd][seen_wd[wd]] if seen_wd[wd] < len(day_budget[wd]) else 0
    seen_wd[wd] += 1

    # aaj koi event chal raha hai?
    event = next((s for s, a, b in EVENTS if a <= d <= b), None)
    # event ke asal din 4/4 posts theek hain, us se pehle 3 tak
    event_cap = 4 if any(d == b for _, _, b in EVENTS) else 3
    today_count = Counter()          # ek page din me 2 se zyada nahi (event ke ilawa)

    for platform, slot in (("Facebook", 1), ("Instagram", 1),
                           ("Facebook", 2), ("Instagram", 2)):
        # slot 1-FB aur 2-IG = din wale slots
        is_day_slot = (platform, slot) in (("Facebook", 1), ("Instagram", 2))

        img = slug = None
        if is_day_slot and quota > 0:
            img = take(day_slug)
            if img:
                slug = day_slug
                quota -= 1
            else:
                short[day_slug] += 1

        if img is None:                       # theme / event / mausam
            season = SEASON.get(d.month)
            order = ([event] if event else [])
            if season and d in season_pick.get(season, ()):
                order.append(season)
            order += [THEMES[(theme_i + k) % len(THEMES)] for k in range(len(THEMES))]
            # Mausam ka page fallback me NAHI daalte - warna Autunno ki saari
            # images October me khatam ho jati hain aur November khali reh jata
            # hai. Theme pages 20+ hain, jagah bhar jayegi.
            for cand in order:
                # Mausam ka page din me sirf 1 dafa - warna 16 images 8 din me
                # khatam ho jati hain aur baqi mausam khali reh jata hai.
                cap = event_cap if cand == event else (1 if cand == season else 2)
                if today_count[cand] >= cap:
                    continue                  # ek hi category din bhar nahi
                img = take(cand)
                if img:
                    slug = cand
                    break
            theme_i += 1

        if img is None:
            print(f"  [!] {d}: koi image nahi bachi - plan yahin khatam")
            break

        today_count[slug] += 1
        row = make(slug, img, platform)
        row["Date"] = d.strftime("%Y-%m-%d")
        row["Time"] = SLOT_TIME[(platform, slot)]
        plan.append(row)
    else:
        continue
    break

with open(os.path.join(HERE, "new_plan.json"), "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ report
days = sorted({p["Date"] for p in plan})
imgs = [p["Image_Link"] for p in plan]
print("=" * 62)
print("  NAYA PLAN")
print("=" * 62)
print(f"  Posts       : {len(plan)}")
print(f"  Din         : {len(days)}  ({days[0]} se {days[-1]})")
print(f"  Facebook    : {sum(1 for p in plan if p['Platform'] == 'Facebook')}")
print(f"  Instagram   : {sum(1 for p in plan if p['Platform'] == 'Instagram')}")
print(f"  Unique imgs : {len(set(imgs))}/{len(imgs)}"
      + ("  (koi repeat nahi)" if len(set(imgs)) == len(imgs) else "  <-- REPEAT!"))
print(f"  Purani se overlap: {len(set(imgs) & used)}  (0 hona chahiye)")

cnt = Counter(p["Post_Link"] for p in plan)
print("\n  Page-wise:")
for slug, v in sorted(pages.items(), key=lambda kv: -cnt.get(kv[1]["url"], 0)):
    n = cnt.get(v["url"], 0)
    if n:
        print(f"    {META.get(slug, (slug,))[0]:32s} {n:3d}")

print("\n  EVENTS:")
for slug, a, b in EVENTS:
    n = sum(1 for p in plan if p["Post_Link"] == pages[slug]["url"])
    print(f"    {META[slug][0]:32s} {n:3d} posts  ({a} - {b})")
for m, slug in sorted(set(SEASON.items())):
    pass
for slug in set(SEASON.values()):
    n = sum(1 for p in plan if p["Post_Link"] == pages[slug]["url"])
    print(f"    {META[slug][0]:32s} {n:3d} posts  (mausam)")
