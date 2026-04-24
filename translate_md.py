#!/usr/bin/env python3
"""
Translate docs/en/*.md -> docs/de/ via DeepL API.
Preserves Markdown structure: links, images, code, frontmatter, HTML comments.

Usage:
    uv run python translate_md.py                  # translate all files
    uv run python translate_md.py --dry-run        # count chars only, no API calls
    uv run python translate_md.py --file people.md # single file
    uv run python translate_md.py --skip-existing  # skip already-translated files
"""

import argparse
import html
import os
import re
from urllib.parse import quote, unquote
import sys
import deepl
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY      = os.environ["DEEPL_API_KEY"]
TARGET_LANG  = "DE"
FORMALITY    = "less"          # du-form
GLOSSARY_ID  = os.environ.get("DEEPL_GLOSSARY_ID")  # optional
SRC_DIR      = Path("docs/en")
DST_DIR      = Path("docs/de")
_TAG         = "x"             # XML ignore tag sent to DeepL


# ── Protect non-translatable spans ───────────────────────────────────────────

def _sub_outside_tags(pattern: str, repl, text: str, **kwargs) -> str:
    """Apply re.sub only to text outside existing <x>...</x> spans."""
    # Split into alternating [outside, tag, outside, tag, ...]
    parts = re.split(rf'(<{_TAG}[^>]*>.*?</{_TAG}>)', text,
                     flags=re.DOTALL)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:          # outside a tag — apply pattern
            out.append(re.sub(pattern, repl, part, **kwargs))
        else:                   # inside a tag — leave untouched
            out.append(part)
    return "".join(out)


def _protect(text: str) -> tuple[str, list[str]]:
    """
    Replace non-translatable content with <x id="N">...</x> tags.
    Returns (xml_string, list_of_original_spans).
    Protected content is HTML-escaped inside the tag so the XML is valid.
    Each step only matches outside already-protected spans.
    """
    protected: list[str] = []

    def ph(content: str) -> str:
        n = len(protected)
        protected.append(content)
        return f'<{_TAG} id="{n}">{html.escape(content, quote=False)}</{_TAG}>'

    # 1. YAML frontmatter (must be first — applied to raw text)
    text = re.sub(
        r'^(---\n.*?\n---\n)',
        lambda m: ph(m.group(1)),
        text, flags=re.DOTALL,
    )

    # 2. Fenced code blocks ```...```
    text = _sub_outside_tags(r'(```[\s\S]*?```)', lambda m: ph(m.group(1)), text)

    # 3. Inline code `...`
    text = _sub_outside_tags(r'(`[^`\n]+`)', lambda m: ph(m.group(1)), text)

    # 4. HTML comments <!-- ... -->
    text = _sub_outside_tags(r'(<!--[\s\S]*?-->)', lambda m: ph(m.group(1)), text)

    # 5a. Markdown autolinks <url> and <email> — invalid XML tags if left bare
    text = _sub_outside_tags(
        r'(<(?:https?://[^>]+|[^@>\s]+@[^@>\s]+)>)',
        lambda m: ph(m.group(1)), text,
    )

    # 5. Image links  ![alt](path){attrs}  — protect entirely
    text = _sub_outside_tags(
        r'(!\[[^\]]*\]\([^)]*\)(?:\{[^}]*\})?)',
        lambda m: ph(m.group(1)), text,
    )

    # 6. Text links  [display text](url){attrs}  — protect entirely so DeepL
    #    cannot mangle the display text (it refuses to translate link text and
    #    may insert typographic quotes around it).  Display texts are translated
    #    in a separate post-processing pass by _fix_all_link_texts().
    #    Negative lookbehind (?<!!) excludes images already protected above.
    text = _sub_outside_tags(
        r'((?<!!)\[[^\]\n]+\]\([^)]*\)(?:\{[^}]*\})?)',
        lambda m: ph(m.group(1)), text,
    )

    # 7. Bare URLs not already protected
    text = _sub_outside_tags(
        r'(?<![">])(https?://[^\s<"]+)',
        lambda m: ph(m.group(1)), text,
    )

    # 8. XML-escape bare & < > outside protected spans so the XML is valid.
    #    These are unescaped again in _restore after translation.
    _XML_ESCAPE = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}
    text = _sub_outside_tags(r'[&<>]', lambda m: _XML_ESCAPE[m.group(0)], text)

    return text, protected


def _restore(text: str, protected: list[str]) -> str:
    """
    Remove <x id="N">...</x> wrappers, restoring original content.
    Looks up by id attribute (robust against DeepL adding extra attributes).
    """
    def replace(m: re.Match) -> str:
        id_hit = re.search(r'\bid="(\d+)"', m.group(0))
        if id_hit:
            idx = int(id_hit.group(1))
            if idx < len(protected):
                return protected[idx]
        # Fallback: unescape whatever DeepL left inside the tag
        inner = re.sub(rf'<{_TAG}[^>]*>(.*?)</{_TAG}>', r'\1', m.group(0), flags=re.DOTALL)
        return html.unescape(inner)

    text = re.sub(rf'<{_TAG}[^>]*>.*?</{_TAG}>', replace, text, flags=re.DOTALL)
    # Safety: remove any orphaned closing tags left by DeepL reordering
    text = text.replace(f'</{_TAG}>', '')
    # Unescape XML entities we added in _protect step 8
    text = html.unescape(text)
    return text


# ── Pre-processing ───────────────────────────────────────────────────────────

def _expand_autolinks(text: str) -> str:
    """Convert <email> and <url> Markdown autolinks to explicit links.
    This avoids bare angle-bracket tags confusing DeepL's XML parser and
    also preserves surrounding whitespace correctly after translation."""
    # <email@domain> → [email@domain](mailto:email@domain)
    text = re.sub(r'<([^@>\s]+@[^@>\s]+)>', r'[\1](mailto:\1)', text)
    # <https://...> → [https://...](https://...)
    text = re.sub(r'<(https?://[^>]+)>', r'[\1](\1)', text)
    return text


def _translate_mailto_subjects(translator: deepl.Translator, text: str) -> str:
    """URL-decode mailto subject values, translate them, re-encode."""
    pattern = r'(mailto:[^)]*[?&](?:subject|body)=)([^&)#\s]+)'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text

    unique = list(dict.fromkeys(unquote(m.group(2)) for m in matches))
    results = translator.translate_text(unique, source_lang="EN", target_lang=TARGET_LANG)
    if isinstance(results, deepl.TextResult):
        results = [results]
    mapping = {orig: res.text for orig, res in zip(unique, results)}

    def replace(m: re.Match) -> str:
        decoded = unquote(m.group(2))
        translated = mapping.get(decoded, decoded)
        return m.group(1) + quote(translated, safe="")

    return re.sub(pattern, replace, text)


# ── Translation ───────────────────────────────────────────────────────────────

def _translate(translator: deepl.Translator, text: str) -> str:
    text = _expand_autolinks(text)
    text = _translate_mailto_subjects(translator, text)

    # Split on blank lines so DeepL never sees paragraph boundaries —
    # this prevents XML whitespace normalisation from collapsing them.
    blocks = text.split("\n\n")
    protected_blocks, stores = [], []
    for block in blocks:
        p, s = _protect(block)
        protected_blocks.append(p)
        stores.append(s)

    kwargs: dict = dict(
        source_lang="EN",
        target_lang=TARGET_LANG,
        tag_handling="xml",
        ignore_tags=[_TAG],
        outline_detection=False,
        split_sentences="nonewlines",
        formality=FORMALITY,
    )
    if GLOSSARY_ID:
        kwargs["glossary"] = GLOSSARY_ID

    # One API call with the full list of blocks
    results = translator.translate_text(protected_blocks, **kwargs)
    if isinstance(results, deepl.TextResult):
        results = [results]

    restored_blocks = [_restore(r.text, s) for r, s in zip(results, stores)]
    translated = "\n\n".join(restored_blocks)

    # Translate link display texts in a separate batch (DeepL refuses to
    # translate them inline when it recognises the [text](url) pattern).
    translated = _fix_internal_link_texts(translator, translated)

    # Strip spaces DeepL inserts inside [ display text ]
    translated = re.sub(r'\[\s*([^\]\n]+?)\s*\](\()', r'[\1]\2', translated)

    return translated


def _fix_internal_link_texts(translator: deepl.Translator, text: str) -> str:
    """Translate display texts of all links: [Some Title](page.md or https://...)."""
    pattern = r'\[([^\]\n]+)\](\([^)]*\)(?:\{[^}]*\})?)'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text

    unique_texts = list(dict.fromkeys(m.group(1).strip() for m in matches))
    kwargs: dict = dict(source_lang="EN", target_lang=TARGET_LANG, formality=FORMALITY)
    if GLOSSARY_ID:
        kwargs["glossary"] = GLOSSARY_ID
    results = translator.translate_text(unique_texts, **kwargs)
    if isinstance(results, deepl.TextResult):
        results = [results]
    mapping = {orig: res.text for orig, res in zip(unique_texts, results)}

    def replace(m: re.Match) -> str:
        original = m.group(1).strip()
        translated = mapping.get(original, original)
        return f"[{translated}]{m.group(2)}"

    return re.sub(pattern, replace, text)


def _char_count(text: str) -> int:
    """Approximate billable characters (protected spans count too in DeepL)."""
    return len(text)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Translate docs/en/*.md to docs/de/")
    parser.add_argument("--dry-run",       action="store_true", help="Count chars only, no API calls")
    parser.add_argument("--skip-existing", action="store_true", help="Skip files already in docs/de/")
    parser.add_argument("--file",          help="Translate a single file (filename only, e.g. people.md)")
    args = parser.parse_args()

    DST_DIR.mkdir(parents=True, exist_ok=True)

    if args.file:
        files = [SRC_DIR / args.file]
    else:
        files = sorted(SRC_DIR.glob("*.md"))

    if not files:
        print("No .md files found.", file=sys.stderr)
        sys.exit(1)

    if args.skip_existing:
        files = [f for f in files if not (DST_DIR / f.name).exists()]
        print(f"Skipping existing files; {len(files)} left to translate.")

    total_chars = sum(_char_count(f.read_text(encoding="utf-8")) for f in files)
    print(f"{len(files)} files, ~{total_chars:,} characters")

    if args.dry_run:
        print("Dry run — no API calls made.")
        return

    translator = deepl.Translator(API_KEY)
    usage = translator.get_usage()
    remaining = usage.character.limit - usage.character.count
    print(f"DeepL quota remaining: {remaining:,} chars")
    if total_chars > remaining:
        print("WARNING: estimated chars exceed remaining quota!", file=sys.stderr)

    for src in files:
        dst = DST_DIR / src.name
        text = src.read_text(encoding="utf-8")
        try:
            translated = _translate(translator, text)
            dst.write_text(translated, encoding="utf-8")
            print(f"  OK  {src.name}")
        except Exception as e:
            print(f"  ERR {src.name}: {e}", file=sys.stderr)

    usage2 = translator.get_usage()
    used = usage2.character.count - usage.character.count
    print(f"\nDone. Used {used:,} chars. Remaining: {usage2.character.limit - usage2.character.count:,}")


if __name__ == "__main__":
    main()
