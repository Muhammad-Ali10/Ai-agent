# 📖 Sheet Kaise Bharni Hai (Roz Ka Kaam)

## 🖊️ Ek Post Add Karna — Column by Column

Nayi row me har column bharo:

| Column | Kya karna | Zaroori? |
|--------|-----------|----------|
| **Platform** | Dropdown se chuno: Pinterest / Facebook / Instagram | ✅ zaroori |
| **Account** | Dropdown: my_pinterest / my_facebook / my_instagram (platform ke hisab se) | ✅ |
| **Board** | **Sirf Pinterest ke liye** — dropdown se board chuno. Facebook/Instagram me **KHALI chhodo** | Pinterest pe zaroori |
| **Date** | Cell pe **DOUBLE-click** → calendar khulega → tareekh chuno | ✅ |
| **Time** | Dropdown se waqt (AM/PM): jaise 9:00 AM, 2:30 PM | ✅ |
| **Title** | Post ka title (Pinterest pe dikhta hai; FB/IG pe optional) | Pinterest pe zaroori |
| **Content** | Post ka caption/text (Italian me jo likhna ho) | ✅ |
| **Image_Link** | Image ka link (Drive ya website) — neeche tareeqa | ✅ |
| **Preview** | ⚠️ Haath mat lagao — image_link daalte hi KHUD image dikhegi | (auto) |
| **Hashtags** | #buongiorno #buongiornissimo etc. (khud lagao) | optional |
| **Post_Link** | Pinterest pin pe click karke jahan jaye (website) — optional | optional |
| **Late_Policy** | post-anyway (time nikal jaye to bhi post karo) / skip | ✅ |
| **Status** | **`pending`** likho/chuno ← ye ZAROORI! isse agent ko pata chalta hai post karni hai | ✅ |
| Posted_At / Post_URL / Error | ⚠️ Haath mat lagao — **agent khud bharega** (gray columns) | (agent) |

> **Yaad rakho:** Status = `pending` na ho to agent us row ko chhoड़ deta hai. Har nayi post pe `pending` zaroor.

---

## 🖼️ Images — 2 Tareeqe

### Tareeqa 1: Google Drive (aasan)

1. **https://drive.google.com/** pe jao (muhammadalitahir6232@gmail.com se)
2. Apni image **upload** karo (ya pehle se hai to us pe jao)
3. Image pe **right-click** → **"Share"** → **"Share"**
4. **"General access"** ko **"Restricted"** se badal kar **"Anyone with the link"** karo ⚠️ (ye zaroori!)
5. **"Copy link"** dabao
6. Wo link Sheet ke **Image_Link** column me paste karo
7. Preview column me image **khud** aa jayegi ✅

> ⚠️ **Sabse ahem:** Sharing **"Anyone with the link"** honi chahiye. "Restricted" rahi to na preview dikhegi na post hogi. Agent Drive link ko khud sahi format me badal leta hai.

### Tareeqa 2: Apni Website (sabse reliable)

Agar images tumhari website (buongiornoimg.it) pe hain, to seedha us image ka URL
(jaise `https://buongiornoimg.it/images/buongiorno1.jpg`) Image_Link me paste kar do.
Ye Drive se bhi zyada reliable hai — sab platforms pe pakka chalega.

---

## ✅ Post Hone Ke Baad

- Agent sahi date/time pe post kar dega (agar us waqt laptop on ho)
- **Status** apne aap badlega:
  - 🟢 `posted` = ho gaya (Post_URL me link mil jayega)
  - 🔴 `failed` = koi masla (Error column me wajah)
  - 🟡 `pending` = abhi waqt nahi aaya / laptop band tha
  - 🟠 `invalid` = kuch galat bhara (Error dekho)

---

## 💡 Tips

- **Hafte bhar ki posts** ek saath daal sakte ho — agent har ek ko apne time pe karega
- **Har platform ki alag row** — ek hi content 3 jagah copy-paste mat karo (spam signal)
- **Hashtags rotate** karo — har post pe bilkul same mat rakhо
- **Daily limit**: Pinterest 10, Facebook 2, Instagram 2 (agent khud rok deta hai)
- Agent kya kar raha hai dekhna ho → `logs\agent.log` khol lo
