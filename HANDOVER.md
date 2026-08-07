# 🤝 HANDOVER — Social Media Posting Agent

> **Ye file naye chat me sabse pehle parhni hai.** Isme pura project hai —
> kya bana, kaise chalta hai, kya baaki hai, aur kya galtiyan pehle ho chuki hain.
>
> **Aakhri update:** 7 August 2026 · **Halat: LIVE aur theek chal raha hai** ✅

---

## 1. Ek Nazar Me

| | |
|---|---|
| **Kaam** | Google Sheet me rakhi posts ko sahi din/waqt pe khud social media pe post karna |
| **Business** | Buongiorno Immagini — Italian "good morning" images · https://buongiornoimg.it |
| **Kharcha** | **₹0** — sab free (Twitter/X isi liye chhoda, wo paid hai) |
| **Kahan chalta** | GitHub Actions (cloud) — laptop band ho to bhi chalta hai |
| **Code** | `E:\ai-agent\` · GitHub: https://github.com/Muhammad-Ali10/Ai-agent (PUBLIC repo) |
| **Sheet** | "Social Agent sheet" — ID `1LNyGPUHSAP3hEKgGkhv7jLuliM9iLccxcYht-5uj84U` |
| **Email** | **muhammadalitahir6232@gmail.com** — Google Cloud, Sheet, Drive, alerts sab isi pe |

### Abhi Ka Haal (7 Aug 2026)
```
Sheet me 240 posts  ->  28 posted · 4 expired · 208 pending
Aaj: Facebook 2/4 · Instagram 2/4  (roz ki chaaron ho chuki)
Tokens: Facebook OK · Instagram OK · Pinterest OK
Agli post: 8 Aug 2026, 8:00 AM (Facebook)
7 din se bina rukawat chal raha hai - 0 failed, 0 duplicate
```

---

## 2. Platforms

| Platform | Halat | Tafseel |
|---|---|---|
| **Facebook** | ✅ **LIVE** | Page: *Buongiorno Immagini • Frasi e Foto* · Page ID `1191608920702497` · **Photo post** (image pe koi link nahi) |
| **Instagram** | ✅ **LIVE** | @buongiornoimmaginii · user_id `17841424039114212` · **"Instagram Login" API** (Facebook Page se linked wala rasta is account pe band tha) |
| **Pinterest** | ⏳ **Sandbox** | App ID `1590994` · 39 boards · **Standard access ka intezar** — Trial se asli pin nahi banti (403 code 29) |
| Twitter/X | ❌ Nikal diya | Paid hai ($0.015/post, link wali $0.20) |
| LinkedIn | ❌ Nikal diya | User ka faisla (14 July) |

### Meta App
- Facebook App: `Social Poster` · App ID `1352683630380448` · **App Mode: LIVE**
- Instagram App: `Social Poster-IG` · App ID `1637380361307739`
- ⚠️ **App Live karna zaroori tha** — Development mode me API-posts sirf app-role wale ko dikhti hain, PUBLIC ko nahi.
  Fix tha: App Settings → Basic → **Privacy Policy URL** (`buongiornoimg.it/informativa-sulla-privacy/`) daal ke **Live** toggle.
  **App Review ki zaroorat NAHI padi** (apne hi account pe post karne ke liye).

---

## 3. Kaise Chalta Hai

```
Google Sheet (posts ka database)
        |
cron-job.org  --har 10 min-->  GitHub Actions workflow chalata hai
        |
GitHub Actions  ->  python src/main.py
        |
Agent: Sheet parho -> due posts dhoondo -> validate -> post karo
        |
Sheet me wapas likho: Status / Posted_At / Post_URL / Error
```

### Cloud Setup
- **Repo**: `Muhammad-Ali10/Ai-agent` — **PUBLIC** (public = unlimited free Actions minutes)
- **Workflow**: `.github/workflows/agent.yml` — har 30 min ka apna cron + `workflow_dispatch`
- **Asli trigger**: **cron-job.org** ka cronjob "Social Agent Trigger" — **har 10 min** GitHub API ko POST karta hai
  - URL: `https://api.github.com/repos/Muhammad-Ali10/Ai-agent/actions/workflows/agent.yml/dispatches`
  - Headers: `Authorization: Bearer <github_pat>`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`, `Content-Type: application/json`
  - Body: `{"ref":"main"}`
  - **Kyun zaroori**: GitHub ka apna cron sust hai (1–2 ghante late chalta tha) — isliye bahar se trigger karte hain
- **GitHub Secrets** (2):
  - `ENV_FILE_B64` — `.env` ka base64
  - `GOOGLE_KEY_B64` — Google service-account JSON ka base64
  - Banane ke liye: `python src/make_secrets.py` (files `credentials/` me banti hain, secrets daalne ke baad delete kar dena)

### Local (backup)
- `run_agent.bat` — double-click, `src/scheduler.py` chalata hai (har 5 min)
- ⚠️ **Cloud ke saath local mat chalao** — dono ek saath = duplicate post ka khatra
- Login pe auto-start wala shortcut **hata diya gaya hai** (cloud primary hai)

---

## 4. Google Sheet Ka Dhancha

**Tabs**: `SHEET_TEMPLATE` (posts) · `Reports` (roz ka hisab) · `Gallery` (Drive images) · `Tokens` (auto-refresh tokens)

**Columns** (16, tarteeb ahem hai):

| Column | Kaun bharta | Kya |
|---|---|---|
| Platform | User | Facebook / Instagram / Pinterest (dropdown) |
| Account | User | my_facebook / my_instagram / my_pinterest |
| Board | User | **sirf Pinterest** ke liye (board ka NAAM, ID nahi) |
| Date | User | double-click → calendar |
| Time | User | AM/PM dropdown (8:00 am) |
| Title | User | post ka title |
| Content | User | caption |
| Image_Link | User | website ka seedha link (ya Drive link, ya Drive image ka naam) |
| Preview | **AGENT** | image khud dikhati hai (self-healing) |
| Hashtags | User | #buongiorno … |
| Post_Link | User | jahan bhejnaho (Pinterest pe pin ka destination) |
| Late_Policy | User | post-anyway / skip |
| **Status** | User → AGENT | ⭐ **`pending` likhna ZAROORI** warna agent chhod deta hai |
| Posted_At | **AGENT** | kab post hui |
| Post_URL | **AGENT** | asli post ka link |
| Error | **AGENT** | fail/rukne ki wajah |

**Protection**: Preview/Posted_At/Post_URL/Error columns **warning-protected** hain (galti se paste karne pe Google warning deta hai).

**Status ke rang**: 🟢 posted · 🔴 failed · 🟡 pending · 🟠 invalid · ⚪ expired

---

## 5. Abhi Ka Content Plan (240 posts)

| | |
|---|---|
| **Range** | 31 July – 28 September 2026 (60 din) |
| **Roz** | 4 posts: **FB 8:00 · IG 8:30 · FB 9:00 · IG 9:30** |
| **Formula** | Har din: **us din ka page** (FB 8:00 + IG 9:30) + **theme page** (IG 8:30 + FB 9:00) |
| **Ferragosto** | 10–16 Aug ke poore hafte theme slots khud Ferragosto ban gaye |
| **Images** | 240/240 unique — koi repeat nahi |

**Site ka stock** (crawl se): 16 pages, **533 images**
- Din wale (187): Lunedì 46 · Martedì 36 · Mercoledì 18 · Giovedì 25 · Venerdì 26 · Sabato 18 · Domenica 18
- Theme (346): Caffè 36 · Fiori 36 · Amore 46 · Amici 18 · Estate 36 · Pioggia 46 · Ferragosto 36 · Generale 46 · WhatsApp 46

> **60 din ki hadd** Sabato/Mercoledì/Domenica ki wajah se hai (sirf 18-18 images).
> Un teen pages pe images barhao to plan kai mahine chal sakta hai — **290+ images abhi bhi bachi hain**.

**Plan document**: https://claude.ai/code/artifact/7cec9769-5d62-49ca-b1b1-f7f00323a1d3

### ⚠️ Content Ka Sabse Ahem Usool
Content **din-specific** hai (Buon Sabato / Lunedì / Ferragosto). **Dates kabhi badlo to weekday zaroor match karo**,
warna "Buon Sabato" Tuesday ko chala jayega. (Plan banate waqt yehi sab se bara masla tha.)

### Caption Ka Format
```
FACEBOOK:
Buongiorno! ☀️ {tafseel}: una nuova immagine di {category} da scaricare e condividere.

👉 Scaricala gratis qui: {page url}

Nuove immagini ogni giorno, senza registrazione. 💛

INSTAGRAM (theme wala):
Buongiorno! ☀️ {tafseel} — {category} 💛

🔗 Scarica gratis qui: {page url}
📌 Salva questo post e condividilo con chi ami.

INSTAGRAM (DIN wala - salaam pehle!):
Buon Venerdì! ☀️ {tafseel} 💛
...
```
- Instagram pe **din wali category salaam hai** — use aakhir me theme ki tarah mat lagao
- Filenames SEO ke liye hain (`Immagini-buongiorno-caffe-...`) — un se description banate waqt SEO hissa hatana padta hai

---

## 6. Files

```
E:\ai-agent\
├── HANDOVER.md              ← YE FILE (naye chat me pehle parho)
├── PLAN.md                  ← master plan + 28 loopholes ka register
├── README.md                ← code setup + chalane ka tareeqa
├── USAGE.md                 ← Sheet kaise bharni hai (rozana kaam)
├── SETUP_GUIDE.md           ← Google Cloud + Pinterest setup
├── SETUP_GUIDE_PHASE4.md    ← Facebook + Instagram setup (Plan B bhi)
├── VIDEO_SCRIPT.md          ← Pinterest Standard access ki demo video guide
├── operator-guide.html      ← social media wale ko dene wali guide
├── social-plan.html         ← 60-din ka plan document
├── run_agent.bat            ← local scheduler (backup)
├── .env                     ← SAARE SECRETS (git-ignored, kabhi share nahi)
├── credentials\             ← Google JSON + tokens (git-ignored)
├── data\                    ← lock files, boards cache (git-ignored)
├── logs\                    ← agent.log (git-ignored)
├── tools\
│   └── status.py            ← `python tools\status.py` = poora haal ek nazar me
└── src\
    ├── main.py              ← AGENT KA DIMAAG (sab yahan se chalta hai)
    ├── config.py            ← settings, limits, UTF-8 fix, paths
    ├── google_sheet.py      ← Sheet parhna/likhna + Reports tab
    ├── validator.py         ← post se pehle jaanch
    ├── image_handler.py     ← image download/check/convert + Drive naam→URL
    ├── text_clean.py        ← caption saaf karna + fbclid/utm hatana
    ├── token_store.py       ← tokens Sheet ki "Tokens" tab me (cloud-safe)
    ├── notifier.py          ← email alerts (abhi BAND - setup nahi)
    ├── facebook_poster.py   ← FB post (photo ya link card)
    ├── facebook_setup.py    ← FB token/page IDs nikalta hai
    ├── instagram_poster.py  ← IG post (2-step + status polling)
    ├── instagram_auth.py    ← IG se connect (ek dafa)
    ├── pinterest_poster.py  ← pin banana + board naam→ID + auto-refresh
    ├── pinterest_auth.py    ← Pinterest se connect (ek dafa)
    ├── list_boards.py       ← Pinterest boards ki list
    ├── setup_sheet.py       ← Sheet me dropdowns/calendar/colors lagata hai
    ├── drive_gallery.py     ← Drive folder → Gallery tab + Preview self-heal
    ├── scheduler.py         ← local hamesha-chalne-wala
    ├── make_secrets.py      ← GitHub secrets banata hai
    └── demo_for_review.py   ← Pinterest review ki demo video ke liye
```

---

## 7. Safety Features (jo already lage hue hain)

| Feature | Kya karta hai |
|---|---|
| **TEST_MODE** | `.env` me `true` karo → post nahi hoti, sirf dikhata hai |
| **Daily limits** | Pinterest 10 · Facebook 4 · Instagram 4 (code me fix) |
| **Duplicate guard** ⭐ | Wahi image usi platform pe pehle ja chuki ho to **skip** kar deta hai |
| **Crash-safe** | Post se pehle "working" likhta hai — crash ho to dobara auto-post NAHI |
| **Lock file** | Agent 2 dafa chale to doosri copy khud band |
| **Sheet structure check** | Column ka naam badla → agent **ruk jata hai** (ghalat jagah nahi likhta) |
| **Expire (24h)** | 24 ghante+ purani pending post kabhi auto-post nahi hoti |
| **Late_Policy** | post-anyway / skip — har row ki apni marzi |
| **Retry** | Fail ho to 3x (2 min gap) — sirf temporary maslon pe (4xx pe foran chhod deta) |
| **Run budget** | 12 min se zyada lage to baaki agle run pe (timeout se bachao) |
| **Waqt ke hisab se tarteeb** | Sheet ke upar-neeche order se nahi, **waqt** ke hisab se post karta hai |
| **Token auto-refresh** | IG token har 7 din khud taza (Sheet ki Tokens tab me) |
| **Text auto-clean** | Fazool quotes, line-breaks, `fbclid`/`utm_` khud hatta hai |
| **Preview self-heal** | Sheet ki Preview column har run pe khud bharti hai |

---

## 8. ⚠️ Jo Galtiyan Ho Chuki Hain (dobara mat karna)

### 🔴 Duplicate posts (1 Aug) — sabse badi
**Kya hua**: Plan Sheet me dobara push karte waqt **saari rows ka Status `pending`** kar diya —
including wo jo post ho chuki thin. Cloud agent (har 10 min) ne unhe **dobara post** kar diya
(kuch posts Instagram pe **4-4 dafa**).

**Usool**: Sheet overwrite karte waqt **posted/failed/expired rows ka Status/Posted_At/Post_URL kabhi mat chhero.**

**Fix ho chuka**: agent me ab **duplicate guard** hai (`main.py` → `already_posted()`) —
wahi image usi platform pe pehle ja chuki ho to skip kar deta hai.

### Doosri seekhi hui baatein
| Masla | Seekh |
|---|---|
| Meta **Development mode** | API-posts public ko dikhti hi nahi. App **Live** karna zaroori tha (Privacy Policy URL chahiye) |
| Pinterest **Trial** | Production pe pin banti hi nahi (403 code 29) — Standard access ka koi shortcut nahi |
| **GitHub cron sust** | 1–2 ghante late chalta tha → cron-job.org se bahar se trigger karna pada |
| **Site rate-limit** | 12 requests ek saath bheje to site ne block kar diya — maine galti se "90 links toote" bata diya tha. **Hamesha aaram se (1-3 workers, gap ke saath) check karo** |
| **fbclid** | Facebook khud click ke waqt lagata hai — **code se roka nahi ja sakta**. Address bar saaf karne ka JS snippet site ke footer me lagana hoga |
| **Instagram bio link** | API se badla **nahi** ja sakta ("does not support this operation"). Bio me sirf ek link ki jagah hai |
| **IG day-post format** | Din wali category **salaam** hai — "…— buon venerdì" nahi, balki "**Buon Venerdì!** ☀️ …" |
| **Windows console** | Italian accents/emoji pe crash karta tha → `config.py` me UTF-8 forced |

---

## 9. Rozana Kaam (user ka)

```
1. Drive/site pe image ready karo
2. Sheet me nayi row: Platform → Date → Time → Title → Content
                     → Image_Link → Hashtags → Late_Policy → Status: pending
3. Bas! Agent apne waqt pe khud post kar dega
```

**Haal dekhne ke liye**: `python tools\status.py`
**Sheet me**: Status column ka rang — 🟢 ho gaya · 🔴 masla (Error column me wajah)

---

## 10. Kya Baaki Hai

| # | Kaam | Ahmiyat |
|---|---|---|
| 1 | **Email alerts** — abhi BAND hain (`EMAIL_APP_PASSWORD` khali). Cloud akela chalta hai, agar kuch toote to **pata hi nahi chalega**. Chahiye: Gmail **App Password** → `.env` + GitHub secret update | 🔴 Sabse zaroori |
| 2 | **GitHub token regenerate** — purana token chat me aa gaya tha. Naya banao → cron-job.org ke `Authorization` header me update | 🟡 |
| 3 | **Pinterest Standard access** — video/guide `VIDEO_SCRIPT.md` me ready hai. Milne ke baad `.env` me `PINTEREST_SANDBOX=false` | 🟡 Pinterest = 10/din, sabse bara channel |
| 4 | **28 Sep ke baad ka content** — plan tab khatam. Ya to Sabato/Mercoledì/Domenica pages pe images barhao, ya naya plan banao | 🟢 waqt hai |
| 5 | **fbclid snippet** site ke footer me (address bar saaf karne ke liye) | 🟢 optional |
| 6 | 2 toote image links (agar abhi bhi 404 hain) — wo ab plan me nahi rahe, lekin site pe upload karna behtar | 🟢 |

---

## 11. Aam Kaam Kaise Karne Hain

| Kaam | Command / Tareeqa |
|---|---|
| Haal dekhna | `python tools\status.py` |
| Agent ek dafa chalana | `python src\main.py` |
| Local hamesha chalana | `run_agent.bat` (⚠️ cloud ke saath nahi) |
| Cloud manually chalana | GitHub → Actions → Social Media Agent → Run workflow |
| Sheet ke dropdowns dobara lagana | `python src\setup_sheet.py` |
| Pinterest boards ki list | `python src\list_boards.py` |
| Drive Gallery refresh | `python src\drive_gallery.py` |
| FB token/IDs dobara nikalna | `python src\facebook_setup.py` (pehle `.env` me naya `FB_SHORT_TOKEN`) |
| Instagram dobara connect | `python src\instagram_auth.py` |
| Pinterest dobara connect | `python src\pinterest_auth.py` |
| GitHub secrets banana | `python src\make_secrets.py` |
| Limits badalna | `src\config.py` → `DAILY_LIMITS` → phir `git push` |
| FB ko link-card banana | `.env` me `FACEBOOK_LINK_CARDS=true` (⚠️ image page ke og:image se aayegi, Image_Link se nahi) |

---

## 12. Naye Chat Me Kya Batana Hai

> Ye file (`E:\ai-agent\HANDOVER.md`) parh lo. Project `E:\ai-agent` me hai,
> Facebook aur Instagram live hain, 240 posts ka plan Sheet me chal raha hai,
> Pinterest sandbox me hai. `python tools\status.py` se current haal mil jayega.

**Agent ki apni memory** bhi hai — `project-social-agent-status.md` aur
`project-social-agent-email.md` (naye chat me khud load ho jati hain).
