"""
test_resume_bot.py  –  Tests the resume capability of toy.py

Runs a full 3-round SimFuture game with:
  • 1 GM
  • 1 randomly chosen human region × 6 ministers

At safe checkpoints (between major actions) each actor randomly:
  1. Closes their browser context — simulates closing the tab / crash
  2. Waits 2–8 seconds
  3. Opens a fresh context and navigates back to their saved token URL
  4. Verifies the page shows the expected game state

This validates that /gm/board?token=... and /dashboard?token=... correctly
reconstruct game state from the DB when a fresh connection arrives.

Usage:
    uv run python test_resume_bot.py
    uv run python test_resume_bot.py --headed
    uv run python test_resume_bot.py --base http://localhost:8899
    uv run python test_resume_bot.py --disconnect-prob 0.7
    uv run python test_resume_bot.py --disconnect-prob 1.0   # always disconnect
"""

import argparse
import asyncio
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
import random

import logging
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# This file's own log/print output includes non-ASCII characters (arrows,
# checkmarks, em-dashes). Under non-UTF-8 stdout (redirected to a file, or a
# non-UTF-8 console codepage) those raise UnicodeEncodeError, which inside
# asyncio.gather(..., return_exceptions=True) is silently swallowed into that
# task's result -- leaving every other bot waiting forever on an event that
# will now never fire. What looks like a hang is actually this crash.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.async_api import BrowserContext, Page, async_playwright

# ── Config ─────────────────────────────────────────────────────────────────────

BASE            = "http://localhost:8899"
HEADED          = False
START_CODE      = "oscar"
MINISTRIES      = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]
NUM_ROUNDS      = 3
TIMEOUT         = 60_000   # ms
SLOW_MO         = 0        # ms between actions
DISCONNECT_PROB = 0.5      # probability of disconnecting at each safe checkpoint

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
ALL_REGIONS = list(REGION_NAMES.keys())

# ── Shared state ───────────────────────────────────────────────────────────────

game_id_event  = asyncio.Event()
game_id_value: str = ""

gm_board_event = asyncio.Event()
join_semaphore = asyncio.Semaphore(3)

round_done_events: list[asyncio.Event] = [asyncio.Event() for _ in range(NUM_ROUNDS + 1)]

errors: list[str] = []

# (actor, checkpoint, success, note_or_None)
reconnect_log: list[tuple] = []

SCREENSHOT_DIR = Path("test_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(actor: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{actor:20s}] {msg}", flush=True)


async def screenshot(page: Page, name: str):
    path = SCREENSHOT_DIR / f"{name}_{datetime.now().strftime('%H%M%S%f')}.png"
    try:
        await page.screenshot(path=str(path))
    except Exception:
        pass


def attach_error_handlers(page: Page, actor: str):
    page.on("pageerror", lambda e: errors.append(f"[{actor}] JS ERROR: {e}"))
    page.on("console",   lambda m: (
        errors.append(f"[{actor}] CONSOLE {m.type.upper()}: {m.text}")
        if m.type in ("error", "warning") else None
    ))


async def click_button(page: Page, text: str, exact: bool = False, timeout: int = TIMEOUT):
    loc = page.get_by_role("button", name=text, exact=exact)
    await loc.first.wait_for(state="visible", timeout=timeout)
    await loc.first.click()


async def wait_for_text(page: Page, text: str, timeout: int = TIMEOUT):
    await page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout)


async def fill_input_in(scope, label: str, value: str, timeout: int = TIMEOUT):
    loc = scope.locator(f'.q-field:has(.q-field__label:text("{label}")) .q-field__native')
    await loc.first.wait_for(state="visible", timeout=timeout)
    await loc.first.fill(value)


async def fill_input(page: Page, label: str, value: str, timeout: int = TIMEOUT):
    await fill_input_in(page, label, value, timeout)


async def select_quasar(page: Page, nth: int, option_text: str, timeout: int = TIMEOUT):
    scope = page.locator(".q-dialog").last
    trigger = scope.get_by_role("combobox").nth(nth)
    await trigger.wait_for(state="visible", timeout=timeout)
    await trigger.click()
    option = page.locator(".q-menu .q-item").filter(has_text=option_text).first
    await option.wait_for(state="visible", timeout=timeout)
    await option.click()


# ── Disconnect / reconnect ─────────────────────────────────────────────────────

async def maybe_reconnect(
    browser,
    ctx: BrowserContext,
    page: Page,
    actor: str,
    saved_url: str,
    checkpoint: str,
    expected_text: str | None = None,
) -> tuple[BrowserContext, Page]:
    """
    With DISCONNECT_PROB probability:
      - Close the current browser context (simulates tab close)
      - Wait 2–8 s
      - Open a fresh context and navigate to saved_url
      - Verify expected_text is present in the page body

    Never raises — failures are appended to reconnect_log and errors[].
    Always returns the current (ctx, page), new or original.
    """
    if random.random() > DISCONNECT_PROB:
        return ctx, page

    delay = round(random.uniform(2, 8), 1)
    log(actor, f"── DISCONNECT [{checkpoint}] — reconnecting in {delay}s ──")

    try:
        await ctx.close()
    except Exception:
        pass

    await asyncio.sleep(delay)

    new_ctx  = await browser.new_context()
    new_page = await new_ctx.new_page()
    attach_error_handlers(new_page, actor)

    try:
        await new_page.goto(saved_url, timeout=TIMEOUT)
        await new_page.wait_for_load_state("networkidle", timeout=30_000)
        # NiceGUI delivers dynamic UI via WebSocket after HTTP load completes.
        # Without this wait the caller may find buttons not yet rendered.
        await new_page.wait_for_timeout(3000)

        if expected_text:
            body = await new_page.inner_text("body")
            ok   = expected_text in body
            note = None if ok else f"'{expected_text}' missing from page"
            reconnect_log.append((actor, checkpoint, ok, note))
            if ok:
                log(actor, f"── RECONNECT OK [{checkpoint}] — '{expected_text}' confirmed ──")
            else:
                log(actor, f"── RECONNECT WARN [{checkpoint}] — '{expected_text}' not found ──")
                errors.append(f"{actor} reconnect at {checkpoint}: {note}")
        else:
            reconnect_log.append((actor, checkpoint, True, None))
            log(actor, f"── RECONNECT OK [{checkpoint}] ──")

    except Exception as e:
        note = str(e)
        reconnect_log.append((actor, checkpoint, False, note))
        errors.append(f"{actor} reconnect failed at {checkpoint}: {e}")
        log(actor, f"── RECONNECT FAILED [{checkpoint}]: {e} ──")

    return new_ctx, new_page


# ── GM flow ────────────────────────────────────────────────────────────────────

async def run_gm(browser, region: str):
    global game_id_value
    ctx: BrowserContext = await browser.new_context()
    page: Page = await ctx.new_page()
    attach_error_handlers(page, "GM")
    gm_url = ""

    try:
        # ── Create game ───────────────────────────────────────────────────────
        log("GM", "Opening home page")
        await page.goto(BASE, timeout=TIMEOUT)
        await click_button(page, "Fresh Game")
        await click_button(page, "Start a new Game")

        await page.wait_for_selector('.q-dialog', timeout=TIMEOUT)
        await page.wait_for_timeout(400)
        dlg = page.locator('.q-dialog').last

        gm_name = f"bot_gm_{datetime.now().strftime('%H%M%S')}"
        log("GM", "Filling new-game dialog")
        try:
            await fill_input_in(dlg, "Username", gm_name, timeout=5_000)
            await fill_input_in(dlg, "start code", START_CODE, timeout=5_000)
        except Exception:
            log("GM", "Label-based fill failed — trying positional fill")
            inputs = dlg.locator('input')
            await inputs.nth(0).fill(gm_name)
            await inputs.nth(1).fill(START_CODE)
        await click_button(page, "Start", exact=True)

        # ── Setup: select 1 human region ─────────────────────────────────────
        log("GM", "Waiting for setup page")
        await page.wait_for_url("**/gm/setup**", timeout=TIMEOUT)
        await page.wait_for_timeout(1000)

        page_text = await page.inner_text("body")
        m = re.search(r'\b([A-Z]{3}-\d{3})\b', page_text)
        if not m:
            raise RuntimeError("Could not find game ID on setup page")
        game_id_value = m.group(1)
        log("GM", f"Game ID: {game_id_value}")
        game_id_event.set()

        label_text = REGION_NAMES[region]
        chk = page.get_by_text(label_text, exact=True).first
        await chk.wait_for(state="visible", timeout=TIMEOUT)
        await chk.click()
        log("GM", f"Selected region {region} ({label_text})")
        await page.wait_for_timeout(200)

        await click_button(page, "Confirm selection")
        await page.wait_for_timeout(500)
        await click_button(page, "Continue to GM Board")
        await page.wait_for_url("**/gm/board**", timeout=TIMEOUT)
        log("GM", "On GM board")
        gm_url = page.url
        gm_board_event.set()

        # ── Play through all rounds ───────────────────────────────────────────
        for rnd in range(1, NUM_ROUNDS + 1):

            # Safe reconnect: start of each round, before Allow Submissions
            ctx, page = await maybe_reconnect(
                browser, ctx, page, "GM", gm_url,
                f"start_of_round_{rnd}",
                expected_text=game_id_value,  # game ID always visible on GM board
            )

            log("GM", f"Round {rnd}: waiting for Allow Submissions")
            await page.get_by_role("button", name="Allow Submissions", exact=False) \
                      .first.wait_for(state="visible", timeout=120_000)

            log("GM", f"Round {rnd}: allowing submissions")
            await click_button(page, "Allow Submissions")
            await page.wait_for_timeout(500)

            log("GM", f"Round {rnd}: waiting for all regions to submit")
            await page.get_by_role("button", name=f"Run model to Round {rnd + 1}", exact=False) \
                      .first.wait_for(state="visible", timeout=300_000)

            log("GM", f"Round {rnd}: running model")
            await click_button(page, f"Run model to Round {rnd + 1}")
            await click_button(page, "Yes, run model")

            log("GM", f"Round {rnd}: model running…")
            await page.wait_for_timeout(5000)
            round_done_events[rnd].set()

            if rnd < NUM_ROUNDS:
                # "Round 3" also appears inside the "Run model to Round 3" button,
                # so it would match while the model is still running.
                # "Round 3/3" (header) only appears after advance_round() fires
                # and the board reloads — guaranteeing current_round is correct
                # before we disconnect and reconnect.
                await wait_for_text(page, f"Round {rnd + 1}/{NUM_ROUNDS}", timeout=60_000)
                await page.wait_for_timeout(3000)

        log("GM", "All rounds done — game complete")

    except Exception as e:
        msg = f"GM FAILED: {e}\n{traceback.format_exc()}"
        errors.append(msg)
        log("GM", msg)
        await screenshot(page, "gm_error")
        game_id_event.set()
        gm_board_event.set()
        for ev in round_done_events:
            ev.set()
    finally:
        if not HEADED:
            await ctx.close()


# ── Minister flow ──────────────────────────────────────────────────────────────

async def run_minister(browser, region: str, ministry: str):
    actor = f"{region}/{ministry[:3]}"
    ctx: BrowserContext = await browser.new_context()
    page: Page = await ctx.new_page()
    attach_error_handlers(page, actor)
    dashboard_url = ""

    try:
        await gm_board_event.wait()
        if not game_id_value:
            raise RuntimeError("No game ID received from GM")

        # Stagger so bots don't all hit the semaphore at once
        ministry_idx = MINISTRIES.index(ministry)
        if ministry_idx:
            await page.wait_for_timeout(ministry_idx * 200)

        # ── Join game ─────────────────────────────────────────────────────────
        async with join_semaphore:
            for join_attempt in range(10):
                if "/dashboard" in page.url:
                    break

                username = f"bot_{region}_{ministry.lower()[:3]}_{random.randint(1, 999999)}"
                log(actor, f"Join attempt {join_attempt + 1}: {username}")

                try:
                    await page.goto(BASE, timeout=TIMEOUT)
                    await click_button(page, "Fresh Game")
                    await click_button(page, "Join a new game")
                    await fill_input(page, "Username", username)
                    await fill_input(page, "Game ID", game_id_value)
                    await click_button(page, "Open game")

                    await select_quasar(page, 0, REGION_NAMES[region])
                    await page.wait_for_timeout(800)
                    await select_quasar(page, 1, ministry)
                    await page.wait_for_timeout(800)

                    await click_button(page, "Join!")
                    await page.wait_for_url("**/dashboard**", timeout=TIMEOUT)
                    break
                except Exception as e:
                    if "/dashboard" in page.url:
                        break
                    for _ in range(15):
                        await page.wait_for_timeout(2000)
                        if "/dashboard" in page.url:
                            break
                    if "/dashboard" in page.url:
                        break
                    log(actor, f"Join attempt {join_attempt + 1} failed: {type(e).__name__}, retrying…")
            else:
                raise RuntimeError("Could not join the game after 10 attempts")

        dashboard_url = page.url
        log(actor, f"Joined — {dashboard_url}")

        # Safe reconnect: immediately after joining, before round 1
        ctx, page = await maybe_reconnect(
            browser, ctx, page, actor, dashboard_url,
            "after_join",
            expected_text="Round: 1",
        )

        # ── Play each round ───────────────────────────────────────────────────
        for rnd in range(1, NUM_ROUNDS + 1):
            log(actor, f"Round {rnd}: on dashboard")

            if ministry != "Future":
                await _interact_slider(page, actor, region, ministry, rnd)
            else:
                await _submit_region(page, actor, rnd)

            # Safe reconnect: after submitting this round, before waiting for model
            ctx, page = await maybe_reconnect(
                browser, ctx, page, actor, dashboard_url,
                f"round_{rnd}_after_submit",
                expected_text=f"Round: {rnd}",
            )

            log(actor, f"Round {rnd}: waiting for model run")
            await round_done_events[rnd].wait()
            await page.wait_for_timeout(2000 + hash(actor) % 2000)

            log(actor, f"Round {rnd}: checking results")
            try:
                await _check_results(page, actor, rnd)
            except RuntimeError:
                if rnd < NUM_ROUNDS:
                    raise
                # Final round: button sometimes vanishes before we click it
                log(actor, "Button gone on final round — polling via reload")
                target = f"Round: {NUM_ROUNDS + 1}"
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
                    log(actor, "Final results not confirmed — non-fatal")

            # Safe reconnect: between rounds, after advancing to rnd+1
            if rnd < NUM_ROUNDS:
                ctx, page = await maybe_reconnect(
                    browser, ctx, page, actor, dashboard_url,
                    f"between_round_{rnd}_and_{rnd + 1}",
                    expected_text=f"Round: {rnd + 1}",
                )

        log(actor, "Done with all rounds")

    except Exception as e:
        msg = f"{actor} FAILED: {e}\n{traceback.format_exc()}"
        errors.append(msg)
        log(actor, msg)
        await screenshot(page, f"{region}_{ministry}_error")
    finally:
        if not HEADED:
            await ctx.close()


# ── Slider / submit helpers (identical to test_game_bot.py) ───────────────────

async def _interact_slider(page: Page, actor: str, region: str, ministry: str, rnd: int):
    try:
        sliders = page.get_by_role("slider")
        await sliders.first.wait_for(state="visible", timeout=15_000)
        all_sliders = await sliders.all()
        for idx, slider in enumerate(all_sliders):
            frac = random.betavariate(3, 20)
            try:
                track = slider.locator(".q-slider__track-container")
                await track.scroll_into_view_if_needed()
                t_box = await track.bounding_box()
                if t_box:
                    x = t_box["x"] + t_box["width"] * frac
                    y = t_box["y"] + t_box["height"] / 2
                    await page.mouse.click(x, y)
                    await page.wait_for_timeout(400)
            except Exception as e:
                log(actor, f"  slider_{idx + 1} error: {e}")
        log(actor, f"Moved {len(all_sliders)} slider(s)")
    except Exception as e:
        log(actor, f"Could not move sliders (non-fatal): {e}")


async def _submit_region(page: Page, actor: str, rnd: int):
    log(actor, f"Round {rnd}: submitting region proposals")
    for attempt in range(10):
        try:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(300)
        except Exception:
            pass

        await click_button(page, "Submit proposals?", timeout=300_000)
        try:
            await page.get_by_role("button", name="Yes, Submit", exact=False) \
                      .first.wait_for(state="visible", timeout=20_000)
            await page.get_by_role("button", name="Yes, Submit", exact=False).first.click()
            log(actor, f"Round {rnd}: submitted")
            return
        except Exception:
            log(actor, f"Round {rnd}: confirm dialog didn't open, retrying ({attempt + 1}/10)…")
            await page.wait_for_timeout(2000)
    raise RuntimeError(f"Could not submit region proposals in round {rnd}")


async def _check_results(page: Page, actor: str, rnd: int):
    target = f"Round: {rnd + 1}"
    for attempt in range(15):
        try:
            if target in await page.inner_text("body"):
                log(actor, f"Advanced to round {rnd + 1}")
                return
            await click_button(page, "Check if results are ready", timeout=10_000)
            await page.wait_for_load_state("networkidle", timeout=20_000)
            await page.wait_for_timeout(1000)
            if target in await page.inner_text("body"):
                log(actor, f"Advanced to round {rnd + 1}")
                return
            log(actor, f"Model not ready yet, retrying ({attempt + 1}/15)…")
            await page.wait_for_timeout(3000)
        except Exception as e:
            log(actor, f"_check_results attempt {attempt + 1}: {e}")
            await page.wait_for_timeout(3000)
    raise RuntimeError(f"Could not advance past round {rnd}")


# ── Reconnect summary ──────────────────────────────────────────────────────────

def _write_reconnect_report():
    total   = len(reconnect_log)
    passed  = sum(1 for _, _, ok, _ in reconnect_log if ok)
    failed  = total - passed
    lines   = ["", "Reconnect Test Report", "═" * 60,
               f"Total disconnects: {total}  |  OK: {passed}  |  WARN/FAIL: {failed}", ""]

    for actor, checkpoint, ok, note in reconnect_log:
        status = "✓" if ok else "✗"
        line   = f"  {status}  [{actor:20s}]  {checkpoint}"
        if note:
            line += f"  →  {note}"
        lines.append(line)

    report = "\n".join(lines)
    print(report)
    Path("reconnect_log.txt").write_text(report, encoding="utf-8")
    print("\nReconnect report also written to reconnect_log.txt")


# ── Entry point ────────────────────────────────────────────────────────────────

async def main(headed: bool, base: str, disconnect_prob: float):
    global BASE, HEADED, DISCONNECT_PROB
    BASE            = base
    HEADED          = headed
    DISCONNECT_PROB = disconnect_prob

    region = random.choice(ALL_REGIONS)
#    region = 'se'

    log("BOT", f"Starting resume test against {BASE}")
    log("BOT", f"Region: {region} ({REGION_NAMES[region]})  "
               f"Rounds: {NUM_ROUNDS}  Disconnect prob: {DISCONNECT_PROB:.0%}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=SLOW_MO,
            args=[
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-background-timer-throttling",
            ],
        )

        tasks = [asyncio.create_task(run_gm(browser, region))]
        for ministry in MINISTRIES:
            tasks.append(asyncio.create_task(run_minister(browser, region, ministry)))

        await asyncio.gather(*tasks, return_exceptions=True)

        if headed:
            input("\nAll tasks done — press Enter to close browser windows… ")
        await browser.close()

    _write_reconnect_report()

    print("\n" + "═" * 60)
    game_errors = [e for e in errors if "reconnect" not in e.lower()]
    if game_errors:
        print(f"FAILED — {len(game_errors)} game error(s):")
        for err in game_errors:
            print(f"\n  {err}")
        sys.exit(1)
    else:
        reconnect_failures = [e for e in errors if "reconnect" in e.lower()]
        if reconnect_failures:
            print(f"GAME OK — but {len(reconnect_failures)} reconnect warning(s) (see reconnect_log.txt)")
        else:
            print("ALL TASKS COMPLETED — no errors recorded")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed",          action="store_true",       help="Show browser windows")
    parser.add_argument("--base",            default="http://localhost:8899", help="Server URL")
    parser.add_argument("--disconnect-prob", default=0.5, type=float,   help="Disconnect probability 0–1")
    args = parser.parse_args()
    asyncio.run(main(args.headed, args.base, args.disconnect_prob))
