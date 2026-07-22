"""
setup_sheet.py - Google Sheet ko "user-friendly" bana deta hai.
Chalao:  python src/setup_sheet.py

Kya karta hai (Layer 1 protection - typo ho hi na sake):
  1. Platform    -> dropdown (Pinterest / Facebook / Instagram)
  2. Account     -> dropdown (my_pinterest / my_facebook / my_instagram)
  3. Board       -> dropdown (tumhare SAARE boards - Pinterest se live aate hain)
  4. Date        -> date picker (calendar khulta hai)
  5. Time        -> dropdown (00:00 se 23:45 tak, 15-15 min ke gap se)
  6. Late_Policy -> dropdown (post-anyway / skip)
  7. Status      -> dropdown (pending / posted / failed / ...)
  8. Header bold + freeze, agent wale columns gray (haath mat lagao)

Board list badal jaye (naya board banao) to yeh script dubara chala lena.
"""
import gspread
from google.oauth2.service_account import Credentials
import config
import pinterest_poster

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

LAST_ROW = 1000  # itni rows tak dropdowns lagenge

# Agent ke columns - user ne inhe haath nahi lagana
AGENT_COLUMNS = ["Status", "Posted_At", "Post_URL", "Error"]


def _ws():
    creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(config.GOOGLE_SHEET_ID).sheet1


def _col_index(headers, name):
    """Column ka 0-based number (naam se)."""
    return headers.index(name)


def _dropdown_rule(values, strict=True):
    return {
        "condition": {
            "type": "ONE_OF_LIST",
            "values": [{"userEnteredValue": str(v)} for v in values],
        },
        "showCustomUi": True,  # yeh dropdown ka teer (arrow) dikhata hai
        "strict": strict,
    }


def _validation_request(sheet_id, col_idx, rule):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,  # header chhod do
                "endRowIndex": LAST_ROW,
                "startColumnIndex": col_idx,
                "endColumnIndex": col_idx + 1,
            },
            "rule": rule,
        }
    }


def _number_format_request(sheet_id, col_idx, fmt_type, pattern):
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": LAST_ROW,
                "startColumnIndex": col_idx,
                "endColumnIndex": col_idx + 1,
            },
            "cell": {"userEnteredFormat": {"numberFormat": {"type": fmt_type, "pattern": pattern}}},
            "fields": "userEnteredFormat.numberFormat",
        }
    }


def _time_options():
    """12-hour AM/PM format me, har 15 minute (jaise 9:00 AM, 2:30 PM)."""
    opts = []
    for h in range(24):
        ampm = "AM" if h < 12 else "PM"
        h12 = h % 12 or 12
        for m in (0, 15, 30, 45):
            opts.append(f"{h12}:{m:02d} {ampm}")
    return opts


# Status ke rang (color-coding - ek nazar me pata chale)
STATUS_COLORS = {
    "posted":  {"red": 0.72, "green": 0.88, "blue": 0.72},   # hara
    "failed":  {"red": 0.96, "green": 0.72, "blue": 0.72},   # laal
    "pending": {"red": 1.00, "green": 0.95, "blue": 0.70},   # peela
    "invalid": {"red": 0.99, "green": 0.85, "blue": 0.65},   # orange
    "expired": {"red": 0.85, "green": 0.85, "blue": 0.85},   # grey
    "working": {"red": 0.80, "green": 0.90, "blue": 0.99},   # halka neela
}


def _status_color_requests(sheet_id, col_idx):
    """Status column pe conditional formatting - har status ka apna rang."""
    reqs = []
    for status, color in STATUS_COLORS.items():
        reqs.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": LAST_ROW,
                        "startColumnIndex": col_idx, "endColumnIndex": col_idx + 1,
                    }],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ",
                                      "values": [{"userEnteredValue": status}]},
                        "format": {"backgroundColor": color},
                    },
                },
                "index": 0,
            }
        })
    return reqs


def _col_width_request(sheet_id, col_idx, pixels):
    return {
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": col_idx, "endIndex": col_idx + 1},
            "properties": {"pixelSize": pixels}, "fields": "pixelSize",
        }
    }


def main():
    print("Sheet se connect kar raha hoon...")
    ws = _ws()
    sheet_id = ws.id
    headers = [h.strip() for h in ws.row_values(1)]
    print(f"Sheet mil gayi. Columns: {len(headers)}")

    # --- Boards Pinterest se live lo ---
    print("\nTumhare boards Pinterest se laa raha hoon...")
    boards, err = pinterest_poster.list_boards()
    if err:
        print(f"[X] Boards nahi mile: {err}")
        print("    (Pehle 'python src/pinterest_auth.py' chala lo)")
        return
    board_names = [b["name"] for b in boards]
    print(f"[OK] {len(board_names)} boards mile")

    requests = []

    # 1. Platform dropdown
    requests.append(_validation_request(
        sheet_id, _col_index(headers, "Platform"),
        _dropdown_rule(config.VALID_PLATFORMS),
    ))

    # 2. Account dropdown
    requests.append(_validation_request(
        sheet_id, _col_index(headers, "Account"),
        _dropdown_rule(["my_pinterest", "my_facebook", "my_instagram"]),
    ))

    # 3. Board dropdown (saare boards)
    requests.append(_validation_request(
        sheet_id, _col_index(headers, "Board"),
        _dropdown_rule(board_names),
    ))

    # 4. Date -> calendar picker + format
    date_idx = _col_index(headers, "Date")
    requests.append(_number_format_request(sheet_id, date_idx, "DATE", "yyyy-mm-dd"))
    requests.append(_validation_request(
        sheet_id, date_idx,
        {"condition": {"type": "DATE_IS_VALID"}, "showCustomUi": True, "strict": False},
    ))

    # 5. Time -> AM/PM dropdown (strict=False taake koi khaas waqt likhna ho to likh sako)
    time_idx = _col_index(headers, "Time")
    requests.append(_number_format_request(sheet_id, time_idx, "TIME", "h:mm AM/PM"))
    requests.append(_validation_request(
        sheet_id, time_idx, _dropdown_rule(_time_options(), strict=False),
    ))

    # 6. Late_Policy dropdown
    requests.append(_validation_request(
        sheet_id, _col_index(headers, "Late_Policy"),
        _dropdown_rule(["post-anyway", "skip"]),
    ))

    # 7. Status dropdown
    requests.append(_validation_request(
        sheet_id, _col_index(headers, "Status"),
        _dropdown_rule(["pending", "posted", "failed", "invalid", "expired", "working"],
                       strict=False),
    ))

    # 8a. Header bold + background
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.85, "green": 0.91, "blue": 0.99},
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor)",
        }
    })

    # 8b. Header row freeze (scroll pe upar rahe)
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    })

    # 8c. Agent wale columns gray (user ne haath nahi lagana)
    for col in AGENT_COLUMNS:
        idx = _col_index(headers, col)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": LAST_ROW,
                    "startColumnIndex": idx, "endColumnIndex": idx + 1,
                },
                "cell": {"userEnteredFormat": {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}
                }},
                "fields": "userEnteredFormat.backgroundColor",
            }
        })

    # 9. Status column pe color-coding (posted=hara, failed=laal, ...)
    requests += _status_color_requests(sheet_id, _col_index(headers, "Status"))

    # 10. Column widths + row heights (Preview image dikhne ke liye)
    widths = {"Content": 220, "Image_Link": 160, "Post_Link": 130, "Error": 200}
    if "Preview" in headers:
        widths["Preview"] = 90
    for col, px in widths.items():
        requests.append(_col_width_request(sheet_id, _col_index(headers, col), px))
    # data rows ki height (image thodi dikhe)
    requests.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS",
                      "startIndex": 1, "endIndex": 120},
            "properties": {"pixelSize": 60}, "fields": "pixelSize",
        }
    })

    print("\nSheet me dropdowns aur formatting laga raha hoon...")
    ws.spreadsheet.batch_update({"requests": requests})

    print("\n" + "=" * 60)
    print("  [OK] SHEET TAYYAR HAI!")
    print("=" * 60)
    print("  Ab in columns me sirf SELECT karna hai (likhna nahi):")
    print(f"    - Platform    : {', '.join(config.VALID_PLATFORMS)}")
    print("    - Account     : my_pinterest / my_facebook / my_instagram")
    print(f"    - Board       : {len(board_names)} boards ka dropdown")
    print("    - Date        : calendar picker (cell pe double-click)")
    print("    - Time        : 00:00 - 23:45 (15 min ke gap se)")
    print("    - Late_Policy : post-anyway / skip")
    print("    - Status      : pending / posted / failed / ...")
    print()
    print("  Gray columns (Status ke baad wale) = AGENT khud bharega, haath mat lagao")
    print("=" * 60)
    print("\n  Naya board banao to yeh script dubara chala lena.\n")


if __name__ == "__main__":
    main()
