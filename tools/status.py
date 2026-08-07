r"""
Agent ka poora haal ek nazar me.
Chalao:  python tools\status.py
"""
import io
import sys
from collections import Counter
from datetime import datetime

import pytz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"E:\ai-agent\src")
import config, google_sheet, main as agent  # noqa: E402

now = datetime.now(pytz.timezone(config.TIMEZONE))
print("=" * 62)
print(f"  SOCIAL AGENT - HAAL  ({now:%Y-%m-%d %I:%M %p} PKT)")
print("=" * 62)
print(f"  TEST_MODE        : {config.TEST_MODE}")
print(f"  FB link cards    : {config.FACEBOOK_LINK_CARDS} (false = photo post)")
print(f"  Pinterest sandbox: {config.PINTEREST_SANDBOX}")
print(f"  Daily limits     : {config.DAILY_LIMITS}")

posts = [p for p in google_sheet.get_all_posts() if str(p.get("Platform", "")).strip()]
st = Counter(str(p.get("Status", "")).strip().lower() or "(khali)" for p in posts)
print(f"\n  Sheet me {len(posts)} posts")
for k, v in st.most_common():
    print(f"    {k:10s}: {v}")

# Aaj kitni ho chuki
today = f"{now:%Y-%m-%d}"
print("\n  Aaj ka hisab:")
for pf, lim in config.DAILY_LIMITS.items():
    n = google_sheet.count_posted_today(posts, pf, today)
    print(f"    {pf:10s}: {n}/{lim}")

# Due lekin abhi tak pending
due = []
for p in posts:
    if str(p.get("Status", "")).strip().lower() != "pending":
        continue
    dt, err = agent.parse_schedule(p)
    if dt and now >= dt:
        due.append((p["_row_number"], p.get("Platform"), p.get("Date"), p.get("Time")))
print(f"\n  DUE lekin abhi pending: {len(due)}")
for r, pf, d, t in due[:6]:
    print(f"    Row {r}: {pf} | {d} {t}")

# Agli post
future = []
for p in posts:
    if str(p.get("Status", "")).strip().lower() != "pending":
        continue
    dt, err = agent.parse_schedule(p)
    if dt and dt > now:
        future.append((dt, p))
if future:
    future.sort(key=lambda x: x[0])
    dt, p = future[0]
    print(f"\n  AGLI POST: {dt:%Y-%m-%d %I:%M %p} | {p.get('Platform')}")
    print(f"    {str(p.get('Title'))[:56]}")
    print(f"  Baqi pending (future): {len(future)}")

# Tokens
print("\n  Tokens:")
for name, mod in (("Facebook", "facebook_poster"), ("Instagram", "instagram_poster"),
                  ("Pinterest", "pinterest_poster")):
    try:
        m = __import__(mod)
        ok, msg = m.check_token()
        print(f"    {name:10s}: {'OK' if ok else 'FAIL'} - {msg[:52]}")
    except Exception as e:
        print(f"    {name:10s}: check nahi ho saka ({type(e).__name__})")
