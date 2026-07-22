"""
facebook_setup.py - Facebook/Instagram ki saari IDs aur token khud nikalta hai.
Chalao:  python src/facebook_setup.py

Kya karta hai:
  1. Short token (Graph API Explorer wala) ko LONG-LIVED banata hai (~60 din / Page token kabhi expire nahi)
  2. Tumhari saari Pages dhoondta hai (naam + ID + Page token)
  3. Har Page ka linked Instagram Business account dhoondta hai
  4. Sab kuch .env me khud daal deta hai (FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)

Zaroori: .env me pehle yeh hon - FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FB_SHORT_TOKEN
"""
import os
import re
import requests
import config

GRAPH = "https://graph.facebook.com/v21.0"


def _update_env(updates):
    """`.env` file me kuch keys update/add karo (baaqi cheezein waise hi rehti hain)."""
    env_path = config._path(".env")
    with open(env_path, encoding="utf-8") as f:
        lines = f.readlines()
    keys_done = set()
    for i, line in enumerate(lines):
        m = re.match(r"^(\w+)=", line)
        if m and m.group(1) in updates:
            lines[i] = f"{m.group(1)}={updates[m.group(1)]}\n"
            keys_done.add(m.group(1))
    for k, v in updates.items():
        if k not in keys_done:
            lines.append(f"{k}={v}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    if not (config.FACEBOOK_APP_ID and config.FACEBOOK_APP_SECRET and config.FB_SHORT_TOKEN):
        print("[X] .env me FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FB_SHORT_TOKEN teeno chahiye.")
        return

    # --- Step 1: short token -> long-lived user token ---
    print("Step 1: Token ko long-lived bana raha hoon...")
    r = requests.get(f"{GRAPH}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": config.FACEBOOK_APP_ID,
        "client_secret": config.FACEBOOK_APP_SECRET,
        "fb_exchange_token": config.FB_SHORT_TOKEN,
    }, timeout=30)
    if r.status_code != 200:
        print("[X] Token exchange fail:", r.text[:300])
        print("\n    Shayad token EXPIRE ho gaya (Graph Explorer token 1-2 ghante chalta hai).")
        print("    Naya token le lo: Graph API Explorer > Generate Access Token,")
        print("    phir .env ke FB_SHORT_TOKEN me daal ke yeh script dubara chalao.")
        return
    long_token = r.json()["access_token"]
    print("[OK] Long-lived user token mil gaya\n")

    # --- Step 2: kaun ho tum? ---
    me = requests.get(f"{GRAPH}/me", params={
        "fields": "id,name", "access_token": long_token}, timeout=30).json()
    print(f"Logged in as: {me.get('name')} (id: {me.get('id')})\n")

    # --- Step 3: Pages nikalo ---
    print("Step 2: Tumhari Facebook Pages dhoondh raha hoon...")
    r = requests.get(f"{GRAPH}/me/accounts", params={
        "fields": "name,id,access_token,instagram_business_account{id,username}",
        "access_token": long_token,
    }, timeout=30)
    pages = r.json().get("data", [])

    if not pages:
        print("\n[X] Koi Facebook Page nahi mili is account pe!")
        print("    Wajah aam tor pe: Graph Explorer me token banate waqt Page ki")
        print("    permission (pages_show_list) nahi di thi, ya tum us Page ke admin nahi.")
        print("    Screenshot bhej do - main exact bata dunga.")
        return

    print(f"[OK] {len(pages)} Page(s) mili:\n")
    print("=" * 62)
    ig_found = None
    chosen = pages[0]
    for i, pg in enumerate(pages):
        ig = pg.get("instagram_business_account")
        print(f"  [{i}] Page: {pg.get('name')}")
        print(f"      Page ID: {pg.get('id')}")
        if ig:
            print(f"      Instagram: @{ig.get('username')} (id: {ig.get('id')})  <-- LINKED!")
            if ig_found is None:
                ig_found = ig
                chosen = pg
        else:
            print("      Instagram: LINKED NAHI")
        print()
    print("=" * 62)

    # --- Step 4: .env me daalo ---
    updates = {
        "FACEBOOK_PAGE_ID": chosen.get("id"),
        "FACEBOOK_ACCESS_TOKEN": chosen.get("access_token"),  # yeh PAGE token hai (long-lived)
    }
    if ig_found:
        updates["INSTAGRAM_ACCOUNT_ID"] = ig_found.get("id")

    _update_env(updates)
    print("\n[OK] .env update ho gaya:")
    print(f"     FACEBOOK_PAGE_ID     = {chosen.get('id')}  ({chosen.get('name')})")
    print("     FACEBOOK_ACCESS_TOKEN = (Page token - long-lived, safe)")
    if ig_found:
        print(f"     INSTAGRAM_ACCOUNT_ID = {ig_found.get('id')}  (@{ig_found.get('username')})")
        print("\n[OK] SAB READY! Facebook aur Instagram dono connect ho gaye.")
    else:
        print("     INSTAGRAM_ACCOUNT_ID = (abhi nahi - IG Page se linked nahi)")
        print("\n[!] FACEBOOK ready hai, lekin INSTAGRAM abhi link nahi.")
        print("    Instagram ko is Page se link karo (Meta Business Suite),")
        print("    phir yeh script dubara chalao - IG ID khud aa jayega.")


if __name__ == "__main__":
    main()
