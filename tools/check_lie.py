#!/usr/bin/env python3
"""3D maths is written one way, DS-MSP's, in both repositories (CLAUDE.md law 0, §11).

tools/lie_reference.py holds DS-MSP's Lie-group functions (ds_msp/core/lie.py). For every course chapter file:

  same body     a function named like a reference function (so3_exp, se3_adjoint, ...) has the reference's
                code; docstrings and comments may differ, so equation tags "(Eq. n)" are fine
  same names    no look-alike names (skew, rodrigues, exp_so3, Exp, adjoint, ...): use the DS-MSP name
  same _EPS     a module-level _EPS equals the reference's

python tools/check_lie.py [--dsmsp <DS-MSP checkout>]   # the option also checks the reference against DS-MSP
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "course" / "chapters"
REFERENCE = ROOT / "tools" / "lie_reference.py"
LOOKALIKES = {"skew", "skew_symmetric", "rodrigues", "exp_so3", "log_so3", "exp_se3", "log_se3", "Exp", "Log",
              "expmap", "logmap", "so3_hat", "se3_hat", "adjoint", "Ad", "jr", "jl", "right_jacobian",
              "left_jacobian", "so3_jr", "so3_jl"}


def functions(text: str) -> dict:
    """name -> AST dump of the function without its docstring (comments are never in the AST)."""
    out = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                body = body[1:]
            out[node.name] = ast.dump(ast.FunctionDef(node.name, node.args, body, node.decorator_list,
                                                      node.returns, None))
    return out


def eps(text: str):
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "_EPS" for t in node.targets):
            return ast.literal_eval(node.value)
    return None


def problems(text: str, rel: str, ref: dict, ref_eps) -> list:
    errs = []
    for name, dump in functions(text).items():
        if name in ref and dump != ref[name]:
            errs.append(f"{rel}: {name} differs from DS-MSP's (tools/lie_reference.py); copy it verbatim")
        if name in LOOKALIKES:
            errs.append(f"{rel}: '{name}' looks like a DS-MSP function; use its name (see tools/lie_reference.py)")
    value = eps(text)
    if value is not None and value != ref_eps:
        errs.append(f"{rel}: _EPS = {value}, DS-MSP uses {ref_eps}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsmsp", type=Path, help="a DS-MSP checkout: also check the reference against it")
    a = ap.parse_args()
    ref_text = REFERENCE.read_text()
    ref, ref_eps = functions(ref_text), eps(ref_text)
    errs = []
    for f in sorted(CHAPTERS.glob("*/*.py")):
        errs += problems(f.read_text(), f.relative_to(ROOT).as_posix(), ref, ref_eps)
    if a.dsmsp:
        upstream = functions((a.dsmsp / "ds_msp" / "core" / "lie.py").read_text())
        errs += [f"tools/lie_reference.py: {n} is not DS-MSP's current version" for n in ref
                 if n in upstream and upstream[n] != ref[n]]
        errs += [f"tools/lie_reference.py: {n} is missing from DS-MSP" for n in ref if n not in upstream]
    if errs:
        print(f"check_lie: {len(errs)} problem(s)")
        for e in errs:
            print("  -", e)
        return 1
    print(f"check_lie: OK ({len(ref)} DS-MSP functions, every chapter copy identical)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
