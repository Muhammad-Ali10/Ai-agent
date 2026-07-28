"""
main.py - Agent ka dimaag. Yeh chalao:  python src/main.py
(Ya hamesha chalane ke liye:  python src/scheduler.py)

Kaam:
  1. Lock file check (agent 2 dafa na chale - L11)
  2. Google Sheet parho + structure verify karo (L14)
  3. Pinterest token ki sehat check karo (L13, auto-refresh hota hai)
  4. Jo posts "pending" hain aur time aa gaya - validate karke post karo
  5. Fail ho to 3x retry (L8), purani (24h+) posts expire karo (L20)
  6. Sheet me Status/Posted_At/Post_URL/Error + Reports tab me daily summary
  7. Kuch fail ho to email alert (agar setup hai)
Safety: TEST_MODE, daily limits (Sheet ke record se ginti), posts ke beech gap,
        crash-protection ("working" status - L4), hashtag repeat warning (L19)
"""
import os
import time
from datetime import datetime, timedelta
import pytz

import config
import google_sheet
import validator
import pinterest_poster
import facebook_poster
import instagram_poster
import notifier

# Har platform ka poster module (naya platform add karna ho to yahan add karo)
POSTERS = {
    "Pinterest": pinterest_poster,
    "Facebook": facebook_poster,
    "Instagram": instagram_poster,
}


def now_pkt():
    """Abhi ka waqt Pakistan time me."""
    return datetime.now(pytz.timezone(config.TIMEZONE))


# Sheet me date/time kai shakalon me aa sakte hain (Google ka format,
# calendar picker, ya haath se likha) - hum sab samajh lete hain (L6)
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]
TIME_FORMATS = ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"]


def parse_schedule(post):
    """
    Post ki Date+Time ko parh kar datetime banao (PKT me).
    Kai formats samajhta hai taake Sheet ka format badle to bhi kaam chale.
    Return: (datetime ya None, error_message)
    """
    date_str = str(post.get("Date", "")).strip()
    time_str = str(post.get("Time", "")).strip()
    if not date_str or not time_str:
        return None, "Date ya Time khali hai"

    # Kabhi Google "2026-07-15 00:00:00" bhej deta hai - date wala hissa lo
    date_str = date_str.split(" ")[0]

    the_date = None
    for fmt in DATE_FORMATS:
        try:
            the_date = datetime.strptime(date_str, fmt).date()
            break
        except ValueError:
            continue
    if the_date is None:
        return None, f"Date ka format samajh nahi aya: '{date_str}' (chahiye: 2026-07-15)"

    the_time = None
    for fmt in TIME_FORMATS:
        try:
            the_time = datetime.strptime(time_str, fmt).time()
            break
        except ValueError:
            continue
    if the_time is None:
        return None, f"Time ka format samajh nahi aya: '{time_str}' (chahiye: 14:30)"

    scheduled = datetime.combine(the_date, the_time)
    return pytz.timezone(config.TIMEZONE).localize(scheduled), ""


def acquire_lock():
    """
    Double-instance protection (L11): agar agent pehle se chal raha hai to band ho jao.
    30 minute purana lock stale maana jata hai (crash ke baad khud theek).
    """
    os.makedirs(os.path.dirname(config.LOCK_FILE), exist_ok=True)
    if os.path.exists(config.LOCK_FILE):
        age_minutes = (time.time() - os.path.getmtime(config.LOCK_FILE)) / 60
        if age_minutes < 30:
            print("[X] Agent pehle se chal raha hai (lock file mili). Yeh copy band ho rahi hai.")
            print("    (Agar pakka koi aur copy NAHI chal rahi to data/agent.lock delete kar do.)")
            return False
    with open(config.LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    try:
        os.remove(config.LOCK_FILE)
    except OSError:
        pass


def check_hashtag_repeat(post, posts):
    """
    L19: pichli posts me bilkul wahi hashtags to nahi? (shadowban se bachao)
    Return: warning message ya khali string.
    """
    tags = str(post.get("Hashtags", "")).strip().lower()
    if not tags:
        return ""
    platform = str(post.get("Platform", "")).strip()
    recent = [
        p for p in posts
        if str(p.get("Platform", "")).strip() == platform
        and str(p.get("Status", "")).strip().lower() == "posted"
    ][-config.HASHTAG_REPEAT_CHECK:]
    same = sum(1 for p in recent if str(p.get("Hashtags", "")).strip().lower() == tags)
    if same >= config.HASHTAG_REPEAT_CHECK:
        return (f"Pichli {same} posts pe bhi BILKUL yehi hashtags the - "
                "thoda badlo warna shadowban ka risk hai")
    return ""


def do_post(post):
    """Platform ke hisab se post karo. Return: (success, msg, post_url)"""
    platform = str(post.get("Platform", "")).strip()
    poster = POSTERS.get(platform)
    if not poster:
        return False, f"'{platform}' support nahi (sirf: {', '.join(POSTERS)})", ""
    return poster.post(
        title=post.get("Title", ""),
        content=post.get("Content", ""),
        hashtags=post.get("Hashtags", ""),
        link=post.get("Post_Link", ""),
        image_link=post.get("Image_Link", ""),
        board=post.get("Board", ""),
    )


def post_with_retry(post):
    """
    Post karo - fail ho to 3x tak koshish (L8).
    Sirf 'temporary' lagne wale masail pe retry - ghalat content pe nahi.
    Return: (success, msg, post_url)
    """
    last_msg = ""
    for attempt in range(1, config.RETRY_COUNT + 1):
        success, msg, post_url = do_post(post)
        if success:
            return True, msg, post_url
        last_msg = msg

        # Yeh masail retry se theek NAHI honge - foran chhod do (waqt zaya na ho).
        # "PERMANENT" tag poster lagata hai jab platform khud kahe ke ghalti hamari hai (4xx).
        permanent = ("PERMANENT", "image ke bina", "abhi support nahi", "Board",
                     "nahi mila", "token", "BOARD_ID")
        if any(w.lower() in msg.lower() for w in permanent):
            return False, msg, ""

        if attempt < config.RETRY_COUNT:
            print(f"    [!] Koshish {attempt}/{config.RETRY_COUNT} fail: {msg[:70]}")
            print(f"        {config.RETRY_GAP_MINUTES} min baad dubara try karunga...")
            if not config.TEST_MODE:
                time.sleep(config.RETRY_GAP_MINUTES * 60)
    return False, f"{config.RETRY_COUNT} koshishon ke baad bhi fail: {last_msg}", ""


def process_post(post, now, posts):
    """
    Ek pending post ko handle karo.
    Return: (result, error_msg) - result: posted/skipped/failed/expired/invalid
    """
    row = post["_row_number"]
    platform = str(post.get("Platform", "")).strip()

    # --- Time check ---
    scheduled, err = parse_schedule(post)
    if err:
        print(f"[!] Row {row}: {err} -> invalid")
        google_sheet.update_status(row, "invalid", error=err)
        return "invalid", err

    if now < scheduled:
        return "skipped", ""  # abhi time nahi hua - kuch nahi karna

    # --- Kitni late hai? (L1 + L20) ---
    late = now - scheduled
    if late > timedelta(hours=config.EXPIRE_HOURS):
        msg = f"{config.EXPIRE_HOURS}h+ purani thi - auto-post nahi hogi. Nai date do."
        print(f"[!] Row {row}: {msg}")
        google_sheet.update_status(row, "expired", error=msg)
        return "expired", msg

    late_policy = str(post.get("Late_Policy", "")).strip().lower() or "post-anyway"
    if late > timedelta(minutes=config.LATE_GRACE_MINUTES) and late_policy == "skip":
        msg = f"Time nikal gaya tha ({int(late.total_seconds()//60)} min late) aur policy 'skip' hai"
        print(f"[!] Row {row}: {msg} -> expired")
        google_sheet.update_status(row, "expired", error=msg)
        return "expired", msg

    # --- Content validation (Layer 2) ---
    problems = validator.validate_post(post)
    if problems:
        msg = " | ".join(problems)
        print(f"[!] Row {row}: validation fail -> {msg}")
        google_sheet.update_status(row, "invalid", error=msg)
        return "invalid", msg

    # --- Hashtag repeat warning (L19) - post rokti nahi, sirf batati hai ---
    warn = check_hashtag_repeat(post, posts)
    if warn:
        print(f"[!] Row {row}: WARNING - {warn}")

    # --- Crash protection (L4): pehle "working" likho, phir post karo ---
    if not config.TEST_MODE:
        google_sheet.update_status(row, "working")

    # --- Post karo (retry ke saath) ---
    print(f"\n[>] Row {row}: {platform} pe post kar raha hoon...")
    success, msg, post_url = post_with_retry(post)

    # --- Result Sheet me likho ---
    if success:
        if config.TEST_MODE:
            # dry-run me status pending hi rehne do taake asli run me post ho sake
            print(f"    [OK] {msg}")
            return "posted", ""
        google_sheet.update_status(
            row, "posted", posted_at=f"{now_pkt():%Y-%m-%d %H:%M}", post_url=post_url
        )
        print(f"    [OK] {msg}")
        return "posted", ""
    else:
        google_sheet.update_status(row, "failed", error=msg)
        print(f"    [FAIL] {msg}")
        return "failed", msg


def run():
    """Ek dafa saari due posts handle karo. Return: summary dict."""
    print("=" * 55)
    print(f"  Social Agent - {now_pkt():%Y-%m-%d %H:%M} PKT")
    print(f"  TEST MODE: {'ON (dry-run, asli post nahi)' if config.TEST_MODE else 'OFF (ASLI POSTING)'}")
    if config.PINTEREST_SANDBOX:
        print("  PINTEREST: SANDBOX (nakli duniya - asli pin NAHI banegi)")
    print("=" * 55)

    summary = {"posted": 0, "failed": 0, "invalid": 0, "expired": 0}

    # Setup check
    problems = config.check_setup()
    if problems:
        print("\n[X] Setup adhura hai:")
        for p in problems:
            print("   -", p)
        print("\nPehle in cheezon ko theek karo (.env aur credentials).")
        return summary

    # Double-instance check (L11)
    if not acquire_lock():
        return summary

    try:
        # Sheet structure verify (L14)
        structure_problems = google_sheet.verify_structure()
        if structure_problems:
            print("\n[X] SHEET KA MASLA - agent ruk gaya (hifazat ke liye):")
            for p in structure_problems:
                print("   -", p)
            notifier.alert_agent_problem(" | ".join(structure_problems), f"{now_pkt():%H:%M}")
            return summary

        # Sheet ko aasan rakho: Image_Link ka dropdown + Preview images
        # (formula mit jaye ya nayi image aaye to khud theek ho jata hai)
        try:
            import drive_gallery
            drive_gallery.sync_sheet(quiet=True)
        except Exception as e:
            print(f"[!] Sheet sync skip (posting phir bhi chalegi): {str(e)[:80]}")

        posts = google_sheet.get_all_posts()
        now = now_pkt()
        today_str = f"{now:%Y-%m-%d}"

        # Har platform ka token health check (L13). Sirf un platforms ka jinki
        # is Sheet me pending post hai - taake FB/IG setup na ho to bhi Pinterest chale.
        pending_platforms = {
            str(p.get("Platform", "")).strip()
            for p in posts
            if str(p.get("Status", "")).strip().lower() == "pending"
        }
        token_ok = {}  # platform -> bool
        for platform, poster in POSTERS.items():
            if platform not in pending_platforms:
                continue
            ok, msg = poster.check_token()
            token_ok[platform] = ok
            if not ok:
                print(f"\n[X] {platform}: {msg}")
                print(f"    (Sirf {platform} posts nahi hongi - theek karke dubara chalao)")
                notifier.alert_agent_problem(f"{platform}: {msg}", f"{now_pkt():%H:%M}")

        # Crash ke baad "working" me atki rows? (L4) - user ko batao
        for p in posts:
            if str(p.get("Status", "")).strip().lower() == "working":
                print(f"[!] Row {p['_row_number']}: pichli dafa 'working' me atki thi - "
                      f"KHUD CHECK karo post hui thi ya nahi, phir Status ko pending/posted karo. "
                      f"(Dubara auto-post NAHI karunga - duplicate se bachne ke liye)")

        # Daily counts Sheet ke record se (restart-proof)
        posted_this_run = 0
        failures = []
        daily_count = {
            pf: google_sheet.count_posted_today(posts, pf, today_str)
            for pf in config.DAILY_LIMITS
        }

        for post in posts:
            status = str(post.get("Status", "")).strip().lower()
            platform = str(post.get("Platform", "")).strip()
            row = post["_row_number"]

            # Sirf "pending" posts karni hain
            if status != "pending":
                continue

            # Is platform ka token kharab hai to skip (baaki platforms chalte rahenge)
            if not token_ok.get(platform, False):
                continue

            # Daily limit check (hard-coded - ban protection)
            limit = config.DAILY_LIMITS.get(platform, 2)
            if daily_count.get(platform, 0) >= limit:
                print(f"[!] Row {row}: {platform} ki aaj ki limit ({limit}/din) puri - kal hogi")
                continue

            # Posts ke beech gap (pehli post ke ilawa)
            if posted_this_run > 0 and not config.TEST_MODE:
                print(f"    ({config.MIN_GAP_MINUTES} min ka gap - spam se bachne ke liye...)")
                time.sleep(config.MIN_GAP_MINUTES * 60)

            result, err_msg = process_post(post, now, posts)
            if result == "posted":
                daily_count[platform] = daily_count.get(platform, 0) + 1
                posted_this_run += 1
                summary["posted"] += 1
            elif result in summary:
                summary[result] += 1
                if result == "failed":
                    failures.append((row, platform, err_msg))

        # --- Daily report (Reports tab) ---
        total = summary["posted"] + summary["failed"] + summary["invalid"] + summary["expired"]
        if total > 0 and not config.TEST_MODE:
            details = f"Posted: {summary['posted']}, Failed: {summary['failed']}, " \
                      f"Invalid: {summary['invalid']}, Expired: {summary['expired']}"
            ok, rep_err = google_sheet.write_daily_report(
                today_str, total, summary["posted"], summary["failed"],
                details, f"{now_pkt():%H:%M}",
            )
            if not ok:
                print(f"[!] {rep_err}")

        # --- Email alert (sirf masla ho tab) ---
        if failures and not config.TEST_MODE:
            sent, note = notifier.alert_failures(failures, f"{now_pkt():%H:%M}")
            print(f"[i] Email alert: {note}")

        print(f"\n[*] Ho gaya. Is run me {posted_this_run} post(s). "
              f"(failed: {summary['failed']}, invalid: {summary['invalid']}, "
              f"expired: {summary['expired']})\n")
        return summary
    finally:
        release_lock()


if __name__ == "__main__":
    run()
