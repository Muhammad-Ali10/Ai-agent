r"""
Image ke filename se SAAF Italian description banata hai.

MASLA: filenames SEO ke liye hain, jaise
    "Immagini-buongiorno-caffe-balcone-con-tazza-e-vista-costa-italiana"
Sidha caption me daalo to category do dafa aa jati hai:
    "Immagini buongiorno caffe balcone... - buongiorno caffe"  <- bhadda

HAL: shuru ka SEO hissa hatao, sirf asli manzar bachao:
    "Balcone con tazza e vista costa italiana"

Ye rules kai koshishon ke baad bane hain - badalne se pehle test chala lena:
    python tools\describe.py        (khud ka test chal jata hai)
"""
import re

# SEO/filler lafz jo filename ke shuru me aate hain
SEO = {"immagini", "immagine", "belle", "bella", "bello", "foto", "gratis",
       "whatsapp", "buongiorno", "buon", "buona", "nuove", "nuova",
       "lunedi", "lunedì", "martedi", "martedì", "mercoledi", "mercoledì",
       "giovedi", "giovedì", "venerdi", "venerdì", "sabato", "domenica"}

# Category ke naam - sirf tab hatao jab pehle koi SEO lafz mila ho
CATS = {"caffe", "caffè", "fiori", "fiore", "amore", "mio", "amici", "amico",
        "estate", "estivo", "estiva", "autunno", "autunnale", "inverno",
        "invernale", "pioggia", "piovoso", "ferragosto", "natale", "natalizio",
        "capodanno", "halloween", "romantico", "romantica", "mamma", "papa",
        # naye pages ki categories.
        # Note: "gatti" (page ka naam) hai lekin "gatto" NAHI - wo aksar
        # asli subject hota hai ("gatto che dorme tra i fiori").
        "bambini", "cuore", "gatti", "nonni", "pietra", "bianca",
        "ali", "sorriso", "fate", "sole", "ritardo", "inedite", "inediti",
        "divertente", "divertenti"}

# Jodne wale chhote lafz
FILL = {"di", "e", "con", "la", "il", "lo", "i", "gli", "le", "un", "una",
        "per", "del", "della", "dei", "da", "al", "alla", "su", "in"}

# Shuru me aane wale aam lafz jo asli manzar nahi hote
LEAD_NOISE = {"gatti", "cani", "gattini", "ombrello", "originale", "originali",
              "bellissime", "bellissimi", "particolare", "raccolta", "musica",
              "parole", "scarica", "giornata", "auguri", "frasi"}

# Akele koi manzar nahi batate
WEAK = {"scaricare", "inviare", "condividere", "speciale", "te", "tutti",
        "tutte", "nuovi", "originali", "originale", "gratis", "auguri"}

# Accent/apostrophe - filename me ye hote hi nahi
ACCENT = [
    ("caffe", "caffè"), ("lunedi", "lunedì"), ("martedi", "martedì"),
    ("mercoledi", "mercoledì"), ("giovedi", "giovedì"), ("venerdi", "venerdì"),
    ("perche", "perché"), ("piu", "più"), ("citta", "città"), ("gia", "già"),
    ("felicita", "felicità"), ("serenita", "serenità"), ("liberta", "libertà"),
    ("papa", "papà"), ("cosi", "così"), ("piedi", "piedi"),
    ("allaperto", "all'aperto"), ("allalba", "all'alba"), ("allombra", "all'ombra"),
    ("dallalto", "dall'alto"), ("dallalba", "dall'alba"), ("dellalba", "dell'alba"),
    ("damore", "d'amore"), ("darancia", "d'arancia"), ("dacqua", "d'acqua"),
    ("dinverno", "d'inverno"), ("destate", "d'estate"), ("dautunno", "d'autunno"),
    ("doro", "d'oro"), ("dellaria", "dell'aria"), ("nellaria", "nell'aria"),
    ("sullacqua", "sull'acqua"), ("unamica", "un'amica"), ("unaltra", "un'altra"),
    ("lalbero", "l'albero"), ("terrace", "terrazza"),
]

# Jagah/naam - pehla harf bara
PROPER = ["Capri", "Positano", "Roma", "Venezia", "Firenze", "Napoli", "Toscana",
          "Amalfitana", "Amalfi", "Trevi", "Vespa", "Fiat", "Sicilia", "Italia",
          "Puglia", "Sardegna", "Como", "Garda", "Portofino", "Dolomiti",
          "Babbo Natale", "Santa Claus", "Befana"]

# Kachra filenames (AI-generated naam, random hash)
JUNK_RE = re.compile(r"gemini|generated.image|removebg|copia|[a-z0-9]{14,}", re.I)

# Lafz jinke BAAD "buongiorno" rakhna zaroori hai (warna jumla toot jata hai)
KEEP_BEFORE = {"un", "uno", "una", "il", "lo", "la", "bel", "bello", "bella",
               "dolce", "tenero", "tenera", "caro", "cara", "nuovo", "nuova",
               "questo", "questa", "ogni", "splendido", "sereno", "che"}
PREPS = {"a", "da", "in", "con", "per", "di", "al", "alla", "sul", "su", "e"}


def _fix_accents(text):
    def repl(m):
        w = m.group(0)
        return w[0].upper() + good[1:] if w[0].isupper() else good
    for bad, good in ACCENT:
        text = re.sub(rf"\b{bad}\b", repl, text, flags=re.IGNORECASE)
    return text


def describe(url, label=""):
    """
    url   : image ka poora link
    label : us page ka naam ("Buongiorno Caffè") - diya ho to description ke
            shuru se wahi lafz hata dete hain (dohra na ho)

    Return: saaf description, ya None (filename me koi manzar tha hi nahi -
            us surat me caption sirf category se banta hai)
    """
    name = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    text = re.sub(r"-\d+x\d+$", "", name).replace("-", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()

    if JUNK_RE.search(text):
        return None

    toks = text.split()

    # 1) "immagini/immagine" shuru ke hisse me ho -> us ke BAAD wala hissa lo
    low = [t.lower() for t in toks]
    idx = [i for i, t in enumerate(low[:6]) if t in ("immagini", "immagine")]
    if idx:
        toks = toks[idx[-1] + 1:]

    # 2) Shuru ke SEO/filler lafz hatao.
    #    Category ka naam sirf TAB hatao jab wo category ke naam ka hissa ho
    #    ("buongiorno caffe"), warna wo asli manzar hai ("caffe all'aperto").
    seen_seo = bool(idx)
    cat_ctx = bool(idx)
    while toks:
        t = toks[0].lower()
        nxt = toks[1].lower() if len(toks) > 1 else ""
        # agle lafz me past participle -> ye noun SUBJECT hai, rakho
        # agle lafz me past participle, ya "che/con/sul..." -> ye noun SUBJECT hai
        subject_next = bool(re.search(r"(ato|ata|uto|uta|ito|ita)$", nxt)) or nxt == "che"
        if t in SEO or t.isdigit():
            seen_seo = True
            cat_ctx = t in {"buongiorno", "buon", "buona"}
            toks.pop(0)
        elif t in CATS and cat_ctx and not subject_next:
            toks.pop(0)
        elif t in LEAD_NOISE and len(toks) > 3:
            seen_seo = True
            toks.pop(0)
        elif t in FILL and seen_seo and len(toks) > 3:
            toks.pop(0)
        else:
            break

    out = " ".join(toks)

    # 3) Aakhir ka "per il buon sabato" jaisa hissa
    out = re.sub(r"\s+per (il |la |l')?(buon|buona|buongiorno)\b.*$", "", out, flags=re.I)
    out = re.sub(r"\s+(buon|buona) (lunedì|lunedi|martedì|martedi|mercoledì|mercoledi|"
                 r"giovedì|giovedi|venerdì|venerdi|sabato|domenica)\s*$", "", out, flags=re.I)

    # 4a) Beech me pade SEO lafz
    out = re.sub(r"\s+(whatsapp\d*|gratis)\b", "", out, flags=re.I)

    # 4b) "buongiorno" hatao - lekin sirf tab jab jumla na toote
    w = out.split()
    keep = []
    for i, tok in enumerate(w):
        prev = w[i - 1].lower() if i > 0 else ""
        nxt = w[i + 1].lower() if i + 1 < len(w) else ""
        if (tok.lower() == "buongiorno" and prev and prev not in KEEP_BEFORE
                and (nxt in PREPS or prev in CATS)):
            continue
        keep.append(tok)
    out = " ".join(keep)

    # 4c) Aakhir ke SEO lafz (jitne bhi hon)
    for _ in range(5):
        new = re.sub(r"\s+(buongiorno|amici|whatsapp\d*|gratis|originali|originale"
                     r"|immagini|immagine|scaricare|condividere|nuova|nuove|nuovi)\s*$",
                     "", out, flags=re.I)
        if new == out:
            break
        out = new

    # 4d) "buongiorno <category>" kahin bhi ho to hatao - naye pages ke
    #     filenames me aam hai ("...si gioca buongiorno bambini pieni di
    #     energia", "...al mattino buongiorno pietra bianca").
    #     "scritta Buongiorno" / "buongiorno lo stesso" nahi hatte, kyunke
    #     un ke baad category ka lafz nahi aata.
    cats = "|".join(sorted(CATS, key=len, reverse=True))
    out = re.sub(rf"\s+buongiorno(\s+(?:{cats}))+", "", out, flags=re.I)
    out = re.sub(r"\s+\d{1,2}\s*$", "", out)        # aakhir ka akela number ("... bambini 1")

    # 5) Page ka naam shuru/aakhir me dohra na ho.
    #    AHEM: label me jitne lafz hain bas utne hi hatao - warna
    #    "Le fate del sole ... sole sorridente" me DONO "sole" ud jate hain
    #    aur jumle ka subject hi khatam ho jata hai.
    if label:
        lab = {x.lower() for x in label.split()
               if x.lower() not in {"buongiorno", "buon", "buona", "con", "i", "mio"}}
        budget = len(label.split())
        w = out.split()
        # Jumle ke shuru me "ma/pero" jaisa harf ho to page ka naam mat hatao -
        # "In ritardo ma non dimenticato" poora jumla hai; "In ritardo" nikalo
        # to "Ritardo ma non dimenticato" adhoora lagta hai.
        CONJ = {"ma", "pero", "però", "anche", "oppure", "eppure"}
        has_conj = any(x.lower() in CONJ for x in w[:4])
        while budget and not has_conj and len(w) > 3 and w[0].lower() in lab:
            if re.search(r"(ato|ata|uto|uta|ito|ita)$", w[1].lower()):
                break          # "Caffè versato..." - subject hai, rakho
            w.pop(0)
            budget -= 1
        budget = len(label.split())
        while budget and len(w) > 3 and w[-1].lower() in lab:
            w.pop()            # "...con scritta Buongiorno le ali" -> "le ali" gaya
            budget -= 1
        out = " ".join(w)

    # 5b) Label hatane ke baad shuru me "Buongiorno" reh sakta hai - wo fazool hai
    #     (caption khud "Buongiorno! ☀️" se shuru hota hai). "Buongiorno amore
    #     mio" jaisa poora phrase na ho to hata do.
    w = out.split()
    while len(w) > 3 and w[0].lower() in SEO and w[0].lower() not in ("bella", "belle"):
        w.pop(0)
    out = " ".join(w)

    out = re.sub(r"\s+in illustrazione\s*$", "", out, flags=re.I)

    # Lambe filenames ke aakhir me SEO padding hoti hai:
    #   "...con scritta Sorridi al nuovo giorno buongiorno allegro per tutti"
    # Jumla pehle se poora hai, to "buongiorno" se aage ka hissa kaat do.
    # ("con scritta Buongiorno" nahi kaatte - wahan buongiorno hi matlab hai.)
    w = out.split()
    if len(w) > 8:
        for i in range(2, len(w)):
            if w[i].lower() == "buongiorno" and w[i - 1].lower() != "scritta":
                out = " ".join(w[:i])
                break
    out = _fix_accents(re.sub(r"\s+", " ", out).strip(" -—,"))
    out = re.sub(r"\b(vita|giornata|questa|tutto) e\b",
                 lambda m: m.group(1) + " è", out, flags=re.I)
    out = re.sub(r"^(di|del|della|da|dal|e|con|in|al)\s+", "", out, flags=re.I).strip()

    for p in PROPER:
        out = re.sub(rf"\b{p}\b", p, out, flags=re.IGNORECASE)

    # 6) Ab bhi kamzor? -> koi description nahi
    noise = SEO | FILL | CATS | LEAD_NOISE | WEAK
    real = [x for x in out.split() if x.lower() not in noise and not x.isdigit()]
    if len(out.split()) < 3 or len(real) < 2:
        return None

    return out[0].upper() + out[1:]


if __name__ == "__main__":
    TESTS = [
        ("Immagini-buongiorno-caffe-balcone-con-tazza-e-vista-costa-italiana.webp",
         "Buongiorno Caffè", "Balcone con tazza e vista costa italiana"),
        ("Buongiorno-con-i-fiori-sentiero-fiorito-in-un-giardino.webp",
         "Buongiorno con i Fiori", "Sentiero fiorito in un giardino"),
        ("Immagini-buon-lunedi-whatsapp-caffe-allaperto-con-vista-panoramica.webp",
         "Buon Lunedì", "Caffè all'aperto con vista panoramica"),
        ("Buongiorno-caffe-versato-lentamente-nella-tazza.webp",
         "Buongiorno Caffè", "Caffè versato lentamente nella tazza"),
        ("Buongiorno-caffe-tazza-di-espresso-sul-bancone.webp",
         "Buongiorno Caffè", "Tazza di espresso sul bancone"),
        ("Buongiorno-pioggia-gatti-gatto-che-dorme-tra-i-fiori.webp",
         "Buongiorno Pioggia", "Gatto che dorme tra i fiori"),
        ("Un-tenero-buongiorno-di-domenica-gattino-che-dorme.webp",
         "Buona Domenica", "Un tenero buongiorno di domenica gattino che dorme"),
        ("Buongiorno-estate-faraglioni-di-capri-vista-dallalto.webp",
         "Buongiorno Estate", "Faraglioni di Capri vista dall'alto"),
        ("Caffe-freddo-con-frutti-di-bosco.webp", "Buon Venerdì",
         "Caffè freddo con frutti di bosco"),
        ("foto-buongiorno.webp", "Immagini Buongiorno", None),
        ("Gemini-Generated-Image-l97getl97g-removebg-preview.png", "Buon Sabato", None),
    ]
    bad = 0
    for fn, lab, want in TESTS:
        got = describe("https://buongiornoimg.it/wp-content/uploads/2026/07/" + fn, lab)
        ok = got == want
        bad += not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {str(got)[:52]}")
        if not ok:
            print(f"       chahiye tha: {want}")
    print(f"\n  {len(TESTS) - bad}/{len(TESTS)} pass")
