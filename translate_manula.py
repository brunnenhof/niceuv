#!/usr/bin/env python3
"""
Translate a Manula XML export from English to another language using the DeepL API.

Preserves:
  - Textile formatting  (h1. h3. *bold* _italic_ # list etc.)
  - Manula tokens       {TOPIC-LINK+xxx}  {IMAGE-LINK+xxx}
  - Image embeds        !{IMAGE-LINK+...}!  !(caption){IMAGE-LINK+...}!
  - URLs in links       "display text":https://...  (URL part kept verbatim)

Usage:
    uv add deepl
    uv run python translate_manula.py input.xml --api-key YOUR_KEY
    uv run python translate_manula.py input.xml --api-key YOUR_KEY --output out.xml --target-lang DE --formality more
    # or set DEEPL_API_KEY env var instead of --api-key
    "428b236c-nnnn-49a8-bc0e-6d1b49aaca05:fx"
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import deepl
except ImportError:
    print("deepl not installed. Run: uv add deepl", file=sys.stderr)
    sys.exit(1)

# Placeholder template for protected spans (plain-text mode)
_PH = "%%{}%%"


# ── XML helpers ───────────────────────────────────────────────────────────────

def _xml_unescape(s: str) -> str:
    return (s
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'"))


# ── Core: protect → translate → restore ──────────────────────────────────────

def _collect_protected_spans(text: str) -> list[tuple[int, int]]:
    """Return sorted, non-overlapping (start, end) spans that must NOT be translated."""
    spans: list[tuple[int, int]] = []

    # 1. Image embeds  !(optional-attrs){IMAGE-LINK+...}!
    for m in re.finditer(r'!(?:\([^)]*\))?\{IMAGE-LINK\+[^}]+\}!', text):
        spans.append((m.start(), m.end()))

    # 2. Standalone Manula tokens  {TOPIC-LINK+xxx}  {IMAGE-LINK+xxx}
    for m in re.finditer(r'\{(?:TOPIC-LINK|IMAGE-LINK)\+[^}]+\}', text):
        spans.append((m.start(), m.end()))

    # 3. URL part only of Textile links  "display text":https://...
    #    We protect just the URL so the display text IS translated.
    for m in re.finditer(r'"[^"\n]+":(https?://[^\s\n]*)', text):
        spans.append((m.start(1), m.end(1)))

    # Sort and drop overlapping spans (first one wins)
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s < merged[-1][1]:
            continue  # overlaps previous span, skip
        merged.append((s, e))

    return merged


def _build_protected_plain(text: str) -> tuple[str, dict[str, str]]:
    """Replace non-translatable spans with %%N%% placeholders.
    Returns (modified text, mapping of placeholder → original span).
    Plain text (no XML) so DeepL never does link-anchor detection.
    """
    spans = _collect_protected_spans(text)
    store: dict[str, str] = {}
    parts: list[str] = []
    last = 0
    for i, (s, e) in enumerate(spans):
        parts.append(text[last:s])
        key = _PH.format(i)
        store[key] = text[s:e]
        parts.append(key)
        last = e
    parts.append(text[last:])
    return "".join(parts), store


def _translate_field(translator: deepl.Translator, text: str,
                     target_lang: str, formality: str) -> str:
    """Translate one Textile/Manula text field via DeepL, protecting special tokens."""
    if not text or not text.strip():
        return text

    protected, store = _build_protected_plain(text)

    kwargs: dict = dict(
        source_lang="EN",
        target_lang=target_lang,
        outline_detection=False,
        split_sentences="nonewlines",
    )
    if formality != "default":
        kwargs["formality"] = formality

    result = translator.translate_text(protected, **kwargs)
    translated = result.text
    for key, original in store.items():
        translated = translated.replace(key, original)
    print(translated)
    return translated


# ── XML I/O ───────────────────────────────────────────────────────────────────

def _write_with_cdata(tree: ET.ElementTree, output_path: Path) -> None:
    """Write XML, wrapping translated field content back in CDATA sections."""
    tree.write(str(output_path), encoding="unicode", xml_declaration=True)
    raw = output_path.read_text(encoding="utf-8")

    def wrap_cdata(m: re.Match) -> str:
        open_tag = m.group(1)
        content  = _xml_unescape(m.group(2))  # undo ElementTree's escaping
        close_tag = m.group(3)
        return f'{open_tag}<![CDATA[{content}]]>{close_tag}'

    raw = re.sub(
        r'(<(?:title|content|keywords) translate="yes">)(.*?)(</(?:title|content|keywords)>)',
        wrap_cdata,
        raw,
        flags=re.DOTALL,
    )
    output_path.write_text(raw, encoding="utf-8")


# ── Main routine ──────────────────────────────────────────────────────────────

def translate_manula_xml(input_path: Path, output_path: Path,
                         api_key: str, target_lang: str, formality: str) -> None:
    translator = deepl.Translator(api_key)

    usage = translator.get_usage()
    print(f"DeepL usage before: {usage.character.count:,} / {usage.character.limit:,} chars")

    tree = ET.parse(input_path)
    root = tree.getroot()

    topics = root.findall(".//topic")
    print(f"Translating {len(topics)} topics → {target_lang} (formality={formality})\n")

    total_chars = 0
    for topic in topics:
        tid = topic.findtext("id", "?")
        for field_name in ("title", "content", "keywords"):
            field = topic.find(field_name)
            if field is None or field.get("translate") != "yes":
                continue
            if not field.text or not field.text.strip():
                continue

            n = len(field.text)
            total_chars += n
            print(f"  [{tid}] {field_name} ({n} chars) … ", end="", flush=True)
            field.text = _translate_field(translator, field.text, target_lang, formality)
            print("OK")

    print(f"\nTotal chars sent: {total_chars:,}")
    _write_with_cdata(tree, output_path)
    print(f"Output written → {output_path}")


def main() -> None:
#    parser = argparse.ArgumentParser(
#        description="Translate a Manula XML export using the DeepL API"
#    )
#    parser.add_argument("input",          help="Input XML file")
#    parser.add_argument("--output",  "-o", help="Output XML file (default: <input>_<lang>.xml)")
#    parser.add_argument("--api-key", "-k", help="DeepL API key (or set DEEPL_API_KEY env var)")
#    parser.add_argument("--target-lang", "-t", default="DE",
#                        help="DeepL target language code, e.g. DE FR NB (default: DE)")
#    parser.add_argument("--formality", "-f",
#                        choices=["default", "more", "less", "prefer_more", "prefer_less"],
#                        default="default",
#                        help="Formality for languages that support it (default: default)")
#    args = parser.parse_args()
#
#    api_key = args.api_key or os.environ.get("DEEPL_API_KEY")
#    if not api_key:
#        print("Error: DeepL API key required (--api-key or DEEPL_API_KEY env var).", file=sys.stderr)
#        sys.exit(1)
#
#    input_path = Path(args.input)
#    if not input_path.exists():
#        print(f"Error: File not found: {input_path}", file=sys.stderr)
#        sys.exit(1)
#
#    lang_suffix = args.target_lang.lower().replace("-", "_")
#    output_path = Path(args.output) if args.output else \
#        input_path.with_name(f"{input_path.stem}_{lang_suffix}.xml")

#    translate_manula_xml(input_path, output_path, api_key, args.target_lang, args.formality)
    translate_manula_xml("scratch/manula_uk_de_260402.xml", "scratch/out.xml", "428b236c-2ac9-49a8-bc0e-6d1b49aaca05:fx", "DE", "less")


if __name__ == "__main__":
    main()
