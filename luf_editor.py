"""
luf_editor.py  —  NiceGUI translation review tool for luf.py
- Password-protected: each password unlocks a specific target language
- Corrections saved server-side only (not downloadable via URL)
- Run as separate service on port 8800

Usage:  uv run python luf_editor.py
"""
import json
import importlib.util
from pathlib import Path
from nicegui import ui, app

# ── passwords → target language (change these!) ───────────────────────────────
PASSWORDS = {
    "french2025":  "fr",
    "norsk2025":   "no",
    "deutsch2025": "de_inf",
}

# ── constants ─────────────────────────────────────────────────────────────────
LUF_PATH   = Path("files/luf.py")
LANG_CODES = ["en", "de", "de_inf", "fr", "no"]
LANG_LABEL = {"fr": "FR", "no": "NO", "de_inf": "DE-Du"}

# Corrections stored here — not served as static files
CORR_DIR = Path("corrections")
CORR_DIR.mkdir(exist_ok=True)

# ── file helpers ──────────────────────────────────────────────────────────────
def load_luf():
    spec = importlib.util.spec_from_file_location("luf", LUF_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def corrections_path(lang: str) -> Path:
    return CORR_DIR / f"corrections_{lang}.json"

def load_corrections(lang: str) -> dict:
    p = corrections_path(lang)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def save_corrections(lang: str, data: dict):
    corrections_path(lang).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

# ── entry builder ─────────────────────────────────────────────────────────────
def build_entries(luf, target_lang: str, corrections: dict) -> list:
    entries = []
    tgt_idx = LANG_CODES.index(target_lang)

    for varname, value in vars(luf).items():
        if varname.startswith("_"):
            continue

        # 5-element list variable
        if (isinstance(value, list) and len(value) == 5
                and all(isinstance(x, str) for x in value)):
            key  = varname
            orig = value[tgt_idx]
            entries.append({
                "key":      key,
                "label":    varname,
                "en":       value[0],
                "de":       value[1],
                "original": orig,
                "current":  corrections.get(key, orig),
            })

        # dict {lang_code: {tag: text}} variable
        elif (isinstance(value, dict)
              and "en" in value
              and target_lang in value
              and isinstance(value["en"], dict)):
            en_sub  = value["en"]
            de_sub  = value.get("de", {})
            tgt_sub = value[target_lang]
            for tag, en_text in en_sub.items():
                key  = f"{varname}::{tag}"
                orig = tgt_sub.get(tag, "")
                entries.append({
                    "key":      key,
                    "label":    f"{varname} › {tag}",
                    "en":       en_text,
                    "de":       de_sub.get(tag, ""),
                    "original": orig,
                    "current":  corrections.get(key, orig),
                })

    return entries


# ── login page ────────────────────────────────────────────────────────────────
@ui.page("/")
def login_page():
    if app.storage.user.get("editor_lang"):
        ui.navigate.to("/editor")
        return

    with ui.card().classes("mx-auto mt-32 p-8 w-80"):
        ui.label("Translation Editor").classes("text-2xl font-bold mb-4")
        pw_input = ui.input("Password", password=True, password_toggle_button=True) \
                     .classes("w-full").props("autofocus")
        err = ui.label("").classes("text-red-500 text-sm")

        def check():
            pw = pw_input.value.strip()
            lang = PASSWORDS.get(pw)
            if not lang:
                err.set_text("Wrong password.")
                pw_input.value = ""
                return
            app.storage.user["editor_lang"] = lang
            ui.navigate.to("/editor")

        pw_input.on("keydown.enter", check)
        ui.button("Enter", on_click=check).classes("w-full mt-2")


# ── editor page ───────────────────────────────────────────────────────────────
@ui.page("/editor")
def editor_page():
    target_lang = app.storage.user.get("editor_lang")
    if not target_lang:
        ui.navigate.to("/")
        return

    luf = load_luf()

    saved_idx = app.storage.user.get(f"editor_idx_{target_lang}", 0)
    state = {
        "ref_lang":    "en",
        "idx":         saved_idx,
        "entries":     [],
        "corrections": load_corrections(target_lang),
    }
    state["entries"] = build_entries(luf, target_lang, state["corrections"])

    edit_area_ref = [None]

    def save_current():
        ea = edit_area_ref[0]
        if ea is None or not state["entries"]:
            return
        val = ea.value.strip()
        key = state["entries"][state["idx"]]["key"]
        if val != state["entries"][state["idx"]]["original"] or key in state["corrections"]:
            state["corrections"][key] = val
            state["entries"][state["idx"]]["current"] = val
            save_corrections(target_lang, state["corrections"])

    def navigate(delta: int):
        save_current()
        n = len(state["entries"])
        state["idx"] = max(0, min(n - 1, state["idx"] + delta))
        app.storage.user[f"editor_idx_{target_lang}"] = state["idx"]
        render.refresh()

    def jump_to(n: int):
        save_current()
        total = len(state["entries"])
        state["idx"] = max(0, min(total - 1, n - 1))
        app.storage.user[f"editor_idx_{target_lang}"] = state["idx"]
        render.refresh()

    # ── header ────────────────────────────────────────────────────────────────
    with ui.row().classes("w-full items-center gap-4 p-4 bg-blue-50"):
        ui.label("Translation Editor").classes("text-xl font-bold")
        ui.badge(LANG_LABEL.get(target_lang, target_lang), color="blue")

        ui.label("Reference:").classes("ml-4")
        ui.toggle(
            ["EN", "DE-Sie"],
            value="EN",
            on_change=lambda e: (
                state.update(ref_lang="en" if e.value == "EN" else "de"),
                render.refresh(),
            ),
        )

        ui.space()
        ui.button("Log out", icon="logout", on_click=lambda: (
            app.storage.user.pop("editor_lang", None),
            ui.navigate.to("/"),
        )).props("flat size=sm")

    # ── main card ─────────────────────────────────────────────────────────────
    @ui.refreshable
    def render():
        entries = state["entries"]
        if not entries:
            ui.label("No entries found.").classes("m-8 text-gray-400")
            return

        idx   = state["idx"]
        n     = len(entries)
        entry = entries[idx]
        ref_text = entry["en"] if state["ref_lang"] == "en" else entry["de"]

        with ui.card().classes("w-full max-w-3xl mx-auto mt-4 p-6 gap-4"):

            # label + counter
            with ui.row().classes("w-full items-center justify-between"):
                ui.label(entry["label"]).classes("font-mono font-bold text-blue-700")
                with ui.row().classes("items-center gap-2"):
                    jump_inp = ui.number(value=idx + 1, min=1, max=n,
                                         format="%.0f").classes("w-20") \
                                 .props("dense outlined")
                    jump_inp.on("keydown.enter",
                                lambda: jump_to(int(jump_inp.value or 1)))
                    ui.label(f"/ {n}").classes("text-gray-500")

            if entry["key"] in state["corrections"]:
                ui.badge("corrected", color="green").classes("self-start")

            # reference (read-only)
            ui.label("Reference (read-only)").classes("text-sm text-gray-500 mt-2")
            ui.textarea(value=ref_text) \
              .classes("w-full") \
              .props("readonly outlined dense rows=3 bg-color=grey-2")

            # target (editable)
            ui.label(f"{LANG_LABEL.get(target_lang, target_lang)} — edit here") \
              .classes("text-sm text-gray-500")
            edit_area_ref[0] = ui.textarea(value=entry["current"]) \
                                 .classes("w-full") \
                                 .props("outlined rows=3")

            # navigation
            with ui.row().classes("w-full justify-between mt-2"):
                ui.button("← Previous", icon="arrow_back",
                          on_click=lambda: navigate(-1)) \
                  .props("outline").set_enabled(idx > 0)
                ui.button("Next →", icon="arrow_forward",
                          on_click=lambda: navigate(+1)) \
                  .props("outline").set_enabled(idx < n - 1)

            # original deepl translation for comparison
            with ui.expansion("Show original DeepL translation").classes("w-full mt-2"):
                ui.label(entry["original"]).classes("text-gray-500 italic text-sm")

    render()


ui.run(port=8900, title="Translation Editor", reload=False,
       storage_secret="luf-editor-secret-change-me")
