"""Email notifications for game events."""
import logging, os, smtplib, threading
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

_SMTP_HOST = os.environ.get("SMTP_HOST", "")
_SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
_SMTP_USER = os.environ.get("SMTP_USER", "")
_SMTP_PASS = os.environ.get("SMTP_PASS", "")
_FROM      = os.environ.get("SMTP_FROM", "")
_TO        = os.environ.get("SMTP_TO", "")

_SUBJECTS = {
    "started":  "SimFuture: Game {gid} started",
    "resumed":  "SimFuture: Game {gid} resumed",
    "finished": "SimFuture: Game {gid} finished",
}
_BODIES = {
    "started":  "Game {gid} started by {gm}.",
    "resumed":  "Game {gid} resumed by {gm}.",
    "finished": "Game {gid} finished (GM: {gm}).",
}


def _send(game_id: str, gm_name: str, event: str) -> None:
    try:
        body = _BODIES[event].format(gid=game_id, gm=gm_name)
        msg  = MIMEText(body)
        msg["Subject"] = _SUBJECTS[event].format(gid=game_id)
        msg["From"]    = _FROM
        msg["To"]      = _TO
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as s:
            s.starttls()
            s.login(_SMTP_USER, _SMTP_PASS)
            s.sendmail(_FROM, [_TO], msg.as_string())
    except Exception as e:
        logging.getLogger(__name__).warning("game alert email failed (%s %s): %s", event, game_id, e)


def game_alert(game_id: str, gm_name: str, event: str) -> None:
    """Fire-and-forget email alert. event = 'started' | 'resumed' | 'finished'."""
    threading.Thread(target=_send, args=(game_id, gm_name, event), daemon=True).start()
