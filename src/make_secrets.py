"""
make_secrets.py - GitHub Actions ke liye 2 secrets tayyar karta hai.
Chalao:  python src/make_secrets.py

Kya karta hai:
  - .env aur Google key file ko base64 me badal ke 2 files me likhta hai
  - Tum in files ko khol ke content copy karke GitHub Secrets me paste karoge

2 Secrets banane hain GitHub me:
  1. ENV_FILE_B64   <- credentials/_gh_ENV_FILE_B64.txt ka content
  2. GOOGLE_KEY_B64 <- credentials/_gh_GOOGLE_KEY_B64.txt ka content

(Yeh .txt files credentials/ me banti hain jo git-ignored hai - GitHub pe nahi jayengi.)
"""
import base64
import os
import config


def _b64_of_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    env_path = config._path(".env")
    key_path = config.GOOGLE_CREDENTIALS_FILE
    out_dir = config._path("credentials")

    problems = []
    if not os.path.exists(env_path):
        problems.append(f".env nahi mili: {env_path}")
    if not os.path.exists(key_path):
        problems.append(f"Google key nahi mili: {key_path}")
    if problems:
        for p in problems:
            print("[X]", p)
        return

    env_b64 = _b64_of_file(env_path)
    key_b64 = _b64_of_file(key_path)

    f1 = os.path.join(out_dir, "_gh_ENV_FILE_B64.txt")
    f2 = os.path.join(out_dir, "_gh_GOOGLE_KEY_B64.txt")
    with open(f1, "w") as f:
        f.write(env_b64)
    with open(f2, "w") as f:
        f.write(key_b64)

    print("=" * 62)
    print("  GitHub SECRETS TAYYAR - 2 files ban gayi credentials/ me:")
    print("=" * 62)
    print(f"\n  Secret 1 ka naam:  ENV_FILE_B64")
    print(f"     Content yahan se copy karo:  {f1}")
    print(f"     (length: {len(env_b64)} characters)")
    print(f"\n  Secret 2 ka naam:  GOOGLE_KEY_B64")
    print(f"     Content yahan se copy karo:  {f2}")
    print(f"     (length: {len(key_b64)} characters)")
    print("\n" + "=" * 62)
    print("  GitHub me kaise daalo:")
    print("  repo > Settings > Secrets and variables > Actions >")
    print("  'New repository secret' > naam + content paste > Add")
    print("  (dono secrets ke liye ek ek karke)")
    print("=" * 62)
    print("\n  [!] Secrets daalne ke baad yeh 2 .txt files DELETE kar dena")
    print("      (yeh git me nahi jatin, phir bhi safai achhi hai).")


if __name__ == "__main__":
    main()
