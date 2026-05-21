"""
Generic translation-review engine.

Call register() once per language to mount two NiceGUI pages:
  /review_{lang}         — volunteer corrects DeepL translations
  /review_{lang}/approve — owner QA: approve file-by-file, publish to docs/{lang}/
"""

import json
from pathlib import Path
from nicegui import ui, app


def register(
    language:      str,
    volunteer_pw:  str,
    approve_pw:    str,
    docs_src:      Path,
    docs_en:       Path        = Path("docs/en"),
    reviewed_dir:  Path | None = None,
    backcheck_dir: Path | None = None,
    reminder_text: str         = "Do not change links [...](…), images ![...](…) or code `...`.",
):
    """Register /review_{language} and /review_{language}/approve pages."""

    lang = language.lower()
    rev_dir  = reviewed_dir  or Path(f"docs/{lang}_reviewed")
    back_dir = backcheck_dir or Path(f"docs/{lang}_backcheck_de")
    appr_file = rev_dir / "_approved.json"

    # storage-key prefixes — kept per language so multiple reviews can coexist
    K_AUTH  = f"review_{lang}_auth"
    K_IDX   = f"review_{lang}_idx"
    KA_AUTH = f"approve_{lang}_auth"
    KA_IDX  = f"approve_{lang}_idx"

    # CSS classes — per language so simultaneous pages don't clash
    CLS_EDITOR = f"{lang}-editor"
    CLS_MD     = f"{lang}-deepl-md"

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _md_files(base_dir: Path) -> list[Path]:
        return sorted(f for f in base_dir.glob("*.md") if not f.name.startswith("_"))

    def _load_approvals() -> dict:
        if appr_file.exists():
            try:
                return json.loads(appr_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_approvals(data: dict):
        rev_dir.mkdir(parents=True, exist_ok=True)
        appr_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ── Volunteer review page ─────────────────────────────────────────────────

    @ui.page(f"/review_{lang}")
    def review_page():
        rev_dir.mkdir(parents=True, exist_ok=True)

        if not app.storage.user.get(K_AUTH):
            with ui.card().classes("mx-auto mt-32 p-8 w-80"):
                ui.label(f"SimFuture – {lang.upper()} Review").classes("text-2xl font-bold mb-4")
                pw  = ui.input("Password", password=True).props("autofocus").classes("w-full")
                err = ui.label("").classes("text-red-500 text-sm mt-1")

                def _login():
                    if pw.value.strip() == volunteer_pw:
                        app.storage.user[K_AUTH] = True
                        ui.navigate.to(f"/review_{lang}")
                    else:
                        err.set_text("Wrong password.")

                pw.on("keydown.enter", _login)
                ui.button("Enter", on_click=_login).classes("w-full mt-3")
            return

        files = _md_files(docs_src)
        if not files:
            ui.label(f"No .md files found in {docs_src}/").classes("text-red-500 mt-16 mx-auto")
            return

        idx = [max(0, min(app.storage.user.get(K_IDX, 0), len(files) - 1))]

        with ui.row().classes("w-full items-center gap-4 px-6 pt-4"):
            file_label   = ui.label("").classes("text-lg font-bold font-mono flex-1")
            status_label = ui.label("").classes("text-sm text-gray-400")
            saved_badge  = ui.label("").classes("text-sm font-bold")
            ui.button("Log out",
                      on_click=lambda: (app.storage.user.update({K_AUTH: False}),
                                        ui.navigate.to(f"/review_{lang}"))) \
              .props("flat size=sm")

        ui.separator()

        _suppress = [False]
        file_opts = {i: f.name for i, f in enumerate(files)}
        file_sel  = ui.select(file_opts, value=idx[0], label="Jump to file",
                              on_change=lambda e: (None if _suppress[0] else (_save(), _load(e.value)))) \
                      .classes("mx-6 w-96")

        with ui.row().classes("w-full px-6 gap-4 mt-2 items-start flex-nowrap"):
            with ui.card().classes("p-4").style("flex:1; min-width:0"):
                ui.label("EN original (read only)").classes("text-xs text-red-400 font-bold mb-2")
                en_view = ui.textarea("") \
                            .props("outlined autogrow readonly") \
                            .classes("w-full font-mono text-xs") \
                            .style("min-height:500px")

            with ui.card().classes("p-4").style("flex:1; min-width:0"):
                ui.label("Translation (rendered live)").classes("text-xs text-red-400 font-bold mb-2")
                md_view = ui.markdown("").classes(f"prose max-w-none {CLS_MD}")

            with ui.card().classes("p-4").style("flex:1; min-width:0"):
                ui.label("Your corrections (edit here)").classes("text-green font-bold mb-2")
                ui.label(reminder_text).classes("text-lg font-bold text-orange-700 mb-2")
                editor = ui.textarea("") \
                           .props("outlined autogrow") \
                           .classes(f"w-full font-mono text-sm {CLS_EDITOR}")

        md_view.bind_content_from(editor, 'value')

        with ui.row().classes("px-6 py-4 gap-3"):
            ui.button("← Previous",
                      on_click=lambda: (_save(), _load(max(0, idx[0] - 1))))
            ui.button("Save", on_click=lambda: _save()).props("color=primary icon=save")
            ui.button("Next →",
                      on_click=lambda: (_save(), _load(min(len(files) - 1, idx[0] + 1))))

        def _reviewed_count():
            return sum(1 for f in files if (rev_dir / f.name).exists())

        def _save():
            dst = rev_dir / files[idx[0]].name
            dst.write_text(editor.value, encoding="utf-8")
            saved_badge.set_text("✓ saved")
            saved_badge.classes(replace="text-sm font-bold text-green-600")
            status_label.set_text(f"{_reviewed_count()}/{len(files)} reviewed")

        def _load(i: int):
            idx[0] = i
            app.storage.user[K_IDX] = i
            _suppress[0] = True
            file_sel.set_value(i)
            _suppress[0] = False
            f    = files[i]
            src  = f.read_text(encoding="utf-8")
            rev  = rev_dir / f.name
            edit = rev.read_text(encoding="utf-8") if rev.exists() else src
            en_f = docs_en / f.name
            en_view.set_value(en_f.read_text(encoding="utf-8") if en_f.exists() else "_(EN source not found)_")
            editor.set_value(edit)
            _edit_snap = edit
            def _js_update():
                ui.run_javascript(
                    f'var ta = document.querySelector(".{CLS_EDITOR} textarea");'
                    f'if(ta){{ta.value={json.dumps(_edit_snap)};'
                    f'ta.dispatchEvent(new Event("input"));}}'
                )
            ui.timer(0.05, _js_update, once=True)
            file_label.set_text(f"{i + 1}/{len(files)}  ·  {f.name}")
            status_label.set_text(f"{_reviewed_count()}/{len(files)} reviewed")
            if rev.exists():
                saved_badge.set_text("✓ saved")
                saved_badge.classes(replace="text-sm font-bold text-green-600")
            else:
                saved_badge.set_text("not yet saved")
                saved_badge.classes(replace="text-sm font-bold text-orange-500")

        _load(idx[0])

    # ── Owner approval page ───────────────────────────────────────────────────

    @ui.page(f"/review_{lang}/approve")
    def approve_page():

        if not app.storage.user.get(KA_AUTH):
            with ui.card().classes("mx-auto mt-32 p-8 w-80"):
                ui.label(f"SimFuture – {lang.upper()} Approve").classes("text-2xl font-bold mb-4")
                pw  = ui.input("Password", password=True).props("autofocus").classes("w-full")
                err = ui.label("").classes("text-red-500 text-sm mt-1")

                def _login():
                    if pw.value.strip() == approve_pw:
                        app.storage.user[KA_AUTH] = True
                        ui.navigate.to(f"/review_{lang}/approve")
                    else:
                        err.set_text("Wrong password.")

                pw.on("keydown.enter", _login)
                ui.button("Enter", on_click=_login).classes("w-full mt-3")
            return

        reviewed_files = _md_files(rev_dir)
        approvals      = _load_approvals()

        if not reviewed_files:
            ui.label(f"No reviewed files yet in {rev_dir}/") \
              .classes("text-orange-500 mt-16 mx-auto")
            return

        backcheck_available = back_dir.exists() and any(back_dir.glob("*.md"))
        if not backcheck_available:
            with ui.card().classes("mx-auto mt-16 p-6 w-xl"):
                ui.label("Back-translations not found").classes("text-xl font-bold mb-2")
                ui.markdown(
                    f"Run this first to generate DE back-translations for QA:\n\n"
                    f"```\nuv run python translate_md.py "
                    f"--src-dir {rev_dir} "
                    f"--dst-dir {back_dir} "
                    f"--source-lang {lang.upper()} --target-lang DE\n```"
                )
            return

        idx = [max(0, min(app.storage.user.get(KA_IDX, 0), len(reviewed_files) - 1))]

        with ui.row().classes("w-full items-center gap-4 px-6 pt-4"):
            file_label    = ui.label("").classes("text-lg font-bold font-mono flex-1")
            approved_lbl  = ui.label("").classes("text-sm text-gray-400")
            approve_badge = ui.label("").classes("text-sm font-bold")
            ui.button("Log out",
                      on_click=lambda: (app.storage.user.update({KA_AUTH: False}),
                                        ui.navigate.to(f"/review_{lang}/approve"))) \
              .props("flat size=sm")

        ui.separator()

        file_opts = {i: f.name for i, f in enumerate(reviewed_files)}
        file_sel  = ui.select(file_opts, value=idx[0], label="Jump to file",
                              on_change=lambda e: _load_a(e.value)) \
                      .classes("mx-6 w-96")

        with ui.row().classes("w-full px-6 gap-4 mt-2 items-start"):
            with ui.card().classes("p-4").style("width:50%"):
                ui.label("DE back-translation (your QA check)") \
                  .classes("text-xs text-gray-400 font-bold mb-2")
                de_view = ui.markdown("").classes("prose max-w-none")

            with ui.card().classes("p-4").style("width:50%"):
                ui.label(f"{lang.upper()} corrected (volunteer's text)") \
                  .classes("text-xs text-gray-400 font-bold mb-2")
                fr_view = ui.markdown("").classes("prose max-w-none")

        with ui.row().classes("px-6 py-4 gap-3 items-center"):
            ui.button("← Previous",
                      on_click=lambda: _load_a(max(0, idx[0] - 1)))
            ui.button("✓ Approve & publish",
                      on_click=lambda: _approve()).props("color=positive icon=check_circle")
            ui.button("✗ Revoke approval",
                      on_click=lambda: _revoke()).props("color=negative icon=cancel flat")
            ui.button("Next →",
                      on_click=lambda: _load_a(min(len(reviewed_files) - 1, idx[0] + 1)))

        def _approved_count():
            return sum(1 for f in reviewed_files if approvals.get(f.name))

        def _approve():
            f = reviewed_files[idx[0]]
            src = rev_dir / f.name
            dst = docs_src / f.name
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            approvals[f.name] = True
            _save_approvals(approvals)
            _refresh_badge()
            ui.notify(f"{f.name} approved and published to {docs_src}/", type="positive")

        def _revoke():
            f = reviewed_files[idx[0]]
            approvals[f.name] = False
            _save_approvals(approvals)
            _refresh_badge()
            ui.notify(f"{f.name} approval revoked.", type="warning")

        def _refresh_badge():
            f = reviewed_files[idx[0]]
            approved_lbl.set_text(f"{_approved_count()}/{len(reviewed_files)} approved")
            if approvals.get(f.name):
                approve_badge.set_text("✓ approved & live")
                approve_badge.classes(replace="text-sm font-bold text-green-600")
            else:
                approve_badge.set_text("pending review")
                approve_badge.classes(replace="text-sm font-bold text-orange-500")

        def _load_a(i: int):
            idx[0] = i
            app.storage.user[KA_IDX] = i
            file_sel.set_value(i)
            f    = reviewed_files[i]
            fr_t = (rev_dir / f.name).read_text(encoding="utf-8")
            de_f = back_dir / f.name
            de_t = de_f.read_text(encoding="utf-8") if de_f.exists() else "_Back-translation not found for this file._"
            de_view.set_content(de_t)
            fr_view.set_content(fr_t)
            file_label.set_text(f"{i + 1}/{len(reviewed_files)}  ·  {f.name}")
            _refresh_badge()

        _load_a(idx[0])
