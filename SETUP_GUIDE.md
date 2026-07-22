# 🧑 SETUP GUIDE — Tumhare Tasks (Step by Step)

> Yeh kaam sirf TUM kar sakte ho (accounts/logins tumhare hain).
> Har task ke aakhir me ek checklist hai. Atak jao to Claude ko batao/screenshot bhejo.
>
> **PLATFORMS**: Pinterest, Facebook, Instagram
> (LinkedIn removed — 14 July 2026 | Twitter/X paid tha isliye pehle hi out)

---

# ✅ TASK 1 — Google Cloud Setup (30 min) — **COMPLETE ✅ (14 July 2026)**

> ⚠️ **Login email**: `muhammadalitahir6232@gmail.com`

<details>
<summary>Steps (complete ho chuka - record ke liye)</summary>

1. https://console.cloud.google.com/ pe login
2. New Project: `social-agent`
3. **Google Sheets API** → Enable
4. **Google Drive API** → Enable
5. APIs & Services → Credentials → Create Credentials → **Service Account** (`sheet-reader`, role: Editor)
6. Service account → Keys → Add Key → **JSON** → download
7. File yahan rakhi: `E:\ai-agent\credentials\service-account.json`
</details>

---

# ✅ TASK 2 — Pinterest Developer App (30 min) — **AB YEH KARNA HAI** ⭐

> Iske liye Pinterest **Business account** chahiye. Personal hai to free me convert
> ho jata hai (Step 1 me bataya hai). Business account ke bina developer app nahi banti.

## Steps:

### Hissa A — Business account (agar pehle se nahi hai)
1. **https://www.pinterest.com/** pe login karo (ya account banao)
2. Personal account ho to: **Settings** → **Account management** →
   **"Convert to a business account"** → follow karo (free hai, 2 min)
   - Ya seedha business account banao: https://business.pinterest.com/

### Hissa B — Developer app banana
3. Browser me jao: **https://developers.pinterest.com/**
4. Upar right **"Log in"** → apne Pinterest (business) se login
5. **"My apps"** → **"Connect app"** / **"Create app"** pe click
6. Form bharo:
   | Field | Kya dalna |
   |-------|-----------|
   | App name | `Social Poster` |
   | Description | `Apni Google Sheet se apne hi account pe pins schedule/post karne ka personal tool` |
7. Terms accept → **Create**
8. **Trial access** milega (isi me hum test karenge — yaad rahe: Trial me pins
   sirf tumhe dikhti hain, public ko nahi. Standard access baad me lenge — Phase 3)

### Hissa C — Keys aur Redirect URI
9. App ke andar jao — wahan milega:
   - **App ID** — copy karke note karo
   - **App secret key** — copy karke note karo (🔒 secret hai — sirf .env file me jayega)
10. **Redirect URIs** section dhoondo → yeh add karo (bilkul aise hi):
    ```
    http://localhost:8000/callback
    ```
    → Save/Add dabao

### Hissa D — Ek board banao (agar nahi hai)
11. Pinterest.com pe wapas jao → apna profile → **Boards** → **"+ Create board"**
    - Naam koi bhi (jaise `My Posts`) — pins isi board pe jayengi

## Checklist Task 2:
- [ ] Pinterest **Business** account hai
- [ ] App `Social Poster` ban gayi (developers.pinterest.com pe)
- [ ] **App ID** mil gaya
- [ ] **App secret** mil gaya
- [ ] Redirect URI add hua: `http://localhost:8000/callback`
- [ ] Kam-az-kam 1 **board** maujood hai

---

# 🎯 Task 2 Ke Baad — Claude Ko Batao

Phir hum saath me yeh karenge (~15 min):
1. `.env` file bharna (App ID/Secret usme)
2. Google Sheet import + service account se share
3. `python src/pinterest_auth.py` → tum browser me "Give access" dabaoge
   → tokens khud save honge + tumhare boards ki list milegi
4. Board ID `.env` me daalna
5. **Dry-run test** (asli pin nahi banegi)
6. Tumhari haan ke baad → **PEHLI ASLI PIN** 🎉
   (Trial me sirf tumhe dikhegi — yeh normal hai. Public wali Phase 3 me.)

---

# 📅 BAAD KE TASKS (abhi nahi)

## TASK 3 — Pinterest Standard Access (Phase 3)
- Chalte hue system ka **demo video** submit karna hoga (video Claude banayega, tum upload karoge)
- Iske baad pins PUBLIC dikhengi

## TASK 4 — Facebook + Instagram (Phase 4)
- FB **Page** banana (agar nahi hai)
- IG account ko **Business/Creator** me convert + FB Page se link
- developers.facebook.com pe app + **Meta review** (material Claude dega)

---

## ❓ Aam Masail (agar aayen)

| Masla | Hal |
|-------|-----|
| "Convert to business" nahi mil raha | Settings me "Account management" dekho, ya business.pinterest.com se naya banao |
| Developer portal login nahi ho raha | Pehle pinterest.com pe login karo, phir developers.pinterest.com kholo |
| App banane pe koi review/wait aya | Trial access turant milta hai — screenshot bhejo agar kuch aur dikhe |
| Redirect URI save nahi ho raha | Bilkul yehi likho: `http://localhost:8000/callback` (spaces nahi) |
| JSON file kahan rakhun (Task 1) | `E:\ai-agent\credentials\` me, naam `service-account.json` |
