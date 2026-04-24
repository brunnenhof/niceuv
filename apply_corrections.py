"""
apply_corrections.py
Applies corrections JSON to luf.py and writes a corrected copy.

Strategy: use AST line numbers only (never col_offset) to locate variable
blocks, get original values from the imported module, generate fresh
assignment text.  Avoids all UTF-8 byte vs. Unicode char offset issues.

Usage:
    uv run python apply_corrections.py fr
    uv run python apply_corrections.py no
    uv run python apply_corrections.py de_inf
"""
import ast
import importlib.util
import json
import sys
from pathlib import Path

LUF_PATH   = Path("files/luf.py")
LANG_CODES = ["en", "de", "de_inf", "fr", "no"]


# ── helpers ───────────────────────────────────────────────────────────────────

def load_luf():
    spec = importlib.util.spec_from_file_location("luf_orig", LUF_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fmt_str(v: str) -> str:
    """Format a string value for Python source output."""
    if "\n" in v:
        # Triple-quoted, preserve leading/trailing newlines exactly
        return f'"""{v}"""'
    return json.dumps(v, ensure_ascii=False)


def fmt_list(varname: str, lst: list) -> str:
    lines = [f"{varname} = [\n"]
    for item in lst:
        lines.append(f"    {fmt_str(item)},\n")
    lines.append("]\n")
    return "".join(lines)


def fmt_inner_dict(d: dict) -> str:
    """Format a {tag: text} dict as Python source (indented for use inside an outer dict)."""
    lines = ["{\n"]
    for k, v in d.items():
        lines.append(f"        {json.dumps(k)}: {fmt_str(v)},\n")
    lines.append("    }")
    return "".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main(target_lang: str):
    corrections_file = Path("corrections") / f"corrections_{target_lang}.json"
    if not corrections_file.exists():
        print(f"No corrections file found: {corrections_file}")
        return

    corrections: dict = json.loads(corrections_file.read_text(encoding="utf-8"))
    if not corrections:
        print("Corrections file is empty — nothing to do.")
        return

    luf      = load_luf()
    source   = LUF_PATH.read_text(encoding="utf-8")
    tree     = ast.parse(source)
    src_lines = source.splitlines(keepends=True)
    tgt_idx  = LANG_CODES.index(target_lang)

    # Map: (start_line_0indexed, end_line_exclusive) → replacement_text
    line_replacements: dict[tuple[int, int], str] = {}

    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        if not isinstance(stmt.targets[0], ast.Name):
            continue
        varname = stmt.targets[0].id
        value   = stmt.value
        s_ln    = stmt.lineno - 1       # 0-indexed slice start
        e_ln    = stmt.end_lineno       # exclusive slice end

        # ── 5-element list with a direct correction ────────────────────────
        if (isinstance(value, ast.List)
                and len(value.elts) == 5
                and varname in corrections):
            orig = getattr(luf, varname, None)
            if not isinstance(orig, list) or len(orig) != 5:
                continue
            corrected       = list(orig)
            corrected[tgt_idx] = corrections[varname]
            line_replacements[(s_ln, e_ln)] = fmt_list(varname, corrected)

        # ── dict {lang: {tag: text}} with per-tag corrections ─────────────
        elif isinstance(value, ast.Dict):
            for k_node, v_node in zip(value.keys, value.values):
                if not (isinstance(k_node, ast.Constant)
                        and k_node.value == target_lang):
                    continue
                if not isinstance(v_node, ast.Dict):
                    continue
                # Collect applicable tag corrections
                tag_fixes = {
                    sk.value: corrections[f"{varname}::{sk.value}"]
                    for sk in v_node.keys
                    if isinstance(sk, ast.Constant)
                    and f"{varname}::{sk.value}" in corrections
                }
                if not tag_fixes:
                    continue
                orig_dict = getattr(luf, varname, None)
                if not isinstance(orig_dict, dict) or target_lang not in orig_dict:
                    continue
                orig_sub = dict(orig_dict[target_lang])
                for tag, new_val in tag_fixes.items():
                    orig_sub[tag] = new_val
                # Replace only the inner-dict lines (v_node lines)
                v_s = v_node.lineno - 1
                v_e = v_node.end_lineno
                line_replacements[(v_s, v_e)] = fmt_inner_dict(orig_sub) + "\n"

    if not line_replacements:
        print("No matching entries found. Check variable names in corrections file.")
        return

    # Apply: walk source lines, substitute replacement blocks
    sorted_ranges = sorted(line_replacements)
    output = []
    i = 0
    while i < len(src_lines):
        replaced = False
        for (s, e) in sorted_ranges:
            if i == s:
                output.append(line_replacements[(s, e)])
                i = e
                replaced = True
                break
        if not replaced:
            output.append(src_lines[i])
            i += 1

    result   = "".join(output)
    out_path = Path(f"files/luf_corrected_{target_lang}.py")
    out_path.write_text(result, encoding="utf-8")
    print(f"Written {len(line_replacements)} corrections → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("fr", "no", "de_inf"):
        print("Usage: uv run python apply_corrections.py fr|no|de_inf")
        sys.exit(1)
    main(sys.argv[1])
