# 🤖 Social Media Posting Agent — MASTER PLAN

> **Project start:** 14 July 2026
> **Status (21 July):** Teeno platforms connected — Pinterest (sandbox, Standard review pending),
> Facebook ✅, Instagram ✅ (Plan B). Dry-runs pass. Asli test posts baaki.
> **Cost target:** 100% FREE (koi paid API/service nahi)
> **Update 14 July 2026:** LinkedIn REMOVED (user ke kehne pe — wahan post nahi karni).
> Pehla platform ab **Pinterest** hai.

---

## 🎯 GOAL (ek line me)

Ek free AI agent jo **Google Sheet** me rakhi posts ko sahi **date/time** pe **Pinterest, Facebook, Instagram** pe automatically post kare — bina account ban ke, bina kharche ke, bina kisi post ke miss/duplicate hue.

**Success ka matlab:** User sirf Sheet bhare, baaki sab khud ho jaye.

---

## ✅ FINAL DECISIONS (locked)

| Cheez | Decision |
|-------|----------|
| Platforms | **Pinterest, Facebook, Instagram** (Twitter/X SKIP — paid: $0.015/post, link wali $0.20 · LinkedIn REMOVED — user ka faisla 14 July) |
| Method | **Official APIs** (free) — browser automation NAHI (ban risk) |
| Content | User khud likhega (AI content-generation nahi = koi LLM cost nahi) |
| Data source | Google Sheet (posts ka database) |
| Images | Google Drive ka dedicated folder; agent image **download karke direct upload** karega (link nahi bhejega) |
| Content type | **Sirf images** (video baad me, alag phase me agar chahiye) |
| Accounts | Har platform pe **1 account** |
| Users | 2 log (user + dost) — Sheet shared |
| **Project email** | **muhammadalitahir6232@gmail.com** — Google Cloud, Google Sheet, Drive folder, email alerts — SAB isi account pe |
| Tech | **Python**; scheduler local → baad me GitHub Actions |
| Pehla platform | **Pinterest** (user ka main platform — 10/din) |
| Timezone | Sheet ka har time = **Pakistan time (PKT)** — code me fixed |

### Daily posting limits (code me hard-coded — ban protection)

| Platform | Hamari limit/din | Platform ki asli limit |
|----------|------------------|------------------------|
| Pinterest | **10** | kaafi zyada |
| Facebook | **2** | koi sakht limit nahi |
| Instagram | **2** | 25/din |

---

## 💰 COST CONFIRMATION (July 2026 research)

| Platform | POST BANTI HAI? | PUBLIC DIKHTI HAI? | Note |
|----------|-----------------|--------------------|------|
| **Facebook** | ✅ haan | ✅ **PUBLIC! (21 July)** | App LIVE kiya → public. App Review NAHI chahiye padi! |
| **Instagram** | ✅ haan | ✅ **PUBLIC! (21 July)** | doosre account se teeno posts dikhin (Follow/Message view) |
| **Pinterest** | ⏳ sandbox only | ❌ (Trial) | Standard access review baaki |

> ✅ **HAL (21 July raat):** Dev mode me API-posts public ko nahi dikhti thi. Fix: App Settings
> > Basic me Privacy Policy URL (buongiornoimg.it/informativa-sulla-privacy) daal ke app ko
> **Live** kar diya. Facebook post ab doosre account (MUhammad Ali) se DIKH rahi hai ✅
> **App Review ki zaroorat NAHI padi** - sirf Live mode kaafi tha (apne account ke liye).
> Instagram bhi ab test karna hai (app Live ho chuka).

| Platform | Posting cost | Shart |
|----------|--------------|-------|
| Pinterest | ₹0 FREE | Business account + demo-video review (Standard access ke liye) |
| Facebook | ₹0 FREE | Page chahiye + Meta app review |
| Instagram | ₹0 FREE | Business/Creator account + FB Page link + Meta review |
| Google Sheets/Drive API | ₹0 FREE | — |
| GitHub Actions (cloud) | ₹0 FREE | free tier kaafi hai |

> Future bonus: **Threads** (Meta) — free API, image+text — Phase 4 ke saath add ho sakta hai.

---

## ⚙️ SYSTEM ARCHITECTURE

```
USER: Sheet me post likhi (date, time, platform, content, image, hashtags)
                    │
                    ▼
AGENT (har 5-10 min): "Koi post due hai?"
                    │
              due mili? ──► VALIDATE: content poora? image zinda? platform sahi?
                    │        aaj ki limit baaki? duplicate to nahi? char-limit OK?
                    │
              sab OK? ──► platform ki OFFICIAL API se post (image direct upload)
                    │
              post hui ──► Sheet me: Status = ✅ posted + waqt + post ka URL
              fail hui ──► 3x retry (5 min gap) ──► phir bhi fail ──► ⚠️ failed + wajah
```

### Google Sheet columns
| Column | Example | Kaun bharta hai |
|--------|---------|------------------|
| Platform | Pinterest (dropdown) | User |
| Account | my_pinterest | User |
| **Board** | Buongiorno Halloween (naam — ID nahi) | User |
| Date | 2026-07-15 | User |
| Time | 14:30 (PKT) | User |
| Title | New Product | User |
| Content | caption text | User |
| Image_Link | Drive link | User |
| Hashtags | #ai #tech | User |
| Post_Link | (optional share link) | User |
| Late_Policy | post-anyway / skip (dropdown) | User |
| Status | pending → agent badlega | AGENT |
| Posted_At | timestamp | AGENT |
| Post_URL | asli post ka link | AGENT |
| Error | fail ki wajah | AGENT |

---

## 👥 KAAM KA BATWARA

### USER ka kaam
| # | Kaam | Status |
|---|------|--------|
| T1 | Google Cloud project + APIs + Service Account JSON (muhammadalitahir6232@gmail.com) | ✅ **DONE (14 July)** |
| T2 | **Pinterest Business account + Developer app** (SETUP_GUIDE.md me steps) | ⏳ **AB YEH** |
| T3 | Ek dafa Pinterest OAuth "Give access" click + Board ID dena | Phase 1 |
| T4 | Test posts approve karna | Har phase |
| T5 | Pinterest Standard access — demo video upload (video Claude dega) | Phase 3 |
| T6 | FB Page + IG Business convert + Meta app + review submit | Phase 4 |
| 🔁 | Sheet me posts bharna | Roz/hafta-war |

### CLAUDE ka kaam
- ✅ Sheet template, project structure, poora Phase-1 code (14 July)
- ✅ Pinterest modules (auth + poster, auto token-refresh) (14 July)
- Safety: dry-run, duplicate protection, limits, lock file, expire — ✅ built
- Phase 2: scheduler + retry + email alerts
- Phase 3: Pinterest demo video material
- Phase 4: FB + IG modules + Meta review material
- Phase 5: GitHub Actions shift
- Har error fix + guidance

> **Policy note:** Passwords/logins USER khud karega — Claude kabhi password enter nahi karega.

---

## 📅 PHASES

| Phase | Kya hoga | Andaza | Checkpoint |
|-------|----------|--------|------------|
| **1** | ~~T1~~✅ ~~T2~~✅ ~~code~~✅ ~~connect~~✅ ~~dry-run~~✅ → **sandbox test** (asli pin Trial me mumkin nahi — L26) | ⏳ sandbox token | ✅ Sandbox me pin ban rahi hai |
| **2** | ~~Scheduler + catch-up + retry + reports + email alerts~~ ✅ **DONE (17 July)** | ✅ | Test Phase 1 ke saath hoga |
| **3** | 🚨 **Pinterest Standard access** (demo video review) — **ab yeh BLOCKER hai**, iske bina EK BHI asli pin nahi banegi | wait 1–2 hafte | ✅ Asli pin ban gayi |
| **4** | Facebook + Instagram (+optional Threads) — Meta approval ke baad | +2–3 din | ✅ Teeno platform chal rahe |
| **5** | GitHub Actions (free cloud) pe shift | +2–3 din | ✅ Laptop band, posts phir bhi ho rahi hain |

**Rule:** Har phase ke baad ruk ke confirm — agla tabhi jab pichla perfect.

---

## 🛡️ MISTAKE-PREVENTION (5 layers)

1. **Sheet-level**: dropdowns, fixed formats — typo ho hi nahi sakti
2. **Pre-post validation**: content/image/limit/platform check — ghalat post kabhi nahi jayegi
3. **Dry-run pehle**: har naya platform pehle test mode me, user approve kare to real
4. **Duplicate/miss impossible**: "working" status → post → foran ✅ mark; crash-safe; catch-up
5. **Ban protection**: official APIs + hard limits + 3-min gap + per-platform alag content

---

## 🔍 LOOPHOLES REGISTER (28 found — sab ke fix)

### Round 1 (L1–L10)
| # | Loophole | Fix | Code me? |
|---|----------|-----|----------|
| L1 | PC band tha, post miss | Catch-up + Late_Policy column; aakhri hal Phase 5 (cloud) | ✅ |
| L2 | Token expiry | Pinterest: refresh token ~1 saal, agent KHUD taza karta hai (LinkedIn se behtar!) | ✅ |
| L3 | Meta review chicken-and-egg | Pehle Pinterest system banao, usi ka video Meta ko do | plan |
| L4 | Double-post (crash ke waqt) | "working" status → post → foran mark; atki row pe manual check | ✅ |
| L5 | Image link dead/ghalat | Post se pehle download+check (dry-run me bhi); fail = ruk gaya | ✅ |
| L6 | Sheet me typo | Dropdowns + validation + "invalid" status | ✅ |
| L7 | Timezone gadbad | Sab PKT — code me fixed | ✅ |
| L8 | API temporary down | 3x retry (5 min gap) — sirf temporary maslon pe | ✅ |
| L9 | IG personal account | Business/Creator convert — Phase 4 se pehle | plan |
| L10 | Pinterest Trial pins hidden | Standard review (Phase 3) — tab tak test samjho | plan |

### Round 3 (L24–L28) — asli testing me mile (17 July)
| # | Loophole | Fix | Code me? |
|---|----------|-----|----------|
| L24 | Scripts sirf `E:\ai-agent` folder se chalti thin — kahin aur se chalao to files na milein/ghalat jagah banein | config.py me `ROOT` — saare paths ab absolute, kahin se bhi chalao | ✅ |
| L25 | Sheet me dropdown/calendar lagane se Google date/time ka format badal deta hai — purana parser samajh nahi pata tha | parse_schedule ab 5 date + 4 time formats samajhta hai | ✅ |
| L26 | **BADA MASLA**: Trial access se production pe pin ban hi NAHI sakti (403 code 29 — "use API Sandbox instead"). Research/blog ne ghalat bataya tha ("pins hidden rehti hain") | Sandbox support add (`PINTEREST_SANDBOX=true`) — pura system abhi test hoga. Asli pins **Standard access** ke baad (Phase 3 ab BLOCKER hai, optional nahi) | ✅ |
| L27 | Retry ne 403 (permanent masla) pe bhi 3 dafa koshish ki — **10 minute zaya** | Poster 4xx pe "PERMANENT" tag lagata hai (429 chhod ke) — retry foran ruk jati hai | ✅ |
| L28 | Sandbox ka `GET /boards` hamesha **khali list** deta hai (halanke `board_count: 39` batata hai) — board naam→ID resolution wahan tootti | Boards ki list `data/boards.json` me cache hoti hai (production se); sandbox wahan se parhta hai. Pin banane ke liye asli board IDs sandbox me chalte hain | ✅ |

### Round 2 (L11–L23)
| # | Loophole | Fix | Code me? |
|---|----------|-----|----------|
| L11 | Agent 2 dafa chala | Lock file — dusri copy khud band | ✅ |
| L12 | Drive private image | Download karke DIRECT upload (base64) — link kabhi nahi | ✅ |
| L13 | Password change = token dead | Har run pe health-check + saaf message | ✅ |
| L14 | Sheet columns chher diye | Naam-se parhna + structure verify; badla = full stop | ✅ |
| L15 | Char-limits (Pin title 100, desc 800; IG 2200/30 tags) | Validator me hard-coded | ✅ |
| L16 | Image format/size reject | Auto-convert JPEG + compress (Pillow) | ✅ |
| L17 | Windows update / sleep | run_agent.bat + Task Scheduler "When I log on" + catch-up | ✅ |
| L18 | GitHub Actions 5–15 min late | Expectation: "2:00–2:15 window" — OK for social | plan |
| L19 | Same hashtags = shadowban | Agent pichli 5 posts check karke warn karta hai | ✅ |
| L20 | Purani pending row | 24h+ = expired, kabhi auto-post nahi | ✅ |
| L21 | Urdu/emoji encoding | **ASLI ME PAKDA GAYA (17 July)**: Windows console `ì`/`🚀` pe crash kar raha tha. Fix: config.py me stdout/stderr UTF-8 | ✅ |
| L22 | Google JSON key leak | credentials/ git-ignored; cloud pe GitHub Secrets | ✅ |
| L23 | Videos alag process | Scope: sirf images; video future | ✅ |

---

## 📊 REPORTING (3 levels)

1. **Live (Sheet me)**: har row pe Status / Posted_At / Post_URL / Error — ✅ built
2. **Daily summary ("Reports" tab)**: Date/Total/Posted/Failed/Details/Last_Run — ✅ built (tab khud ban jayega)
3. **Email alert (sirf masla ho tab)**: **muhammadalitahir6232@gmail.com** pe — ✅ built
   (Gmail **App Password** chahiye `.env` me — na ho to email chup-chaap band, baaki sab chalta hai)

---

## 💻 ONLINE/OFFLINE

- **Phase 1–4:** Laptop ON + internet chahiye post ke waqt. Band tha to late (catch-up), gum kabhi nahi.
- **Phase 5:** GitHub Actions pe 24/7 — laptop ki mohtaji khatam.

---

## 📁 PROJECT STRUCTURE (current)

```
E:\ai-agent\
├── PLAN.md                 ← yeh file (master plan)
├── SETUP_GUIDE.md          ← user ke tasks ki step-by-step guide
├── README.md               ← code setup + chalane ka tareeqa
├── credentials\            ← Google JSON + Pinterest tokens (git-ignored)
├── data\
│   └── SHEET_TEMPLATE.csv  ← Google Sheet me import karne wala template
├── run_agent.bat           ← double-click: agent hamesha chalu (Task Scheduler ke liye bhi)
├── src\
│   ├── config.py           ← settings (limits LOCKED, UTF-8 fix, sandbox)
│   ├── google_sheet.py     ← Sheet parhna/likhna + Reports tab (naam-se, L14-safe)
│   ├── validator.py        ← post se pehle jaanch (L6/L15)
│   ├── image_handler.py    ← image download/check/convert (L12/L16)
│   ├── notifier.py         ← email alerts (sirf masla ho tab)
│   ├── pinterest_auth.py   ← EK DAFA: Pinterest login (tokens auto-save)
│   ├── pinterest_poster.py ← pin banana + board naam→ID (auto token-refresh)
│   ├── facebook_poster.py  ← FB Page pe post (Phase 4)
│   ├── instagram_poster.py ← IG Business pe post (Phase 4)
│   ├── list_boards.py      ← boards ki list (dropdown banane ke liye)
│   ├── setup_sheet.py      ← Sheet me dropdowns/calendar/formatting lagata hai
│   ├── demo_for_review.py  ← Pinterest Standard access ki demo video ke liye
│   ├── main.py             ← agent ka dimaag (ek run, POSTERS dict = har platform)
│   └── scheduler.py        ← hamesha chalne wala (har 5 min)
├── .env.example / .env     ← secrets (git-ignored)
└── requirements.txt
```

---

## 🚀 NEXT ACTIONS

- [x] **USER**: Task 1 — Google Cloud ✅ (14 July 2026)
- [x] **CLAUDE**: Project structure + Phase-1 code ✅ (14 July 2026)
- [x] **CLAUDE**: LinkedIn remove + Pinterest modules (auth/poster) ✅ (14 July 2026)
- [x] **USER**: Task 2 — Pinterest app ✅ (App ID `1590994`, Redirect URI added, boards maujood)
- [x] **USER**: Google Sheet + share + connection test ✅ (17 July)
- [x] **CLAUDE**: Board column (Option A) + **poora Phase 2** ✅ (17 July)
      — scheduler, retry, Reports tab, email alerts, hashtag warning, run_agent.bat
- [x] **USER**: `.env` me `PINTEREST_APP_SECRET` ✅ (17 July)
- [x] **USER**: `pinterest_auth.py` → tokens save ✅ (17 July) — 39 boards mile
- [x] **CLAUDE**: `setup_sheet.py` — Sheet me saare dropdowns + calendar + time picker ✅ (17 July)
- [x] **CLAUDE**: 3 bugs fix (paths L24, date-format L25, UTF-8 crash L21) ✅ (17 July)
- [x] **DONO**: **DRY-RUN PASS** ✅ (17 July) — board→ID, image, emoji, retry, expire — sab kaam kar rahe
- [x] **CLAUDE**: Sandbox support + retry fix (L26, L27) ✅ (17 July)
- [x] **USER**: Sandbox token ✅ (17 July)
- [x] **DONO**: 🎉 **SANDBOX END-TO-END PASS** ✅ (17 July) — Sheet → board resolve → image →
      pin (201 Created) → Status `posted` + Post_URL + Reports tab. **Poora system verified.**
- [x] **CLAUDE**: Demo script + video guide ✅ (17 July) — `src/demo_for_review.py` + `VIDEO_SCRIPT.md`
- [ ] **USER**: 🚨 **Pinterest Standard access** apply — video record karo (VIDEO_SCRIPT.md) ← **ab yeh**
      ⚠️ Video ki #1 reject-wajah: OAuth consent screen na dikhana. Demo script yeh khud handle karti hai
      (purani token file ho to chalne se rok deti hai).
- [ ] **USER (optional)**: Gmail App Password → `.env` me `EMAIL_APP_PASSWORD` (email alerts ke liye)

### Phase 4 — Facebook + Instagram (chal raha hai, 17 July)
- [x] **CLAUDE**: FB + IG poster modules ✅ (17 July) — main.py ab generic (POSTERS dict),
      har platform ka apna token-check; Pinterest regression test pass
- [x] **CLAUDE**: SETUP_GUIDE_PHASE4.md ✅ (17 July)
- [x] **USER**: Instagram ko Business banaya ✅ (20 July)
- [x] **USER**: Meta Developer app `Social Poster` (App ID 1352683630380448) ✅ (20 July)
- [x] **CLAUDE**: facebook_setup.py — token exchange + page/IG discovery ✅ (20 July)
- [x] **DONO**: **FACEBOOK READY** ✅ (20 July) — Page ID 1191608920702497, long-lived
      Page token, dry-run PASS. (Real test post baaki — user OK pe)
- [x] **CLAUDE**: Instagram **Plan B** code ✅ (21 July) — FB Page ↔ IG link is account pe
      band tha (business-portfolio limited settings). Isliye "Instagram Login" API pe switch:
      instagram_auth.py + instagram_poster.py (graph.instagram.com) — Page ki zaroorat NAHI
- [x] **USER**: Instagram business login enable + tester role + token ✅ (21 July)
- [x] **DONO**: **INSTAGRAM READY** ✅ (21 July) — @buongiornoimmaginii, user_id 17841424039114212,
      token .env me, dry-run PASS. Plan B (Instagram Login) kaam kar gaya!
- [x] **DONO**: 🎉 **FB + IG ASLI POST LIVE** ✅ (21 July 2026)
      FB: facebook.com/1191608920702497_122115636273359782
      IG: instagram.com/p/DbC3BpEDB6I — dono real, dev mode me apne account pe chal gaya
- [x] **DONO**: 🎉🎉 **END-TO-END TEST PASS** ✅ (21 July 2026)
      Sheet me FB+IG rows daale → agent ne khud parhe, due dekhe, dono post kiye
      (3-min gap ke saath), Status=posted + Post_URL + Reports tab — sab khud likha.
      FB: .../122115637011359782 · IG: instagram.com/p/DbC30utDCSC
      **Yeh woh asli "agent" experience hai jiske liye system bana.**
- [ ] **USER**: (baad me) Meta App Review agar kabhi doosre accounts add karne hon

### Local Scheduler ✅ (21 July)
- [x] **CLAUDE**: scheduler.py — logs/agent.log me likhta hai, scheduler-lock (do instance na chalein)
- [x] **CLAUDE**: Startup folder shortcut (admin ke baghair auto-start at login, pythonw = hidden)
      `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SocialMediaAgent.lnk`
- [x] **CLAUDE**: run_agent.bat (manual visible run) — full python path
- [x] **DONO**: verified — scheduler chal ke Sheet check karta hai, logs likhta hai ✅
      (Task Scheduler admin maangta tha, isliye Startup folder use kiya)

### Sheet improvements ✅ (21 July)
- [x] AM/PM time dropdown (agent dono formats parhta hai), Status color-coding,
      Image Preview column (IMAGE formula, Drive links convert), purani test rows clear

### Phase 5 (baaki)
- [ ] GitHub Actions pe shift (laptop band ho to bhi 24/7 - subah ke posts ke liye zaroori)
