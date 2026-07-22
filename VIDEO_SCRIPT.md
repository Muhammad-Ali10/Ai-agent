# 🎬 Pinterest Standard Access — Demo Video Script

> **Maqsad:** Pinterest reviewers ko dikhana ke app OAuth sahi karti hai aur asli API
> action karti hai. Yehi ek raasta hai asli pins banane ka.

---

## ⚠️ Sabse Zaroori Baat (video reject hone ki #1 wajah)

Pinterest ki shart:

> *"Reviewers want to see the **user-authorization screen**, the **token exchange**, and an
> **authenticated API call** in the **same recording**. If your video starts after the token
> already exists, expect a denial."*

**Matlab:** Video me OAuth se le kar pin banne tak — **sab kuch ek hi recording me, bina
kaate**. Agar token pehle se maujood ho aur tum seedha pin banao → **REJECT**.

Isliye `src/demo_for_review.py` banayi hai — wo yeh sab **ek run me** kar deti hai.

---

## 📋 Recording Se Pehle (5 min ki tayyari)

- [ ] **1. Purani token file delete karo** (bohot zaroori — warna OAuth flow nahi dikhega):
      ```
      del credentials\pinterest_token.json
      ```
- [ ] **2. Pinterest me pehle se login raho** (browser me) — taake video me sirf
      "Give access" wala consent screen aaye, password typing nahi
- [ ] **3. Terminal ka font bara karo** (Ctrl + Shift + Plus) — text saaf parha jaye
- [ ] **4. Terminal saaf karo**: `cls`
- [ ] **5. Zaati cheezein band karo** — WhatsApp, email, personal tabs (video Pinterest dekhega)
- [ ] **6. Recording tool: SNIPPING TOOL** (neeche tareeqa)

> ⚠️ **Xbox Game Bar (Win+G) kaam NAHI karega!** Wo sirf ek app window record karta hai
> aur desktop pe kehta hai *"Gaming features aren't available for the Windows desktop"*.
> Hamari video me **terminal AUR browser dono** chahiye — isliye **Snipping Tool** use karo.

### 🎥 Snipping Tool se recording (built-in hai, kuch install nahi karna)

1. **Start** dabao → likho `Snipping Tool` → kholo
2. Upar **camera** aur **video camera** ke 2 icons honge → **video camera** 🎥 wala chuno
3. **"+ New"** dabao
4. Mouse se **poori screen** select karo (ya jitna hissa chahiye)
5. **"Start"** dabao → 3-2-1 countdown → recording shuru
6. Ab apna demo karo (terminal → browser → terminal)
7. Khatam pe **stop** (■) dabao
8. **"Save"** dabao → video `.mp4` me save ho jayegi

> Snipping Tool poori screen record karta hai — app badalne pe bhi recording chalti rehti hai.
> Awaaz nahi aati, lekin Pinterest ko awaaz chahiye bhi nahi.

**Agar Snipping Tool me video wala option na mile** → Microsoft Store se update kar lo,
ya [OBS Studio](https://obsproject.com/) (free) install kar lo.

---

## 🎥 Recording (2–3 minute, ek hi take)

### Shot 1 — Terminal (0:00)
Recording shuru karo. Terminal dikhe. Yeh chalao:

```
cd E:\ai-agent
python src\demo_for_review.py
```

Script khud sab kuch batati chalegi. **Kuch bolna zaroori nahi** (Pinterest ko awaaz nahi chahiye).

### Shot 2 — OAuth consent screen (~0:15) ⭐ SABSE AHEM
- Browser khud khulega → Pinterest ka **"Give access"** page
- **2-3 second ruko** taake reviewer permissions parh le
- Phir **"Give access"** dabao
- ✅ Yeh screen video me saaf dikhni chahiye — yehi wo cheez hai jiske bina reject hota hai

### Shot 3 — Wapas terminal (~0:30)
Terminal pe wapas aao. Script khud dikhayegi:
- ✅ Authorization code received
- ✅ Access token received
- ✅ Refresh token received
- ✅ `GET /user_account` → 200 (tumhara username, board_count)
- ✅ `GET /boards` → 200 (boards ki list)
- ✅ `POST /pins` → **201 Created** (pin ban gayi)

**Har step pe 2 second ka gap khud hai** — script me `sleep` daala hai taake reviewer parh sake.

### Shot 4 — Khatam (~2:00)
`DEMO COMPLETE` dikhne ke baad **2-3 second ruk kar** recording band karo.

---

## ✅ Video Check Karo (bhejne se pehle)

- [ ] **Pinterest ka "Give access" wala screen** saaf dikh raha hai?
- [ ] **Token exchange** (Access token received) dikha?
- [ ] **API call ka response 200/201** dikha?
- [ ] Ek hi recording hai — **beech me kaat to nahi**?
- [ ] Text parha ja raha hai (chhota to nahi)?
- [ ] Koi zaati/private cheez to nazar nahi aa rahi?

Agar koi bhi ❌ hai → dubara record karo (token file phir delete karke).

---

## 📝 Application Form Ka Text (copy-paste karo)

### App purpose / What does your app do?
```
Social Poster is a personal scheduling tool for my own Pinterest business
account (Buongiorno Immagini - buongiornoimg.it).

I maintain a Google Sheet where I plan my daily "buongiorno" (good morning)
image posts - each row has the image, title, description, hashtags, target
board, and the date/time I want it published. The app reads that sheet and
creates the Pin on my own board at the scheduled time using the v5 API.

It only ever posts to my own account and my own boards. It does not access
other users' data, does not run ads, and is not offered to anyone else.
```

### Which endpoints do you use?
```
POST /v5/pins           - create the scheduled Pin (core action)
GET  /v5/boards         - list my own boards so the sheet can target the right one
GET  /v5/user_account   - verify the authenticated account
OAuth 2.0               - authorization code flow with refresh tokens
```

### Why do you need Standard access?
```
Trial access cannot create Pins in production (403, code 29 - "Apps with
Trial access may not create Pins in production"). The demo therefore shows
the Pin creation against the API Sandbox, exactly as that error message
instructs.

Standard access is required for the app to publish Pins to my own live
boards, which is its only purpose.
```

### Rate limits / volume
```
Very low volume: a maximum of 10 Pins per day to a single account, spaced
at least 3 minutes apart. These limits are hard-coded in the application.
```

---

## ⏱️ Review Ka Waqt

- **Saaf application** → aam tor pe **1 hafte** ke andar jawab
- Agar wo kuch tabdeeli maangein → **3–4 hafte**

Is doran hum **Facebook + Instagram** (Phase 4) pe kaam kar sakte hain — waqt zaya nahi hoga.

---

## ❌ Reject Hone Ki Aam Wajah (in se bacho)

| Wajah | Bachne ka tareeqa |
|-------|-------------------|
| **OAuth consent screen nahi dikha** (#1 wajah) | Token file pehle delete karo — script khud rok degi warna |
| **API action saaf nahi dikha** | Script response status khud print karti hai |
| Video kaat kar joda hua | Ek hi take me record karo |
| Token pehle se maujood tha | `del credentials\pinterest_token.json` |
| Text parha nahi ja raha | Font bara karo |
| Sirf terminal record hua, browser nahi | Game Bar mat use karo — **Snipping Tool** se poori screen record karo |

---

## 🆘 Kuch Ghalat Ho To

Script koi error de → **screenshot bhej do**, main foran fix kar dunga.
Video reject ho jaye → Pinterest wajah batata hai, wo bhej dena — hum theek karke dubara bhejenge.
