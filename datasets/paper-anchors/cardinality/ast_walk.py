#!/usr/bin/env python3
"""
AST walker for T-R1-10-R3-04 (N_free parameter provenance).

READ-ONLY. Does not import / execute engine code. Uses ast.parse + regex only.

Scans Musical_Intelligence/**/*.py and extracts every numerical constant:
 - Module-level assignments (including tuples/lists/dicts of numbers)
 - Class attribute declarations with numerical defaults
 - Dataclass field() defaults with numerical values
 - Function default arguments with numerical values
 - Dict literals mapping strings to numerical values

Output columns:
  file_path,line,scope,name,value,dtype,context_before,context_after,
  has_citation_in_context,has_citation_author,has_citation_year

No classification performed here; classification in classify.py.
"""
from __future__ import annotations

import ast
import csv
import re
import sys
from pathlib import Path

ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Musical_Intelligence")
OUT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R1-10-R3-04")
OUT.mkdir(parents=True, exist_ok=True)

# Regex for author-year citation patterns in comments / docstrings
CITATION_RE = re.compile(
    r"(?P<author>[A-Z][A-Za-z\-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z\-]+)?"
    r"(?:\s+et\s+al\.?)?)\s*"
    r"(?P<year>\(?\d{4}[a-z]?\)?)"
)

# Known citation-token bag (author surnames frequently cited in engine).
KNOWN_CITATION_TOKENS = {
    "sethares", "plomp", "levelt", "krumhansl", "kessler", "stumpf",
    "helmholtz", "kuttruff", "stevens", "terhardt", "parncutt", "moore",
    "bidelman", "bregman", "shepard", "bowling", "koelsch", "zatorre",
    "salimpoor", "ferreri", "schultz", "friston", "pearce", "cheung",
    "jakubowski", "janata", "huron", "grahn", "witek", "mcadams",
    "bastos", "rao", "ballard", "dayan", "herrero", "marjieh", "eerola",
    "iec", "zwicker", "a-weighting", "stumpf", "kuttruff", "patel",
    "rohrmeier", "kim", "juslin", "vastfjall", "sammler", "belin",
    "griffiths", "warren", "mas-herrero", "pauli", "edlow", "bornstein",
    "coffey", "doelling", "ding", "simon", "chandrasekaran", "kraus",
    "blood", "schirmer", "shapiro", "poeppel", "hickok", "sugimoto",
    "haueisen", "schnupp", "yeshurun", "jacoby", "mcdermott", "trost",
    "quiroga", "quiroga-martinez", "hyde", "perani", "large",
    "pantev", "lenc", "jones", "nozaradan", "mcauley", "repp",
    "menon", "levitin", "damasio", "grewe", "deliege", "roederer",
    "thompson", "russo", "balkwill", "fechner", "weber", "stevens",
    "von bekesy", "bekesy", "fletcher", "mcadams", "grey",
    "ding", "singer", "tiesinga", "kopell", "whittington",
    "brunel", "wang", "deco", "knight", "haufe", "oostenveld",
    "tognoli", "kelso", "freeman", "buzsaki", "lisman", "hasselmo",
}

TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|PLACEHOLDER|HACK|STUB)\b", re.IGNORECASE)


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] could not read {path}: {exc}", file=sys.stderr)
        return ""


def literal_to_summary(node: ast.AST) -> tuple[str | None, str | None]:
    """Return (value_string, dtype) if node is (or contains) a numerical literal.

    dtype in {'int', 'float', 'bool', 'tuple-numeric', 'list-numeric',
               'dict-numeric', 'complex', 'negnum'}
    """
    try:
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool):
                return repr(v), "bool"
            if isinstance(v, (int, float)):
                return repr(v), "float" if isinstance(v, float) else "int"
            if isinstance(v, complex):
                return repr(v), "complex"
            return None, None
        # negative numbers appear as UnaryOp(USub, Constant)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            inner_val, inner_dt = literal_to_summary(node.operand)
            if inner_val is None:
                return None, None
            sign = "-" if isinstance(node.op, ast.USub) else "+"
            return f"{sign}{inner_val}", f"neg{inner_dt}" if isinstance(node.op, ast.USub) else inner_dt
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            vals: list[str] = []
            all_numeric = True
            for elt in node.elts:
                vv, dt = literal_to_summary(elt)
                if vv is None or dt not in ("int", "float", "bool", "complex", "negint", "negfloat"):
                    all_numeric = False
                    break
                vals.append(vv)
            if all_numeric and vals:
                kind = "tuple-numeric" if isinstance(node, ast.Tuple) else "list-numeric" if isinstance(node, ast.List) else "set-numeric"
                return "[" + ", ".join(vals) + "]", kind
            return None, None
        if isinstance(node, ast.Dict):
            vals = []
            all_numeric_keys_or_vals = True
            for k, v in zip(node.keys, node.values):
                kv, kdt = literal_to_summary(k) if k is not None else (None, None)
                vv, vdt = literal_to_summary(v)
                if vv is None or vdt not in ("int", "float", "bool", "complex", "negint", "negfloat"):
                    all_numeric_keys_or_vals = False
                    break
                k_str = kv if kv is not None else (
                    ast.unparse(k) if k is not None else "None"
                )
                vals.append(f"{k_str}:{vv}")
            if all_numeric_keys_or_vals and vals:
                return "{" + ", ".join(vals) + "}", "dict-numeric"
            return None, None
        # Call -> e.g. np.array([...]) — try to find numeric literal in args
        if isinstance(node, ast.Call):
            for a in node.args:
                r = literal_to_summary(a)
                if r[0] is not None:
                    return r
            return None, None
    except Exception:
        return None, None
    return None, None


def is_numeric_dtype(dt: str | None) -> bool:
    if dt is None:
        return False
    return dt in (
        "int", "float", "bool", "complex", "negint", "negfloat",
        "tuple-numeric", "list-numeric", "set-numeric", "dict-numeric",
    )


def get_context_lines(lines: list[str], lineno: int) -> tuple[str, str]:
    # 3 lines before + 3 lines after, joined with ' | ' delimiter
    before = lines[max(0, lineno - 4): lineno - 1]
    after = lines[lineno: lineno + 3]
    return " | ".join(s.strip() for s in before), " | ".join(s.strip() for s in after)


def detect_citation(context_text: str) -> tuple[bool, str, str]:
    m = CITATION_RE.search(context_text)
    if m:
        return True, m.group("author"), m.group("year")
    lower = context_text.lower()
    for tok in KNOWN_CITATION_TOKENS:
        if tok in lower:
            return True, tok, ""
    return False, "", ""


def walk_file(path: Path, rel: str, writer: csv.writer) -> int:
    src = read_source(path)
    if not src:
        return 0
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return 0
    lines = src.splitlines()
    count = 0

    def process_target(target_node: ast.AST, value_node: ast.AST, scope: str, lineno: int):
        nonlocal count
        vsummary, dtype = literal_to_summary(value_node)
        if vsummary is None or not is_numeric_dtype(dtype):
            return
        # target name
        if isinstance(target_node, ast.Name):
            name = target_node.id
        elif isinstance(target_node, ast.Attribute):
            name = ast.unparse(target_node)
        else:
            try:
                name = ast.unparse(target_node)
            except Exception:
                name = "<unknown>"
        # skip obvious type hints like _: int = 0 (uninteresting)
        before, after = get_context_lines(lines, lineno)
        ctx_text = before + " " + after + " " + (lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else "")
        has_cit, cit_author, cit_year = detect_citation(ctx_text)
        has_todo = bool(TODO_RE.search(ctx_text))
        writer.writerow([
            rel, lineno, scope, name, vsummary, dtype,
            before, after,
            int(has_cit), cit_author, cit_year,
            int(has_todo),
        ])
        count += 1

    def visit(node: ast.AST, scope: str):
        # Module-level / class-level / function-level assignments
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            new_scope = scope
            if isinstance(node, ast.ClassDef):
                new_scope = f"{scope}::class {node.name}"
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                new_scope = f"{scope}::def {node.name}"

            # For function: also extract default argument values
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args
                all_args = args.args + args.kwonlyargs
                # positional defaults align with tail of args.args; kwonly align with kwonlyargs
                defaults = args.defaults
                kw_defaults = args.kw_defaults
                if defaults:
                    start = len(args.args) - len(defaults)
                    for i, d in enumerate(defaults):
                        arg = args.args[start + i]
                        # synthetic "target" name for default
                        fake = ast.Name(id=f"{node.name}.{arg.arg}")
                        fake.lineno = getattr(d, "lineno", node.lineno)
                        fake.col_offset = 0
                        process_target(fake, d, f"{new_scope}::arg-default", fake.lineno)
                for i, d in enumerate(kw_defaults):
                    if d is None:
                        continue
                    arg = args.kwonlyargs[i]
                    fake = ast.Name(id=f"{node.name}.{arg.arg}")
                    fake.lineno = getattr(d, "lineno", node.lineno)
                    fake.col_offset = 0
                    process_target(fake, d, f"{new_scope}::kw-default", fake.lineno)

            for child in node.body:
                # Assignments
                if isinstance(child, ast.Assign):
                    for tgt in child.targets:
                        process_target(tgt, child.value, new_scope, child.lineno)
                elif isinstance(child, ast.AnnAssign) and child.value is not None:
                    process_target(child.target, child.value, new_scope, child.lineno)
                # recurse into class/function bodies for nested declarations
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, new_scope)

    visit(tree, "module")
    return count


def main() -> int:
    out_csv = OUT / "raw_constants_inventory.csv"
    files = sorted(ROOT.rglob("*.py"))
    # Exclude __pycache__ and tests-like dirs? Keep __pycache__ excluded.
    files = [f for f in files if "__pycache__" not in f.parts]
    n_files = 0
    n_consts = 0
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "file_path", "line", "scope", "name", "value", "dtype",
            "context_before", "context_after",
            "has_citation_in_context", "citation_author", "citation_year",
            "has_todo_fixme",
        ])
        for p in files:
            rel = str(p.relative_to(ROOT))
            added = walk_file(p, rel, w)
            if added:
                n_files += 1
                n_consts += added
    print(f"scanned {len(files)} .py files; wrote {n_consts} constants from {n_files} files")
    print(f"output: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
