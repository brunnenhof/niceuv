"""
toy.py  –  Minimal NiceGUI state-management demo
=================================================

Teaches the token-in-URL + DB-session pattern.

Roles: GM | Poverty | Inequality | Empowerment | Food | Energy | Future

Flow
----
  /         →  type username
              known user  → redirect to /dashboard?token=...
              new user    → popup: choose role → /dashboard?token=...
  /dashboard →  db_get(token) → show identity + prefs + sign-out

Key lessons
-----------
  - app.storage.user  is shared across ALL tabs in the same browser
  - token in URL      is unique per tab (each tab has its own URL)
  - DB session        is the single source of truth after login
  - lang / dark saved to DB (post-login) or app.storage.user (pre-login)
  - After reconnect/crash, token in URL restores correct identity from DB
"""

import random
import secrets
import sqlite3
import string
import time
from contextlib import contextmanager
from pathlib import Path

from nicegui import app, run, ui

import database as maindb
import game_plot_ug
from files import luf_original

app.add_static_files('/static', 'static')

# ── Constants ─────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "sdg3_game.db"

ROLES = ["GM", "Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]

MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]

REGIONS = [
    "USA", "Africa South of Sahara", "China",
    "Middle East & North Africa", "South Asia", "Latin America",
    "Pacific Rim", "East Europe & Central Asia", "Europe", "Southeast Asia",
]
REGION_ABBR = ["us", "af", "cn", "me", "sa", "la", "pa", "ec", "eu", "se"]

LANG_OPTIONS = {"en": "🇬🇧 EN", "de": "🇩🇪 DE"}

app.colors(primary="#014873", secondary="#0383A1", my_orange="#FF8A05")

# ── DB ────────────────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    # Ensure all game tables exist first (policies, players, human_regions, etc.)
    maindb.init_database()

    with get_db() as conn:
        # Migrate: drop old sdg3 sessions schema if it lacks toy.py-specific columns
        existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()}
        if existing_cols and "game_token" not in existing_cols:
            conn.execute("DROP TABLE sessions")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token         TEXT PRIMARY KEY,
                username      TEXT UNIQUE,
                role          TEXT,
                lang          TEXT    DEFAULT 'en',
                dark          INTEGER DEFAULT 0,
                human_regions TEXT    DEFAULT '',
                setup_done    INTEGER DEFAULT 0,
                game_id       TEXT    DEFAULT '',
                game_token    TEXT    DEFAULT '',
                region        TEXT    DEFAULT '',
                current_round INTEGER DEFAULT 1,
                num_rounds    INTEGER DEFAULT 3,
                submitted     INTEGER DEFAULT 0,
                last_active   INTEGER DEFAULT 0
            )
        """)
        # Migrate: add last_active if missing (existing DB)
        existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(sessions)").fetchall()}
        if "last_active" not in existing_cols:
            conn.execute("ALTER TABLE sessions ADD COLUMN last_active INTEGER DEFAULT 0")
        # Deduplicate human_regions: keep the row with MAX(sub_1) per (game_id, region_tag)
        conn.execute("""
            DELETE FROM human_regions WHERE id NOT IN (
                SELECT MAX(id) FROM human_regions GROUP BY game_id, region_tag
            )
        """)
        conn.commit()


def db_create(token: str, username: str, role: str, lang: str = "en", dark: int = 0):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sessions (token, username, role, lang, dark) "
            "VALUES (?,?,?,?,?)",
            (token, username, role, lang, dark),
        )
        conn.commit()


def db_get(token: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        return dict(row) if row else None


def db_next_gm_username() -> str:
    """Return the first free gmN username: gm1, gm2, ..."""
    with get_db() as conn:
        existing = {r[0] for r in conn.execute(
            "SELECT username FROM sessions WHERE username LIKE 'gm%'"
        ).fetchall()}
    n = 1
    while f"gm{n}" in existing:
        n += 1
    return f"gm{n}"


def db_find_by_username(username: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None


def db_get_players(game_token: str, game_id: str = "") -> list[dict]:
    """All player sessions that joined this GM's game."""
    with get_db() as conn:
        if game_id:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE game_token = ? AND game_id = ?",
                (game_token, game_id),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE game_token = ?", (game_token,)
            ).fetchall()
        return [dict(r) for r in rows]


def db_generate_game_id() -> str:
    """Return a unique ABC-123 game ID."""
    while True:
        gid = (
            "".join(random.choices(string.ascii_uppercase, k=3))
            + "-"
            + "".join(random.choices(string.digits, k=3))
        )
        with get_db() as conn:
            exists = conn.execute(
                "SELECT 1 FROM sessions WHERE game_id = ?", (gid,)
            ).fetchone()
        if not exists:
            return gid


def db_find_by_game_id(game_id: str) -> dict | None:
    """Find the GM session for a given game ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE game_id = ? AND role = 'GM'", (game_id,)
        ).fetchone()
        return dict(row) if row else None


def db_update(token: str, **kwargs):
    """Generic column updater.  db_update(token, setup_done=1, human_regions='Food,Energy')"""
    if not kwargs:
        return
    fields = [f"{k} = ?" for k in kwargs]
    values = list(kwargs.values()) + [token]
    with get_db() as conn:
        conn.execute(f"UPDATE sessions SET {', '.join(fields)} WHERE token = ?", values)
        conn.commit()


def db_heartbeat(token: str):
    """Touch last_active so the session appears 'in use' in the resume dialog."""
    db_update(token, last_active=int(time.time()))


def db_update_prefs(token: str, lang: str = None, dark: int = None):
    fields, values = [], []
    if lang is not None:
        fields.append("lang = ?");  values.append(lang)
    if dark is not None:
        fields.append("dark = ?");  values.append(dark)
    if not fields:
        return
    values.append(token)
    with get_db() as conn:
        conn.execute(f"UPDATE sessions SET {', '.join(fields)} WHERE token = ?", values)
        conn.commit()


# ── Pre-login prefs (browser storage) ─────────────────────────────────────────

def get_lang() -> str:
    return app.storage.user.get("lang", "en")

def get_dark() -> bool:
    return bool(app.storage.user.get("dark", 0))

def set_lang(lang: str):
    app.storage.user["lang"] = lang

def set_dark(dark: bool):
    app.storage.user["dark"] = int(dark)


# ── Token ─────────────────────────────────────────────────────────────────────

def get_or_create_token() -> str:
    if "token" not in app.storage.user:
        app.storage.user["token"] = secrets.token_urlsafe(16)
    return app.storage.user["token"]


# ── Header ────────────────────────────────────────────────────────────────────

def create_header(token: str | None = None):
    """
    Call at the top of every page.

    token=None  → prefs saved to browser storage only  (public / login page)
    token=<str> → prefs saved to DB AND browser storage (protected pages)

    Lesson: the dark-mode object must be created at page scope so NiceGUI
    applies it when the page loads.  Buttons only toggle it afterwards.
    """
    # Determine current prefs (DB wins over browser storage on protected pages)
    if token:
        session = db_get(token)
        lang = session["lang"] if session else get_lang()
        dark = bool(session["dark"]) if session else get_dark()
    else:
        lang = get_lang()
        dark = get_dark()

    langx = 0 if lang == "en" else 1
    # Apply dark mode for this page load
    dark_mode = ui.dark_mode(value=dark)

    def _toggle_dark():
        new_val = not dark_mode.value
        dark_mode.set_value(new_val)
        set_dark(new_val)
        if token:
            db_update_prefs(token, dark=int(new_val))

    def _change_lang(new_lang: str):
        set_lang(new_lang)
        if token:
            db_update_prefs(token, lang=new_lang)
        ui.navigate.reload()

    # ui.colors(primary="#014873", secondary="#0383a1")

    with ui.header().classes("items-center justify-between px-4 py-2"):
        # Left: title
        with ui.link(target="/").classes("text-white no-underline"):
            with ui.column().classes('gap-0 text-white font-bold'):
                ui.label(luf_original.simfuture[langx]).classes('text-2xl')
                ui.label(luf_original.the_age_of_consequences[langx]).classes('font-italic text-sm')

        # Right: controls
        with ui.row().classes("items-center gap-2"):
            m_lang = LANG_OPTIONS[lang]
            langx = 0 if lang == "en" else 1
            if langx == 0:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/uk/topic/sinn-und-zweck'
            elif langx == 1 or langx == 2:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/de/topic/sinn-und-zweck'
            else:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/uk/topic/sinn-und-zweck'

            with ui.button(icon='blind',
                on_click=lambda: ui.navigate.to(help_link, new_tab=True)
                        ).props('flat round dense').classes('text-white font-bold'):
                ui.tooltip(luf_original.help_tip[langx]).classes('bg-green-300 text-black')

            with ui.button(icon='gavel',
                on_click=lambda: ui.navigate.to('/legal')
                        ).props('flat round dense').classes('text-white font-bold'):
                ui.tooltip(luf_original.legal[langx]).classes('bg-green-300 text-black')
                            
            with ui.button(
                on_click=lambda: ui.navigate.to('https://claude.ai/login', new_tab=True)
                        ).props('flat round dense icon=img:/static/claudeAI.png').classes('text-white font-bold'):
                ui.tooltip(luf_original.claude[langx]).classes('bg-green-300 text-black')

            # Dark mode toggle
            ui.button(
                icon="dark_mode",
                on_click=_toggle_dark,
            ).props("flat round dense").classes("text-white")

            # Language selector – custom button+menu so flags render in Chrome
            with ui.button(LANG_OPTIONS[lang]).props("flat dense").classes("text-white"):
                with ui.menu():
                    for code, label in LANG_OPTIONS.items():
                        ui.menu_item(label, on_click=lambda _, c=code: _change_lang(c))


# ── Pages ─────────────────────────────────────────────────────────────────────

@ui.page("/")
def home():
    token = get_or_create_token()
    create_header()
#    ui.colors(my_orange="#FF8A05")

    def _resumable_sessions():
        """All sessions (GM + player) that belong to non-complete games."""
        abbr_to_name = dict(zip(REGION_ABBR, REGIONS))
        with get_db() as conn:
            all_s = [dict(r) for r in conn.execute("SELECT * FROM sessions").fetchall()]
            open_games = {r["game_id"]: dict(r) for r in conn.execute(
                "SELECT game_id, current_round, num_rounds FROM games WHERE state != 'complete'"
            ).fetchall()}
            token_to_gid = {s["token"]: s["game_id"] for s in all_s if s.get("game_id")}

        result = []
        for s in all_s:
            if s["role"] == "GM":
                gid = s.get("game_id", "")
            else:
                gid = token_to_gid.get(s.get("game_token", ""), "")
            if not gid or gid not in open_games:
                continue
            g = open_games[gid]
            region = s.get("region", "")
            region_label = abbr_to_name.get(region, region) if region else ""
            if s["role"] == "GM":
                desc = f"{gid}  (r{g['current_round']}/{g['num_rounds']})  –  GM  [{s['username']}]"
            else:
                desc = (f"{gid}  (r{g['current_round']}/{g['num_rounds']})  –  "
                        f"{s['role']}, {region_label}  [{s['username']}]")
            result.append({
                "token":   s["token"],
                "role":    s["role"],
                "game_id": gid,
                "desc":    desc,
            })
        result.sort(key=lambda x: (x["game_id"], x["role"]))
        return result

    def _open_resume_dialog():
        abbr_to_name = dict(zip(REGION_ABBR, REGIONS))

        with ui.dialog() as dlg, ui.card().classes("p-6 w-80"):
            ui.label(luf_original.resume_a_game[langx]).classes("text-xl font-bold mb-4")

            gid_input = ui.input(luf_original.gm_id_title_str[langx], placeholder=luf_original.ABC123[langx]) \
                          .props("autofocus").classes("w-full")
            err_label  = ui.label("").classes("text-red-500 text-sm mt-1")
            detail_col = ui.column().classes("w-full")
            sessions_ref = [[]]   # mutable ref

            def look_up():
                gid = gid_input.value.strip().upper()
                err_label.set_text("")
                detail_col.clear()
                sessions_ref[0] = []
                if not gid:
                    err_label.set_text("Enter a game ID.")
                    return
                with get_db() as conn:
                    game = conn.execute(
                        "SELECT * FROM games WHERE game_id = ? AND state != 'complete'",
                        (gid,)
                    ).fetchone()
                if not game:
                    err_label.set_text(f"Game '{gid}' not found or already complete.")
                    return
                # Collect sessions for this game
                with get_db() as conn:
                    gm_row = conn.execute(
                        "SELECT * FROM sessions WHERE game_id = ? AND role = 'GM'", (gid,)
                    ).fetchone()
                    player_rows = []
                    if gm_row:
                        player_rows = conn.execute(
                            "SELECT * FROM sessions WHERE game_token = ?",
                            (gm_row["token"],)
                        ).fetchall()
                cutoff = int(time.time()) - 90  # active in the last 90 s → flag as live
                sessions = []
                if gm_row:
                    gd = dict(gm_row)
                    live = gd.get("last_active", 0) > cutoff
                    desc = f"GM  [{gd['username']}]" + ("  ⚡ active" if live else "")
                    sessions.append({"token": gd["token"], "role": "GM", "desc": desc})
                for row in player_rows:
                    pd = dict(row)
                    live = pd.get("last_active", 0) > cutoff
                    rl = abbr_to_name.get(pd.get("region", ""), pd.get("region", ""))
                    desc = (f"{pd['role']}, {rl}  [{pd['username']}]"
                            + ("  ⚡ active" if live else ""))
                    sessions.append({"token": pd["token"], "role": pd["role"], "desc": desc})
                if not sessions:
                    err_label.set_text("No one has joined this game yet.")
                    return
                sessions_ref[0] = sessions
                opts = {s["token"]: s["desc"] for s in sessions}

                with detail_col:
                    sel = ui.select(opts, label=luf_original.your_session[langx],
                                    value=next(iter(opts))).classes("w-full mt-3")

                    def do_resume():
                        chosen = sel.value
                        s = next((x for x in sessions_ref[0]
                                  if x["token"] == chosen), None)
                        if not s:
                            err_label.set_text("Session not found.")
                            return
                        if s["role"] == "GM":
                            with ui.dialog() as code_dlg, ui.card().classes("p-6"):
                                ui.label(luf_original.gm_verification[langx]).classes("text-xl font-bold mb-4")
                                ui.label(luf_original.enter_the_GM_start_code[langx]) \
                                  .classes("text-gray-500 mb-2")
                                code_input = ui.input(password=True,
                                                      placeholder=luf_original.enter_code_tx[langx]) \
                                               .props("autofocus").classes("w-full")
                                code_err = ui.label("").classes("text-red-500 text-sm")

                                def confirm_code():
                                    if code_input.value.strip().lower() != "oscar":
                                        code_err.set_text("Wrong code – try again.")
                                        return
                                    app.storage.user["token"] = chosen
                                    code_dlg.close()
                                    dlg.close()
                                    ui.navigate.to(f"/gm/board?token={chosen}")

                                code_input.on("keydown.enter", confirm_code)
                                with ui.row().classes("mt-4 gap-2"):
                                    ui.button(luf_original.weiter[langx], on_click=confirm_code)
                                    ui.button(luf_original.cancel_btn[langx], on_click=code_dlg.close).props("flat")
                            code_dlg.open()
                            return
                        app.storage.user["token"] = chosen
                        dlg.close()
                        ui.navigate.to(f"/dashboard?token={chosen}")

                    ui.button(luf_original.resume[langx], icon="login", on_click=do_resume) \
                      .props("color=primary").classes("w-full mt-3")

            gid_input.on("keydown.enter", look_up)
            ui.button(luf_original.look_up_game[langx], on_click=look_up) \
              .props("color=secondary").classes("w-full mt-2")
            ui.button(luf_original.cancel_btn[langx], on_click=dlg.close).props("flat").classes("w-full mt-1")
        dlg.open()

    # ── New game dialog ────────────────────────────────────────────────────────
    def open_new_game():
        with ui.dialog() as dlg, ui.card().classes("p-6 w-80"):
            ui.label(luf_original.new_game[langx]).classes("text-xl font-bold mb-4")
            name_input = ui.input(luf_original.your_name_for_this_game[langx],
                                  placeholder=luf_original.eg_class_10a[langx]) \
                           .props("autofocus").classes("w-full mb-2")
            ui.label(luf_original.enter_the_start_code[langx]).classes("text-gray-500 mb-1")
            code_input = ui.input(password=True, placeholder=luf_original.the_semi_secret_start_code[langx]) \
                           .classes("w-full")
            err_label = ui.label("").classes("text-red-500 text-sm mt-1")

            def do_new():
                name = name_input.value.strip()
                if not name:
                    err_label.set_text(luf_original.enter_a_name_for_this_game[langx])
                    return
                if db_find_by_username(name):
                    is_already_taken_choose_another = luf_original.is_already_taken_choose_another[langx]
                    err_label.set_text(f"'{name}' {is_already_taken_choose_another}")
                    return
                if code_input.value.strip().lower() != "oscar":
                    err_label.set_text(luf_original.wrong_code_try_again[langx])
                    return
                game_id = db_generate_game_id()
                db_create(token, name, "GM",
                          lang=get_lang(), dark=int(get_dark()))
                db_update(token, game_id=game_id)
                _lang = get_lang()
                with get_db() as _conn:
                    _conn.execute(
                        "INSERT OR IGNORE INTO games (game_id, gm_username, num_rounds, "
                        "current_round, state, lang, langx, mode, state_x) "
                        "VALUES (?,?,3,1,'active',?,?,'normal',1)",
                        (game_id, name, _lang, 0 if _lang == "en" else 1),
                    )
                    _conn.commit()
                dlg.close()
                ui.navigate.to(f"/gm/setup?token={token}")

            name_input.on("keydown.enter", lambda: code_input.run_method("focus"))
            code_input.on("keydown.enter", do_new)
            with ui.row().classes("mt-4 gap-2"):
                ui.button(luf_original.start[langx], on_click=do_new)
                ui.button(luf_original.cancel_btn[langx], on_click=dlg.close).props("flat")

        dlg.open()

    # ── Join game dialog ────────────────────────────────────────────────────────
    def open_join():
        with ui.dialog() as dlg, ui.card().classes("p-6 w-96"):
            ui.label(luf_original.join_game[langx]).classes("text-xl font-bold mb-4")

            name_input = ui.input(luf_original.please_enter_a_username[langx], placeholder=luf_original.choose_unique_username[langx]).props("autofocus") \
                           .classes("w-full")
            gid_input  = ui.input(luf_original.gm_id_title_str[langx],  placeholder=luf_original.ABC123[langx]) \
                           .classes("w-full mt-2")
            err_label  = ui.label("").classes("text-red-500 text-sm mt-1")

            # Region + ministry selectors revealed after game-ID validation
            extra = ui.column().classes("w-full")
            gm_token_ref  = [None]
            check_btn_ref = [None]

            def validate():
                name = name_input.value.strip()
                gid  = gid_input.value.strip().upper()
                err_label.set_text("")

                if not name:
                    err_label.set_text(luf_original.player_join_name[langx])
                    return
                if db_find_by_username(name):
                    is_already_taken_choose_another = luf_original.is_already_taken_choose_another[langx]
                    err_label.set_text(f"'{name}' {is_already_taken_choose_another}")
                    return
                if not gid:
                    err_label.set_text(luf_original.please_enter_a_Game_ID[langx])
                    return

                gm = db_find_by_game_id(gid)
                if not gm:
                    game_ug = luf_original.game_ug[langx]
                    not_found_ug = luf_original.not_found[langx]
                    err_label.set_text(f"{game_ug} '{gid}' {not_found_ug}.")
                    return

                gm_token_ref[0] = gm["token"]
                human_abbrs = [r for r in (gm.get("human_regions") or "").split(",") if r]
                abbr_to_name = dict(zip(REGION_ABBR, REGIONS))
                region_opts  = {a: abbr_to_name.get(a, a) for a in human_abbrs}

                if check_btn_ref[0]:
                    check_btn_ref[0].set_visibility(False)
                extra.clear()
                with extra:
                    ui.label(luf_original.select_your_region_and_ministry[langx]) \
                      .classes("font-bold mt-3 mb-1")

                    def taken_slots():
                        return db_get_players(gm_token_ref[0])

                    def avail_ministries(region_abbr, players):
                        used = {p["role"] for p in players
                                if p["region"] == region_abbr}
                        return [m for m in MINISTRIES if m not in used]

                    def avail_regions(players):
                        fully = {abbr for abbr in human_abbrs
                                 if len({p["role"] for p in players
                                         if p["region"] == abbr}) >= len(MINISTRIES)}
                        return {a: region_opts[a] for a in human_abbrs
                                if a not in fully}

                    players_now   = taken_slots()
                    ministry_ref  = [None]   # filled after ministry_sel is created

                    def on_region_change(e):
                        ms = ministry_ref[0]
                        if ms is None:
                            return
                        if not e.value:
                            ms.set_options([])
                            return
                        opts = avail_ministries(e.value, taken_slots())
                        ms.set_options(opts, value=opts[0] if opts else None)

                    region_sel   = ui.select(avail_regions(players_now),
                                             label=luf_original.region[langx],
                                             on_change=on_region_change) \
                                     .classes("w-full")
                    ministry_sel = ui.select([], label=luf_original.ministry[langx]) \
                                     .classes("w-full mt-2")
                    ministry_ref[0] = ministry_sel

                    def refresh_availability():
                        ps = taken_slots()
                        ar = avail_regions(ps)
                        region_sel.set_options(ar)
                        if region_sel.value not in ar:
                            region_sel.value = None
                            ministry_sel.set_options([])
                        elif region_sel.value:
                            opts = avail_ministries(region_sel.value, ps)
                            ministry_sel.set_options(opts)
                            if ministry_sel.value not in opts:
                                ministry_sel.value = opts[0] if opts else None

                    ui.timer(2.0, refresh_availability)

                    def do_join():
                        if not region_sel.value:
                            err_label.set_text(luf_original.select_a_region_before_joining[langx])
                            return
                        if not ministry_sel.value:
                            err_label.set_text(luf_original.select_a_ministry_before_joining[langx])
                            return
                        # Final race-condition check
                        ps = taken_slots()
                        if any(p["region"] == region_sel.value and
                               p["role"]   == ministry_sel.value for p in ps):
                            err_label.set_text(luf_original.that_slot_was_just_taken_please_pick_another[langx])
                            refresh_availability()
                            return
                        player_token = secrets.token_urlsafe(16)
                        app.storage.user["token"] = player_token
                        db_create(player_token, name, ministry_sel.value,
                                  lang=get_lang(), dark=int(get_dark()))
                        gm_s = db_get(gm_token_ref[0]) if gm_token_ref[0] else {}
                        gm_game_id = gm_s.get("game_id", "") if gm_s else ""
                        db_update(player_token,
                                  game_token=gm_token_ref[0],
                                  game_id=gm_game_id,
                                  region=region_sel.value)
                        if gm_s and gm_s.get("game_id"):
                            with get_db() as _conn:
                                exists = _conn.execute(
                                    "SELECT 1 FROM human_regions "
                                    "WHERE game_id=? AND region_tag=?",
                                    (gm_s["game_id"], region_sel.value),
                                ).fetchone()
                                if not exists:
                                    _conn.execute(
                                        "INSERT INTO human_regions "
                                        "(game_id, region_tag, sub_1, sub_2, sub_3) "
                                        "VALUES (?,?,0,0,0)",
                                        (gm_s["game_id"], region_sel.value),
                                    )
                                _conn.commit()
                        dlg.close()
                        ui.navigate.to(f"/dashboard?token={player_token}")

                    ui.button(luf_original.join_ug[langx], icon="sports_esports",
                              on_click=do_join, color="positive") \
                      .classes("mt-3 w-full")

            gid_input.on("keydown.enter", validate)
            with ui.row().classes("mt-4 gap-2"):
                check_btn = ui.button(luf_original.check_game[langx], on_click=validate)
                check_btn_ref[0] = check_btn
                ui.button(luf_original.cancel_btn[langx], on_click=dlg.close).props("flat")

        dlg.open()

    # ── Unified home card ───────────────────────────────────────────────────────
    has_resumable = len(_resumable_sessions()) > 0

    def open_new_or_join():
        with ui.dialog() as dlg, ui.card().classes("p-6 w-96"):
            ui.label(luf_original.fresh_game[langx]).classes("text-xl font-bold mb-4")
            ui.button(luf_original.start_a_new_game_as_game_leader[langx], icon="add_circle",
                      on_click=lambda: (dlg.close(), open_new_game())) \
              .classes("w-full mb-2")
            ui.button(luf_original.join_a_new_game_as_player[langx], icon="sports_esports",
                      on_click=lambda: (dlg.close(), open_join())) \
              .props("color=secondary").classes("w-full")
            ui.button(luf_original.cancel_btn[langx], on_click=dlg.close).props("flat").classes("w-full mt-2")
        dlg.open()

    lang = get_lang()
    langx = 0 if lang == "en" else 1
    with ui.card().classes("mx-auto mt-16 p-8 w-80"):
        ui.label(luf_original.welcome[langx]).classes("text-3xl font-bold mb-4")
        ui.button(luf_original.about_btn_tx[langx], icon='info',
                  on_click=lambda: ui.navigate.to('/about'), color='#FF8F2E').classes('w-full text-black font-bold')
        ui.button(luf_original.a_fresh_game_start_or_join[langx], icon="add_circle",
                  on_click=open_new_or_join).classes("w-full mb-2")
        if has_resumable:
            ui.label(luf_original.or_ug[langx]).classes("text-lg font-bold text-center my-2 w-full")
            ui.button(luf_original.resume_existing_game[langx], icon="list",
                      on_click=_open_resume_dialog).classes("w-full").props("color=green-5")

    # ── Debug ─────────────────────────────────────────────────────────────────
    with ui.expansion("Debug: sessions DB").classes("mt-8 mx-auto"):
        @ui.refreshable
        def show_db():
            with get_db() as conn:
                rows = conn.execute("SELECT * FROM sessions").fetchall()
            if not rows:
                ui.label("(empty)").classes("text-gray-400")
            else:
                ui.table(
                    columns=[
                        {"name": "token",    "label": "token",    "field": "token"},
                        {"name": "username", "label": "username", "field": "username"},
                        {"name": "game_id", "label": "game_id", "field": "game_id"},
                        {"name": "role",     "label": "role",     "field": "role"},
                        {"name": "lang",     "label": "lang",     "field": "lang"},
                        {"name": "dark",     "label": "dark",     "field": "dark"},
                    ],
                    rows=[{**dict(r), "token": r["token"][:8]+"..."} for r in rows],
                ).classes("w-full")

        show_db()
        with ui.row().classes("gap-2"):
            ui.button(luf_original.refresh[langx], on_click=show_db.refresh).props("flat size=sm")
            def clear_all():
                with get_db() as conn:
                    conn.execute("DELETE FROM sessions")
                    conn.execute("DELETE FROM games")
                    conn.execute("DELETE FROM players")
                    conn.execute("DELETE FROM ai_regions")
                    conn.execute("DELETE FROM human_regions")
                    conn.execute("DELETE FROM policy_decisions")
                    conn.execute("DELETE FROM region_submissions")
                    conn.commit()
                app.storage.user.clear()
                show_db.refresh()
                ui.notify("All sessions cleared.", color="warning")
            ui.button("Clear all sessions", on_click=clear_all, color="negative").props("flat size=sm")


@ui.page("/gm/setup")
def gm_setup(token: str):
    session = db_get(token)
    if not session or session["role"] != "GM":
        ui.navigate.to("/")
        return

    create_header(token)
    db_heartbeat(token)
    ui.timer(30, lambda: db_heartbeat(token))

    # ── Read current state from DB ────────────────────────────────────────────
    human_regions = set(session.get("human_regions", "").split(",")) - {""}
    setup_done = bool(session.get("setup_done", 0))

    lang = get_lang()
    langx = 0 if lang == "en" else 1
    with ui.column().classes("w-full max-w-2xl mx-auto p-8 gap-4"):
        game_setup = luf_original.game_setup[langx]
        ui.label(f"{game_setup} · {session['username']}").classes("text-2xl font-bold")
        gm_id_title_str = luf_original.gm_id_title_str[langx]
        ui.label(f"{gm_id_title_str}: {session.get('game_id', '…')}") \
          .classes("text-orange-600 font-mono font-bold text-lg")

        # ── Card 1: Instructions  (hidden once confirmed) ─────────────────────
        with ui.card().classes("w-full p-4 bg-amber-50") as card_instructions:
            ui.label(luf_original.select_human_players[langx]).classes("text-lg font-bold mb-1 text-black")
            hinweise = luf_original.tick_every_region_that_will_be_played_by_a_human[langx] + "\n" + luf_original.unticked_regions_are_simulated_by_the_model[langx]
            ui.label(hinweise).classes("text-gray-600 text-sm")
        card_instructions.set_visibility(not setup_done)

        # ── Card 2: Region checkboxes  (visible while setup not confirmed) ────
        # key = region abbreviation, so human_regions stores abbrs (e.g. 'us,eu')
        checkboxes: dict[str, ui.checkbox] = {}

        with ui.card().classes("w-full p-4 bg-blue-50") as card_select:
            ui.label(luf_original.regions[langx]).classes("font-bold mb-2 text-black")
            with ui.column().classes("gap-1"):
                for abbr, name in zip(REGION_ABBR, REGIONS):
                    checkboxes[abbr] = ui.checkbox(name, value=(abbr in human_regions)).classes('text-black').props("dense color=primary keep-color")

            def confirm():
                selected = [abbr for abbr, cb in checkboxes.items() if cb.value]
                if not selected:
                    ui.notify(luf_original.at_least_one_region_must_be_played_by_human_players[langx], color="negative")
                    return
                db_update(token, human_regions=",".join(selected), setup_done=1)
                card_instructions.set_visibility(False)
                card_select.set_visibility(False)
                card_confirmed.set_visibility(True)
                show_confirmed.refresh()

            ui.button(luf_original.confirm_selection[langx], icon="check", on_click=confirm).classes("mt-3")

        card_select.set_visibility(not setup_done)

        # ── Card 3: Confirmed summary  (visible after confirmation) ───────────
        with ui.card().classes("w-full p-4 bg-green-50") as card_confirmed:

            @ui.refreshable
            def show_confirmed():
                s = db_get(token)
                abbr_to_name = dict(zip(REGION_ABBR, REGIONS))
                selected_abbrs = [r for r in (s.get("human_regions") or "").split(",") if r]
                ui.label(luf_original.regions_played_by_human_players[langx]).classes("font-bold mb-2 text-black")
                with ui.row().classes("flex-wrap gap-2 mb-4"):
                    for abbr in selected_abbrs:
                        ui.badge(abbr_to_name.get(abbr, abbr), color="green")
                with ui.row().classes("gap-2"):
                    ui.button(
                        luf_original.edit[langx],
                        icon="edit",
                        on_click=lambda: (
                            db_update(token, setup_done=0),
                            card_confirmed.set_visibility(False),
                            card_instructions.set_visibility(True),
                            card_select.set_visibility(True),
                        ),
                    ).props("outline")
                    ui.button(
                        luf_original.continue_to_GM_board[langx],
                        icon="arrow_forward",
                        on_click=lambda: ui.navigate.to(f"/gm/board?token={token}"),
                    )

            show_confirmed()

        card_confirmed.set_visibility(setup_done)


@ui.page("/gm/board")
def gm_board(token: str):
    session = db_get(token)
    if not session or session["role"] != "GM":
        ui.navigate.to("/")
        return

    create_header(token)
    db_heartbeat(token)
    ui.timer(30, lambda: db_heartbeat(token))

    abbr_to_name = dict(zip(REGION_ABBR, REGIONS))
    human_abbrs  = [r for r in session.get("human_regions", "").split(",") if r]
    current_round = session.get("current_round", 1)
    num_rounds    = session.get("num_rounds", 3)
    lang    = session.get("lang", "en")
    langx   = 0 if lang == "en" else 1

    # Generate AI policy decisions on first load if none exist yet
    gid = session.get("game_id", "")
    if gid:
        with get_db() as _conn:
            already = _conn.execute(
                "SELECT COUNT(*) FROM policy_decisions WHERE game_id = ?", (gid,)
            ).fetchone()[0]
        if not already:
            human_regs = set(r for r in (session.get("human_regions") or "").split(",") if r)
            ai_regs = [r for r in REGION_ABBR if r not in human_regs]
            with get_db() as _conn:
                _conn.execute("DELETE FROM ai_regions WHERE game_id=?", (gid,))
                for r in ai_regs:
                    _conn.execute(
                        "INSERT OR IGNORE INTO ai_regions (game_id, region_tag) VALUES (?,?)",
                        (gid, r),
                    )
                _conn.commit()
            # Show spinner, generate in background, reload once done
            with ui.card().classes("mx-auto mt-32 p-8 items-center gap-4"):
                ui.spinner(size="xl")
                ui.label(luf_original.generating_random_policy_decisions[langx]).classes("text-lg")

            async def _do_generate():
                await run.io_bound(maindb.generate_ai_policy_decisions, gid)
                ui.navigate.to(f"/gm/board?token={token}")

            ui.timer(0.1, _do_generate, once=True)
            return


    # Which players have joined / submitted this round?
    _gm_game_id = session.get("game_id", "")
    players = db_get_players(token, _gm_game_id)

    def _missing_slots(ps):
        """Return {abbr: [missing_ministry, ...]} for every incomplete region."""
        joined_map = {}
        for p in ps:
            r = p["region"]
            if r:
                joined_map.setdefault(r, set()).add(p["role"])
        result = {}
        for abbr in human_abbrs:
            missing_m = [m for m in MINISTRIES if m not in joined_map.get(abbr, set())]
            if missing_m:
                result[abbr] = missing_m
        return result

    missing_slots = _missing_slots(players)
    all_in    = len(missing_slots) == 0 and len(human_abbrs) > 0

    # Submission: region complete when Future has submitted (mark_region_submitted called)
    def _unsubmitted():
        """Return {abbr: True} for regions where Future hasn't submitted yet."""
        gid = session.get("game_id", "")
        rnd = session.get("current_round", 1)
        result = {}
        for abbr in human_abbrs:
            if not maindb.is_region_submitted(gid, rnd, abbr):
                result[abbr] = abbr
        return result

    unsub_slots = _unsubmitted()
    all_sub   = len(unsub_slots) == 0 and all_in
    game_done = current_round > num_rounds

    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-4"):

        # ── Title row ────────────────────────────────────────────────────────
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label(luf_original.gm_board[langx]).classes("text-3xl font-bold")
                game_id_ug = luf_original.gm_id_title_str[langx]
                your_username = luf_original.your_username[langx]
                round_ug = luf_original.runde[langx]
                ui.label(
                    f"#{game_id_ug}: {session.get('game_id','?')}  ·  "
                    f"{round_ug} {current_round}/{num_rounds}  · {your_username}: {session['username']}"
                ).classes("text-orange-600 font-mono font-bold")


        ui.separator()

        # ── Card 1: Instructions  (always visible) ────────────────────────────
        with ui.card().classes("w-full p-2 bg-amber-50"):
            ui.label("[Card 1 – Status]").classes("text-xs text-gray-400 italic")
            def __show_player_ids():
                ps = db_get_players(token, game_id_gm)
                with ui.dialog() as dlg, ui.card().classes("w-full max-w-2xl"):
                    ui.label(luf_original.player_ids[langx]).classes("text-2xl font-bold mb-4")
                    reg_ug = luf_original.region[langx]
                    mini_ug = luf_original.ministry[langx]
                    login_id = luf_original.login_id[langx]
                    if not ps:
                        ui.label(luf_original.no_players_have_joined_this_game_yet[langx]).classes("text-orange-600")
                    else:
                        ui.table(
                            columns=[
                                {"name": "region",   "label": reg_ug,   "field": "region",   "align": "left"},
                                {"name": "ministry", "label": mini_ug, "field": "ministry", "align": "left"},
                                {"name": "username", "label": login_id, "field": "username", "align": "left"},
                            ],
                            rows=[{"region": abbr_to_name.get(p["region"], p["region"]),
                                    "ministry": p["role"],
                                    "username": p["username"]}
                                    for p in ps if p.get("region")],
                            row_key="username",
                        ).props("dense flat").classes("w-full")
                    ui.button(luf_original.close_ug[langx], on_click=dlg.close).classes("w-full mt-4")
                dlg.open()
            ui.button(luf_original.show_playerids[langx], icon="badge", on_click=__show_player_ids).props("flat dense size=sm")
            status_label = ui.label("").classes("text-lg font-bold text-primary")
            anweisung_label   = ui.markdown("").classes("text-sm text-orange-800 mt-1")
            info_label   = ui.label("").classes("text-sm text-orange-800 mt-1")

            def _update_labels(rnd, all_joined, all_submitted, done):
                if done:
                    status_label.set_text(luf_original.game_complete[langx])
                    anweisung_label.set_content(luf_original.pcgd_rd1_infoend_str[langx])
#                    info_label.set_text("All rounds have been played.")
                elif not all_joined:
                    ui.notify(f'current_round={current_round}',type='warning')
                    runde_ug = luf_original.runde[langx]
                    waiting_for_players_to_join = luf_original.waiting_for_players_to_join[langx]
                    status_label.set_text(f"{runde_ug} {rnd} {waiting_for_players_to_join}")
                    if current_round == 1:
                        anweisung_label.set_content(luf_original.ui_gm_info_start[langx])
                    elif current_round == 2:
                        anweisung_label.set_content(luf_original.gm_checkbox_open40_tx[langx])
                    elif current_round == 3:
                        anweisung_label.set_content(luf_original.gm_checkbox_open60_tx[langx])
                    elif current_round == 4:
                        anweisung_label.set_content(luf_original.gm_checkbox_open21_tx[langx])
                    info_label.set_text(luf_original.some_regions_have_not_joined_yet[langx])
                elif not all_submitted:
                    runde_ug = luf_original.runde[langx]
                    waiting_for_submissions = luf_original.waiting_for_submissions[langx]
                    status_label.set_text(f"{runde_ug} {rnd} {waiting_for_submissions}")
                    anweisung_label.set_content(luf_original.not_all_submitted[langx])
                    info_label.set_text("")
                else:
                    runde_ug = luf_original.runde[langx]
                    ready_to_run_the_model_and_advance = luf_original.ready_to_run_the_model_and_advance[langx]
                    all_submitted = luf_original.all_submitted[langx]
                    status_label.set_text(f"{runde_ug} {rnd} {all_submitted}")
#                    anweisung_label.set_content('else')
                    info_label.set_text(ready_to_run_the_model_and_advance)

            _update_labels(current_round, all_in, all_sub, game_done)

        # ── Card 2: Missing players  (visible when not all joined) ───────────
        with ui.card().classes("w-full p-4 bg-red-100") as card_missing:
            ui.label("[Card 2 – Missing players]").classes("text-xs text-gray-400 italic")
            with ui.row().classes("w-full items-center justify-between mb-1"):
                ui.label(luf_original.waiting_for_these_ministry_slots_to_join[langx]).classes("font-bold text-black")
            missing_col = ui.column().classes("gap-0")
            def _fill_missing(slots: dict):
                missing_col.clear()
                with missing_col:
                    for a, ministries in slots.items():
                        ui.label(f"• {abbr_to_name.get(a, a)}").classes("text-red-700 font-semibold leading-tight")
                        for m in ministries:
                            ui.label(f"    – {m}").classes("text-red-600 ml-4 text-sm leading-none")
            _fill_missing(missing_slots)
        card_missing.set_visibility(not all_in and not game_done)

        # ── Card 3: Allow / Prevent submissions  (visible when all joined, not all submitted)
        game_id_gm = session.get("game_id", "")

        with ui.card().classes("w-full p-4 bg-amber-400") as card_allow_prevent:
            ui.label("[Card 3 – Allow/Prevent submissions]").classes("text-xs text-gray-600 italic")
            allow_label = ui.label("").classes("font-bold text-xl mb-3 text-black")
            allow_btn   = ui.button("", icon="toggle_on")

            def _refresh_allow_btn():
                try:
                    cur = maindb.get_accept_decisions(game_id_gm, current_round)
                except Exception:
                    cur = 0
                if cur == 1:
                    allow_label.set_text(luf_original.submissions_are_ALLOWED_the_ministers_for_the_Future_can_submit[langx])
                    allow_btn.set_text(luf_original.prevent_submissions[langx])
                    allow_btn.props("color=negative")
                else:
                    allow_label.set_text(luf_original.submissions_are_blocked_the_ministers_for_the_Future_can_submit[langx])
                    allow_btn.set_text(luf_original.allow_submissions[langx])
                    allow_btn.props("color=positive")

            def _toggle_allow():
                try:
                    cur = maindb.get_accept_decisions(game_id_gm, current_round)
                    maindb.set_accept_decisions(game_id_gm, current_round, 0 if cur == 1 else 1)
                except Exception:
                    pass
                _refresh_allow_btn()

            allow_btn.on_click(_toggle_allow)
            _refresh_allow_btn()
        card_allow_prevent.set_visibility(all_in and not all_sub and not game_done)

        # ── Card 4 (was 3): Submission status  (visible when all joined, not all submitted)
        with ui.card().classes("w-full p-4 bg-amber-100") as card_submissions:
            ui.label("[Card 4 – Submission status]").classes("text-xs text-gray-400 italic")
            ui.label(luf_original.submission_status[langx]).classes("font-bold mb-2")
            sub_col = ui.column()
            def _fill_submissions(ps, h_abbrs, gm_round):
                sub_col.clear()
                post_model = all_sub  # True = model has run, tracking who checked results
                region_map = {}
                for p in ps:
                    r = p["region"]
                    if r:
                        region_map.setdefault(r, []).append(p)
                with sub_col:
                    if post_model:
                        ui.label(luf_original.waiting_for_players_to_check_results[langx]).classes("text-sm text-gray-500 mb-1")
                    for a in h_abbrs:
                        members = region_map.get(a, [])
                        if post_model:
                            # Phase B: who has clicked "Check if results are ready"?
                            checked = {p["role"]: p.get("current_round", 1) >= gm_round for p in members}
                            region_done = all(checked.values()) if checked else False
                        else:
                            # Phase A: who has submitted sliders/proposals?
                            checked = {p["role"]: bool(p.get("submitted", 0)) for p in members}
                            region_done = maindb.is_region_submitted(game_id_gm, current_round, a)
                        r_icon  = "check_circle" if region_done else "pending"
                        r_color = "text-green-600" if region_done else "text-orange-500"
                        with ui.row().classes("items-center gap-2"):
                            ui.icon(r_icon).classes(r_color)
                            ui.label(abbr_to_name.get(a, a)).classes(r_color + " font-semibold")
                        if post_model:
                            # Phase B: show per-player who has clicked "Check results"
                            for m in MINISTRIES:
                                done = checked.get(m, False)
                                m_icon  = "check" if done else "schedule"
                                m_color = "text-green-500" if done else "text-orange-400"
                                with ui.row().classes("items-center gap-1 ml-6"):
                                    ui.icon(m_icon).classes(m_color + " text-sm")
                                    ui.label(m).classes(m_color + " text-sm")
            _fill_submissions(players, human_abbrs, current_round)
        try:
            _accept_init = maindb.get_accept_decisions(game_id_gm, current_round)
        except Exception:
            _accept_init = 0
        _all_checked_init = all(
            p.get("current_round", 1) >= current_round for p in players
        ) if players else True
        card_submissions.set_visibility(
            all_in and not game_done and (
                (not all_sub and _accept_init == 1) or        # Phase A: tracking submissions
                (all_sub and not _all_checked_init)           # Phase B: tracking result checks
            )
        )

        # ── Card 4: Advance round  (visible when all submitted, game not done) ─
        with ui.card().classes("w-full p-4 bg-green-100") as card_advance:
            ui.label("[Card 5 – Run model]").classes("text-xs text-gray-400 italic")
            ui.label(luf_original.all_regions_have_submitted[langx]).classes("font-bold text-black mb-2")
            ready_to_run_model_and_advance_to_round = luf_original.ready_to_run_model_and_advance_to_round[langx]
            ui.label(f"{ready_to_run_model_and_advance_to_round} {current_round + 1}.").classes("text-sm mb-3")

            def advance():
                # Guard: re-check submissions at click time
                unsub_now = _unsubmitted()
                if unsub_now:
                    with ui.dialog() as warn_dlg, ui.card().classes("p-6"):
                        ui.label(luf_original.not_all_regions_have_submitted[langx]).classes("text-xl font-bold text-red-600 mb-2")
                        for reg, minis in unsub_now.items():
                            ui.label(f"• {abbr_to_name.get(reg, reg)}: {', '.join(minis)}").classes("text-orange-600")
                        ui.button(luf_original.ok_ug[langx], on_click=warn_dlg.close).props("color=primary")
                    warn_dlg.open()
                    return

                with ui.dialog() as dlg, ui.card().classes("p-6"):
                    ui.label(luf_original.run_model_advance[langx]).classes("text-xl font-bold mb-2")
                    all_regions_submitted_run_the_simulation_for_round = luf_original.all_regions_submitted_run_the_simulation_for_round[langx]
                    and_advance_to_round = luf_original.and_advance_to_round[langx]
                    ui.label(
                        f"{all_regions_submitted_run_the_simulation_for_round} {current_round} "
                        f"{and_advance_to_round} {current_round + 1}?"
                    ).classes("text-sm text-black mb-2")

                    async def do_advance():
                        dlg.close()
                        gid = session.get("game_id", "")
                        notify = ui.notify(luf_original.model_running_please_wait[langx],
                                           type="ongoing", timeout=0, position="center")
                        import ugregmod as _ugregmod
                        await run.io_bound(_ugregmod.ugregmod, gid, current_round)
                        if notify:
                            notify.dismiss()
                        # Advance in game DB (increments current_round, resets accept_decisions)
                        if gid:
                            maindb.advance_round(gid)
                        # Advance GM session only; players advance when they click "Check if results are ready"
                        next_round = current_round + 1
                        db_update(token, current_round=next_round)
                        ui.navigate.to(f"/gm/board?token={token}")

                    with ui.row().classes("gap-2 justify-end mt-4"):
                        ui.button(luf_original.cancel_btn[langx], on_click=dlg.close).props("flat")
                        ui.button(luf_original.yes_run_model[langx], icon="play_arrow",
                                  on_click=do_advance).props("color=positive")
                dlg.open()

            run_model_to_round = luf_original.run_model_to_round[langx]
            ui.button(f"{run_model_to_round} {current_round + 1}",
                      icon="model_training", on_click=advance, color="positive")
        card_advance.set_visibility(all_sub and not game_done)

        # ── Card 5: Game complete ─────────────────────────────────────────────
        with ui.card().classes("w-full p-4 bg-purple-100") as card_done:
            ui.label("[Card 6 – Game complete]").classes("text-xs text-gray-400 italic")
            ui.label(luf_original.game_complete[langx]).classes("text-xl font-bold text-purple-700 mb-2")
            ui.label(luf_original.all_rounds_have_been_played_thank_you_for_playing[langx]).classes("text-sm")
        card_done.set_visibility(False)

        # ── Card 6: GM graphs (visible once all players joined) ───────────────
        lang    = session.get("lang", "en")
        langx   = 0 if lang == "en" else 1

        @ui.refreshable
        def gm_graphs():
            try:
                plot_vars = maindb.get_plot_variables_for_ministry("GM")
            except Exception:
                plot_vars = []

            if not plot_vars:
                return

            rnd   = db_get(token).get("current_round", 1)
            runde = rnd - 1  # 0 = historical; 1+ = post-model-run results
            game_data, actual_runde = game_plot_ug.load_game_data(game_id_gm, runde)
            if game_data is None:
                return
            
            ui.notify(f'card 7 - gm_graphs current_round={current_round}', type="positive")

            if current_round == 1:
                luf_head7 = luf_original.historical_data[langx]
            elif current_round == 2:
                luf_head7 = luf_original.hist_2040[langx]
            elif current_round == 3:
                luf_head7 = luf_original.hist_2060[langx]
            elif current_round == 4:
                luf_head7 = luf_original.hist_2100[langx]
            else:
                luf_head7 = f'card 7 - gm_graphs current_round={current_round}'
            with ui.card().classes("w-full p-6"):
                ui.label("[Card 7 – GM graphs]").classes("text-xs text-gray-400 italic")
                ui.label(luf_head7).classes("text-2xl font-bold mb-1")
                ui.label(
                    f"{luf_original.monitoring[langx]}{len(plot_vars)}"
                    f"{luf_original.indicator_for[langx]}{luf_original.mini_to_long[langx].get('GM','Game Master')}"
                ).classes("text-orange-500 font-bold mb-4")

                graphs = []
                for pv in plot_vars:
                    img = game_plot_ug.do_graph(game_data, pv, actual_runde, "glob", "GM", langx)
                    graphs.append((pv, img))

                with ui.column().classes("w-full gap-4"):
                    for i in range(0, len(graphs), 2):
                        with ui.row().classes("w-full gap-4"):
                            pv, img = graphs[i]
                            with ui.card().classes("lg:flex-1 w-full p-4"):
                                if img:
                                    ui.image(img)
                                else:
                                    ui.label(pv.get("pv_indicator","")).classes("text-lg font-bold")
                                    ui.label(luf_original.graph_data_unavailable[langx]).classes("text-sm text-orange-400 italic")
                            if i + 1 < len(graphs):
                                pv, img = graphs[i + 1]
                                with ui.card().classes("lg:flex-1 w-full p-4"):
                                    if img:
                                        ui.image(img)
                                    else:
                                        ui.label(pv.get("pv_indicator","")).classes("text-lg font-bold")
                                        ui.label(luf_original.graph_data_unavailable[langx]).classes("text-sm text-orange-400 italic")
                            else:
                                ui.element("div").classes("lg:flex-1 w-full")

                try:
                    overlay = game_plot_ug.make_glob_overlay(game_data, lang)
                    if overlay:
                        with ui.card().classes("w-full p-4"):
                            ui.image(overlay).classes("w-full")
                except Exception:
                    pass

        # ── Card 8: Refresh ───────────────────────────────────────────────────
        with ui.card().classes("w-full p-2 bg-stone-50") as card_refresh:
            ui.label("[Card 8 – Refresh]").classes("text-xs text-gray-400 italic")
            def refresh():
                s        = db_get(token)
                ps       = db_get_players(token, s.get("game_id", ""))
                h_abbrs  = [r for r in (s.get("human_regions") or "").split(",") if r]
                rnd      = s.get("current_round", 1)
                n_rounds = s.get("num_rounds", 3)
                done     = rnd > n_rounds
                miss     = _missing_slots(ps)
                a_in     = len(miss) == 0 and len(h_abbrs) > 0
                unsub    = _unsubmitted()
                a_sub    = len(unsub) == 0 and a_in

                _update_labels(rnd, a_in, a_sub, done)
                _fill_missing(miss)
                _fill_submissions(ps, h_abbrs, rnd)

                card_missing.set_visibility(not a_in and not done)
                card_allow_prevent.set_visibility(a_in and not a_sub and not done)
                try:
                    _acc = maindb.get_accept_decisions(game_id_gm, rnd)
                except Exception:
                    _acc = 0
                _all_checked = all(
                    p.get("current_round", 1) >= rnd for p in ps
                ) if ps else True
                card_submissions.set_visibility(
                    a_in and not done and (
                        (not a_sub and _acc == 1) or
                        (a_sub and not _all_checked)
                    )
                )
                card_advance.set_visibility(a_sub and not done)
                card_done.set_visibility(done)
                card_refresh.set_visibility(not done and not a_sub)
                if a_in:
                    gm_graphs.refresh()

            ui.button(luf_original.refresh_btn[langx], icon="refresh", on_click=refresh).props("flat")
        card_refresh.set_visibility(not game_done and not all_sub)

        # ── Card 7: GM graphs (visible once all players joined) ───────────────
        gm_graphs()


# ── Dashboard render helpers ──────────────────────────────────────────────────

def _check_results_btn(token: str, game_id: str, current_round: int, region: str):
    """'Check if results are ready' button — shared by all ministry dashboards."""
    lang = get_lang()
    langx = 0 if lang == "en" else 1
    def check_results():
        
        lang = get_lang()
        langx = 0 if lang == "en" else 1
        if not maindb.is_region_submitted(game_id, current_round, region):
            ui.notify(luf_original.waiting_for_Future_to_submit_proposals[langx], type="warning")
            return
        try:
            with maindb.get_db() as c:
                row = c.execute(
                    "SELECT current_round, state FROM games WHERE game_id=?", (game_id,)
                ).fetchone()
            new_round = row["current_round"] if row else current_round
            game_complete = row and row["state"] == "complete"
        except Exception:
            new_round, game_complete = current_round, False
        if new_round > current_round or game_complete:
            db_update(token, current_round=new_round, submitted=0)
            ui.navigate.to(f"/dashboard?token={token}")
        else:
            ui.notify(luf_original.results_not_ready_yet__the_gm_is_still_running_the_model[langx],
                      type="warning", position='center')
    ui.button(luf_original.check_if_results_are_ready[langx], icon="refresh",
              on_click=check_results).props("color=primary")


def _render_graphs(game_id: str, region: str, role: str, lang: str, langx: int,
                   current_round: int = 1):
    """Historical + post-model-run graphs card — shared by ministry and Future dashboards."""
    try:
        plot_vars = maindb.get_plot_variables_for_ministry(role)
    except Exception as e:
        no_graph_data_available = luf_original.no_graph_data_available[langx]
        ui.label(f"{no_graph_data_available}: {e}").classes("text-orange-400 italic")
        return
    if not plot_vars:
        ui.label(no_graph_data_available).classes("text-gray-400 italic")
        return

    runde = current_round - 1  # 0=historical, 1=after round1 run, etc.
    game_data, actual_runde = game_plot_ug.load_game_data(game_id, runde)
#    ui.notify(f'runde={runde} actual_runde={actual_runde}')
    if actual_runde == 0:
        lufhead = luf_original.historical_data[langx]
        lufinfo = luf_original.pcgd_rd1_info_tx_str[langx]
    elif actual_runde == 1:
        lufhead = luf_original.hist_2040[langx]
        lufinfo = luf_original.pcgd_rd1_info_tx_str[langx]
    elif actual_runde == 2:
        lufhead = luf_original.hist_2060[langx]
        lufinfo = luf_original.pcgd_rd1_info_tx_str[langx]
    elif actual_runde == 3:
        lufhead = luf_original.hist_2100[langx]
        lufinfo = luf_original.pcgd_rd1_infoend_str[langx]
    else:
        lufhead = f'ERROR: actual_runde={actual_runde}'
        lufinfo = f'ERROR lufinfo: actual_runde={actual_runde}'
        
    if game_data is None:
        ui.label(luf_original.no_graph_data_available[langx]).classes("text-gray-400 italic")
        return

    try:
        ministry_label = luf_original.minis[lang][role]
    except Exception:
        ministry_label = role

    with ui.card().classes("w-full p-6"):
        ui.label("[Card A – Graphs]").classes("text-xs text-gray-400 italic")
        ui.label(lufhead).classes("text-2xl font-bold mb-1")
        ui.label(
            f"{luf_original.monitoring[langx]}{len(plot_vars)}{luf_original.indicator_for[langx]}{ministry_label}"
        ).classes("text-orange-500 font-bold mb-4")
        ui.markdown(lufinfo)

        graphs = []
        for pv in plot_vars:
            img = game_plot_ug.do_graph(game_data, pv, actual_runde, region, role, langx)
            graphs.append((pv, img))

        with ui.column().classes("w-full gap-4"):
            for i in range(0, len(graphs), 2):
                with ui.row().classes("w-full gap-4"):
                    pv, img = graphs[i]
                    with ui.card().classes("lg:flex-1 w-full p-4"):
                        if img:
                            ui.image(img)
                        else:
                            ui.label(pv.get("pv_indicator", "")).classes("text-lg font-bold")
                            ui.label(luf_original.no_graph_data_available[langx]).classes("text-sm text-orange-400 italic")
                    if i + 1 < len(graphs):
                        pv, img = graphs[i + 1]
                        with ui.card().classes("lg:flex-1 w-full p-4"):
                            if img:
                                ui.image(img)
                            else:
                                ui.label(pv.get("pv_indicator", "")).classes("text-lg font-bold")
                                ui.label(luf_original.no_graph_data_available[langx]).classes("text-sm text-orange-400 italic")
                    else:
                        ui.element("div").classes("lg:flex-1 w-full")


def _render_sliders(token: str, game_id: str, current_round: int,
                    region: str, role: str, lang: str, langx: int, display_region: str):
    """Policy slider card for non-Future ministries."""
    round_ranges = [luf_original.now_2040, luf_original.to_2060, luf_original.to_2100]
    rrange = round_ranges[min(current_round - 1, 2)][langx]

    try:
        pol_expls = luf_original.pols_expl[lang]
    except Exception:
        pol_expls = {}

    @ui.refreshable
    def slider_section():
        s = db_get(token)

        # Game over – nothing more to do
        try:
            with maindb.get_db() as _c:
                _g = _c.execute("SELECT state, num_rounds FROM games WHERE game_id=?", (game_id,)).fetchone()
            if _g and (_g["state"] == "complete" or current_round > _g["num_rounds"]):
                return
        except Exception:
            pass

        # Future submitted for this region → lock sliders for everyone
        if maindb.is_region_submitted(game_id, current_round, region):
            with ui.card().classes("w-full p-4 bg-green-50"):
                ui.label("[Card B – Region submitted / check results]").classes("text-xs text-gray-400 italic")
                ui.label(luf_original.all_investment_proposals_for_your_region_have_been_submitted[langx]) \
                  .classes("text-xl font-bold text-green-700 mb-3")
                _check_results_btn(token, game_id, current_round, region)
            return

        if s and s.get("submitted", 0):
            with ui.card().classes("w-full p-4 bg-green-50"):
                ui.label("[Card B – Your decisions submitted / check results]").classes("text-xs text-gray-400 italic")
                ui.label(luf_original.your_policy_decisions_have_been_submitted[langx]) \
                  .classes("text-xl font-bold text-green-700 mb-3")
                _check_results_btn(token, game_id, current_round, region)
            return

        try:
            policies = maindb.get_policies_for_ministry(role)
        except Exception as e:
            ui.label(f"Policy data unavailable: {e}").classes("text-orange-400 italic")
            return

        slider_metadata: dict = {}

        def handle_slider_change(e):
            meta = slider_metadata.get(e.sender.id)
            if not meta:
                return
            try:
                maindb.save_policy_decision_from_slider(
                    meta["game_id"], meta["current_round"], meta["region_tag"],
                    meta["ministry"], meta["pol_id"], e.value, meta["pol_tag"],
                )
            except Exception as ex:
                ui.notify(f"Save error: {ex}", type="warning")

        with ui.card().classes("w-full p-4"):
            ui.label("[Card C – Policy sliders]").classes("text-xs text-gray-400 italic")
            ui.label(f"{luf_original.pol_decs[langx]} – {display_region} – {role}") \
              .classes("text-2xl font-bold mb-2")
            ui.label(luf_original.dec_title_tx_str[langx] + str(current_round) + rrange) \
              .classes("text-lg text-orange-700 mb-4")
            ui.markdown(luf_original.dec_info_tx_str[langx])

            if not policies:
                ui.label(f"No policies assigned to {role}").classes("text-red-600")
                return

            for policy in policies:
                pol_id  = policy["pol_id"]
                pol_tag = policy["pol_tag"]
                pol_min = policy["pol_min"]
                pol_max = policy["pol_max"]
                try:
                    current_value = maindb.get_one_policy_decision(
                        game_id, current_round, region, role, pol_tag)
                except Exception:
                    current_value = pol_min

                with ui.card().classes("w-full mb-1 bg-gray-50").tight():
                    exp = ui.expansion(policy["pol_name"], icon="info").classes("w-full font-bold")
                    exp.props('header-class="text-primary"')
                    with exp:
                        ui.label(pol_expls.get(pol_tag, policy["pol_name"])) \
                          .classes("text-base text-orange-600 font-bold")

                    with ui.row().classes("w-full items-center gap-4"):
                        ui.label(f"{pol_min}").classes("text-base text-orange-700 w-12 text-right")
                        with ui.element("div").classes("flex-grow"):
                            slider = ui.slider(
                                min=pol_min, max=pol_max, value=current_value,
                                step=(pol_max - pol_min) / 10,
                                on_change=handle_slider_change,
                            ).props("label-always").classes("w-full")
                            slider_metadata[slider.id] = {
                                "game_id": game_id, "current_round": current_round,
                                "pol_id": pol_id, "pol_tag": pol_tag,
                                "region_tag": region, "ministry": role,
                            }
                        ui.label().bind_text_from(slider, "value") \
                          .classes("text-lg font-mono text-green-600 w-20")
                        ui.label(f"{pol_max}").classes("text-base text-orange-600 w-12")

    slider_section()

    # Auto-refresh until the region submits (Future locks in proposals)
    def _poll_region_submitted():
        if maindb.is_region_submitted(game_id, current_round, region):
            slider_section.refresh()
            _poll_timer.cancel()

    _poll_timer = ui.timer(5.0, _poll_region_submitted)


def _render_budget(token: str, game_id: str, current_round: int,
                   region: str, role: str, lang: str, langx: int, display_region: str):
    """Budget submission card for the Future ministry."""
    round_ranges = [luf_original.now_2040, luf_original.to_2060, luf_original.to_2100]
    rrange = round_ranges[min(current_round - 1, 2)][langx]
    grand_total  = [0.0]
    poll_paused  = [False]   # True while confirm dialog is open

    try:
        budg = maindb.get_budget(
            "START" if current_round == 1 else game_id,
            0 if current_round == 1 else current_round - 1,
            region, "bud",
        )
        bud = float(budg[0]) if budg else 999.0
    except Exception:
        bud = 999.0

    @ui.refreshable
    def budget_section():
        # Check game state from DB (num_rounds may differ from session current_round)
        try:
            with maindb.get_db() as _c:
                _g = _c.execute(
                    "SELECT state, num_rounds FROM games WHERE game_id=?", (game_id,)
                ).fetchone()
            game_complete = _g and _g["state"] == "complete"
            num_rounds_db = _g["num_rounds"] if _g else 3
        except Exception:
            game_complete, num_rounds_db = False, 3

        # After final model run – nothing more to show on the budget card
        if game_complete or current_round > num_rounds_db:
            return

        if maindb.is_region_submitted(game_id, current_round, region):
            with ui.card().classes("w-full p-4 bg-green-50"):
                ui.label("[Card D – Proposals submitted / check results]").classes("text-xs text-gray-400 italic")
                ui.label(luf_original.all_investment_proposals_for_your_region_have_been_submitted[langx]) \
                  .classes("text-xl font-bold text-green-700 mb-3")
                _check_results_btn(token, game_id, current_round, region)
            return

        with ui.card().classes("w-full p-2 gap-2"):
            ui.label("[Card D – Budget proposals]").classes("text-xs text-gray-400 italic")
            ui.label(f"{luf_original.budget_considerations[langx]}, {display_region}") \
              .classes("text-2xl font-bold")
            ui.label(luf_original.bud_title_tx_str[langx] + str(current_round) + rrange) \
              .classes("text-blue-600 text-lg")
            ui.markdown(luf_original.every_10_sec[langx]) \
              .classes("text-black dark:text-white")

#            ui.button(
#                luf.check_your_colleagues_investment_proposals[langx],
#                icon="refresh",
#                on_click=lambda: _load_proposals(),
#            ).props("color=primary")

            summary_col   = ui.column().classes("w-full")
            proposals_col = ui.column().classes("w-full gap-2")

            def _submit_proposals():
                try:
                    allowed = maindb.get_accept_decisions(game_id, current_round, region)
                except Exception:
                    allowed = 1
                if allowed == 0:
                    ui.notify(luf_original.ooops_GM_changed_mind[langx],
                              type="negative", position="center")
                    return
                with ui.dialog() as confirm_dlg, ui.card():
                    ui.label(luf_original.confirm_submission[langx]).classes("text-xl font-bold mb-2")
                    ui.label(luf_original.are_you_sure_you_want_to_submit_all_investment_proposals[langx])
                    ui.label(f"{luf_original.budget2[langx]}: {bud:.1f}")
                    ui.label(f"{luf_original.total2[langx]}: {grand_total[0]:.1f}")
                    ui.label(luf_original.once_submitted[langx]).classes("text-orange-600 mt-2")
                    with ui.row().classes("w-full justify-end gap-2 mt-4"):
                        def _cancel():
                            poll_paused[0] = False
                            confirm_dlg.close()
                        ui.button(luf_original.cancel_btn[langx],
                                  on_click=_cancel).props("flat color=secondary")
                        def _do_submit():
                            try:
                                maindb.mark_region_submitted(game_id, current_round, region)
                                db_update(token, submitted=1)
                            except Exception:
                                db_update(token, submitted=1)
                            poll_paused[0] = False
                            confirm_dlg.close()
                            budget_section.refresh()
                        ui.button(luf_original.yes_submit[langx], on_click=_do_submit).props("color=primary")
                poll_paused[0] = True
                confirm_dlg.open()

            def _load_proposals():
                proposals_col.clear()
                summary_col.clear()
                grand_total[0] = 0.0

                # Who has joined this region? (toy.py DB)
                player_session = db_get(token)
                gm_tok = player_session.get("game_token", "") if player_session else ""
                region_players = [p for p in db_get_players(gm_tok) if p["region"] == region]
                joined_minis   = {p["role"] for p in region_players}
                non_fut_minis  = [m for m in MINISTRIES if m != "Future"]

                # Policy decisions from maindb (safe – only existing rows returned)
                try:
                    budget_data = maindb.get_budget_by_ministry_and_policy(
                        game_id, current_round, region)
                except Exception as e:
                    budget_data = {}
                    with proposals_col:
                        ui.label(f"Could not load proposals: {e}").classes("text-orange-400 italic")

                # Direct check for decisions (independent of budget JOIN)
                def _has_decisions(ministry):
                    try:
                        with maindb.get_db() as c:
                            return c.execute(
                                "SELECT 1 FROM policy_decisions "
                                "WHERE game_id=? AND round=? AND region_tag=? AND ministry=? LIMIT 1",
                                (game_id, current_round, region, ministry),
                            ).fetchone() is not None
                    except Exception:
                        return ministry in budget_data

                def _get_decision_rows(ministry):
                    try:
                        with maindb.get_db() as c:
                            rows = c.execute(
                                """SELECT pd.pol_tag, p.pol_name, pd.value
                                   FROM policy_decisions pd
                                   JOIN policies p ON p.pol_tag = pd.pol_tag
                                   WHERE pd.game_id=? AND pd.round=? AND pd.region_tag=? AND pd.ministry=?
                                   ORDER BY p.pol_name""",
                                (game_id, current_round, region, ministry),
                            ).fetchall()
                        return [{"policy": r["pol_name"], "value": f"{r['value']:.1f}", "amount": "–"}
                                for r in rows]
                    except Exception:
                        return []

                with proposals_col:
                    for m in non_fut_minis:
                        if m not in joined_minis:
                            with ui.card().classes("w-full p-3 bg-gray-50"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("person_off").classes("text-gray-400")
                                    ui.label(f"{m}  –  not joined yet").classes("text-gray-400 italic")
                            continue
                        if m in budget_data:
                            # Full data: decisions + amounts
                            min_info  = budget_data[m]
                            min_total = min_info["total"]
                            grand_total[0] += min_total
                            with ui.card().classes("w-full p-3"):
                                with ui.row().classes("items-center gap-2 mb-2"):
                                    ui.icon("account_balance").classes("text-primary")
                                    ui.label(f"{m}  –  {luf_original.total[langx]}: {min_total:.1f}").classes("font-semibold")
                                ui.table(
                                    columns=[
                                        {"name": "policy", "label": luf_original.policy[langx],    "field": "policy", "align": "left"},
                                        {"name": "value",  "label": luf_original.pct_value[langx], "field": "value",  "align": "right"},
                                        {"name": "amount", "label": luf_original.amount2[langx],   "field": "amount", "align": "right"},
                                    ],
                                    rows=[{"policy": p["name"], "value": f"{p['value']:.1f}", "amount": f"{p['amount']:.1f}"}
                                          for p in min_info["policies"]],
                                    row_key="policy",
                                ).props("dense flat").classes("w-full")
                        elif _has_decisions(m):
                            # Decisions saved but budget amounts not yet computed
                            dec_rows = _get_decision_rows(m)
                            with ui.card().classes("w-full p-3"):
                                with ui.row().classes("items-center gap-2 mb-2"):
                                    ui.icon("account_balance").classes("text-green-600")
                                    decisions_submitted = luf_original.decisions_submitted[langx]
                                    ui.label(f"{m} {decisions_submitted}").classes("font-semibold text-green-700")
                                ui.table(
                                    columns=[
                                        {"name": "policy", "label": luf_original.policy[langx], "field": "policy", "align": "left"},
                                        {"name": "value",  "label": luf_original.pct_value[langx], "field": "value", "align": "right"},
                                    ],
                                    rows=dec_rows,
                                    row_key="policy",
                                ).classes("w-full")
                        else:
                            # Joined but sliders not yet moved
                            with ui.card().classes("w-full p-3 bg-amber-50"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("pending").classes("text-orange-400")
                                    no_slider_decisions_yet = luf_original.no_slider_decisions_yet[langx]
                                    ui.label(f"{m} {no_slider_decisions_yet}").classes("text-orange-400 italic")

                with summary_col:
                    all_joined = len(joined_minis & set(non_fut_minis)) == len(non_fut_minis)
                    if not all_joined:
                        with ui.card().classes("w-full bg-gray-50 p-1"):
                            missing_names = ", ".join(m for m in non_fut_minis if m not in joined_minis)
                            these_ministries_havent_yet_looked_at_their_graphs = luf_original.these_ministries_havent_yet_looked_at_their_graphs[langx]
                            ui.label(f"{these_ministries_havent_yet_looked_at_their_graphs} {missing_names}") \
                              .classes("text-red-600 font-bold")
                    # Warn if any joined ministry hasn't clicked "Check if results are ready"
                    not_checked = [
                        p["role"] for p in region_players
                        if p["role"] in joined_minis
                        and p.get("current_round", 1) < current_round
                    ]
                    if not_checked:
                        with ui.card().classes("w-full bg-gray-50 p-1"):
                            these_ministries_havent_yet_looked_at_their_graphs = luf_original.these_ministries_havent_yet_looked_at_their_graphs[langx]
                            ui.label(these_ministries_havent_yet_looked_at_their_graphs).classes("text-red-400 font-bold mb-1")
                            ui.label(", ".join(not_checked)).classes("text-red-600 font-bold")
                    if all_joined and not not_checked and grand_total[0] <= bud:
                        with ui.card().classes("w-full bg-green-50 p-1"):
                            ui.label(
                                f"{luf_original.your_budget[langx]} {bud:.1f}  –  "
                                f"{luf_original.all_investment_plans_summed_up_for_your_region[langx]} {grand_total[0]:.1f}"
                            ).classes("text-xl font-bold text-green-700 mb-1")
                            ui.button(luf_original.submit_plans2[langx], icon="send",
                                      on_click=_submit_proposals).props("color=green")
                    elif all_joined and not not_checked and grand_total[0] > bud:
                        with ui.card().classes("w-full bg-orange-50 p-1"):
                            ui.label(
                                f"{luf_original.plans[langx]}{grand_total[0]:.1f}"
                                f"{luf_original.plans2[langx]}{bud:.1f}{luf_original.plans3[langx]}"
                            ).classes("text-orange-700 text-lg font-bold")

            _load_proposals()

    budget_section()

    # Auto-refresh proposals so Future always sees current slider values
    def _poll_proposals():
        if maindb.is_region_submitted(game_id, current_round, region):
            _budget_poll.cancel()
        elif not poll_paused[0]:
            budget_section.refresh()

    _budget_poll = ui.timer(10.0, _poll_proposals)


@ui.page("/dashboard")
def dashboard(token: str):
    session = db_get(token)
    if not session:
        ui.label(luf_original.session_not_found__redirecting[langx]).classes("text-red-500 m-8")
        ui.timer(1.5, lambda: ui.navigate.to("/"), once=True)
        return

    create_header(token)
    db_heartbeat(token)
    ui.timer(30, lambda: db_heartbeat(token))

    username = session["username"]
    role     = session["role"]
    lang     = session.get("lang", "en") or "en"
    langx    = 0 if lang == "en" else 1
    region   = session.get("region", "")

    # Game context from GM session
    gm_session    = db_get(session.get("game_token", "")) if session.get("game_token") else None
    game_id       = gm_session.get("game_id", "") if gm_session else ""
    current_round = gm_session.get("current_round", 1) if gm_session else 1
    num_rounds    = gm_session.get("num_rounds", 3) if gm_session else 3

    # If the player refreshed their browser after the GM advanced, their own
    # session current_round may lag behind.  Sync it now so that future-dashboard
    # not_checked detection and _check_results_btn both work correctly.
    if session.get("current_round", 1) < current_round:
        db_update(token, current_round=current_round, submitted=0)

    abbr_to_name   = dict(zip(REGION_ABBR, REGIONS))
    display_region = abbr_to_name.get(region, region)

    with ui.column().classes("w-full max-w-6xl mx-auto p-8 gap-6"):
        # ── Title ─────────────────────────────────────────────────────────────
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-1"):
                ui.label(f"{username}").classes("text-3xl font-bold")
                ui.label(f"{display_region} – {role}").classes("text-2xl text-orange-600")
                game_ug = luf_original.game[langx]
                runde_ug = luf_original.runde[langx]
                ui.label(
                    f"{game_ug}: {game_id}  |  {runde_ug}: {current_round} / {num_rounds}"
                ).classes("text-lg text-orange-400 font-mono")

        ui.separator()

        if role in MINISTRIES and role != "Future":
            _render_graphs(game_id, region, role, lang, langx, current_round)
            _render_sliders(token, game_id, current_round, region, role, lang, langx, display_region)
        elif role == "Future":
            _render_graphs(game_id, region, role, lang, langx, current_round)
            _render_budget(token, game_id, current_round, region, role, lang, langx, display_region)
        else:
            ui.label(f"Role '{role}' has no dashboard yet.").classes("text-gray-400 italic")


# ============================================================================
# About
# ============================================================================

@ui.page('/about')
def about_page(token: str = ""):
    create_header(token)
    if token:
        db_heartbeat(token)
    
    lang = get_lang()
    langx = 0 if lang == "en" else 1
     
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6 items-center'):
        # Centered markdown content
        ui.markdown(luf_original.about_md[langx]).classes('w-full')
        # Back button
        ui.button(luf_original.btn_back[langx], 
                 on_click=lambda: ui.navigate.back(),
                 icon='arrow_back').classes('mt-4')
        
# ============================================================================
# Legal
# ============================================================================

@ui.page('/legal')
def legal_page(token: str = ""):
    create_header(token)
    if token:
        db_heartbeat(token)
     
    lang = get_lang()
    langx = 0 if lang == "en" else 1

    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6 items-center'):
        # Centered markdown content
        ui.markdown(luf_original.legal_md[langx]).classes('w-full')
        # Back button
        ui.button(luf_original.btn_back[langx], 
                 on_click=lambda: ui.navigate.back(),
                 icon='arrow_back').classes('mt-4')


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ in {"__main__", "__mp_main__"}:
    init_db()
    ui.run(
        title="SimFuture",
        storage_secret="toy-secret",
        port=8899,
        reload=False,
        show=True,
    )
