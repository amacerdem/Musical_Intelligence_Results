#!/usr/bin/env python3
"""
AST walker v3 — adds Call-literal harvesting everywhere + Link-constructor handling.

On top of v2:
 * Scan EVERY Call node in every file for positional + keyword numeric literals
   (needed for RegionLink(...), NeuroLink(...), Citation(...), LayerSpec(...),
   H3DemandSpec(...) factory calls whose signature interleaves strings and
   numeric literals).
 * Harvest numeric literals inside return tuples / comprehensions at module
   level and function level.

Classification tags added:
  kind = "link-weight"  when Call.func.id in {RegionLink, NeuroLink}
  kind = "layer-spec"   when Call.func.id == LayerSpec
  kind = "h3-demand"    when Call.func.id == H3DemandSpec or _h3
  kind = "call-posarg"  when other Call positional arg is numeric
  kind = "call-kwarg"   when Call kwarg value is numeric

This is intentionally over-inclusive; classify.py prunes/filters.

READ-ONLY. ast.parse + regex only. No engine imports.
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
    "hove", "stupacher", "rayleigh", "shannon", "nyquist", "fourier",
    "gold", "fiveash", "keller", "snyder", "loui", "meyer", "trainor",
    "hannon", "trehub", "nelken", "chi", "temperley", "narmour", "lerdahl",
    "jackendoff", "bharucha", "handel", "berridge", "kringelbach",
    "mallik", "mohebi", "pauli", "brattico", "samiee", "chen",
    "omigie", "sloboda", "gabrielsson", "juslin", "vastfjall",
    "tillmann", "peretz", "patel", "margulis", "bharucha",
    "gjerdingen", "tekman", "dalla-bella", "lartillot", "toiviainen",
    "papp", "rosen", "fmri", "pet", "meg", "eeg", "ffr",
}

TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|PLACEHOLDER|HACK|STUB)\b", re.IGNORECASE)

LINK_CALL_NAMES = {"RegionLink", "NeuroLink"}
SPEC_CALL_NAMES = {"LayerSpec", "H3DemandSpec", "_h3"}
CITATION_CALL_NAMES = {"Citation"}


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] {path}: {exc}", file=sys.stderr)
        return ""


def numeric_literal(node: ast.AST) -> tuple[str | None, str | None]:
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
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        vals: list[str] = []
        for elt in node.elts:
            vv, dt = numeric_literal(elt)
            if vv is None:
                vv2, _ = collection_summary(elt)
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
        for k, v in zip(node.keys, node.values):
            vv, _ = numeric_literal(v)
            if vv is None:
                vv, _ = collection_summary(v)
            if vv is None:
                return None, None
            if isinstance(k, ast.Constant):
                krepr = repr(k.value)
            else:
                try:
                    krepr = ast.unparse(k) if k is not None else "None"
                except Exception:
                    krepr = "<k>"
            parts.append(f"{krepr}:{vv}")
        if parts:
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


def call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        try:
            return ast.unparse(f)
        except Exception:
            return f.attr
    return "<call>"


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
    # de-dupe within file by (line, name, value, kind)
    seen: set[tuple[int, str, str, str]] = set()

    def emit(lineno: int, scope: str, name: str, vsummary: str, dtype: str, kind: str):
        nonlocal count
        key = (lineno, name, vsummary, kind)
        if key in seen:
            return
        seen.add(key)
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

    # Build scope map via parent tracking
    parent: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for c in ast.iter_child_nodes(node):
            parent[id(c)] = node

    def scope_of(n: ast.AST) -> str:
        chain: list[str] = []
        cur: ast.AST | None = n
        while cur is not None:
            if isinstance(cur, ast.ClassDef):
                chain.append(f"class {cur.name}")
            elif isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chain.append(f"def {cur.name}")
            cur = parent.get(id(cur))
        chain.reverse()
        return "module" + ("::" + "::".join(chain) if chain else "")

    # 1) Top-level assignments + class attrs + ann-assigns (explicit names)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # only emit if the scope is module/class (function-body assignments
            # are intra-expression weight literals we capture differently)
            scope = scope_of(node)
            r = literal_to_summary(node.value)
            if r[0] and is_numeric_dtype(r[1]):
                for tgt in node.targets:
                    emit(node.lineno, scope, target_name(tgt), r[0], r[1],
                         "class-attr" if "class " in scope and "def " not in scope.split("class ")[-1] else "module-assign")
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            r = literal_to_summary(node.value)
            if r[0] and is_numeric_dtype(r[1]):
                scope = scope_of(node)
                emit(node.lineno, scope, target_name(node.target), r[0], r[1], "ann-assign")

    # 2) Function def defaults (arg-default + kw-default)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = scope_of(node)
            a = node.args
            if a.defaults:
                start = len(a.args) - len(a.defaults)
                for i, d in enumerate(a.defaults):
                    arg = a.args[start + i]
                    r = literal_to_summary(d)
                    if r[0] and is_numeric_dtype(r[1]):
                        emit(getattr(d, "lineno", node.lineno),
                             f"{scope}::def {node.name}", f"{node.name}.{arg.arg}",
                             r[0], r[1], "arg-default")
            for i, d in enumerate(a.kw_defaults):
                if d is None:
                    continue
                arg = a.kwonlyargs[i]
                r = literal_to_summary(d)
                if r[0] and is_numeric_dtype(r[1]):
                    emit(getattr(d, "lineno", node.lineno),
                         f"{scope}::def {node.name}", f"{node.name}.{arg.arg}",
                         r[0], r[1], "kw-default")

    # 3) Every Call — harvest numeric positional + kw args
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope = scope_of(node)
        cname = call_name(node)
        base_kind = "link-weight" if cname in LINK_CALL_NAMES else (
            "spec-numeric" if cname in SPEC_CALL_NAMES else (
                "citation-call" if cname in CITATION_CALL_NAMES else "call"
            )
        )
        # positional args
        for i, a in enumerate(node.args):
            r = literal_to_summary(a)
            if r[0] is None or not is_numeric_dtype(r[1]):
                continue
            # skip trivial scalars in generic calls (but keep in link/spec)
            try:
                vf = float(r[0]) if r[1] in ("int", "float", "negint", "negfloat") else None
            except Exception:
                vf = None
            if base_kind == "call" and vf is not None and vf in (0.0, 1.0, -1.0) and r[1] in ("int", "negint"):
                continue
            kind = f"{base_kind}-posarg{i}"
            name_str = f"{cname}.arg{i}"
            emit(getattr(a, "lineno", node.lineno), scope, name_str, r[0], r[1], kind)
        # keyword args
        for kw in node.keywords:
            if kw.arg is None:
                continue
            r = literal_to_summary(kw.value)
            if r[0] is None or not is_numeric_dtype(r[1]):
                continue
            try:
                vf = float(r[0]) if r[1] in ("int", "float", "negint", "negfloat") else None
            except Exception:
                vf = None
            if base_kind == "call" and vf is not None and vf in (0.0, 1.0, -1.0) and r[1] in ("int", "negint") and kw.arg in ("dim", "axis", "keepdim"):
                continue
            kind = f"{base_kind}-kw"
            emit(getattr(kw.value, "lineno", node.lineno), scope, f"{cname}.{kw.arg}", r[0], r[1], kind)

    # 4) In-function-body expression literals (BinOp + Compare) — weight multipliers
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        fn_scope = scope_of(node)
        for sub in ast.walk(node):
            if isinstance(sub, ast.BinOp):
                for label, side in (("L", sub.left), ("R", sub.right)):
                    lit = numeric_literal(side)
                    if lit[0] is None:
                        continue
                    try:
                        v = float(lit[0])
                    except Exception:
                        v = None
                    # skip trivial integer {-1, 0, 1, 2} in expressions
                    if v is not None and v in (-1.0, 0.0, 1.0, 2.0) and lit[1] in ("int", "negint"):
                        continue
                    emit(getattr(side, "lineno", sub.lineno), fn_scope,
                         f"<expr-{label}>", lit[0], lit[1], "expr-literal")
            elif isinstance(sub, ast.Compare):
                for comp in sub.comparators:
                    lit = numeric_literal(comp)
                    if lit[0] is None:
                        continue
                    try:
                        v = float(lit[0])
                    except Exception:
                        v = None
                    if v is not None and v in (-1.0, 0.0, 1.0) and lit[1] in ("int", "negint"):
                        continue
                    emit(getattr(comp, "lineno", sub.lineno), fn_scope,
                         "<cmp-threshold>", lit[0], lit[1], "expr-literal")

    return count


def main() -> int:
    out_csv = OUT / "raw_constants_inventory.csv"
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
