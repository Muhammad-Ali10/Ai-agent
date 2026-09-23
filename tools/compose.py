r"""
Ek post ka Title / Content / Hashtags banata hai.

build_plan.py (naya plan) aur fix_broken.py (toota image badalna) dono yahi
istemal karte hain - taake caption ka andaaz har jagah ek jaisa rahe.
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from describe import describe  # noqa: E402

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
# Din wali posts ke liye (Instagram pe "Buon Lunedi! ..." ke baad)
NO_DESC_DAY = [
    "Buona giornata a tutti 💛",
    "Che sia una giornata serena 💛",
    "Un sorriso per iniziare 💛",
    "Nuova immagine da scaricare e condividere 💛",
    "Un pensiero gentile per te 💛",
    "Buon risveglio a tutti 💛",
    "Che sia una bella giornata 💛",
    "Un augurio speciale per oggi 💛",
]
# Har (platform, page) ka apna counter - warna ek hi variant dohra jata hai
_n = defaultdict(int)


def make(slug, img, platform, page_url, is_day):
    """
    slug     : page ka slug ("buongiorno-caffe")
    img      : image ka poora link
    platform : "Facebook" ya "Instagram"
    page_url : us page ka URL
    is_day   : ye din wala page hai? (Buon Lunedi etc.)

    Return: Sheet ki ek row (dict)
    """
    label, tags = META.get(slug, (slug, "#buongiorno"))
    desc = describe(img, label)
    if not desc:
        _n[(platform, slug)] += 1
    k = _n[(platform, slug)] - 1

    if platform == "Facebook":
        if desc:
            opening = (f"Buongiorno! ☀️ {desc}: una nuova immagine di "
                       f"{label.lower()} da scaricare e condividere.")
        else:
            opening = "Buongiorno! ☀️ " + NO_DESC_FB[k % len(NO_DESC_FB)].format(
                c=label.lower())
        content = (f"{opening}\n\n👉 Scaricala gratis qui: {page_url}\n\n"
                   f"Nuove immagini ogni giorno, senza registrazione. 💛")
        hashtags = f"{BASE_TAGS} {tags}"
    else:
        # DIN wali category khud ek SALAAM hai -> "Buon Venerdì! ☀️ ..."
        if desc:
            opening = (f"{label}! ☀️ {desc} 💛" if is_day
                       else f"Buongiorno! ☀️ {desc} — {label.lower()} 💛")
        elif is_day:
            opening = f"{label}! ☀️ " + NO_DESC_DAY[k % len(NO_DESC_DAY)]
        else:
            opening = "Buongiorno! ☀️ " + NO_DESC_IG[k % len(NO_DESC_IG)].format(c=label)
        content = (f"{opening}\n\n🔗 Scarica gratis qui: {page_url}\n"
                   f"📌 Salva questo post e condividilo con chi ami.")
        hashtags = f"{BASE_TAGS} {tags} {IG_EXTRA}"

    return {
        "Platform": platform,
        "Account": "my_facebook" if platform == "Facebook" else "my_instagram",
        "Board": "", "Title": f"{label} — {desc}" if desc else label,
        "Content": content, "Image_Link": img, "Preview": "", "Hashtags": hashtags,
        "Post_Link": page_url, "Late_Policy": "post-anyway", "Status": "pending",
        "Posted_At": "", "Post_URL": "", "Error": "",
    }
