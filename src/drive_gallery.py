"""
drive_gallery.py - Drive folder ki saari images ko Sheet ki "Gallery" tab me
preview + ready link ke saath daal deta hai.
Chalao:  python src/drive_gallery.py

Kaam ka kab: jab Drive folder me nayi images upload karo - yeh chala do,
Gallery tab refresh ho jayegi. Phir jo image chahiye uska link copy karke
post row ke Image_Link me daal do.

Zaroori: .env me DRIVE_FOLDER_ID + folder service account se shared ho.
"""
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]
GALLERY_TAB = "Gallery"


def list_images():
    """Folder ki saari images lo (naam + id). Naye pehle."""
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    session = AuthorizedSession(creds)
    images, token = [], None
    while True:
        params = {
            "q": f"'{config.DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed=false",
            "fields": "files(id,name),nextPageToken",
            "pageSize": 100,
            "orderBy": "createdTime desc",
        }
        if token:
            params["pageToken"] = token
        r = session.get("https://www.googleapis.com/drive/v3/files", params=params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Drive error {r.status_code}: {r.text[:200]}")
        data = r.json()
        images += data.get("files", [])
        token = data.get("nextPageToken")
        if not token:
            break
    return images


def main():
    if not config.DRIVE_FOLDER_ID:
        print("[X] .env me DRIVE_FOLDER_ID nahi hai.")
        return

    print("Drive folder se images laa raha hoon...")
    images = list_images()
    print(f"[OK] {len(images)} images mili")

    creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    ss = gspread.authorize(creds).open_by_key(config.GOOGLE_SHEET_ID)

    # Gallery tab lo ya banao
    try:
        ws = ss.worksheet(GALLERY_TAB)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=GALLERY_TAB, rows=500, cols=3)

    # Header + rows (Preview formula + naam + copy-link)
    rows = [["Preview", "Image Name", "Link (ye copy karke Image_Link me daalo)"]]
    for img in images:
        url = f"https://lh3.googleusercontent.com/d/{img['id']}"
        preview = f'=IMAGE("{url}")'
        rows.append([preview, img["name"], url])

    ws.update(values=rows, range_name=f"A1:C{len(rows)}", value_input_option="USER_ENTERED")

    # Thodi formatting: header bold, preview column wide + rows tall
    sid = ws.id
    ss.batch_update({"requests": [
        {"repeatCell": {
            "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True},
                     "backgroundColor": {"red": 0.85, "green": 0.91, "blue": 0.99}}},
            "fields": "userEnteredFormat(textFormat,backgroundColor)"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 120}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3},
            "properties": {"pixelSize": 380}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {
            "range": {"sheetId": sid, "dimension": "ROWS", "startIndex": 1, "endIndex": len(rows)},
            "properties": {"pixelSize": 90}, "fields": "pixelSize"}},
    ]})

    print(f"\n[OK] 'Gallery' tab tayyar - {len(images)} images preview + link ke saath.")
    print("     Sheet me 'Gallery' tab kholo, jo image chahiye uska Link copy karke")
    print("     post row ke Image_Link me daal do.")
    if not images:
        print("\n[!] Folder abhi khali hai - pehle Drive folder me images upload karo,")
        print("    phir yeh dubara chalao.")


if __name__ == "__main__":
    main()
