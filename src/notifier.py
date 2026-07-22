"""
notifier.py - Email alerts (Phase 2).

Rule: sab theek chale to KOI email nahi (spam nahi karte).
Email sirf tab jab kuch ghalat ho - post fail, token dead, agent ruka.

Setup: Gmail "App Password" chahiye (.env me EMAIL_APP_PASSWORD).
Nahi hai to email chup-chaap band rehti hai - baaki sab kaam chalta rahega.
"""
import smtplib
from email.message import EmailMessage
import config


def is_enabled():
    return bool(config.EMAIL_APP_PASSWORD)


def send_alert(subject, body):
    """
    Alert email bhejo.
    Return: (sent: bool, message: str)
    """
    if not is_enabled():
        return False, "Email band hai (.env me EMAIL_APP_PASSWORD nahi hai)"

    msg = EmailMessage()
    msg["Subject"] = f"[Social Agent] {subject}"
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = config.ALERT_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(config.EMAIL_SENDER, config.EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return True, "Email bhej di"
    except Exception as e:
        return False, f"Email nahi gayi: {e}"


def alert_failures(failures, run_time):
    """
    Fail hui posts ka alert. failures = list of (row, platform, error)
    """
    if not failures:
        return False, "Koi fail nahi - email ki zaroorat nahi"

    lines = [
        f"Agent chala: {run_time} PKT",
        f"{len(failures)} post(s) FAIL huin:",
        "",
    ]
    for row, platform, error in failures:
        lines.append(f"  Row {row} ({platform}): {error}")
    lines += [
        "",
        "Sheet me jaake dekho - Error column me poori wajah likhi hai.",
        "Theek karke Status ko 'pending' kar do, agent dubara koshish karega.",
    ]
    return send_alert(f"{len(failures)} post fail huin", "\n".join(lines))


def alert_agent_problem(problem, run_time):
    """Agent hi ruk gaya (token dead / Sheet ka masla) - yeh serious hai."""
    body = (
        f"Agent chala: {run_time} PKT\n\n"
        f"MASLA: {problem}\n\n"
        "Jab tak yeh theek nahi hota, posts NAHI hongi.\n"
    )
    return send_alert("Agent ruk gaya - dhyan do", body)
