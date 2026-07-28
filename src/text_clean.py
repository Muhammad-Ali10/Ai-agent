"""
text_clean.py - Post ka text/URL saaf karne wale chhote auzaar.

Kyun: copy-paste se aksar gandagi saath aa jati hai -
  - fazool quote (") aur line-breaks
  - URLs me tracking (fbclid, utm_source, gclid...) jo Facebook/Google lagate hain

NOTE: Facebook jo `fbclid` CLICK ke waqt khud lagata hai use hum nahi rok sakte -
wo FB ke server pe hota hai, hamare link me nahi. Yahan hum sirf ye pakka karte
hain ke JO link hum bhejte hain wo bilkul saaf ho.
"""
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Yeh tracking parameters hata dete hain
JUNK_PARAMS = {
    "fbclid", "gclid", "msclkid", "igshid", "mc_cid", "mc_eid", "_ga", "ref",
}
JUNK_PREFIXES = ("utm_",)

_URL_RE = re.compile(r"https?://[^\s<>\"']+")


def clean_url(url):
    """Ek URL me se tracking parameters hata do (baaki sab waisa hi)."""
    url = str(url).strip()
    if not url.lower().startswith(("http://", "https://")):
        return url
    try:
        parts = urlsplit(url)
        keep = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                if k.lower() not in JUNK_PARAMS
                and not k.lower().startswith(JUNK_PREFIXES)]
        return urlunsplit((parts.scheme, parts.netloc, parts.path,
                           urlencode(keep), parts.fragment))
    except ValueError:
        return url


def clean_text(text):
    """
    Post ka text saaf karo:
      - shuru/aakhir ke extra space aur line-break
      - fazool quote (") jo copy karte waqt saath aa jata hai
      - text ke andar jo URLs hain unki tracking bhi hata do
    Baaki content bilkul waisa hi rehta hai.
    """
    t = str(text).strip()

    # Bin-jodi quote (paste ki ghalti) - hata do
    while t.count('"') % 2 == 1 and (t.endswith('"') or t.startswith('"')):
        t = t[:-1].strip() if t.endswith('"') else t[1:].strip()

    # Text ke andar wale URLs saaf karo
    return _URL_RE.sub(lambda m: clean_url(m.group(0)), t)
