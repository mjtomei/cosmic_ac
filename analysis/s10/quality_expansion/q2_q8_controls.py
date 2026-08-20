#!/usr/bin/env python3
"""The controls Q2 and Q8 were blocked on, now runnable: the id-keyed grades
were recovered from arch-home's workflow transcripts (2026-08-20).

PROVENANCE. The stage-1/2 DQI grading ran on the arch-home account in project
-home-mjtomei-quality-expansion (session de18652d..., workflows wf_c9c346c4
= stage 1, wf_3ce5e231 = stage 2; archives committed beside this file as
arch_quality_wf.tgz / arch_stage2_wf.tgz). Harvested rows are committed as
stage1_grades_by_id.json (840 Q-ids), stage2_grades_by_id.json (682 R-ids)
and screen_by_id.json, and each stage's score multiset matches the committed
results_stage{1,2}.json EXACTLY, so these are the original grades, not a
regrade. Joining on the ids against key.json / key2.json supplies seg_id,
speaker and n_words per row -- the fields whose absence blocked Q2 and Q8.

WHAT RUNS HERE
  Q8  the published models re-estimated with cluster-robust (CR1) errors on
      SPEAKER, beside the published HC1 t's. Stage 1: 840 segments from the
      key's speakers; stage 2 nearly one-segment-per-speaker.
  Q2  stage 2 with a within-chamber log-length term BESIDE the raw
      coefficient -- length is a channel, not a nuisance (Matthew,
      2026-08-19), so raw is never replaced.

Usage: python q2_q8_controls.py
"""
import json
import math
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENT = {"respect_demands", "respect_counterargs"}


def load(stage):
    g = json.load(open(os.path.join(HERE, f"stage{stage}_grades_by_id.json")))
    key = json.load(open(os.path.join(HERE, "key.json" if stage == 1 else "key2.json")))
    scr = json.load(open(os.path.join(HERE, "screen_by_id.json")))
    rows = []
    for sid, o in g.items():
        k = key.get(sid)
        if not k:
            continue
        r = dict(o)
        r.update({"speaker": k.get("speaker"), "n_words": float(k.get("n_words") or 0),
                  "genre": k.get("genre") or "n/a", "era": k.get("era") or "n/a",
                  "chamber": k.get("chamber"), "verdict": k.get("verdict"),
                  "ai": (scr.get(sid) or {}).get("ai_guess")})
        rows.append(r)
    return rows


def fit(y, X, clusters=None):
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ (X.T @ y)
    e = y - X @ b
    n, kk = X.shape
    if clusters is None:
        V = (n / max(n - kk, 1)) * XtXi @ ((X * (e**2)[:, None]).T @ X) @ XtXi
    else:
        cl = defaultdict(list)
        for i, c in enumerate(clusters):
            cl[c].append(i)
        M = np.zeros((kk, kk))
        for ii in cl.values():
            u = X[ii].T @ e[ii]
            M += np.outer(u, u)
        G = len(cl)
        V = (G / max(G - 1, 1)) * (n - 1) / max(n - kk, 1) * XtXi @ M @ XtXi
    return b, V


def main():
    print("=" * 70)
    print("Q8 — cluster-robust on speaker, beside the published HC1")
    print("=" * 70)
    for stage in (1, 2):
        rows = load(stage)
        sp = {r["speaker"] for r in rows}
        print(f"\nstage {stage}: {len(rows)} segments, {len(sp)} speakers "
              f"(mean cluster {len(rows)/len(sp):.2f})")
        print(f"  {'dimension':<20s}{'coef':>8s}{'t HC1':>8s}{'t CR1':>8s}")
        for d in DIMS:
            sub = [r for r in rows if r[d] is not None
                   and not (d in SENT and r[d] == -1)
                   and (stage == 2 or r["ai"] is not None)]
            y = [r[d] for r in sub]
            if stage == 1:
                gs = sorted({r["genre"] for r in sub})[1:]
                es = sorted({r["era"] for r in sub})[1:]
                X = [[1.0, r["ai"]/100.0]
                     + [1.0 if r["genre"] == g else 0.0 for g in gs]
                     + [1.0 if r["era"] == e else 0.0 for e in es] for r in sub]
            else:
                chs = sorted({r["chamber"] for r in sub})[1:]
                X = [[1.0, 1.0 if r["verdict"] in ("AI", "Mixed") else 0.0]
                     + [1.0 if r["chamber"] == c else 0.0 for c in chs] for r in sub]
            b, Vh = fit(y, X)
            _, Vc = fit(y, X, clusters=[r["speaker"] for r in sub])
            print(f"  {d:<20s}{b[1]:>+8.3f}{b[1]/math.sqrt(Vh[1,1]):>8.1f}"
                  f"{b[1]/math.sqrt(max(Vc[1,1],1e-12)):>8.1f}")

    print("\n" + "=" * 70)
    print("Q2 — stage 2 with a within-chamber log-length term (raw beside it)")
    print("=" * 70)
    rows = load(2)
    print(f"  {'dimension':<20s}{'raw':>14s}{'+ log length':>16s}{'length t':>10s}")
    for d in DIMS:
        sub = [r for r in rows if r[d] is not None
               and not (d in SENT and r[d] == -1) and r["n_words"] > 0]
        y = [r[d] for r in sub]
        chs = sorted({r["chamber"] for r in sub})[1:]
        base = [[1.0, 1.0 if r["verdict"] in ("AI", "Mixed") else 0.0]
                + [1.0 if r["chamber"] == c else 0.0 for c in chs] for r in sub]
        ln = np.log([r["n_words"] for r in sub])
        ln = (ln - ln.mean()) / ln.std()
        ctl = [row + [ln[i]] for i, row in enumerate(base)]
        b0, V0 = fit(y, base, clusters=[r["speaker"] for r in sub])
        b1, V1 = fit(y, ctl, clusters=[r["speaker"] for r in sub])
        print(f"  {d:<20s}{b0[1]:>+7.3f} (t {b0[1]/math.sqrt(V0[1,1]):+.1f})"
              f"{b1[1]:>+9.3f} (t {b1[1]/math.sqrt(V1[1,1]):+.1f})"
              f"{b1[-1]/math.sqrt(V1[-1,-1]):>10.1f}")


if __name__ == "__main__":
    main()
