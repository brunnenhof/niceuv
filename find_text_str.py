"""
find_text_str.py
Scan toy.py for hardcoded human-visible strings in NiceGUI UI calls.
Reports line number, call type, and the string found.
"""

import re
import sys

TARGET = "toy.py"

# ── patterns ──────────────────────────────────────────────────────────────────

# Positional string in ui.XXX("string" ...)
# Captures: widget name + the string literal (single or double quoted)
UI_POSITIONAL = re.compile(
    r'ui\.(label|button|markdown|notify|tooltip|badge|expansion|html|tab)\s*\(\s*'
    r'(?:f?)(["\'])((?:(?!\2).|\\.)*)\2',
)

# Keyword arguments that carry visible text
UI_KWARG = re.compile(
    r'\b(placeholder|label|title|message|caption|content|text)\s*=\s*'
    r'(?:f?)(["\'])((?:(?!\2).|\\.)*)\2',
)

# ── filters ───────────────────────────────────────────────────────────────────

# Skip strings that look like Tailwind classes, icon names, colors, or are empty
SKIP_RE = re.compile(
    r'^$'                        # empty
    r'|^[a-z_-]+$'              # single lowercase word (likely icon name)
    r'|^[\w\s\-:/\.]+px'        # CSS sizes
    r'|text-|bg-|p-\d|m-\d|w-|h-|gap-|flex|grid|items-|justify-|font-|rounded'
    r'|^#[0-9a-fA-F]{3,6}$'    # hex colour
    r'|luf\.'                   # already translated
    r'|\{.*\}'                  # pure f-string interpolation (no literal text)
)

def is_skip(s: str) -> bool:
    s = s.strip()
    if not s:
        return True
    if SKIP_RE.search(s):
        return True
    # Mostly braces / format placeholders → not human text
    non_brace = re.sub(r'\{[^}]*\}', '', s).strip()
    if not non_brace:
        return True
    return False

# ── scan ──────────────────────────────────────────────────────────────────────

results = []

with open(TARGET, encoding="utf-8") as fh:
    for lineno, line in enumerate(fh, 1):
        stripped = line.strip()
        # skip comment lines
        if stripped.startswith("#"):
            continue

        for m in UI_POSITIONAL.finditer(line):
            widget, _, text = m.group(1), m.group(2), m.group(3)
            if not is_skip(text):
                results.append((lineno, f"ui.{widget}()", text))

        for m in UI_KWARG.finditer(line):
            kw, _, text = m.group(1), m.group(2), m.group(3)
            if not is_skip(text):
                results.append((lineno, f"{kw}=", text))

# ── report ────────────────────────────────────────────────────────────────────

print(f"{'Line':>6}  {'Call':<20}  Text")
print("-" * 80)
for lineno, call, text in results:
    # Truncate long strings for readability
    display = text if len(text) <= 60 else text[:57] + "..."
    print(f"{lineno:>6}  {call:<20}  {display}")
#    print(display)

print(f"\n{len(results)} hardcoded strings found in {TARGET}")
