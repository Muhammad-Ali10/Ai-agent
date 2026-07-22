# 🤖 Social Media Posting Agent

Google Sheet se posts parh kar automatically social media pe post karta hai.
**Bilkul FREE** (official APIs). Platforms: **Pinterest, Facebook, Instagram**.
Phase 1 = Pinterest.

---

## 📁 Folder Structure

```
ai-agent/
├── PLAN.md                 # MASTER PLAN (goal, phases, 23 loopholes+fixes)
├── SETUP_GUIDE.md          # USER ke tasks ki step-by-step guide
├── run_agent.bat           # DOUBLE-CLICK: agent hamesha ke liye chalu
├── src/                    # saara code
│   ├── config.py           # settings + secret keys load (limits LOCKED)
│   ├── google_sheet.py     # Sheet parhna/likhna + Reports tab (L14 safe)
│   ├── validator.py        # post se pehle har cheez ki jaanch (L6/L15)
│   ├── image_handler.py    # image download/check/convert (L12/L16)
│   ├── notifier.py         # email alerts (sirf masla ho tab)
│   ├── pinterest_auth.py   # EK DAFA: Pinterest login (tokens auto-save)
│   ├── pinterest_poster.py # Pinterest pe pin banana (auto token-refresh)
│   ├── list_boards.py      # tumhare boards ki list dikhata hai
│   ├── main.py             # ek dafa chalne wala (dimaag)
│   └── scheduler.py        # HAMESHA chalne wala (har 5 min check)
├── credentials/            # Google JSON + Pinterest tokens (SECRET)
├── data/
│   └── SHEET_TEMPLATE.csv  # Google Sheet ka template
├── logs/
├── .env.example            # secret keys ka template
├── .env                    # asli secrets (tum banaoge - kabhi share nahi)
└── requirements.txt
```

---

## 🚀 Setup Steps (Pehli Baar)

### 1. Python libraries install karo
```
pip install -r requirements.txt
```

### 2. `.env` file banao
`.env.example` ko copy karke `.env` banao, phir usme apni details bharo
(Pinterest App ID/Secret — SETUP_GUIDE.md ke Task 2 se milte hain).

### 3. Google Sheet banao
- `data/SHEET_TEMPLATE.csv` ko Google Sheets me **import** karo (File > Import)
- Sheet ka **ID** URL me se copy karke `.env` ke `GOOGLE_SHEET_ID` me daalo
- Sheet ko apni **service account email** ke saath **share** karo (Editor)
  (email JSON file ke andar "client_email" me hoti hai)

### 4. Google JSON file rakho
- Google Cloud se downloaded JSON ko `credentials/service-account.json` naam se rakho ✅ (ho chuka)

### 5. Pinterest se connect karo (ek dafa)
```
python src/pinterest_auth.py
```
- Browser khulega -> tum login karke "Give access" dabao
- Tokens KHUD save ho jayenge + tumhare boards ki list milegi
- Ek board ka ID `.env` ke `PINTEREST_BOARD_ID=` me daalo
- (Refresh token ~1 saal chalta hai - baar baar login NAHI karna padega)

### 6. Chala do! (pehle TEST MODE me)
```
python src/main.py
```
- `.env` me `TEST_MODE=true` rakho -> asli post nahi hogi, sirf dikhayega
- Sab theek lage to `TEST_MODE=false` karke asli post

### 7. Hamesha chalane ke liye (Phase 2)
```
python src/scheduler.py
```
Ya seedha **`run_agent.bat` pe double-click** karo.
Yeh har 5 minute baad Sheet check karta rehta hai. Ctrl+C = band.

**Laptop on hote hi khud chalu ho (L17 fix):**
1. Windows me **Task Scheduler** kholo
2. **Create Basic Task** -> naam: `Social Agent`
3. Trigger: **When I log on**
4. Action: **Start a program** -> `E:\ai-agent\run_agent.bat` choose karo
5. Finish — bas! Ab laptop on karte hi agent chalna shuru.

---

## 📌 Boards (Pinterest)

Har pin apne sahi board me jayegi. Sheet ke **Board** column me bas board ka
**naam** likho (ID nahi) — jaise `Buongiorno Halloween`.

Apne saare boards dekhne ke liye:
```
python src/list_boards.py
```
Yeh naam + ID dono dikhata hai, aur dropdown banane ke liye list bhi deta hai.

> Board khali chhod do to `.env` wala `PINTEREST_BOARD_ID` (default) use hoga.

---

## 🛡️ Safety Features (built-in)
- **TEST_MODE**: dry-run - bina post kiye test (image link bhi check hota hai)
- **Daily limits**: Pinterest 10/din, FB/IG 2/din - hard-coded (ban se bachao)
- **Duplicate protection**: "posted" dubara nahi + crash-safe "working" status
- **Lock file**: agent ghalti se 2 dafa chale to dusri copy khud band
- **Sheet structure check**: column ka naam badla to agent ruk jata hai
- **Expire rule**: 24h+ purani pending post kabhi auto-post nahi hogi
- **Late_Policy**: time nikal jaye to har post ki apni marzi (post-anyway/skip)
- **Posts ke beech gap**: 3 min (spam signal se bachao)
- **Token auto-refresh**: Pinterest token khud taza hota rahega (~1 saal login-free)
- **Status tracking**: pending/posted/failed/invalid/expired + Post_URL Sheet me
- **Timezone**: har time Pakistan (PKT) me
- **Retry**: fail ho to 3x koshish (5 min gap) - sirf temporary maslon pe
- **Catch-up**: laptop band tha? on hote hi reh gayi posts ho jayengi
- **Hashtag warning**: pichli 5 posts pe wahi hashtags hon to batata hai (shadowban se bachao)
- **Reports tab**: roz ki summary Sheet me khud likhta hai
- **Email alert**: sirf masla ho tab (setup optional)

---

## 📝 Sheet Columns
| Column | Kaam |
|--------|------|
| Platform | Pinterest / Facebook / Instagram |
| Account | account ka naam (record ke liye) |
| **Board** | **kaunse board me pin jaye (naam likho) - Pinterest ke liye** |
| Date | 2026-07-15 (aisa format) |
| Time | 14:30 (24-hour, PKT) |
| Title | post/pin ka title |
| Content | caption/description |
| Image_Link | image ka link (Drive share-link chalega) |
| Hashtags | #ai #tech |
| Post_Link | pin pe click karne se jahan jana ho (optional) |
| Late_Policy | post-anyway / skip (agar time nikal gaya) |
| Status | pending -> agent khud badlega |
| Posted_At | kab post hui (agent likhta hai) |
| Post_URL | asli post ka link (agent likhta hai) |
| Error | agar fail ho to wajah (agent likhta hai) |

> **Naya post add karna:** nayi row banao, Status me `pending` likho. Bas.
> **Image:** Google Drive me rakho -> right-click -> Share -> "Anyone with the link" -> link copy karke Image_Link me daalo. Agent khud direct format me badal lega.
> **Note (Trial access):** jab tak Pinterest Standard access nahi milta (Phase 3), pins sirf TUMHE dikhengi - yeh normal hai, bug nahi.
