# 🧑 SETUP GUIDE — Phase 4: Facebook + Instagram

> Meta (Facebook/Instagram) ka rasta Pinterest se thoda lamba hai, lekin FREE hai.
> Steps ko tarteeb se karo. Atak jao to Claude ko batao/screenshot bhejo.

---

## ⚠️ Meta ke 3 sakht rules (pehle samajh lo)

1. **Facebook**: API sirf **Page** pe post karti hai — personal profile pe NAHI (Page hai tumhare paas ✅)
2. **Instagram**: sirf **Business ya Creator** account pe kaam karti hai — personal pe NAHI
3. **Instagram** ka **Facebook Page se linked** hona zaroori hai

---

## ✅ STEP 1 — Instagram ko Business/Creator banao (10 min) — **PEHLE YEH**

Phone pe Instagram app me:
1. Apni **profile** → upar right **☰ (menu)** → **Settings and privacy**
2. Neeche **"Account type and tools"** (ya "Creator/Business tools")
3. **"Switch to professional account"**
4. **Creator** ya **Business** chuno (dono chalenge — Business behtar hai)
5. Category chuno (jaise "Digital creator" ya "Personal blog")
6. Steps follow karke complete karo

## ✅ STEP 2 — Instagram ko Facebook Page se link karo (5 min)

Instagram app me:
1. **Profile** → **Edit profile**
2. **"Page"** (ya "Connect or create") pe click
3. Apni **Facebook Page** select karke link kar do

> Ya Facebook Page ki settings se bhi ho sakta hai: Page → Settings → "Linked accounts" → Instagram

## ✅ STEP 3 — Meta Developer App banao (15 min)

1. **https://developers.facebook.com/** → apne Facebook se login
2. Upar right **"My Apps"** → **"Create App"**
3. **Use case** puchega → **"Other"** → **Next**
4. App type: **"Business"** → **Next**
5. App name: `Social Poster` → email → **Create app**
6. App ban jayegi → dashboard khulega

## ✅ STEP 4 — Products add karo

Dashboard me **"Add products"** me se:
1. **"Facebook Login"** → Set up
2. Search karke **"Instagram"** ya **"Instagram Graph API"** bhi add karo

## ✅ STEP 5 — Token aur IDs nikalo (Claude madad karega)

Yeh thoda technical hai. Values `.env` me jaati hain (KABHI is doc me nahi — yeh file
protected nahi hoti). Lagti yeh hain:
- **App ID** + **App Secret** (Settings → Basic me) → `.env` ke `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET`
- **Graph API Explorer ka (short) token** → `.env` ke `FB_SHORT_TOKEN`
- Phir `python src/facebook_setup.py` chalao — wo khud:
  - short token ko **long-lived** (kabhi expire na ho) banata hai
  - tumhari **Page ID + Page token + Instagram Account ID** dhoond ke `.env` me daal deta hai

> ⚠️ `/me` me agar personal profile ka naam (jaise "Ch Ch") aaye — matlab abhi USER token
> hai, Page token nahi. facebook_setup.py isse theek Page token me badal deta hai.

---

# 🅱️ INSTAGRAM — Plan B (Instagram Login, FB Page ke baghair)

> Kyun: Is account ka business-portfolio jis tarah set hai, Facebook Page ↔ Instagram
> link ka rasta band hai. Isliye Instagram ko **seedha** connect karte hain (Page ki
> zaroorat nahi). Yeh Meta ka official "Instagram API with Instagram business login" hai.

## Step B1 — App me Instagram business login enable karo

1. **https://developers.facebook.com/** → My Apps → **Social Poster**
2. Left sidebar → **Products** → **Instagram** → **"API setup with Instagram business login"**
   (do options hongi — "with Facebook login" NAHI, balki **"Instagram business login"** wala)
3. Neeche **"Business login settings"** / **"Set up Instagram business login"** section kholo
4. **"OAuth redirect URIs"** me yeh daalo (bilkul aise hi) aur **Save**:
   ```
   https://localhost:8000/callback
   ```

## Step B2 — Instagram App ID + Secret nikalo

Usi Instagram business login settings me (ya Instagram > "App settings" me):
- **Instagram app ID** — copy karo (yeh Facebook App ID se ALAG hai)
- **Instagram app secret** — copy karo

`.env` me daalo:
```
INSTAGRAM_APP_ID=yahan_instagram_app_id
INSTAGRAM_APP_SECRET=yahan_instagram_app_secret
```

## Step B3 — Connect karo

```
python src/instagram_auth.py
```
- Browser khulega → Instagram (business) se login → **Allow**
- Login ke baad browser `https://localhost:8000/...` pe jayega jo **load nahi hoga**
  (yeh normal hai) — bas us page ka **poora URL address bar se copy** karke terminal me paste karo
- Token + user ID khud `.env` me save ho jayenge ✅

---

## ✅ STEP 6 — App Review (Meta ka approval)

Standard access ke liye Meta review maangta hai (Pinterest ki tarah):
- **Permissions chahiye**: `pages_manage_posts`, `pages_read_engagement`,
  `instagram_basic`, `instagram_content_publish`
- **Screencast video** + business verification maang sakte hain
- Video/descriptions **Claude banayega** (Pinterest wali tarah)

> ⏱️ Meta review: aam tor pe **kuch din se 2-3 hafte**. Isliye jaldi shuru karna behtar.

---

## 📋 Checklist

- [ ] Instagram **Business/Creator** ban gaya
- [ ] Instagram **FB Page se linked**
- [ ] Meta **Developer app** bani (`Social Poster`, Business type)
- [ ] Facebook Login + Instagram products add hue
- [ ] App ID + Secret mile
- [ ] Page Access Token + Page ID + IG Account ID mile (Claude ke saath)
- [ ] App Review submit (baad me)

---

## 🎯 Abhi Karo

**STEP 1 aur 2** (Instagram business banao + FB Page se link) — yeh phone pe 15 min ka kaam hai.
Phir **STEP 3** (Meta app). Step 5 pe aa kar Claude ko batao — wo tokens nikalne me madad karega.

Claude is doran **FB + IG ka posting code** bana raha hai (parallel), taake accounts tayyar hote hi test kar sakein.
