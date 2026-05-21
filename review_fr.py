"""FR translation review — config only. Logic lives in review_lang.py."""

from pathlib import Path
from nicegui import app
import review_lang

app.add_static_files('/assets', 'docs/assets')

# ── Config ────────────────────────────────────────────────────────────────────
LANGUAGE      = "fr"
VOLUNTEER_PW  = "merci"
APPROVE_PW    = "oscar2702"

review_lang.register(
    language      = LANGUAGE,
    volunteer_pw  = VOLUNTEER_PW,
    approve_pw    = APPROVE_PW,
    docs_src      = Path("docs/fr"),
    docs_en       = Path("docs/en"),
    reminder_text = "Ne modifiez pas les liens [...](…), les images ![...](…) ni le code `...`.",
)
