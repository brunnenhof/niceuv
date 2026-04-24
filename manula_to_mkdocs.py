#!/usr/bin/env python3
"""
Convert Manula XML export(s) to MkDocs Markdown files.

Usage:
    uv run python manula_to_mkdocs.py --en scratch/manula_uk_de_260402.xml
    uv run python manula_to_mkdocs.py \
        --en scratch/manula_uk_de_260402.xml \
        --de scratch/manula_uk_de_260402_reviewed.xml \
        --out docs

Output structure:
    docs/
      en/
        the-point-of-the-game.md
        ...
      de/
        the-point-of-the-game.md   (same slugs, German content)
      assets/
        images/                    (place downloaded Manula images here)
    mkdocs.yml                     (generated nav skeleton)
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# ── Manula-slug → generated-file-slug mapping ────────────────────────────────
# Keys = {TOPIC-LINK+KEY} values found in Manula content.
# Values = the filename slug (without .md) that this script generates.
# Extend/override as needed when you add topics.
MANULA_SLUG_MAP: dict[str, str] = {
    "2-szenarien":              "two-scenarios",
    "bip":                      "gdp",
    "carbontax":                "carbon-tax-vs-cap-and-trade-example",
    "engage":                   "engage-players-in-conversation-discussion-and-negotiation",
    "eroi-ag":                  "the-energy-cost-of-feeding-the-world",
    "escimo":                   "emissions-and-temperature",
    "exps":                     "expand-policy-space",
    "fc":                       "off-balance-sheet-financing",
    "fmpldd":                   "fraction-of-credit-with-private-lenders-not-drawn-down-per-year",
    "ictr":                     "increase-consumption-tax-rate",
    "ineq":                     "inequality-and-social-tension",
    "lizenz":                   "licence",
    "lpb":                      "lending-from-public-bodies-lpb",
    "lpbgrant":                 "lpb-funds-given-as-loans-or-grants",
    "nep":                      "pensions-to-all",        # best guess – verify
    "people":                   "people",
    "power":                    "let-players-experience-differences-in-power",
    "rounds":                   "rounds",
    "sdgs":                     "let-players-learn-about-the-un-sustainable-development-goals",
    "sliders":                  "policy-sliders",
    "strup":                    "strengthen-unions",
    "systems":                  "lead-players-from-one-simple-causal-feedbackloop-to-a-systems-understanding",
    "technology":               "technology",
    "tow":                      "taxing-owners-wealth",
    "wie-lese-ich-eine-grafik": "how-do-i-read-a-graph",
    "wreaction":                "worker-reaction",
    "xtaxcom":                  "introduce-a-universal-basic-dividend",
    "xtaxrateemp":              "increase-worker-income-tax-rate",
}

# Image assets base path relative to each language doc file.
# With docs/en/page.md, images at docs/assets/images/ → "../../assets/images/"
IMAGES_REL_PATH = "../assets/images"


# ── Slug generation ───────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    """Turn a topic title into a filename-safe slug."""
    s = title.lower()
    s = re.sub(r"[äÄ]", "ae", s)
    s = re.sub(r"[öÖ]", "oe", s)
    s = re.sub(r"[üÜ]", "ue", s)
    s = re.sub(r"ß", "ss", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


# ── Textile → Markdown ────────────────────────────────────────────────────────

def _replace_image(m: re.Match) -> str:
    caption = m.group(1) or ""
    name = m.group(2)
    alt = caption if caption else name
    return f"![{alt}]({IMAGES_REL_PATH}/{name}.png)"


def _replace_topic_link(m: re.Match, unresolved: set[str]) -> str:
    display = m.group(1).strip()
    slug = m.group(2)
    target_slug = MANULA_SLUG_MAP.get(slug)
    if target_slug is None:
        unresolved.add(slug)
        target_slug = slug          # keep the Manula slug as-is so it's visible
    return f"[{display}]({target_slug}.md)"


def textile_to_markdown(text: str, unresolved: set[str]) -> str:
    """Convert a Textile/Manula content field to Markdown."""
    lines = text.split("\n")
    out: list[str] = []

    for line in lines:
        # ── Block-level headings ──────────────────────────────────────────
        for level in (1, 2, 3, 4, 5, 6):
            prefix = f"h{level}. "
            if line.startswith(prefix):
                line = "#" * level + " " + line[len(prefix):]
                break

        # ── Numbered list: "# item" → "1. item" ──────────────────────────
        # Only at line start and followed by space (avoid URLs like #anchor)
        if re.match(r"^# ", line):
            line = "1. " + line[2:]

        # ── Bulleted list: "* item" → "- item" ───────────────────────────
        # Only at line start; bold *text* handled below for inline occurrences
        if re.match(r"^\* ", line):
            line = "- " + line[2:]

        # ── Inline: images (before link patterns) ────────────────────────
        # !(caption){IMAGE-LINK+name}!
        line = re.sub(
            r"!\(([^)]*)\)\{IMAGE-LINK\+([^}]+)\}!",
            _replace_image,
            line,
        )
        # !{IMAGE-LINK+name}!
        line = re.sub(
            r"!\{IMAGE-LINK\+([^}]+)\}!",
            lambda m: f"![{m.group(1)}]({IMAGES_REL_PATH}/{m.group(1)}.png)",
            line,
        )

        # ── Textile links with TOPIC-LINK ─────────────────────────────────
        line = re.sub(
            r'"([^"\n]+)":\s*\{(?:TOPIC-LINK|IMAGE-LINK)\+([^}]+)\}',
            lambda m: _replace_topic_link(m, unresolved),
            line,
        )

        # ── Textile links with URL ────────────────────────────────────────
        # Exclude trailing punctuation from URL span (,.)
        line = re.sub(
            r'"([^"\n]+)":\s*(https?://[^\s\n]*?)([,.)]*(?:\s|$))',
            lambda m: f"[{m.group(1)}]({m.group(2)}){m.group(3)}",
            line,
        )
        # mailto
        line = re.sub(
            r'"([^"\n]+)":\s*(mailto:[^\s\n]*)',
            lambda m: f"[{m.group(1)}]({m.group(2)})",
            line,
        )

        # ── Inline bold *text* → **text** ─────────────────────────────────
        # Use a non-greedy match; skip if only one char (avoid false positives)
        line = re.sub(r"\*([^*\n]{1,}?)\*", r"**\1**", line)

        # ── Inline italic _text_ → *text* ────────────────────────────────
        line = re.sub(r"_([^_\n]{1,}?)_", r"*\1*", line)

        # ── Blank line before list items ──────────────────────────────────
        # Python-Markdown requires a blank line before a list that follows
        # a non-empty, non-list paragraph line.
        is_list = bool(re.match(r"^(1\.|- )", line))
        prev = out[-1] if out else ""
        prev_is_list = bool(re.match(r"^(1\.|- |\d+\.)", prev))
        if is_list and prev.strip() and not prev_is_list:
            out.append("")

        out.append(line)

    return "\n".join(out)


# ── XML helpers ───────────────────────────────────────────────────────────────

def _read_topics(xml_path: Path) -> list[dict]:
    """Parse Manula XML, return list of topic dicts."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    topics = []
    for el in root.findall(".//topic"):
        topics.append({
            "id":       el.findtext("id", ""),
            "title":    el.findtext("title", ""),
            "content":  el.findtext("content", ""),
            "keywords": el.findtext("keywords", ""),
        })
    return topics


# ── Writer ────────────────────────────────────────────────────────────────────

def write_lang(topics: list[dict], id_to_slug: dict[str, str],
               lang: str, out_dir: Path,
               unresolved: set[str]) -> list[tuple[str, str]]:
    """
    Write one .md file per topic into out_dir/lang/.
    Returns list of (slug, title) in document order for nav generation.
    """
    lang_dir = out_dir / lang
    lang_dir.mkdir(parents=True, exist_ok=True)

    nav_entries: list[tuple[str, str]] = []
    for t in topics:
        slug = id_to_slug[t["id"]]
        title = t["title"].strip()
        content = t["content"].strip()
        keywords = t["keywords"].strip()

        md_lines = [f"# {title}", ""]
        if content:
            md_lines.append(textile_to_markdown(content, unresolved))
        if keywords:
            md_lines += ["", f"<!-- keywords: {keywords} -->"]
        md_lines.append("")        # trailing newline

        md_path = lang_dir / f"{slug}.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        nav_entries.append((slug, title))

    return nav_entries


# ── Nav hierarchy ─────────────────────────────────────────────────────────────
#
# Each element is either:
#   str              → leaf page (slug)
#   (str, list)      → section whose header IS a page (slug) + children
#
# This mirrors the Manula table of contents exactly.
# Children follow the same rules recursively.

NAV_STRUCTURE = [
    ("the-point-of-the-game", [
        "two-scenarios",
        "thanks",
    ]),
    ("ways-to-play-the-game", [
        "let-players-learn-about-the-un-sustainable-development-goals",
        "engage-players-in-conversation-discussion-and-negotiation",
        "let-players-experience-differences-in-power",
        ("lead-players-from-one-simple-causal-feedbackloop-to-a-systems-understanding", [
            "inequality-and-social-tension",
            "emissions-and-temperature",
            "carbon-tax-vs-cap-and-trade-example",
        ]),
    ]),
    ("what-you-need-to-play", [
        "people",
        "place",
        "technology",
        "privacy",
    ]),
    ("gameplay", [
        "rounds",
        "how-do-i-read-a-graph",
        "policy-sliders",
    ]),
    ("policies-in-depth", [
        "expand-policy-space",
        "lending-from-public-bodies-lpb",
        "lpb-split-the-use-of-funds-from-public-lenders",
        "lpb-funds-given-as-loans-or-grants",
        "fraction-of-credit-with-private-lenders-not-drawn-down-per-year",
        "taxing-owners-wealth",
        "cancel-debt-from-public-lenders",
        "leakage-fraction-reduction",
        "stretch-repayment",
        "extra-taxes-paid-by-the-super-rich",
        "strengthen-unions",
        "worker-reaction",
        "introduce-a-universal-basic-dividend",
        "increase-consumption-tax-rate",
        "increase-owner-income-tax-rate",
        "increase-worker-income-tax-rate",
        "introduce-a-carbon-tax",
        "shift-govt-spending-to-investment",
        "education-to-all",
        "female-leadership",
        "pensions-to-all",
        "food-waste-reduction",
        "regenerative-agriculture",
        "change-diets",
        "reduce-food-imports",
        "max-forest-cutting",
        "reforestation",
        "energy-system-efficiency",
        "electrify-everything",
        "invest-in-renewables",
        "ccs-is-carbon-capture-and-storage-at-source",
        "direct-air-capture",
    ]),
    ("glossary", [
        "gdp",
        "off-balance-sheet-financing",
        "the-energy-cost-of-feeding-the-world",
    ]),
    "licence",
    "impressum-legal",
]


# ── mkdocs.yml generation ─────────────────────────────────────────────────────

_LANG_LABELS = {"en": "English", "de": "Deutsch", "fr": "Français", "no": "Norsk"}

_MKDOCS_HEADER = """\
site_name: SimFuture - Manual
site_url: https://blue-way.net/simfuture/
docs_dir: docs
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.indexes
    - toc.integrate

plugins:
  - search

"""


def _nav_block(node, lang: str, titles: dict[str, str], indent: int) -> list[str]:
    """Recursively render one NAV_STRUCTURE node as mkdocs.yml lines."""
    pad = "  " * indent
    lines: list[str] = []
    if isinstance(node, str):
        slug = node
        title = titles.get(slug, slug).replace("'", "\\'")
        lines.append(f"{pad}- '{title}': {lang}/{slug}.md")
    else:
        slug, children = node
        title = titles.get(slug, slug).replace("'", "\\'")
        lines.append(f"{pad}- '{title}':")
        # Section header page first
        lines.append(f"{pad}    - '{title}': {lang}/{slug}.md")
        for child in children:
            lines.extend(_nav_block(child, lang, titles, indent + 2))
    return lines


def write_mkdocs_yml(lang_navs: dict[str, list[tuple[str, str]]],
                     out_dir: Path) -> None:
    """lang_navs: {lang: [(slug, title), ...]} in document order."""
    lines = [_MKDOCS_HEADER, "nav:"]
    for lang, entries in lang_navs.items():
        label = _LANG_LABELS.get(lang, lang.upper())
        titles = {slug: title for slug, title in entries}
        lines.append(f"  - {label}:")
        for node in NAV_STRUCTURE:
            lines.extend(_nav_block(node, lang, titles, indent=2))
    lines.append("")

    yml_path = out_dir.parent / "mkdocs.yml"
    yml_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"mkdocs.yml written -> {yml_path}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Manula XML export(s) to MkDocs Markdown"
    )
    parser.add_argument("--en",  required=True, help="EN source XML (defines topic order & slugs)")
    parser.add_argument("--de",  help="DE translation XML")
    parser.add_argument("--fr",  help="FR translation XML")
    parser.add_argument("--no",  dest="no_", help="NO translation XML")
    parser.add_argument("--out", default="docs", help="Output root directory (default: docs)")
    args = parser.parse_args()

    out_dir = Path(args.out)

    # EN is always written
    lang_files: list[tuple[str, Path]] = [("en", Path(args.en))]
    for lang, path_str in [("de", args.de), ("fr", args.fr), ("no", args.no_)]:
        if path_str:
            lang_files.append((lang, Path(path_str)))

    # Read EN first – it defines the canonical topic order and slug generation
    en_topics = _read_topics(lang_files[0][1])

    # Build id → slug from EN titles
    id_to_slug: dict[str, str] = {}
    seen_slugs: set[str] = set()
    for t in en_topics:
        base = slugify(t["title"])
        slug = base
        n = 2
        while slug in seen_slugs:       # deduplicate (unlikely but safe)
            slug = f"{base}-{n}"
            n += 1
        seen_slugs.add(slug)
        id_to_slug[t["id"]] = slug

    unresolved: set[str] = set()
    lang_navs: dict[str, list[tuple[str, str]]] = {}

    for lang, xml_path in lang_files:
        if not xml_path.exists():
            print(f"Warning: {xml_path} not found - skipping {lang}", file=sys.stderr)
            continue
        topics = _read_topics(xml_path)
        nav = write_lang(topics, id_to_slug, lang, out_dir, unresolved)
        lang_navs[lang] = nav
        print(f"[{lang}] {len(topics)} topics -> {out_dir}/{lang}/")

    if unresolved:
        print(f"\nWarning - unresolved TOPIC-LINKs (add to MANULA_SLUG_MAP):")
        for s in sorted(unresolved):
            print(f"  {s!r}")

    write_mkdocs_yml(lang_navs, out_dir)

    # Create assets/images placeholder
    assets_dir = out_dir / "assets" / "images"
    assets_dir.mkdir(parents=True, exist_ok=True)
    readme = assets_dir / "README.txt"
    if not readme.exists():
        readme.write_text(
            "Place downloaded Manula image files here.\n"
            "Filenames should match the IMAGE-LINK slugs, e.g. ineq.png, escimo1.png\n",
            encoding="utf-8",
        )

    print(f"\nPlace Manula images in: {assets_dir}")
    print("Done.")


if __name__ == "__main__":
    main()
