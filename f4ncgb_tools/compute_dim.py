#!/usr/bin/env python3
"""
Compute the dimension of the quotient algebra F/I from a Gröbner basis output
file (one polynomial per line, msolve-style, leading term printed first).

A standard monomial is one not divisible (as a contiguous substring in the
non-commutative sense) by any leading monomial in the basis. Quotient dim =
number of standard monomials.

Usage:
    python3 compute_dim.py path/to/basis.txt --max-deg 12
"""

from __future__ import annotations
import argparse
import re


def parse_leading_monomials(basis_path: str) -> list[list[str]]:
    """Each basis line is 'term1 + term2 + ...' with term1 being the leading
    term in f4ncgb's chosen monomial ordering. Strip its coefficient and
    return the monomial as a list of variable names (in order)."""
    lms: list[list[str]] = []
    with open(basis_path) as f:
        for raw in f:
            line = raw.strip().rstrip(",")
            if not line:
                continue
            # Leading term is everything before the first ' + ' or ' - '
            # (with surrounding whitespace, since terms are separated by
            # spaces around the sign in msolve output).
            for sep in (" + ", " - ", "+", "-"):
                idx = line.find(sep, 1)  # start at 1 to skip optional leading "-"
                if idx > 0:
                    line = line[:idx]
                    break
            # Now strip the coefficient prefix: digits[*]
            m = re.match(r"^([0-9]+/[0-9]+|[0-9]+)\*?", line)
            if m and (line[m.end():].lstrip("*") or "").strip() != "":
                mon = line[m.end():].lstrip("*")
            else:
                mon = line
            mon = mon.strip()
            if mon == "" or mon.isdigit():
                # Pure constant term — quotient is zero algebra
                return [[]]
            vars = [v.strip() for v in mon.split("*") if v.strip()]
            lms.append(vars)
    return lms


def is_divisible(word: list[str], lm: list[str]) -> bool:
    """Non-commutative divisibility: does `lm` appear as a contiguous substring
    of `word`?"""
    if not lm:
        return True
    n = len(word)
    m = len(lm)
    if m > n:
        return False
    for i in range(n - m + 1):
        if word[i:i + m] == lm:
            return True
    return False


def is_standard(word: list[str], lms: list[list[str]]) -> bool:
    for lm in lms:
        if is_divisible(word, lm):
            return False
    return True


def count_standard_monomials(lms: list[list[str]], variables: list[str],
                              max_deg: int) -> tuple[int, list[int]]:
    """BFS through standard monomials. Returns (total_count, [count_per_deg])."""
    counts = [0] * (max_deg + 1)
    # Degree 0: identity (empty word)
    counts[0] = 1
    frontier: list[list[str]] = [[]]
    for d in range(1, max_deg + 1):
        next_frontier: list[list[str]] = []
        for w in frontier:
            for v in variables:
                cand = w + [v]
                if is_standard(cand, lms):
                    next_frontier.append(cand)
        counts[d] = len(next_frontier)
        frontier = next_frontier
        if counts[d] == 0:
            break
    return sum(counts), counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("basis", help="path to f4ncgb basis output")
    ap.add_argument("--max-deg", type=int, default=20,
                    help="upper bound on monomial degree to enumerate")
    ap.add_argument("--vars", help="comma-separated variable names; defaults to "
                                    "x1,x2,...,y_{n-1} inferred from input")
    args = ap.parse_args()

    lms = parse_leading_monomials(args.basis)
    print(f"Read {len(lms)} leading monomials.")

    # Default variable set: collect from the LMs themselves (preserves the
    # set actually appearing). For msolve, the user-declared order is what
    # f4ncgb used; we can read it from a sibling .ms input, but easier is to
    # derive from LMs.
    if args.vars:
        variables = args.vars.split(",")
    else:
        seen = set()
        for lm in lms:
            seen.update(lm)
        variables = sorted(seen)
    print(f"Variables (count {len(variables)}): {variables}")

    total, by_deg = count_standard_monomials(lms, variables, args.max_deg)
    print(f"Quotient dimension (up to deg {args.max_deg}): {total}")
    print(f"Hilbert series (deg 0..): {by_deg}")
    # Print non-zero suffix only
    last_nonzero = max((i for i, c in enumerate(by_deg) if c > 0), default=0)
    print(f"  (last nonzero: deg {last_nonzero}, count {by_deg[last_nonzero]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
