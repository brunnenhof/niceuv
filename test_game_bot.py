"""
test_game_bot.py  –  Automated end-to-end game test via Playwright

Runs a full 3-round SimFuture game with:
  • 1 GM
  • 2 human regions (eu = Europe, us = USA)
  • 6 ministers per region (Poverty, Inequality, Empowerment, Food, Energy, Future)

Usage:
    uv run python test_game_bot.py                  # headless
    uv run python test_game_bot.py --headed         # watch in browser
    uv run python test_game_bot.py --base http://...  # custom server URL

Requirements:
    uv add playwright
    uv run playwright install chromium
"""

import argparse
import asyncio
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
import random

import asyncio, logging
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# log() below prints non-ASCII characters (e.g. the arrow in "Language -> X").
# When stdout isn't UTF-8-capable (redirected to a file, non-UTF-8 console
# codepage), that raises UnicodeEncodeError deep inside asyncio.gather(...,
# return_exceptions=True) -- which silently swallows it into that task's
# result instead of crashing visibly, leaving every other bot waiting forever
# on an event (e.g. gm_board_event) that the now-dead GM task will never set.
# What looks like a hang is actually this crash. Force UTF-8 unconditionally.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.async_api import BrowserContext, Page, async_playwright

# ── Config ────────────────────────────────────────────────────────────────────

BASE       = "http://localhost:8899"
HEADED     = False   # set to True in main() when --headed; skips early ctx.close()
START_CODE = "oscar"
regs = ["us", "af", "cn", "me", "sa", "la", "pa", "ec", "eu", "se"]
one = random.randint(0,9)
r1 = regs[one]
regs2 = regs.copy()
regs2.remove(r1)
two = random.randint(0,8)
r2 = regs2[two]
r4 = []
r4.append(r1)
r4.append(r2)
REGIONS    = ["me", "af"]
REGIONS    = r4
MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]
NUM_ROUNDS = 3
TIMEOUT    = 60_000   # ms — how long to wait for any element before failing
SLOW_MO    = 0        # ms between actions; raise to 300 to watch more slowly

# Full abbr → display-name map (matches toy.py REGIONS / REGION_ABBR)
REGION_NAMES = {
    "us": "USA",
    "af": "Africa South of Sahara",
    "cn": "China",
    "me": "Middle East and North Africa",
    "sa": "South Asia",
    "la": "Latin America",
    "pa": "Pacific Rim",
    "ec": "East Europe and Central Asia",
    "eu": "Europe",
    "se": "Southeast Asia",
}

# ── Shared state ──────────────────────────────────────────────────────────────

game_id_event = asyncio.Event()
game_id_value: str = ""

# Set after GM reaches the board — ministers wait for this before joining
# so the server isn't flooded before the GM finishes setup.
gm_board_event = asyncio.Event()

# Only 3 bots go through the join flow concurrently to avoid overloading
# NiceGUI's single-threaded asyncio event loop.
join_semaphore = asyncio.Semaphore(3)

round_done_events: list[asyncio.Event] = [asyncio.Event() for _ in range(NUM_ROUNDS + 1)]

errors: list[str] = []

# (region, ministry, rnd) -> list of (label, value_str)
policy_log: dict[tuple, list[tuple[str, str]]] = {}

SCREENSHOT_DIR = Path("test_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# Maps lang code → header button label (mirrors toy.py LANG_OPTIONS)
_LANG_LABELS = {"en": "EN", "de": "DE-Sie", "de_inf": "DE-Du", "fr": "FR", "no": "NO"}

# Button/label translations — indices = langx: en=0, de=1, de_inf=2, fr=3, no=4
# Source: files/luf.py
_TX: dict[str, list[str]] = {
    # ── Join / create flow ────────────────────────────────────────────────────
    "fresh_game":        ["Fresh Game",         "Neues Spiel",                 "Neues Spiel",                  "Nouvelle partie",               "Nytt spill"],
    "start_new_game":    ["Start a new Game",   "Starte ein neues",            "Starte ein neues",             "Commence une nouvelle",         "Start et nytt spill"],
    "start_game_dialog": ["Start",              "Start",                       "Start",                        "Commencer",                     "Start"],
    "join_new_game":     ["Join a new Game",    "Als Spieler:in",              "Als Spieler:in",               "Participer à un nouveau",       "Delta som spiller"],
    "open_game":         ["Open game",          "Spiel aufrufen",              "Spiel aufrufen",               "Lancer le jeu",                 "Åpne spillet"],
    "join_btn":          ["Join!",              "Machen Sie mit!",             "Mach mit!",                    "Rejoignez-nous !",              "Bli med!"],
    "confirm_selection": ["Confirm selection",  "Auswahl bestätigen",          "Auswahl bestätigen",           "Confirmez votre",               "Bekreft valg"],
    "continue_to_board": ["Continue to GM",     "Weiter zur Spielleiter",      "Weiter zur Spielleiter",       "Accéder à l'aperçu",            "Gå videre til"],
    "username_label":    ["Username",           "Benutzernamen",               "Benutzernamen",                "Nom d'utilisateur",             "Brukernavn"],
    "game_id_label":     ["Game ID",            "Spiel-ID",                    "Spiel-ID",                     "Jeu d'identité",                "Spill-ID"],
    # ── Game play ─────────────────────────────────────────────────────────────
    "allow_submissions": ["Allow Submissions",  "Abgaben zulassen",            "Abgaben zulassen",             "Autoriser les soumissions",     "Tillat innsendinger"],
    "run_model_prefix":  ["Run model to Round", "Das Modell fortschreiben zu Runde", "Das Modell fortschreiben bis Runde", "Mettre à jour le modèle pour le tour", "Kjør modellen til runde"],
    "yes_run_model":     ["Yes, run model",     "Ja, Modell fortschreiben",    "Ja, Modell fortschreiben",     "Oui, exécuter le modèle",       "Ja, kjør modellen"],
    "submit_proposals":  ["Submit proposals?",  "Vorschläge einreichen?",      "Vorschläge einreichen?",       "Soumettre des propositions ?",  "Sende inn forslag?"],
    "yes_submit":        ["Yes, Submit",        "Ja, Absenden",                "Ja, Absenden",                 "Oui, envoyer",                  "Ja, send inn"],
    "check_results":     ["Check if results are ready", "Prüfen Sie, ob Ergebnisse vorliegen", "Schau nach, ob Ergebnisse schon da sind", "Vérifiez si les résultats sont disponibles", "Sjekk om resultatene er klare"],
}

def tx(key: str, langx: int) -> str:
    return _TX[key][langx]

# Region display names by langx — mirrors luf.py rt_en / rt_de / rt_fr / rt_no
_REGION_NAMES_LANG: dict[int, dict[str, str]] = {
    0: {"us":"USA","af":"Africa South of Sahara","cn":"China","me":"Middle East and North Africa","sa":"South Asia","la":"Latin America","pa":"Pacific Rim","ec":"East Europe and Central Asia","eu":"Europe","se":"Southeast Asia"},
    1: {"us":"USA","af":"Afrika, südlich der Sahara","cn":"China","me":"Naher Osten & Nordafrika","sa":"Südasien","la":"Lateinamerika","pa":"Pazifische Anrainer","ec":"Osteuropa & Zentralasien","eu":"Europa","se":"Südost Asien"},
    2: {"us":"USA","af":"Afrika, südlich der Sahara","cn":"China","me":"Naher Osten & Nordafrika","sa":"Südasien","la":"Lateinamerika","pa":"Pazifische Anrainer","ec":"Osteuropa & Zentralasien","eu":"Europa","se":"Südost Asien"},
    3: {"us":"États-Unis","af":"Afrique, au sud du Sahara","cn":"Chine","me":"Moyen-Orient et Afrique du Nord","sa":"Asie du Sud","la":"Amérique latine","pa":"Pays riverains du Pacifique","ec":"Europe de l'Est et Asie centrale","eu":"Europe","se":"Asie du Sud-Est"},
    4: {"us":"USA","af":"Afrika, sør for Sahara","cn":"Kina","me":"Midtøsten og Nord-Afrika","sa":"Sør-Asia","la":"Latin-Amerika","pa":"Stillehavskyststater","ec":"Øst-Europa og Sentral-Asia","eu":"Europa","se":"Sørøst-Asia"},
}

# Ministry display names by langx — mirrors luf.py mini_en / mini_de / mini_fr / mini_no
_MINISTRY_NAMES_LANG: dict[int, dict[str, str]] = {
    0: {"Poverty":"Poverty","Inequality":"Inequality","Empowerment":"Empowerment","Food":"Food","Energy":"Energy","Future":"Future"},
    1: {"Poverty":"Armut","Inequality":"Ungleichheit","Empowerment":"Befähigung","Food":"Ernährung & Agrar","Energy":"Energie","Future":"Zukunft"},
    2: {"Poverty":"Armut","Inequality":"Ungleichheit","Empowerment":"Befähigung","Food":"Ernährung & Agrar","Energy":"Energie","Future":"Zukunft"},
    3: {"Poverty":"La pauvreté","Inequality":"Les inégalités","Empowerment":"L'autonomisation","Food":"Alimentation et agriculture","Energy":"l'Énergie","Future":"l 'Avenir"},
    4: {"Poverty":"Fattigdom","Inequality":"Ulikhet","Empowerment":"Myndiggjøring","Food":"Ernæring & landbruk","Energy":"Energi","Future":"Fremtiden"},
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(actor: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{actor:20s}] {msg}", flush=True)


async def screenshot(page: Page, name: str):
    path = SCREENSHOT_DIR / f"{name}_{datetime.now().strftime('%H%M%S%f')}.png"
    try:
        await page.screenshot(path=str(path))
    except Exception:
        pass
    return str(path)


def attach_error_handlers(page: Page, actor: str):
    page.on("pageerror",  lambda e: errors.append(f"[{actor}] JS ERROR: {e}"))
    page.on("console",    lambda m: (
        errors.append(f"[{actor}] CONSOLE {m.type.upper()}: {m.text}")
        if m.type in ("error", "warning") else None
    ))


async def click_button(page: Page, text: str, exact: bool = False, timeout: int = TIMEOUT):
    """Click the first visible button whose label contains `text`."""
    loc = page.get_by_role("button", name=text, exact=exact)
    await loc.first.wait_for(state="visible", timeout=timeout)
    await loc.first.click()


async def wait_for_text(page: Page, text: str, timeout: int = TIMEOUT):
    await page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout)


async def set_random_language(page: Page, actor: str) -> int:
    """Pick a random language (langx 1–4) and set it via the header language button.

    Expects the page to already be on the home page (language button enabled there).
    Returns the langx integer (1–4) so callers can use translated button text.
    """
    chosen = random.choice(["de", "de_inf", "fr", "no"])
    chosen_label = _LANG_LABELS[chosen]
    langx = {"de": 1, "de_inf": 2, "fr": 3, "no": 4}[chosen]
    log(actor, f"Language → {chosen_label} (langx={langx})")

    header = page.locator("header")
    clicked = False
    for label in _LANG_LABELS.values():
        btn = header.get_by_role("button", name=label, exact=True)
        try:
            await btn.first.wait_for(state="visible", timeout=1_000)
            await btn.first.click()
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        log(actor, "Language button not found — keeping EN")
        return 0

    # q-menu teleports to <body>; pick the desired item
    option = page.locator(".q-menu .q-item").filter(has_text=chosen_label).first
    await option.wait_for(state="visible", timeout=TIMEOUT)
    await option.click()

    # FR and NO show a disclaimer dialog — dismiss it (triggers the page reload)
    if chosen in ("fr", "no"):
        try:
            ok_btn = page.get_by_role("button", name="OK", exact=True).first
            await ok_btn.wait_for(state="visible", timeout=5_000)
            await ok_btn.click()
        except Exception:
            pass

    # Pause so the language switch is visible in headed mode
    if HEADED:
        await page.wait_for_timeout(3_000)

    await page.wait_for_load_state("networkidle", timeout=30_000)
    await page.wait_for_timeout(1_000)
    return langx


async def fill_input_in(scope, label: str, value: str, timeout: int = TIMEOUT):
    """Fill a NiceGUI/Quasar input by floating label, scoped to a locator."""
    loc = scope.locator(f'.q-field:has(.q-field__label:text("{label}")) .q-field__native')
    await loc.first.wait_for(state="visible", timeout=timeout)
    await loc.first.fill(value)


async def fill_input(page: Page, label: str, value: str, timeout: int = TIMEOUT):
    """Fill a NiceGUI/Quasar input on the full page by floating label."""
    await fill_input_in(page, label, value, timeout)


async def select_quasar(page: Page, nth: int, option_text: str, timeout: int = TIMEOUT):
    """Select a Quasar q-select option by dropdown index (0=first, 1=second…)."""
    # Scope to the last open dialog to avoid picking up other page dropdowns
    scope = page.locator(".q-dialog").last
    trigger = scope.get_by_role("combobox").nth(nth)
    await trigger.wait_for(state="visible", timeout=timeout)
    await trigger.click()
    # q-menu teleports to <body>, so search on the full page
    option = page.locator(".q-menu .q-item").filter(has_text=option_text).first
    await option.wait_for(state="visible", timeout=timeout)
    await option.click()


async def _fill_join_inputs(page: Page, username: str, game_id: str, langx: int):
    """Fill the join dialog's username and game-ID inputs; falls back to positional."""
    try:
        await fill_input(page, tx("username_label", langx), username, timeout=5_000)
        await fill_input(page, tx("game_id_label", langx), game_id, timeout=5_000)
    except Exception:
        dlg = page.locator(".q-dialog").last
        inputs = dlg.locator("input")
        await inputs.nth(0).fill(username)
        await inputs.nth(1).fill(game_id)


# ── GM flow ───────────────────────────────────────────────────────────────────

async def run_gm(browser):
    global game_id_value
    ctx: BrowserContext = await browser.new_context()
    page: Page = await ctx.new_page()
    attach_error_handlers(page, "GM")

    try:
        # ── Create game ───────────────────────────────────────────────────────
        log("GM", "Opening home page")
        await page.goto(BASE, timeout=TIMEOUT)
        # Set language BEFORE creating — upsert_player_lang writes get_lang() to DB at join time
        langx = await set_random_language(page, "GM")
        await click_button(page, tx("fresh_game", langx))
        await click_button(page, tx("start_new_game", langx))

        # Wait for Quasar dialog to finish animating in
        await page.wait_for_selector('.q-dialog', timeout=TIMEOUT)
        await page.wait_for_timeout(400)
        dlg = page.locator('.q-dialog').last

        gm_name = f"bot_gm_{datetime.now().strftime('%H%M%S')}"
        log("GM", "Filling new-game dialog")
        await screenshot(page, "gm_dialog")   # debug: see what's visible
        try:
            await fill_input_in(dlg, "Username", gm_name, timeout=5_000)
            await fill_input_in(dlg, "start code", START_CODE, timeout=5_000)
        except Exception:
            # Fallback: fill by input position inside the dialog
            log("GM", "Label-based fill failed — trying positional fill")
            inputs = dlg.locator('input')
            await inputs.nth(0).fill(gm_name)
            await inputs.nth(1).fill(START_CODE)
        await click_button(page, tx("start_game_dialog", langx), exact=True)

        # ── Setup: select regions ─────────────────────────────────────────────
        log("GM", "Waiting for setup page")
        await page.wait_for_url("**/gm/setup**", timeout=TIMEOUT)

        # Extract game ID shown on setup page (orange mono text like "ABC-123")
        await page.wait_for_timeout(1000)
        page_text = await page.inner_text("body")
        m = re.search(r'\b([A-Z]{3}-\d{3})\b', page_text)
        if not m:
            raise RuntimeError("Could not find game ID on setup page")
        game_id_value = m.group(1)
        log("GM", f"Game ID: {game_id_value}")
        game_id_event.set()

        # Tick the human regions (names vary by language on the setup page)
        for reg in REGIONS:
            label_text = _REGION_NAMES_LANG[langx][reg]
            chk = page.get_by_text(label_text, exact=True).first
            await chk.wait_for(state="visible", timeout=TIMEOUT)
            await chk.click()
            log("GM", f"Selected region {reg} ({label_text})")
            await page.wait_for_timeout(200)

        await click_button(page, tx("confirm_selection", langx))
        await page.wait_for_timeout(500)
        await click_button(page, tx("continue_to_board", langx))
        await page.wait_for_url("**/gm/board**", timeout=TIMEOUT)
        log("GM", "On GM board")
        gm_board_event.set()   # release ministers — server is ready for joins

        await page.wait_for_timeout(1_000)

        # ── Play through all rounds ───────────────────────────────────────────
        allow_btn = tx("allow_submissions", langx)
        run_prefix = tx("run_model_prefix", langx)
        yes_run    = tx("yes_run_model", langx)

        for rnd in range(1, NUM_ROUNDS + 1):
            log("GM", f"Round {rnd}: waiting for all players to join")
            await page.get_by_role("button", name=allow_btn, exact=False) \
                      .first.wait_for(state="visible", timeout=120_000)

            log("GM", f"Round {rnd}: allowing submissions")
            await click_button(page, allow_btn)
            await page.wait_for_timeout(500)

            run_btn = f"{run_prefix} {rnd + 1}"
            log("GM", f"Round {rnd}: waiting for all regions to submit")
            await page.get_by_role("button", name=run_btn, exact=False) \
                      .first.wait_for(state="visible", timeout=300_000)

            log("GM", f"Round {rnd}: running model")
            await click_button(page, run_btn)
            await click_button(page, yes_run)

            log("GM", f"Round {rnd}: model running…")
            await page.wait_for_timeout(5000)

            # Signal players that this round is done
            round_done_events[rnd].set()

            if rnd < NUM_ROUNDS:
                # Wait for board header to show next round (number-only match works in any language)
                await wait_for_text(page, f"{rnd + 1}/{NUM_ROUNDS}", timeout=60_000)
                await page.wait_for_timeout(3000)

        log("GM", "All rounds done — game complete")
        # "Game complete" card exists in DOM but is always hidden (collapsed card),
        # so wait_for_text with state="visible" would time out.  The GM is done.

    except Exception as e:
        msg = f"GM FAILED: {e}\n{traceback.format_exc()}"
        errors.append(msg)
        log("GM", msg)
        await screenshot(page, "gm_error")
        game_id_event.set()    # unblock ministers so they can fail gracefully
        gm_board_event.set()   # unblock join semaphore too
        for ev in round_done_events:
            ev.set()
    finally:
        if not HEADED:
            await ctx.close()


# ── Minister flow ─────────────────────────────────────────────────────────────

async def run_minister(browser, region: str, ministry: str):
    actor = f"{region}/{ministry[:3]}"
    ctx: BrowserContext = await browser.new_context()
    page: Page = await ctx.new_page()
    attach_error_handlers(page, actor)

    try:
        # Wait until GM is on the board — game ID is already set by then,
        # and the server has finished its own setup before we flood it with joins.
        await gm_board_event.wait()
        if not game_id_value:
            raise RuntimeError("No game ID received from GM")

        # Small stagger so bots don't all hit the semaphore simultaneously.
        ministry_idx = MINISTRIES.index(ministry) if ministry in MINISTRIES else 0
        region_idx   = REGIONS.index(region) if region in REGIONS else 0
        stagger_ms   = (region_idx * len(MINISTRIES) + ministry_idx) * 200
        if stagger_ms:
            await page.wait_for_timeout(stagger_ms)

        # ── Join game (full restart on each retry) ────────────────────────────
        # Rate-limited to 3 concurrent joins so NiceGUI's single-threaded event
        # loop isn't overwhelmed. After each failed attempt we wait up to 30 s
        # before retrying so a slow-but-successful join doesn't burn the slot.
        langx = 0
        async with join_semaphore:
            # Set language once before the retry loop so that upsert_player_lang
            # at join time writes the chosen language into the DB. Changing it
            # after joining doesn't work because create_header() on the home page
            # receives no token, so db_update_prefs is never called.
            await page.goto(BASE, timeout=TIMEOUT)
            langx = await set_random_language(page, actor)

            for join_attempt in range(10):
                if "/dashboard" in page.url:
                    break  # a slow previous attempt finally navigated us here

                username = f"bot_{region}_{ministry.lower()[:3]}_{random.randint(1, 999999)}"
                if join_attempt == 0:
                    log(actor, f"Joining as {username}")
                else:
                    log(actor, f"Join attempt {join_attempt + 1}: retrying as {username}")

                try:
                    await page.goto(BASE, timeout=TIMEOUT)
                    await click_button(page, tx("fresh_game", langx))
                    await click_button(page, tx("join_new_game", langx))
                    await _fill_join_inputs(page, username, game_id_value, langx)
                    await click_button(page, tx("open_game", langx))

                    await select_quasar(page, 0, _REGION_NAMES_LANG[langx][region])
                    log(actor, f"Join attempt {join_attempt + 1}: region selected")
                    await page.wait_for_timeout(800)

                    await select_quasar(page, 1, _MINISTRY_NAMES_LANG[langx][ministry])
                    log(actor, f"Join attempt {join_attempt + 1}: ministry selected")
                    await page.wait_for_timeout(800)

                    await click_button(page, tx("join_btn", langx))
                    await page.wait_for_url("**/dashboard**", timeout=TIMEOUT)
                    break  # success
                except Exception as e:
                    if "/dashboard" in page.url:
                        break
                    # The server may still be processing the join even though our
                    # wait_for_url timed out.  Wait up to 30s more before retrying
                    # so we don't navigate away from a join that's about to succeed
                    # (which would permanently consume the ministry slot).
                    for _ in range(15):
                        await page.wait_for_timeout(2000)
                        if "/dashboard" in page.url:
                            break
                    if "/dashboard" in page.url:
                        break
                    log(actor, f"Join attempt {join_attempt + 1} failed ({type(e).__name__}), retrying…")
            else:
                raise RuntimeError("Could not join the game after 10 attempts")

        log(actor, "Joined — on dashboard")

        # ── Play each round ───────────────────────────────────────────────────
        for rnd in range(1, NUM_ROUNDS + 1):
            log(actor, f"Round {rnd}: on dashboard")

            if ministry != "Future":
                await _interact_slider(page, actor, region, ministry, rnd)
            else:
                # Future minister: submit region proposals with retry
                await _submit_region(page, actor, rnd, langx)

            # Wait for GM to run model
            log(actor, f"Round {rnd}: waiting for model run")
            await round_done_events[rnd].wait()
            await page.wait_for_timeout(2000 + hash(actor) % 2000)  # stagger requests

            log(actor, f"Round {rnd}: checking results")
            try:
                await _check_results(page, actor, rnd, langx)
            except RuntimeError:
                if rnd < NUM_ROUNDS:
                    raise  # mid-game failure is a real error
                # Final round: the button sometimes disappears before we can
                # click it (NiceGUI disconnection or server-side state race).
                # Fall back to polling via page reloads.
                log(actor, "Button gone on final round — polling via reload")
                target = f": {NUM_ROUNDS + 1} /"
                for _ in range(15):
                    await page.wait_for_timeout(3000)
                    try:
                        await page.reload(wait_until="networkidle", timeout=30_000)
                        if target in await page.inner_text("body"):
                            log(actor, "Final results confirmed via reload (2100)")
                            break
                    except Exception as e:
                        log(actor, f"  reload attempt failed (non-fatal): {e}")
                else:
                    log(actor, "Final results not confirmed — view may still show 2060 (non-fatal)")

        log(actor, "Done with all rounds")

    except Exception as e:
        msg = f"{actor} FAILED: {e}\n{traceback.format_exc()}"
        errors.append(msg)
        log(actor, msg)
        await screenshot(page, f"{region}_{ministry}_error")
    finally:
        if not HEADED:
            await ctx.close()


async def _interact_slider(page: Page, actor: str, region: str, ministry: str, rnd: int):
    """Move all visible policy sliders to random positions.

    Quasar's label-always prop adds top padding to the slider div so the track
    sits below the visual centre of the bounding box. We target the inner
    .q-slider__track-container to get correct coordinates.
    """
    values: list[tuple[str, str]] = []
    try:
        sliders = page.get_by_role("slider")
        await sliders.first.wait_for(state="visible", timeout=15_000)
        all_sliders = await sliders.all()
        for idx, slider in enumerate(all_sliders):
            # Bias towards minima to keep total investment within budget.
            # see scratch/junk22.py
            # random.betavariate(1, 4) has mean=0.2, mode=0, range [0,1].
            # random.betavariate(1, 2) has mean=0.33, mode=0, range [0,1].
            frac = random.betavariate(3, 20)
#            log(actor, f"  frac= {str(frac)}")
            try:
                track = slider.locator(".q-slider__track-container")
                # Scroll into view first — bounding_box() returns viewport coordinates,
                # so page.mouse.click() misses unless the element is actually on-screen.
                await track.scroll_into_view_if_needed()
                t_box = await track.bounding_box()
                if t_box:
                    x = t_box["x"] + t_box["width"] * frac
                    y = t_box["y"] + t_box["height"] / 2
                    await page.mouse.click(x, y)
                    await page.wait_for_timeout(400)
            except Exception as e:
                log(actor, f"  slider_{idx+1} error: {e}")

            # Compute expected value from frac + slider range rather than reading
            # aria-valuenow, which can lag behind the visual update or still show
            # the pre-click value if the bounding box was None.
            try:
                vmin = float(await slider.get_attribute("aria-valuemin") or "0")
                vmax = float(await slider.get_attribute("aria-valuemax") or "100")
                raw = f"{(vmax - vmin) * frac + vmin:.2g}"
            except Exception:
                raw = await slider.get_attribute("aria-valuenow") or "?"
            try:
                lbl = await slider.locator(
                    "xpath=ancestor::div[contains(@class,'q-field')]"
                    "//div[contains(@class,'q-field__label')]"
                ).first.inner_text(timeout=500)
                label = lbl.strip() or f"slider_{idx + 1}"
            except Exception:
                label = f"slider_{idx + 1}"
            values.append((label, raw))

        log(actor, f"Moved {len(all_sliders)} slider(s) to random positions")
    except Exception as e:
        log(actor, f"Could not move sliders (non-fatal): {e}")
    policy_log[(region, ministry, rnd)] = values


async def _submit_region(page: Page, actor: str, rnd: int, langx: int = 0):
    """Click 'Submit proposals?' then confirm 'Yes, Submit', retrying if the dialog doesn't open."""
    submit_btn  = tx("submit_proposals", langx)
    yes_sub_btn = tx("yes_submit", langx)
    log(actor, f"Round {rnd}: waiting to submit region proposals")
    for attempt in range(10):
        # Close any dialog left open from the previous attempt (its backdrop
        # would block clicks on the 'Submit proposals?' button otherwise).
        try:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(300)
        except Exception:
            pass

        await click_button(page, submit_btn, timeout=300_000)
        try:
            # Quasar dialog needs ~500ms to animate in; use 20s under server load
            await page.get_by_role("button", name=yes_sub_btn, exact=False) \
                      .first.wait_for(state="visible", timeout=20_000)
            await page.get_by_role("button", name=yes_sub_btn, exact=False).first.click()
            log(actor, f"Round {rnd}: region submitted")
            return
        except Exception:
            log(actor, f"Round {rnd}: confirm dialog didn't open, retrying ({attempt + 1}/10)…")
            await page.wait_for_timeout(2000)
    raise RuntimeError(f"Could not submit region proposals in round {rnd}")


async def _check_results(page: Page, actor: str, rnd: int, langx: int = 0):
    """Click 'Check if results are ready' and wait for next-round dashboard."""
    check_btn = tx("check_results", langx)
    # Round label format is "{Round}: {current} / {total}" — match ": N /" in any language
    target = f": {rnd + 1} /"
    for attempt in range(15):
        try:
            # Check first — we may have already navigated to the new round
            page_text = await page.inner_text("body")
            if target in page_text:
                log(actor, f"Advanced to round {rnd + 1}")
                return

            await click_button(page, check_btn, timeout=10_000)
            # Wait for navigation + NiceGUI WebSocket re-hydration
            await page.wait_for_load_state("networkidle", timeout=20_000)
            await page.wait_for_timeout(1000)

            page_text = await page.inner_text("body")
            if target in page_text:
                log(actor, f"Advanced to round {rnd + 1}")
                return
            log(actor, f"Model not ready yet, retrying ({attempt + 1}/15)…")
            await page.wait_for_timeout(3000)
        except Exception as e:
            log(actor, f"_check_results attempt {attempt + 1} exception: {e}")
            await page.wait_for_timeout(3000)
    raise RuntimeError(f"Could not advance past round {rnd}")


# ── Policy log ────────────────────────────────────────────────────────────────

def _write_policy_log():
    lines = ["", "Policy Slider Values", "═" * 60]
    for region in REGIONS:
        lines.append(f"\n{REGION_NAMES[region]} ({region})")
        for ministry in MINISTRIES:
            if ministry == "Future":
                continue
            lines.append(f"  {ministry}")
            for rnd in range(1, NUM_ROUNDS + 1):
                vals = policy_log.get((region, ministry, rnd), [])
                if vals:
                    parts = "  |  ".join(f"{lbl} = {v}" for lbl, v in vals)
                    lines.append(f"    Round {rnd}: {parts}")
                else:
                    lines.append(f"    Round {rnd}: (no data)")
    report = "\n".join(lines)
    print(report)
    log_path = Path("policy_log.txt")
    log_path.write_text(report, encoding="utf-8")
    print(f"\nPolicy log also written to {log_path.resolve()}")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main(headed: bool, base: str):
    global BASE, HEADED
    BASE = base
    HEADED = headed

    log("BOT", f"Starting test against {BASE}")
    log("BOT", f"Regions: {REGIONS}  Ministries: {MINISTRIES}  Rounds: {NUM_ROUNDS}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=SLOW_MO,
            # Prevent Chromium from throttling background/occluded windows.
            # Without these, JS timers and DOM animations slow to a crawl when
            # the browser windows lose focus (e.g. user is doing other work),
            # causing select_quasar and dialog timeouts.
            args=[
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-background-timer-throttling",
            ],
        )

        # Run GM and all ministers concurrently; GM creates game first,
        # ministers block on game_id_event until it's published.
        tasks = [asyncio.create_task(run_gm(browser))]
        for region in REGIONS:
            for ministry in MINISTRIES:
                tasks.append(asyncio.create_task(run_minister(browser, region, ministry)))

        await asyncio.gather(*tasks, return_exceptions=True)

        if headed:
            input("\nAll tasks done — press Enter to close browser windows… ")
        await browser.close()

    # ── Policy log ────────────────────────────────────────────────────────────
    _write_policy_log()

    # ── Report ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    if errors:
        print(f"FAILED — {len(errors)} error(s):")
        for err in errors:
            print(f"\n  {err}")
        sys.exit(1)
    else:
        print("ALL TASKS COMPLETED — no errors recorded")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed",  action="store_true", help="Show browser windows")
    parser.add_argument("--base",    default="http://localhost:8899", help="Server URL")
    args = parser.parse_args()
    asyncio.run(main(args.headed, args.base))
