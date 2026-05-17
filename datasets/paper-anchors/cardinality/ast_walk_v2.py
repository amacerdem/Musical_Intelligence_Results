#!/usr/bin/env python3
"""
AST walker v2 — broader catch for T-R1-10-R3-04 N_free provenance.

Adds on top of v1:
 1. In-expression numeric literals (weight multipliers inside function bodies).
    These are the PRIMARY hand-tuned-weight candidates per R3.md §A5 (reward
    weights, F1-BCH temporal integration weights, etc.).
 2. Keyword-argument numeric literals in Call expressions (e.g.,
    Region(index=15, mni_coords=(24, -4, -18), ...)).
 3. Dict literals with (number | tuple-of-numbers) values even when other
    keys/values are strings (for REFERENCE_VALUES, INTERACTIONS patterns).

READ-ONLY. ast.parse + regex only. No engine imports.

Output columns:
  file_path,line,scope,name,value,dtype,kind,context_before,context_after,
  has_citation_in_context,citation_author,citation_year,has_todo_fixme

kind in {'module-assign', 'class-attr', 'ann-assign', 'arg-default',
         'kw-default', 'call-kwarg', 'call-posarg', 'expr-literal',
         'dict-field'}
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

# Trivial values we skip as expr-literals (too noisy to count).
TRIVIAL_INTS = {-1, 0, 1, 2}

CITATION_RE = re.compile(
    r"(?P<author>[A-Z][A-Za-z\-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z\-]+)?"
    r"(?:\s+et\s+al\.?)?)\s*"
    r"(?P<year>\(?\d{4}[a-z]?\)?)"
)

KNOWN_CITATION_TOKENS = {
    "sethares", "plomp", "levelt", "krumhansl", "kessler", "stumpf",
    "helmholtz", "kuttruff", "stevens", "terhardt", "parncutt", "moore",
    "bidelman", "bregman", "shepard", "bowling", "koelsch", "zatorre",
    "salimpoor", "ferreri", "schultz", "friston", "pearce", "cheung",
    "jakubowski", "janata", "huron", "grahn", "witek", "mcadams",
    "bastos", "rao", "ballard", "dayan", "herrero", "marjieh", "eerola",
    "iec", "zwicker", "patel", "rohrmeier", "kim", "juslin", "vastfjall",
    "sammler", "belin", "griffiths", "warren", "mas-herrero", "pauli",
    "edlow", "bornstein", "coffey", "doelling", "ding", "simon",
    "chandrasekaran", "kraus", "blood", "schirmer", "shapiro", "poeppel",
    "hickok", "sugimoto", "haueisen", "schnupp", "yeshurun", "jacoby",
    "mcdermott", "trost", "quiroga", "quiroga-martinez", "hyde", "perani",
    "large", "pantev", "lenc", "jones", "nozaradan", "mcauley", "repp",
    "menon", "levitin", "damasio", "grewe", "deliege", "roederer",
    "thompson", "russo", "balkwill", "fechner", "weber", "bekesy",
    "fletcher", "grey", "tiesinga", "kopell", "whittington",
    "brunel", "wang", "deco", "knight", "haufe", "oostenveld",
    "tognoli", "kelso", "freeman", "buzsaki", "lisman", "hasselmo",
    "parncutt", "terhardt", "hove", "repp", "stupacher", "rayleigh",
    "shannon", "nyquist", "fourier",  # analytic classics
    "ferreri", "mas-herrero", "gold", "fiveash", "keller",
    "snyder", "loui", "meyer", "trainor", "hannon", "thompson",
    "trehub", "nelken", "chi", "temperley", "narmour", "lerdahl",
    "jackendoff", "bharucha", "krumhansl", "handel", "berridge",
    "kringelbach", "blood", "pauli",
    # Framework abbreviations
    "fmri", "pet", "meg", "eeg", "ffr",
}

TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|PLACEHOLDER|HACK|STUB)\b", re.IGNORECASE)


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] {path}: {exc}", file=sys.stderr)
        return ""


def numeric_literal(node: ast.AST) -> tuple[str | None, str | None]:
    """Return (repr, dtype) if node is a (possibly negated) scalar literal."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return repr(node.value), ("float" if isinstance(node.value, float) else "int")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = numeric_literal(node.operand)
        if inner[0] is None:
            return None, None
        sign = "-" if isinstance(node.op, ast.USub) else "+"
        return f"{sign}{inner[0]}", f"neg{inner[1]}" if isinstance(node.op, ast.USub) else inner[1]
    return None, None


def collection_summary(node: ast.AST) -> tuple[str | None, str | None]:
    """Return summary for tuple/list/set/dict node if contents are numeric-ish."""
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        vals: list[str] = []
        for elt in node.elts:
            vv, dt = numeric_literal(elt)
            if vv is None:
                vv2, dt2 = collection_summary(elt)
                if vv2 is None:
                    return None, None
                vv = vv2
            vals.append(vv)
        if vals:
            kind = "tuple-numeric" if isinstance(node, ast.Tuple) else (
                "list-numeric" if isinstance(node, ast.List) else "set-numeric"
            )
            return "[" + ", ".join(vals) + "]", kind
    if isinstance(node, ast.Dict):
        parts: list[str] = []
        numeric_vals = 0
        for k, v in zip(node.keys, node.values):
            # value must be numeric (scalar or collection of scalars)
            vv, vdt = numeric_literal(v)
            if vv is None:
                vv, vdt = collection_summary(v)
            if vv is None:
                return None, None
            # key — stringify
            if isinstance(k, ast.Constant):
                krepr = repr(k.value)
            elif k is None:
                krepr = "None"
            else:
                try:
                    krepr = ast.unparse(k)
                except Exception:
                    krepr = "<k>"
            parts.append(f"{krepr}:{vv}")
            numeric_vals += 1
        if numeric_vals:
            return "{" + ", ".join(parts) + "}", "dict-numeric"
    return None, None


def literal_to_summary(node: ast.AST) -> tuple[str | None, str | None]:
    r = numeric_literal(node)
    if r[0] is not None:
        return r
    return collection_summary(node)


def is_numeric_dtype(dt: str | None) -> bool:
    if dt is None:
        return False
    return dt in (
        "int", "float", "negint", "negfloat",
        "tuple-numeric", "list-numeric", "set-numeric", "dict-numeric",
    )


def get_context(lines: list[str], lineno: int) -> tuple[str, str, str]:
    line = lines[lineno - 1].strip() if 0 <= lineno - 1 < len(lines) else ""
    before = " | ".join(s.strip() for s in lines[max(0, lineno - 4): lineno - 1])
    after = " | ".join(s.strip() for s in lines[lineno: lineno + 3])
    return before, line, after


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

    # Track scope stack via ast.walk w/ parent decoration
    # We need path-aware traversal. We'll do recursive visit.

    def emit(lineno: int, scope: str, name: str, vsummary: str, dtype: str, kind: str):
        nonlocal count
        before, line, after = get_context(lines, lineno)
        ctx = " ".join([before, line, after])
        has_cit, cit_author, cit_year = detect_citation(ctx)
        has_todo = bool(TODO_RE.search(ctx))
        writer.writerow([
            rel, lineno, scope, name, vsummary, dtype, kind,
            before, line, after,
            int(has_cit), cit_author, cit_year,
            int(has_todo),
        ])
        count += 1

    def target_name(t: ast.AST) -> str:
        if isinstance(t, ast.Name):
            return t.id
        try:
            return ast.unparse(t)
        except Exception:
            return "<anon>"

    def visit(node: ast.AST, scope: str, in_class: bool = False):
        # Handle scope transitions
        if isinstance(node, ast.ClassDef):
            new_scope = f"{scope}::class {node.name}"
            # visit children with in_class=True
            for child in node.body:
                if isinstance(child, ast.Assign):
                    for tgt in child.targets:
                        r = literal_to_summary(child.value)
                        if r[0] and is_numeric_dtype(r[1]):
                            emit(child.lineno, new_scope, target_name(tgt), r[0], r[1], "class-attr")
                elif isinstance(child, ast.AnnAssign) and child.value is not None:
                    r = literal_to_summary(child.value)
                    if r[0] and is_numeric_dtype(r[1]):
                        emit(child.lineno, new_scope, target_name(child.target), r[0], r[1], "ann-assign")
                visit(child, new_scope, in_class=True)
            return

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            new_scope = f"{scope}::def {node.name}"
            # arg defaults
            args = node.args
            defaults = args.defaults
            kw_defaults = args.kw_defaults
            if defaults:
                start = len(args.args) - len(defaults)
                for i, d in enumerate(defaults):
                    arg = args.args[start + i]
                    r = literal_to_summary(d)
                    if r[0] and is_numeric_dtype(r[1]):
                        emit(getattr(d, "lineno", node.lineno), new_scope,
                             f"{node.name}.{arg.arg}", r[0], r[1], "arg-default")
            for i, d in enumerate(kw_defaults):
                if d is None:
                    continue
                arg = args.kwonlyargs[i]
                r = literal_to_summary(d)
                if r[0] and is_numeric_dtype(r[1]):
                    emit(getattr(d, "lineno", node.lineno), new_scope,
                         f"{node.name}.{arg.arg}", r[0], r[1], "kw-default")
            # Traverse body for in-expression literals + nested defs
            for child in ast.walk(node):
                # stop at nested FunctionDef/ClassDef to avoid double-visit
                pass
            # Walk body manually
            for stmt in node.body:
                visit_expr(stmt, new_scope)
            # Recurse into nested classes/defs
            for child in ast.walk(node):
                if child is node:
                    continue
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Handled by visit_expr? No — need explicit visit
                    pass
            # Call visit on nested class/func definitions via walk
            def _recurse_nested(n: ast.AST):
                for c in ast.iter_child_nodes(n):
                    if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        visit(c, new_scope)
                    else:
                        _recurse_nested(c)
            _recurse_nested(node)
            return

        if isinstance(node, ast.Module):
            new_scope = scope
            for child in node.body:
                if isinstance(child, ast.Assign):
                    for tgt in child.targets:
                        r = literal_to_summary(child.value)
                        if r[0] and is_numeric_dtype(r[1]):
                            emit(child.lineno, new_scope, target_name(tgt), r[0], r[1], "module-assign")
                        # Also: if value is a Call (e.g., Region(index=15, ...)),
                        # harvest keyword numeric literals.
                        if isinstance(child.value, ast.Call):
                            harvest_call(child.value, new_scope, target_name(tgt))
                elif isinstance(child, ast.AnnAssign) and child.value is not None:
                    r = literal_to_summary(child.value)
                    if r[0] and is_numeric_dtype(r[1]):
                        emit(child.lineno, new_scope, target_name(child.target), r[0], r[1], "ann-assign")
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, new_scope)
            return

    def harvest_call(call: ast.Call, scope: str, outer_name: str):
        # kwargs with numeric values
        for kw in call.keywords:
            if kw.arg is None:
                continue
            r = literal_to_summary(kw.value)
            if r[0] and is_numeric_dtype(r[1]):
                emit(kw.value.lineno if hasattr(kw.value, "lineno") else call.lineno,
                     scope, f"{outer_name}.{kw.arg}", r[0], r[1], "call-kwarg")
        # positional numeric args — capture (but nameless)
        for i, a in enumerate(call.args):
            r = literal_to_summary(a)
            if r[0] and is_numeric_dtype(r[1]):
                emit(a.lineno if hasattr(a, "lineno") else call.lineno,
                     scope, f"{outer_name}.arg{i}", r[0], r[1], "call-posarg")

    def visit_expr(stmt: ast.AST, scope: str):
        """Walk statements inside function bodies to extract in-expression numeric literals.

        Heuristic: for any BinOp whose right-hand-side is a numeric literal (weight multiplier
        pattern like ``0.20 * h3(...)``), record it. Skip trivial {-1, 0, 1, 2} ints.
        """
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.BinOp):
                # Check left + right for numeric literal operand
                for side_name, side in (("L", sub.left), ("R", sub.right)):
                    lit = numeric_literal(side)
                    if lit[0] is None:
                        continue
                    # skip trivial
                    try:
                        v = float(lit[0])
                    except Exception:
                        v = None
                    if v is not None:
                        # skip integers 0,1,2,-1 (too noisy)
                        if v in (0.0, 1.0, 2.0, -1.0) and lit[1] in ("int", "negint"):
                            continue
                    emit(getattr(side, "lineno", stmt.lineno), scope,
                         f"<expr-{side_name}>", lit[0], lit[1], "expr-literal")
            elif isinstance(sub, ast.Compare):
                # comparison thresholds: x > 0.5, etc.
                for comp in sub.comparators:
                    lit = numeric_literal(comp)
                    if lit[0]:
                        try:
                            v = float(lit[0])
                        except Exception:
                            v = None
                        if v is not None and v in (0.0, 1.0, -1.0) and lit[1] in ("int", "negint"):
                            continue
                        emit(getattr(comp, "lineno", stmt.lineno), scope,
                             "<cmp-threshold>", lit[0], lit[1], "expr-literal")
            elif isinstance(sub, ast.Call):
                # kwargs with numeric literals (torch.clamp(x, min=0.2, max=0.8) etc.)
                for kw in sub.keywords:
                    if kw.arg is None:
                        continue
                    lit = literal_to_summary(kw.value)
                    if lit[0] and is_numeric_dtype(lit[1]):
                        # skip trivial {0, 1} int defaults that show up everywhere (dim=0, dim=1)
                        if lit[0] in ("0", "1") and lit[1] == "int" and kw.arg in ("dim", "axis"):
                            continue
                        emit(getattr(kw.value, "lineno", sub.lineno), scope,
                             f"call.{kw.arg}", lit[0], lit[1], "call-kwarg")

    visit(tree, "module")
    return count


def main() -> int:
    out_csv = OUT / "raw_constants_inventory_v2.csv"
    files = sorted(ROOT.rglob("*.py"))
    files = [f for f in files if "__pycache__" not in f.parts]
    n_files = 0
    n_consts = 0
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "file_path", "line", "scope", "name", "value", "dtype", "kind",
            "context_before", "context_line", "context_after",
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
