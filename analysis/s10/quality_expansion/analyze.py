#!/usr/bin/env python3
"""Analyse the genre-controlled DQI grading.

THE QUESTION

The quality arm found AI-flagged legislative speech is better-formed and
worse-engaged than human speech. Its unsolved confound is genre: AI
concentrates in scripted formats, so the finding may partly be "scripted
speech engages opponents less."

This pool is balanced by construction — 140 segments in each of
{SO31 scripted, Oral Questions unscripted, Government Orders debate} x
{2018-19, 2025-26} — so the comparison can hold genre fixed.

Three things are reported, in this order:

  1. DESCRIPTIVE — DQI dimensions by genre and era. Establishes that the
     genres differ, which is the premise of the confound.
  2. THE CONFOUND TEST — the AI-quality association, unconditional and then
     within genre. If the association survives genre fixed effects, the
     original finding stands; if it collapses, it was genre all along.
  3. LEAKAGE — whether the quality differences are really style detection.
     The judge scored ai_guess separately; if the quality gap vanishes once
     ai_guess is controlled, the judge was smelling AI, not measuring quality.

AI status comes from the phase-1 screen on the same text, kept separate from
the grading pass so a single agent never sees both jobs for one segment.

Usage: python analyze.py [WORKFLOW_RUN_DIR]
       (with no argument, searches the newest run dir containing Q-ids)
"""
import glob
import json
import math
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
# v2b's seven dimensions. respect_groups and respect_counterargs were
# missing from an earlier 6-dimension paraphrase of this rubric; the names
# here must match the schema in grade_workflow.js exactly or harvest() will
# silently drop every grade.
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
# -1 means INAPPLICABLE (no other demand / no counterargument on the table),
# not a low score. Averaging it in would score "nothing to engage with" as
# worse than "engaged badly", so it is excluded from those two means and the
# applicable-rate is reported instead.
SENTINEL = {"respect_demands", "respect_counterargs"}
BASE = os.path.expanduser("~/.claude/projects")


def harvest(run_dir):
    """Pull {id: record} out of the workflow transcripts."""
    screen, grade = {}, {}

    def absorb(o):
        if isinstance(o, dict):
            i = o.get("id")
            if isinstance(i, str) and i[:1] in ("Q", "R") and len(i) == 5:
                if "justification" in o:
                    grade[i] = o
                elif "ai_guess" in o:
                    screen[i] = o
            else:
                for v in o.values():
                    absorb(v)
        elif isinstance(o, list):
            for v in o:
                absorb(v)

    for p in glob.glob(os.path.join(run_dir, "*.jsonl")):
        for line in open(p):
            try:
                absorb(json.loads(line))
            except Exception:
                pass
    return screen, grade


def find_run():
    cands = sorted(glob.glob(os.path.join(BASE, "*", "*", "subagents",
                                          "workflows", "wf_*")),
                   key=os.path.getmtime, reverse=True)
    for c in cands:
        s, g = harvest(c)
        if g:
            return c
    return None


def ols(Y, X, names):
    n, k = len(Y), len(X[0])
    A = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
         for a in range(k)]
    yv = [sum(X[i][a] * Y[i] for i in range(n)) for a in range(k)]
    I = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    M = [r[:] for r in A]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        I[c], I[p] = I[p], I[c]
        d = M[c][c]
        if abs(d) < 1e-12:
            return None
        M[c] = [v / d for v in M[c]]
        I[c] = [v / d for v in I[c]]
        for r in range(k):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(k)]
                I[r] = [I[r][j] - f * I[c][j] for j in range(k)]
    beta = [sum(I[a][b] * yv[b] for b in range(k)) for a in range(k)]
    res = [Y[i] - sum(X[i][j] * beta[j] for j in range(k)) for i in range(n)]
    meat = [[sum(X[i][a] * X[i][b] * res[i] ** 2 for i in range(n))
             for b in range(k)] for a in range(k)]
    sc = n / max(n - k, 1)
    V = [[sc * sum(I[a][p] * meat[p][q] * I[b][q]
                   for p in range(k) for q in range(k))
          for b in range(k)] for a in range(k)]
    return {nm: (beta[j], math.sqrt(max(V[j][j], 0))) for j, nm in enumerate(names)}


def main():
    # --key key2.json selects the stage-2 pool; stage 2 has chamber+verdict
    # metadata instead of genre+era, so the genre section is skipped for it.
    keyname = "key.json"
    argv = [a for a in sys.argv[1:]]
    if "--key" in argv:
        i = argv.index("--key")
        keyname = argv[i + 1]
        del argv[i:i + 2]
    run = argv[0] if argv else find_run()
    if not run:
        sys.exit("no workflow run directory with Q-ids found — pass one explicitly")
    print(f"run dir: {run}")
    key = json.load(open(os.path.join(HERE, keyname)))
    screen, grade = harvest(run)
    print(f"harvested {len(screen)} screen scores, {len(grade)} DQI grades "
          f"of {len(key)} segments\n")
    if len(grade) < 200:
        sys.exit("too few grades — did the Grade phase complete?")

    rows = []
    for sid, g in grade.items():
        k = key.get(sid)
        if not k:
            continue
        r = {"genre": k.get("genre") or "n/a", "era": k.get("era") or "n/a",
             "chamber": k.get("chamber"), "verdict": k.get("verdict"),
             "ai": screen.get(sid, {}).get("ai_guess"),
             "judge_ai": g.get("ai_guess")}
        for d in DIMS:
            r[d] = g.get(d)
        if all(r[d] is not None for d in DIMS):
            rows.append(r)

    # 1 — descriptive
    print("=== 1. DQI by genre and era (the confound's premise) ===")
    print(f"{'genre':<8s} {'era':<5s} {'n':>4s} " +
          " ".join(f"{d[:9]:>9s}" for d in DIMS) + f"{'screenAI':>9s}")
    for gnr in ("SO31", "OQ", "DEBATE"):
        for era in ("pre", "post"):
            sub = [r for r in rows if r["genre"] == gnr and r["era"] == era]
            if not sub:
                continue
            ais = [r["ai"] for r in sub if r["ai"] is not None]
            cells = []
            for d in DIMS:
                vals = [r[d] for r in sub
                        if not (d in SENTINEL and r[d] == -1)]
                cells.append(f"{statistics.mean(vals):>9.2f}" if vals
                             else f"{'n/a':>9s}")
            print(f"{gnr:<8s} {era:<5s} {len(sub):>4d} " + " ".join(cells) +
                  f"{statistics.mean(ais) if ais else float('nan'):>9.1f}")

    # 2 — the confound test
    scored = [r for r in rows if r["ai"] is not None]
    if len(scored) < 200:
        print("\n(no screen scores — cannot run the confound test)")
        return
    print(f"\n=== 2. Does the AI-quality association survive genre? "
          f"(n={len(scored)}) ===")
    genres = sorted({r["genre"] for r in scored})[1:]
    eras = sorted({r["era"] for r in scored})[1:]
    print(f"{'dimension':<18s} {'AI coef alone':>14s} "
          f"{'+ genre & era FE':>18s}")
    for d in DIMS:
        # drop inapplicable rows for the two sentinel dimensions rather than
        # regressing on a -1 that means "question did not arise"
        sub = [r for r in scored if not (d in SENTINEL and r[d] == -1)]
        if len(sub) < 100:
            print(f"{d:<18s} {'too few applicable rows':>30s}")
            continue
        Y = [r[d] for r in sub]
        X1 = [[1.0, r["ai"] / 100.0] for r in sub]
        f1 = ols(Y, X1, ["const", "ai"])
        X2 = [[1.0, r["ai"] / 100.0] +
              [1.0 if r["genre"] == g else 0.0 for g in genres] +
              [1.0 if r["era"] == e else 0.0 for e in eras] for r in sub]
        f2 = ols(Y, X2, ["const", "ai"] + [f"g_{g}" for g in genres] +
                 [f"e_{e}" for e in eras])
        if not f1 or not f2:
            continue
        b1, s1 = f1["ai"]
        b2, s2 = f2["ai"]
        print(f"{d:<18s} {b1:>+9.3f} (t{b1/s1:>+5.1f}) "
              f"{b2:>+11.3f} (t{b2/s2:>+5.1f})"
              f"{' *' if abs(b2/s2) > 1.96 else ''}")

    # 3 — leakage
    jl = [r for r in rows if r["judge_ai"] is not None and r["ai"] is not None]
    if len(jl) > 100:
        xs = [r["ai"] for r in jl]
        ys = [r["judge_ai"] for r in jl]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = math.sqrt(sum((a - mx) ** 2 for a in xs) *
                        sum((b - my) ** 2 for b in ys))
        print(f"\n=== 3. Leakage probe ===")
        print(f"  screen ai_guess vs grading-judge ai_guess: r = {num/den:+.3f}")
        print(f"  (a correlation between TWO DIFFERENT models — a fact about a")
        print(f"   shared style signal, not one model agreeing with itself)")

        # 3b — the documented control test (README/RUNME). Run once, reported
        # in Appendix D of the write-up, NOT relied on: judge_ai is scored
        # AFTER the quality codes (a post-treatment descendant of them) and in
        # stage 1 it is a second noisy reading of the same latent as the AI
        # regressor, so it attenuates by construction. Kept because the docs
        # promised it and an unrun documented test is its own defect.
        print(f"\n=== 3b. Documented control: DQI ~ ai + genre/era FE + judge_ai ===")
        print(f"  (BAD CONTROL — collider + collinearity; see Appendix D. "
              f"Shown, not adopted.)")
        print(f"{'dimension':<18s} {'AI + FE':>12s} {'+ judge_ai':>14s}")
        for d in DIMS:
            sub = [r for r in scored
                   if r["judge_ai"] is not None
                   and not (d in SENTINEL and r[d] == -1)]
            if len(sub) < 100:
                continue
            Y = [r[d] for r in sub]
            base = [[1.0, r["ai"] / 100.0] +
                    [1.0 if r["genre"] == g else 0.0 for g in genres] +
                    [1.0 if r["era"] == e else 0.0 for e in eras] for r in sub]
            ctl = [row + [sub[i]["judge_ai"] / 100.0]
                   for i, row in enumerate(base)]
            fb = ols(Y, base, ["const", "ai"] + [f"g{g}" for g in genres] +
                     [f"e{e}" for e in eras])
            fc = ols(Y, ctl, ["const", "ai"] + [f"g{g}" for g in genres] +
                     [f"e{e}" for e in eras] + ["judge_ai"])
            if not fb or not fc:
                continue
            bb, sb = fb["ai"]
            bc, sc = fc["ai"]
            print(f"{d:<18s} {bb:>+8.3f}(t{bb/sb:>+4.1f}) "
                  f"{bc:>+9.3f}(t{bc/sc:>+4.1f})")

    out = os.path.join(HERE, "results.json")
    json.dump(rows, open(out, "w"), indent=1)
    print(f"\nwrote {out} ({len(rows)} graded segments with metadata)")


if __name__ == "__main__":
    main()
