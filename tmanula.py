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
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import time

try:
    import deepl
except ImportError:
    print("deepl not installed. Run: uv add deepl", file=sys.stderr)
    sys.exit(1)

# Short XML tag name used as DeepL ignore tag
_NOTRANSLATE = "x"


# ── XML helpers ───────────────────────────────────────────────────────────────

def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    #    Exclude trailing punctuation (,.) from the URL span to avoid double punctuation.
    for m in re.finditer(r'"[^"\n]+":(https?://[^\s\n]*?)([,.)]*(?:\s|$))', text):
        spans.append((m.start(1), m.end(1)))

    # Sort and drop overlapping spans (first one wins)
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s < merged[-1][1]:
            continue  # overlaps previous span, skip
        merged.append((s, e))

    return merged


def _build_protected_xml(text: str) -> str:
    """
    Build an XML string where non-translatable spans are wrapped in <x>...</x>
    and the rest is XML-escaped.  The whole thing is wrapped in <root>.
    """
    spans = _collect_protected_spans(text)
    parts: list[str] = ["<root>"]
    last = 0
    for s, e in spans:
        parts.append(_xml_escape(text[last:s]))
        parts.append(f"<{_NOTRANSLATE}>{_xml_escape(text[s:e])}</{_NOTRANSLATE}>")
        last = e
    parts.append(_xml_escape(text[last:]))
    parts.append("</root>")
    return "".join(parts)

def _extract_from_protected_xml(xml_str: str) -> str:
    xml_str = xml_str.strip()
    xml_str = re.sub(r'^<root>(.*)</root>$', r'\1', xml_str, flags=re.DOTALL)
    xml_str = re.sub(rf'<{_NOTRANSLATE}[^>]*>(.*?)</{_NOTRANSLATE}>', r'\1', xml_str, flags=re.DOTALL)
    return _xml_unescape(xml_str)


def _fix_topic_link_display_texts(translator: deepl.Translator, text: str,
                                   target_lang: str, formality: str,
                                   glossary_id: str | None = None) -> str:
    """Post-processing: translate display texts of {TOPIC-LINK+xxx} links.

    DeepL skips anchor text in "text":{TOPIC-LINK+xxx} patterns during the main
    translation pass.  This function collects those display texts, translates them
    in one batch call, and substitutes them back.
    """
    # Match both ASCII " and typographic quotes „ " " that DeepL inserts
    _oq = r'["\u201c\u201e]'   # opening: " „ "
    _cq = r'["\u201c\u201d]'   # closing:  " " "
    pattern = rf'{_oq}([^"\u201c\u201d\u201e\n]+){_cq}:\s*(\{{(?:TOPIC-LINK|IMAGE-LINK)\+[^}}]+\}})'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text

    # Unique display texts, order-preserving
    unique_texts = list(dict.fromkeys(m.group(1) for m in matches))

    kwargs: dict = dict(source_lang="EN", target_lang=target_lang)
    if formality != "default":
        kwargs["formality"] = formality
    if glossary_id:
        kwargs["glossary"] = glossary_id
    results = translator.translate_text(unique_texts, **kwargs)
    if isinstance(results, deepl.TextResult):
        results = [results]

    mapping = {orig: res.text for orig, res in zip(unique_texts, results)}

    def replace(m: re.Match) -> str:
        return f'"{mapping.get(m.group(1), m.group(1))}":{m.group(2)}'

    return re.sub(pattern, replace, text)


def _translate_field(translator: deepl.Translator, text: str,
                     target_lang: str, formality: str,
                     glossary_id: str | None = None) -> str:
    """Translate one Textile/Manula text field via DeepL, protecting special tokens."""
    if not text or not text.strip():
        return text

    protected_xml = _build_protected_xml(text)

    kwargs: dict = dict(
        source_lang="EN",
        target_lang=target_lang,
        tag_handling="xml",
        ignore_tags=[_NOTRANSLATE],
        outline_detection=False,
        split_sentences="nonewlines",   # preserve line-break structure
    )
    if formality != "default":
        kwargs["formality"] = formality
    if glossary_id:
        kwargs["glossary"] = glossary_id

#    result = text + '_test_'
#    print(result)
#    return result
    result = translator.translate_text(protected_xml, **kwargs)
    translated = _extract_from_protected_xml(result.text)
    translated = _fix_topic_link_display_texts(translator, translated, target_lang, formality, glossary_id)
    # Restore ASCII quotes in Textile links: „text":url or "text":url → "text":url
    translated = re.sub(r'[\u201c\u201e]([^\u201c\u201d\u201e\n]+)[\u201c\u201d]:(https?://)',
                        r'"\1":\2', translated)
    # Remove space DeepL inserts between closing quote and URL: "text": https:// → "text":https://
    translated = re.sub(r'"([^"\n]+)":\s+(https?://)', r'"\1":\2', translated)
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

def translate_manula_xml(input_path, output_path,
                         api_key: str, target_lang: str, formality: str,
                         glossary_id: str | None = None) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)
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
            field.text = _translate_field(translator, field.text, target_lang, formality, glossary_id)
            print("OK... sleep 2 sec")
            time.sleep(2)

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
    api_key = os.environ.get("DEEPL_API_KEY")
    if not api_key:
        print("Error: set DEEPL_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    glossary_id = os.environ.get("DEEPL_GLOSSARY_ID")
    translate_manula_xml("scratch/manula_uk_de_260402.xml", "scratch/out.xml", api_key, "DE", "less",
                         glossary_id=glossary_id)


if __name__ == "__main__":
    main()
