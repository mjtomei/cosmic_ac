#!/usr/bin/env python3
"""Apply accepted changes from a round2 workflow result to the draft.

Prose rewrites are applied mechanically: the proposal's verbatim `current` text
is located in the draft and replaced by `proposed`. A change is applied ONLY if
its `current` matches exactly once (after a whitespace-tolerant fallback for
line-rewrap differences). Anything ambiguous is skipped and reported --- never
guessed at.

Structural changes (move/split/merge) are natural-language instructions, not
diffs, so they are NOT auto-applied; they are written to a review queue.

Usage: apply_changes.py <result.json> [--draft PATH] [--dry-run]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT = os.path.join(HERE, "S10-WRITEUP-DRAFT.md")


def find_span(text, needle):
    """Return (start, end) of the unique occurrence of needle, or None/'multi'."""
    n = text.count(needle)
    if n == 1:
        i = text.index(needle)
        return (i, i + len(needle))
    if n > 1:
        return "multi"
    # whitespace-tolerant: the draft may wrap lines differently
    pat = re.compile(r"\s+".join(re.escape(t) for t in needle.split()), re.S)
    hits = list(pat.finditer(text))
    if len(hits) == 1:
        return (hits[0].start(), hits[0].end())
    return "multi" if len(hits) > 1 else None


def main():
    res = json.load(open(sys.argv[1]))
    draft = DRAFT
    if "--draft" in sys.argv:
        draft = sys.argv[sys.argv.index("--draft") + 1]
    dry = "--dry-run" in sys.argv
    text = open(draft, encoding="utf-8").read()
    before = len(text)

    # AUTO-ACCEPT REQUIRES UNANIMITY (Matthew, 2026-09-02): a single dissenting
    # vote sends a change to the review queue instead of the draft.
    def unanimous(c):
        v = c.get("verdict", {})
        # Unanimous among whoever voted on THIS change. Quota can run out mid-run,
        # so n varies between changes; that is fine, and thin decisions are
        # flagged in the report so they can be revisited after the iteration.
        return v.get("accepted") and v.get("n", 0) > 0 and v.get("keeps") == v["n"]
    accepted = [c for c in res.get("changes", []) if unanimous(c)]
    split = [c for c in res.get("changes", []) if c.get("verdict", {}).get("accepted") and not unanimous(c)]
    prose = [c for c in accepted if c.get("type") == "prose" and c.get("action") in ("rewrite", "merge")]
    other = [c for c in accepted if c not in prose]

    # Competing variants: when several accepted proposals rewrite the SAME passage,
    # only one can land. Pick the best-scoring variant (composite, then support),
    # not whichever happens to come first in the list.
    def norm(c):
        return " ".join((c.get("current") or "").split())
    groups = {}
    for c in prose:
        groups.setdefault(norm(c), []).append(c)
    contested = {k: v for k, v in groups.items() if len(v) > 1}
    prose = []
    for k, v in groups.items():
        v.sort(key=lambda c: (-(c.get("verdict", {}).get("composite") or 0), -(c.get("support") or 0), c["id"]))
        prose.append(v[0])
    if contested:
        print(f"  {len(contested)} passage(s) had competing rewrites; kept the best-scoring variant:")
        for k, v in contested.items():
            best = min(v, key=lambda c: (-(c.get("verdict", {}).get("composite") or 0), -(c.get("support") or 0), c["id"]))
            others = [f"{o['id']}({o.get('verdict',{}).get('composite')})" for o in v if o is not best]
            print(f"    kept {best['id']}(composite {best.get('verdict',{}).get('composite')}) over {', '.join(others)}")

    applied, skipped = [], []
    for c in prose:
        cur, prop = (c.get("current") or "").strip(), (c.get("proposed") or "").strip()
        if not cur or not prop:
            skipped.append((c["id"], "empty current/proposed")); continue
        span = find_span(text, cur)
        if span is None:
            skipped.append((c["id"], "current text not found (superseded by an earlier change?)")); continue
        if span == "multi":
            skipped.append((c["id"], "current text is ambiguous (matches more than once)")); continue
        s, e = span
        text = text[:s] + prop + text[e:]
        applied.append(c["id"])

    # STRUCTURAL CONTENTION (same rule as prose: highest composite wins).
    # Proposals acting on the same section with the same action are rival takes on
    # one reorganization; keep the best-scoring and drop the rest. Different
    # actions on one section can be complementary (e.g. a move that another
    # proposal's split builds on), so those are kept and the applier is
    # responsible for skipping any residual conflict it meets.
    def sec(c):
        m = re.search(r"(\d+(?:\.\d+[a-z]?)?)", str(c.get("locus") or ""))
        return m.group(1) if m else str(c.get("locus"))[:12]
    sgroups = {}
    for c in other:
        sgroups.setdefault((sec(c), c.get("action")), []).append(c)
    other_kept, structural_dropped = [], []
    for k, v in sgroups.items():
        v.sort(key=lambda c: (-(c.get("verdict", {}).get("composite") or 0), c["id"]))
        other_kept.append(v[0]); structural_dropped += v[1:]
    if structural_dropped:
        print(f"  structural contention: dropped {len(structural_dropped)} rival take(s) "
              f"-> {[c['id'] for c in structural_dropped]}")
    other = other_kept

    queue = [{"id": c["id"], "locus": c.get("locus"), "type": c.get("type"), "action": c.get("action"),
              "proposed": c.get("proposed"), "rationale": c.get("rationale"),
              "keeps": c.get("verdict", {}).get("keeps"), "n": c.get("verdict", {}).get("n"),
              "composite": c.get("verdict", {}).get("composite"),
              "dependencies": c.get("verdict", {}).get("dependencies", []),
              "why_queued": "structural" if c in other else "not unanimous"} for c in other + split]

    print(f"unanimous {len(accepted)}: {len(prose)} prose-appliable, {len(other)} structural/queued")
    print(f"  majority-but-not-unanimous (queued, not applied): {len(split)}")
    thin = [c for c in accepted if c.get("verdict", {}).get("thin")]
    if thin:
        detail = ", ".join("{} {}/{}".format(c["id"], c["verdict"]["keeps"], c["verdict"]["n"])
                           for c in thin[:8])
        print("  {} change(s) decided by a reduced panel (ballots lost mid-run) — "
              "revisit if desired: {}".format(len(thin), detail))
    print(f"  applied: {len(applied)}  skipped: {len(skipped)}")
    for i, why in skipped:
        print(f"    - {i}: {why}")
    print(f"  draft {before:,} -> {len(text):,} bytes ({len(text)-before:+,})")

    if dry:
        print("  (dry run --- nothing written)")
        return
    open(draft, "w", encoding="utf-8").write(text)
    qp = os.path.join(HERE, "REWRITES-round2",
                      f"structural-queue-{res.get('scope','all')}-iter{res.get('iteration',0)}.json")
    os.makedirs(os.path.dirname(qp), exist_ok=True)
    json.dump(queue, open(qp, "w"), indent=1)
    print(f"  wrote {qp} ({len(queue)} awaiting review)")


if __name__ == "__main__":
    main()
