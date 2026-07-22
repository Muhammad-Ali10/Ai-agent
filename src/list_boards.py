"""
list_boards.py - Tumhare saare Pinterest boards ki list dikhata hai.
Chalao:  python src/list_boards.py

Kaam ka kab: Sheet me Board column ka dropdown banana ho, ya dekhna ho
ke agent ko kaunse boards nazar aa rahe hain.

(Yeh dubara login nahi maangta - saved token use karta hai.)
"""
import pinterest_poster


def main():
    boards, err = pinterest_poster.list_boards()
    if err:
        print("[X]", err)
        return

    if not boards:
        print("Koi board nahi mila! Pinterest pe pehle ek board banao.")
        return

    print("=" * 70)
    print(f"  TUMHARE {len(boards)} BOARDS")
    print("=" * 70)
    for b in boards:
        print(f"  {b['name']:45s}  ID: {b['id']}")
    print("=" * 70)
    print("\nSheet ke 'Board' column me bas NAAM likhna hai (ID nahi).")
    print("Dropdown banane ke liye yeh list copy kar sakte ho:\n")
    print(",".join(b["name"] for b in boards))
    print()


if __name__ == "__main__":
    main()
