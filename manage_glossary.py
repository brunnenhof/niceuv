#!/usr/bin/env python3
"""
Manage the DeepL EN→DE glossary used by translate_md.py.

DeepL does not allow modifying a glossary in place — entries are replaced by
creating a new glossary and deleting the old one.  DEEPL_GLOSSARY_ID in .env
is updated automatically after every change, so translate_md.py picks it up.

Usage:
    uv run python manage_glossary.py list
    uv run python manage_glossary.py add "SimFuture" "SimFuture"
    uv run python manage_glossary.py delete "old term"
"""

import os
import re
import sys
from pathlib import Path

import deepl
from dotenv import load_dotenv

load_dotenv()

ENV_FILE      = Path(".env")
SOURCE_LANG   = "EN"
TARGET_LANG   = "DE"
GLOSSARY_NAME = "sdg-game EN->DE"


# ── DeepL helpers ─────────────────────────────────────────────────────────────

def _translator() -> deepl.Translator:
    key = os.environ.get("DEEPL_API_KEY", "")
    if not key:
        sys.exit("ERROR: DEEPL_API_KEY not set in .env")
    return deepl.Translator(key)


def _glossary_id() -> str:
    return os.environ.get("DEEPL_GLOSSARY_ID", "")


def _load_entries(translator: deepl.Translator) -> dict[str, str]:
    gid = _glossary_id()
    if not gid:
        return {}
    try:
        return translator.get_glossary_entries(gid)
    except deepl.DeepLException as e:
        print(f"WARNING: could not load glossary {gid}: {e}", file=sys.stderr)
        return {}


def _save_entries(translator: deepl.Translator, entries: dict[str, str]) -> None:
    """Delete all same-named glossaries, create new one, update .env."""
    # Delete the tracked glossary AND any stale ones with the same name —
    # DeepL enforces a per-account glossary count limit.
    known_id = _glossary_id()
    for g in translator.list_glossaries():
        if g.glossary_id == known_id or g.name == GLOSSARY_NAME:
            try:
                translator.delete_glossary(g.glossary_id)
                print(f"Deleted old glossary  id={g.glossary_id}  name={g.name!r}")
            except Exception:
                pass

    if not entries:
        _write_env_id("")
        print("Glossary is now empty and has been removed.")
        return

    g = translator.create_glossary(
        GLOSSARY_NAME,
        source_lang=SOURCE_LANG,
        target_lang=TARGET_LANG,
        entries=entries,
    )
    _write_env_id(g.glossary_id)
    print(f"Glossary recreated  id={g.glossary_id}")


def _write_env_id(new_id: str) -> None:
    """Write/replace DEEPL_GLOSSARY_ID line in .env."""
    if ENV_FILE.exists():
        text = ENV_FILE.read_text(encoding="utf-8")
        if re.search(r"^DEEPL_GLOSSARY_ID=", text, re.MULTILINE):
            text = re.sub(
                r"^DEEPL_GLOSSARY_ID=.*$",
                f"DEEPL_GLOSSARY_ID={new_id}",
                text,
                flags=re.MULTILINE,
            )
        else:
            text = text.rstrip("\n") + f"\nDEEPL_GLOSSARY_ID={new_id}\n"
    else:
        text = f"DEEPL_GLOSSARY_ID={new_id}\n"
    ENV_FILE.write_text(text, encoding="utf-8")
    os.environ["DEEPL_GLOSSARY_ID"] = new_id
    print(f".env updated        DEEPL_GLOSSARY_ID={new_id or '(removed)'}")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list(translator: deepl.Translator) -> None:
    gid = _glossary_id()
    if not gid:
        print("No glossary configured (DEEPL_GLOSSARY_ID not set in .env).")
        return
    entries = _load_entries(translator)
    if not entries:
        print("Glossary is empty.")
        return
    col = max(len(k) for k in entries)
    print(f"{len(entries)} entries  (id {gid[:8]}…)\n")
    print(f"  {'EN':{col}}   DE")
    print(f"  {'-'*col}   {'-'*36}")
    for src, tgt in sorted(entries.items(), key=lambda x: x[0].lower()):
        print(f"  {src:{col}}   {tgt}")


def cmd_add(translator: deepl.Translator, source: str, target: str) -> None:
    entries = _load_entries(translator)
    old = entries.get(source)
    if old == target:
        print(f"Already present: {source!r} → {target!r}")
        return
    entries[source] = target
    _save_entries(translator, entries)
    if old is None:
        print(f"Added:   {source!r} → {target!r}")
    else:
        print(f"Updated: {source!r}  was {old!r}, now {target!r}")
    print(f"Total entries: {len(entries)}")


def cmd_delete(translator: deepl.Translator, source: str) -> None:
    entries = _load_entries(translator)
    if source not in entries:
        sys.exit(f"Entry not found: {source!r}")
    removed = entries.pop(source)
    _save_entries(translator, entries)
    print(f"Removed: {source!r} → {removed!r}")
    print(f"Total entries: {len(entries)}")


def cmd_list_all(translator: deepl.Translator) -> None:
    """Show every glossary on the DeepL account (not just the configured one)."""
    glossaries = translator.list_glossaries()
    if not glossaries:
        print("No glossaries on this DeepL account.")
        return
    current = _glossary_id()
    print(f"{len(glossaries)} glossary/glossaries on account:\n")
    for g in glossaries:
        marker = " ← current" if g.glossary_id == current else ""
        print(f"  {g.glossary_id}  {g.source_lang}→{g.target_lang}  "
              f"{g.entry_count} entries  name={g.name!r}{marker}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Manage DeepL EN→DE glossary")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list",     help="Show entries in the configured glossary")
    sub.add_parser("list-all", help="Show all glossaries on the DeepL account")

    p_add = sub.add_parser("add", help="Add or update an entry")
    p_add.add_argument("source", help="EN term")
    p_add.add_argument("target", help="DE translation")

    p_del = sub.add_parser("delete", help="Remove an entry by its EN term")
    p_del.add_argument("source", help="EN term to remove")

    args = parser.parse_args()
    t = _translator()

    if args.cmd == "list":
        cmd_list(t)
    elif args.cmd == "list-all":
        cmd_list_all(t)
    elif args.cmd == "add":
        cmd_add(t, args.source, args.target)
    elif args.cmd == "delete":
        cmd_delete(t, args.source)


if __name__ == "__main__":
    main()
