"""
scheduler.py - Agent ko HAMESHA chalane ke liye. Yeh chalao:  python src/scheduler.py

Kya karta hai:
  - Har 5 minute baad Sheet check karta hai (config me badal sakte ho)
  - Jo post due ho, kar deta hai
  - Ctrl+C dabao to band ho jata hai

Catch-up (L1): laptop band tha? On hote hi yeh chala do - jo posts reh gayi thin
wo (Late_Policy ke mutabiq) ho jayengi. 24h+ purani apne aap expire ho jati hain.

Windows me khud-b-khud chalane ke liye: run_agent.bat + Task Scheduler
(README me tareeqa likha hai)
"""
import os
import sys
import time
from datetime import datetime
import pytz

import config
import main as agent


class _Tee:
    """Output ko console (agar ho) AUR logs/agent.log dono me likho."""
    def __init__(self, logfile, console):
        self.logfile = logfile
        self.console = console

    def write(self, text):
        try:
            self.logfile.write(text)
            self.logfile.flush()
        except Exception:
            pass
        if self.console:
            try:
                self.console.write(text)
            except Exception:
                pass

    def flush(self):
        try:
            self.logfile.flush()
        except Exception:
            pass


def _setup_logging():
    """Sab output logs/agent.log me jaye (background me console nahi hota)."""
    log_path = config._path("logs/agent.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logfile = open(log_path, "a", encoding="utf-8", buffering=1)
    tee = _Tee(logfile, sys.__stdout__)
    sys.stdout = tee
    sys.stderr = tee


SCHED_LOCK = config._path("data/scheduler.lock")


def acquire_scheduler_lock():
    """
    Sirf EK scheduler chale (do dafa login pe bhi). Running scheduler har loop me
    is file ko chhoo leta hai; 15 min tak taza = koi aur chal raha hai -> exit.
    """
    os.makedirs(os.path.dirname(SCHED_LOCK), exist_ok=True)
    if os.path.exists(SCHED_LOCK):
        age_min = (time.time() - os.path.getmtime(SCHED_LOCK)) / 60
        if age_min < 15:
            print(f"[X] Scheduler pehle se chal raha hai ({now_pkt():%H:%M}). Yeh copy band.")
            return False
    _touch_scheduler_lock()
    return True


def _touch_scheduler_lock():
    with open(SCHED_LOCK, "w") as f:
        f.write(str(os.getpid()))


def release_scheduler_lock():
    try:
        os.remove(SCHED_LOCK)
    except OSError:
        pass


def now_pkt():
    return datetime.now(pytz.timezone(config.TIMEZONE))


def run_forever():
    print("*" * 60)
    print("  SOCIAL AGENT SCHEDULER")
    print(f"  Har {config.CHECK_INTERVAL_MINUTES} minute baad Sheet check hogi")
    print(f"  TEST MODE: {'ON (dry-run)' if config.TEST_MODE else 'OFF (ASLI POSTING)'}")
    print("  Band karne ke liye: Ctrl+C")
    print("*" * 60)
    print()

    runs = 0
    while True:
        try:
            runs += 1
            _touch_scheduler_lock()  # "main zinda hoon" - dusra scheduler na chale
            agent.run()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Ek run fail ho to scheduler band nahi hona chahiye
            print(f"\n[X] Is run me masla aya (agent chalta rahega): {e}\n")
            agent.release_lock()

        next_check = config.CHECK_INTERVAL_MINUTES
        print(f"[z] Soo raha hoon {next_check} min... "
              f"(ab tak {runs} run | {now_pkt():%H:%M} PKT | Ctrl+C = band)")
        try:
            time.sleep(next_check * 60)
        except KeyboardInterrupt:
            raise


if __name__ == "__main__":
    _setup_logging()
    if not acquire_scheduler_lock():
        sys.exit(0)
    try:
        run_forever()
    except KeyboardInterrupt:
        print("\n\n[*] Scheduler band ho gaya. Khuda hafiz!\n")
    finally:
        agent.release_lock()
        release_scheduler_lock()
