"""
validator.py - Har post ko bhejne se PEHLE jaanchna (Layer 2 protection).
Ghalat post KABHI nahi jayegi - yahin ruk jayegi aur Sheet me wajah likhi jayegi.

Checks: platform sahi? content hai? limits ke andar? hashtags zyada to nahi?
"""
import config


def validate_post(post):
    """
    Ek post (dict) ko jaancho.
    Return: list of problems (khali list = sab theek).
    """
    problems = []

    platform = str(post.get("Platform", "")).strip()
    content = str(post.get("Content", "")).strip()
    title = str(post.get("Title", "")).strip()
    hashtags = str(post.get("Hashtags", "")).strip()
    image_link = str(post.get("Image_Link", "")).strip()
    late_policy = str(post.get("Late_Policy", "")).strip().lower()

    # Platform sahi likha hai? (typo pakadna - L6)
    if platform not in config.VALID_PLATFORMS:
        problems.append(
            f"Platform '{platform}' ghalat hai - sirf yeh chalenge: "
            + ", ".join(config.VALID_PLATFORMS)
        )
        return problems  # platform hi ghalat to aage check bekaar

    # Content zaroori hai
    if not content:
        problems.append("Content khali hai - kuch to likho")

    # Character limits (L15)
    limits = config.CHAR_LIMITS.get(platform, {})
    full_text_len = len(content) + len(hashtags) + 2
    if "content" in limits and full_text_len > limits["content"]:
        problems.append(
            f"{platform} pe max {limits['content']} characters chalte hain, "
            f"tumhara (content+hashtags) {full_text_len} hai - chhota karo"
        )
    if "title" in limits and len(title) > limits["title"]:
        problems.append(
            f"{platform} pe title max {limits['title']} characters - tumhara {len(title)} hai"
        )

    # Hashtags ki ginti (L15/L19)
    tag_count = len([t for t in hashtags.split() if t.startswith("#")])
    max_tags = limits.get("max_hashtags", 30)
    if tag_count > max_tags:
        problems.append(f"{platform} pe max {max_tags} hashtags - tumhare {tag_count} hain")

    # Late_Policy sahi hai?
    if late_policy and late_policy not in ("post-anyway", "skip"):
        problems.append("Late_Policy sirf 'post-anyway' ya 'skip' ho sakti hai")

    # Pinterest pe image lazmi hoti hai
    if platform == "Pinterest" and not image_link:
        problems.append("Pinterest pe image ke bina pin nahi banti - Image_Link do")

    # Pinterest pe board chahiye (Sheet me ya .env me default)
    if platform == "Pinterest":
        board = str(post.get("Board", "")).strip()
        if not board and not config.PINTEREST_BOARD_ID:
            problems.append("Board khali hai - Sheet ke Board column me board ka naam likho")

    return problems
