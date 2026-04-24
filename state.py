"""
state.py  –  Session & preference management

Philosophy
----------
- BEFORE sign-in  : lang + dark mode live in app.storage.user (cookie-based,
                    browser-wide).  Fine for prefs; harmless if tabs share it.
- AFTER  sign-in  : DB is the single source of truth.  Every page receives a
                    `token` via URL param (?token=...) and looks up its own
                    identity from DB.  Tabs are isolated because each tab has
                    its own URL.
- Crash recovery  : DB stores `last_page` per token.  On sign-in, if a live
                    session already exists the user is redirected there.

DB table required (add to database.py)
---------------------------------------
    CREATE TABLE IF NOT EXISTS sessions (
        token      TEXT PRIMARY KEY,
        username   TEXT,
        game_id    TEXT,
        role       TEXT,   -- 'gm' | 'Poverty' | 'Inequality' | 'Empowerment' |
                           --  'Food' | 'Energy' | 'Future'
        ministry   TEXT,
        region_tag TEXT,
        lang       TEXT    DEFAULT 'en',
        dark       INTEGER DEFAULT 0,
        last_page  TEXT    DEFAULT '/'
    );

"""

import secrets
from nicegui import ui, app

# ── import your database module here ──────────────────────────────────────────
import database as db

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_LANG = 'en'
DEFAULT_DARK = False
ROLES = {'GM', 'Poverty', 'Inequality', 'Empowerment', 'Food', 'Energy', 'Future'}


# ==============================================================================
# PRE-LOGIN  –  browser-local prefs  (app.storage.user)
# ==============================================================================

def get_lang() -> str:
    return app.storage.user.get('lang', DEFAULT_LANG)

def get_dark() -> bool:
    return bool(app.storage.user.get('dark', DEFAULT_DARK))

def set_lang(lang: str):
    app.storage.user['lang'] = lang

def set_dark(dark: bool):
    app.storage.user['dark'] = dark


# ==============================================================================
# TOKEN  –  one per browser session, created on first visit
# ==============================================================================

def get_or_create_token() -> str:
    """
    Returns the browser-wide token stored in app.storage.user.
    Created once; survives page reloads; unique per browser cookie.
    In production (one user per device) this is also unique per user.
    For multi-tab testing use Firefox containers or separate browser profiles.
    """
    if 'token' not in app.storage.user:
        app.storage.user['token'] = secrets.token_urlsafe(16)
    return app.storage.user['token']


# ==============================================================================
# POST-LOGIN  –  DB-backed session
# ==============================================================================

def get_session(token: str) -> dict | None:
    """Return the session row from DB, or None if not signed in."""
    return db.get_session(token)          # implement in database.py


def sign_in(token: str, username: str, game_id: str,
            role: str, ministry: str, region_tag: str) -> str:
    """
    Called after a player/GM selects their identity on the login page.
    Merges current browser prefs into the new DB session.
    Returns the token (same one passed in, for convenience).
    """
    if role not in ROLES:
        raise ValueError(f'Unknown role: {role}')
    db.create_session(
        token=token,
        username=username,
        game_id=game_id,
        role=role,
        ministry=ministry,
        region_tag=region_tag,
        lang=get_lang(),
        dark=int(get_dark()),
    )
    return token


def resume_or_sign_in(token: str) -> str | None:
    """
    If a live session exists for this token, return the last_page so the
    caller can redirect there (crash recovery).
    Returns None if no session exists (user must sign in fresh).
    """
    session = get_session(token)
    if session:
        # Sync browser prefs from DB so pre-login pages look right too
        set_lang(session['lang'])
        set_dark(bool(session['dark']))
        return session['last_page']
    return None


def sign_out(token: str):
    """Clear DB session; browser prefs are kept."""
    db.delete_session(token)            # implement in database.py


# ==============================================================================
# PER-PAGE  –  helpers called at the top of every @ui.page
# ==============================================================================

def require_role(token: str, *roles: str) -> dict | None:
    """
    Auth guard.  Call at the top of every protected page:

        session = state.require_role(token, 'gm')
        if not session:
            return

    Returns the session dict on success, None + navigates to / on failure.
    """
    session = get_session(token)
    if not session or session['role'] not in roles:
        ui.navigate.to('/')
        return None
    return session


def save_last_page(token: str, path: str):
    """
    Call at the top of every protected page so crash recovery works:

        state.save_last_page(token, '/gm/board')
    """
    db.update_session(token, last_page=path)   # implement in database.py


def update_prefs(token: str, lang: str = None, dark: bool = None):
    """Update lang/dark in both browser storage and DB simultaneously."""
    updates = {}
    if lang is not None:
        set_lang(lang)
        updates['lang'] = lang
    if dark is not None:
        set_dark(dark)
        updates['dark'] = int(dark)
    if updates:
        db.update_session(token, **updates)


# ==============================================================================
# HEADER  –  shared UI component, works pre- and post-login
# ==============================================================================

def create_header(token: str | None = None):
    """
    Render the app header with dark-mode toggle and language selector.

    Pass token=None on public pages (/about, /legal, /) where the user
    is not yet signed in; changes will only update browser storage.
    Pass token=<str> on protected pages so changes are also saved to DB.

    Usage:
        with ui.header():
            state.create_header(token)   # protected page
            state.create_header()        # public page
    """
    dark_mode = ui.dark_mode(value=get_dark())

    def _set_dark(value: bool):
        dark_mode.set_value(value)
        if token:
            update_prefs(token, dark=value)
        else:
            set_dark(value)

    def _set_lang(lang: str):
        if token:
            update_prefs(token, lang=lang)
        else:
            set_lang(lang)
        ui.navigate.reload()

    ui.space()
    ui.button(icon='dark_mode',
              on_click=lambda: _set_dark(not dark_mode.value)
              ).props('flat round')

    with ui.button_group().props('flat'):
        ui.button('EN', on_click=lambda: _set_lang('en')).props('flat')
        ui.button('DE', on_click=lambda: _set_lang('de')).props('flat')


# ==============================================================================
# DATABASE STUBS  –  paste these into database.py
# ==============================================================================
#
# CREATE TABLE IF NOT EXISTS sessions (
#     token      TEXT PRIMARY KEY,
#     username   TEXT,
#     game_id    TEXT,
#     role       TEXT,
#     ministry   TEXT,
#     region_tag TEXT,
#     lang       TEXT    DEFAULT 'en',
#     dark       INTEGER DEFAULT 0,
#     last_page  TEXT    DEFAULT '/'
# );
#
# def get_session(token: str) -> dict | None:
#     with get_db() as conn:
#         row = conn.execute(
#             'SELECT * FROM sessions WHERE token = ?', (token,)
#         ).fetchone()
#         return dict(row) if row else None
#
# def create_session(token, username, game_id, role, ministry,
#                    region_tag, lang, dark):
#     with get_db() as conn:
#         conn.execute('''
#             INSERT OR REPLACE INTO sessions
#             (token, username, game_id, role, ministry, region_tag, lang, dark)
#             VALUES (?,?,?,?,?,?,?,?)
#         ''', (token, username, game_id, role, ministry, region_tag, lang, dark))
#         conn.commit()
#
# def update_session(token: str, **kwargs):
#     if not kwargs:
#         return
#     cols = ', '.join(f'{k} = ?' for k in kwargs)
#     with get_db() as conn:
#         conn.execute(
#             f'UPDATE sessions SET {cols} WHERE token = ?',
#             (*kwargs.values(), token)
#         )
#         conn.commit()
#
# def delete_session(token: str):
#     with get_db() as conn:
#         conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
#         conn.commit()


# ==============================================================================
# HOW TO USE IN main.py
# ==============================================================================
#
# PUBLIC PAGE EXAMPLE  (/, /about, /legal)
# -----------------------------------------
@ui.page('/')
def home():
    token = get_or_create_token()
    last = resume_or_sign_in(token)
    if last and last != '/':
        ui.navigate.to(f'{last}?token={token}')
        return
    with ui.header():
        ui.label('MyApp')
        create_header()           # no token → browser-only prefs
    # ... login UI ...
    def do_login(username, game_id, role, ministry, region_tag):
        sign_in(token, username, game_id, role, ministry, region_tag)
        ui.navigate.to(f'/player/dashboard?token={token}')


# PROTECTED PAGE EXAMPLE  (/player/dashboard)
# --------------------------------------------
@ui.page('/player/dashboard')
def player_dashboard(token: str):
    session = require_role(token, 'Poverty', 'Inequality', 'Empowerment',
                                        'Food', 'Energy', 'Future')
    if not session:
        return
    save_last_page(token, '/player/dashboard')
    with ui.header():
        ui.label(session['username'])
        create_header(token)      # token → prefs saved to DB too
    langx = 0 if session['lang'] == 'en' else 1
    ministry = session['ministry']
    region_tag = session['region_tag']
    game_id = session['game_id']
#     # ... rest of dashboard ...


# GM PAGE EXAMPLE  (/gm/board)
# ----------------------------
@ui.page('/gm/board')
def gm_board(token: str):
    session = require_role(token, 'gm')
    if not session:
        return
    save_last_page(token, '/gm/board')
    # ...
# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    # Initialize database
#    db.init_database()
#    db.load_policies_data()
#    db.load_plot_variables_data()
    
    # Run NiceGUI app
    ui.run(
        title='SF_stage',
        dark=None,  # Auto-detect dark mode
        reload=False,
        show=True,
        storage_secret='freitag',
        port=8888  # Use port 8888 to avoid Windows permission issues
    )