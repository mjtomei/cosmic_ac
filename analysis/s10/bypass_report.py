#!/usr/bin/env python3
"""The bypass arm, computed from the stored Pangram verdicts.

WHY THIS EXISTS

Every number in section 4.9 was originally computed ad hoc, in a chat session,
one run at a time. Two of them turned out to be wrong in ways that only a
single recomputation over all four runs at once could expose (see below). This
script is the artifact: it reads the four verdict files, pools them, and prints
every figure the write-up quotes.

TWO RATES, AND BOTH BELONG IN THE WRITE-UP

  PER VARIANT, ALL FOUR RUNS -- 8.5%. The conservative figure. It averages two
  superseded searches into the denominator and asks how often a RANDOM attempt
  succeeds. Use it when the claim is about the detector.

  PER TARGET, FINAL SEARCH ONLY -- 22.5%. The operational figure. It asks
  whether the speech an adversary wanted through got through, which is the
  only question they care about; discarded drafts cost them nothing. Use it
  when the claim is about what an attacker achieves, and as the figure a fresh
  study replicating our best method should expect. The denominator is targets
  SEARCHED, not targets that yielded a submittable variant -- see the block
  below. Using the yielded count instead gave 24.6%, which is the same error
  as reporting a treatment effect on completers only.

Neither supersedes the other. Quoting only the first understates the exposure;
quoting only the second overstates the detector's weakness.

THE QUANTITY, NAMED CAREFULLY

We report an ADVERSARIALLY-INDUCED FALSE-NEGATIVE RATE: of all rewritten
variants submitted to Pangram, the fraction it labels Human. That is not the
same quantity as a vendor's published FNR, for two reasons that must travel
with the number:

  1. Ground truth here is a Pangram verdict on the ORIGINAL, not known
     authorship. A "false negative" means the detector reversed itself on text
     it had flagged -- not that we know a machine wrote it.
  2. The variants are the output of a search that optimised against a
     correlated proxy. This is a rate under attack, not under clean conditions.

Published clean-condition FNRs are ~0.3-2%; published adversarial FNRs for the
same detector are ~0.4-2.9%. Ours is higher than both. Comparison is in the
write-up, with the labelling made explicit -- Rice's ~8% is a FALSE POSITIVE
rate on n=50 and is not comparable to this.

TWO CORRECTIONS THIS SCRIPT ENCODES

  * "seed AI 22% vs Mixed 76%" was computed on batch 0 (100 of 129) before the
    rest landed, and the two figures are NOT the same statistic: it counted
    "not confidently AI" as a flip, so a Mixed seed that stayed Mixed scored as
    a success. Recomputed like-for-like below, the seed effect is directional
    but far smaller, and does not reach significance per-variant.
  * Rates must be reported per-variant AND per-text. Per-text rates are
    conditional on the search budget (~6 rounds x 3 variants) and are not
    detector properties.
  * Per-variant intervals were Wilson, which assumes 461 independent trials.
    They are up to 18 rewrites of each of 92 texts and success clusters by
    text: design effect 3.55, effective n ~130. Now a cluster bootstrap over
    texts, which roughly doubles the width.
  * The per-target denominator counted only targets that produced a variant
    under the submission gate. Sixteen of 106 searched targets (15%) never
    did, across four to six full rounds each. They are attack failures and
    belong in the denominator: 24.6% -> 22.5%.

Usage: python bypass_report.py
"""
import collections
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def cluster_boot(rows, pred, seed=0, n=20000):
    """Rate and 95% CI, resampling TEXTS rather than variants.

    The per-variant rate is up to 18 rewrites of each of 92 texts, and success
    is strongly text-clustered -- which is exactly what this arm's own band
    analysis asserts, that evadability is a property of the original. Wilson
    assumes independent Bernoulli trials and is therefore about half the width
    it should be: cluster-robust SE is 2.44pp against a naive 1.30pp, a design
    effect of 3.55, so the effective n is ~130 rather than 461.

    Returns (rate, lo, hi, n_clusters, n_variants, design_effect).
    """
    cl = collections.defaultdict(list)
    for r in rows:
        cl[r["seg_id"]].append(bool(pred(r)))
    keys = list(cl)
    m = len(keys)
    N = sum(len(cl[k]) for k in keys)
    p = sum(sum(cl[k]) for k in keys) / N
    var = m / (m - 1) * sum((sum(cl[k]) - p * len(cl[k])) ** 2
                            for k in keys) / N ** 2
    naive = math.sqrt(p * (1 - p) / N) if 0 < p < 1 else float("nan")
    rng = random.Random(seed)
    draws = []
    for _ in range(n):
        s = [cl[keys[rng.randrange(m)]] for _ in range(m)]
        tot = sum(len(x) for x in s)
        if tot:
            draws.append(sum(sum(x) for x in s) / tot)
    draws.sort()
    return (p, draws[int(.025 * len(draws))], draws[int(.975 * len(draws))],
            m, N, (math.sqrt(var) / naive) ** 2)


def fisher(a, b, c, d):
    """Two-sided Fisher exact on [[a,b],[c,d]]."""
    def lc(n, k):
        return (math.lgamma(n + 1) - math.lgamma(k + 1)
                - math.lgamma(n - k + 1))
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def pr(x):
        return math.exp(lc(r1, x) + lc(n - r1, c1 - x) - lc(n, c1))
    obs = pr(a)
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1)
                        if pr(x) <= obs * (1 + 1e-9)))


def load():
    """-> list of {run, seg_id, seed_verdict, verdict, strict}

    strict is True when a re-score returned fraction_ai == 0.0, None when the
    variant was not re-scored (only Human-labelled variants were).
    """
    J = lambda f: json.load(open(os.path.join(HERE, f)))
    rows = []

    # run 1: v2 blind search, New Brunswick, AI-only seeds
    strict = J("bp_reflip_fractions.json")
    for i, r in J("bypass_pangram_results.json").items():
        rows.append({"run": "NB v2 blind", "seg_id": r["seg_id"],
                     "seed_verdict": "AI", "verdict": r["pangram"],
                     "strict": strict.get(i, {}).get("fraction_ai") == 0.0
                     if r["pangram"] == "Human" else None})

    # run 2: v3 contrastive search, New Brunswick, AI-only seeds
    strict = J("nb_reflip_fractions.json")
    for i, r in J("bypass_v3_pangram.json").items():
        rows.append({"run": "NB v3 contrastive", "seg_id": r["seg_id"],
                     "seed_verdict": "AI", "verdict": r["pangram"],
                     "strict": strict.get(i, {}).get("fraction_ai") == 0.0
                     if r["pangram"] == "Human" else None})

    # run 3: Government Orders, seeds chosen BY OPUS SCORE (biased; see
    # BYPASS_METHODOLOGY.md sample 2). Kept in the pool because excluding a
    # run that produced zero successes would inflate the pooled rate.
    for i, r in J("gov_opusselected_pangram.json").items():
        v = r["pangram"] if isinstance(r, dict) else r
        sid = r.get("seg_id", i) if isinstance(r, dict) else i
        rows.append({"run": "GO Opus-selected", "seg_id": sid,
                     "seed_verdict": "AI", "verdict": v,
                     "strict": None})

    # run 4: Government Orders, all 31 uniform-draw positives, AI and Mixed
    key = {k["id"]: k for k in J("pangram_gov_all_key.json")}
    strict = J("go_reflip_fractions.json")
    for i, v in J("gov_all_pangram.json").items():
        rows.append({"run": "GO all-31 uniform", "seg_id": key[i]["seg_id"],
                     "seed_verdict": key[i]["seed_verdict"], "verdict": v,
                     "strict": strict.get(i, {}).get("fraction_ai") == 0.0
                     if v == "Human" else None})
    return rows


def main():
    rows = load()

    print("PER-RUN\n")
    print(f"{'run':<20s} {'seeds':>6s} {'var':>5s} {'AI':>4s} {'Mix':>4s} "
          f"{'Hum':>4s} {'strict':>7s}")
    for run in ["NB v2 blind", "NB v3 contrastive", "GO Opus-selected",
                "GO all-31 uniform"]:
        v = [r for r in rows if r["run"] == run]
        c = collections.Counter(r["verdict"] for r in v)
        st = sum(1 for r in v if r["strict"])
        print(f"{run:<20s} {len(set(r['seg_id'] for r in v)):>6d} "
              f"{len(v):>5d} {c['AI']:>4d} {c['Mixed']:>4d} {c['Human']:>4d} "
              f"{st:>7d}")

    n = len(rows)
    h = sum(1 for r in rows if r["verdict"] == "Human")
    s = sum(1 for r in rows if r["strict"])
    # CLUSTER ON TEXT. Wilson would assume 461 independent trials; these are
    # up to 18 rewrites of each of 92 texts.
    hp, hlo, hhi, m, _, hdeff = cluster_boot(
        rows, lambda r: r["verdict"] == "Human")
    sp, slo2, shi2, _, _, sdeff = cluster_boot(rows, lambda r: r["strict"])
    print(f"\nPOOLED INDUCED FALSE-NEGATIVE RATE (per variant)")
    print(f"  {m} text clusters over {n} variants; intervals are a "
          f"non-parametric")
    print(f"  cluster bootstrap over texts, 20,000 draws.")
    print(f"  Human label       {h:>3d}/{n} = {100*hp:.1f}% "
          f"[{100*hlo:.1f}, {100*hhi:.1f}]   design effect {hdeff:.2f}")
    print(f"  fraction_ai = 0.0 {s:>3d}/{n} = {100*sp:.1f}% "
          f"[{100*slo2:.1f}, {100*shi2:.1f}]   design effect {sdeff:.2f}")
    print(f"  (Wilson on the same counts would give "
          f"[{100*wilson(h,n)[0]:.1f}, {100*wilson(h,n)[1]:.1f}] and "
          f"[{100*wilson(s,n)[0]:.1f}, {100*wilson(s,n)[1]:.1f}] -- about half")
    print(f"  the width, because it treats each rewrite as independent.)")

    ai = [r for r in rows if r["seed_verdict"] == "AI"]
    ah = sum(1 for r in ai if r["verdict"] == "Human")
    asr = sum(1 for r in ai if r["strict"])
    ap, alo, ahi, am, _, _ = cluster_boot(
        ai, lambda r: r["verdict"] == "Human", seed=1)
    print(f"\n  restricted to unambiguously AI-seeded originals "
          f"({am} clusters):")
    print(f"    Human label     {ah:>3d}/{len(ai)} = {100*ap:.1f}% "
          f"[{100*alo:.1f}, {100*ahi:.1f}]")
    print(f"    strict          {asr:>3d}/{len(ai)} = "
          f"{100*asr/len(ai):.1f}%")

    # -- the seed-verdict question, computed like-for-like -----------------
    go = [r for r in rows if r["run"] == "GO all-31 uniform"]
    print("\nSEED VERDICT: does Pangram's own uncertainty predict evasion?")
    print("  (GO all-31 only -- the sole run containing Mixed seeds)\n")
    print(f"  {'seed':<7s} {'var':>4s} {'->AI':>5s} {'->Mix':>6s} "
          f"{'->Hum':>6s} {'Human rate':>18s}")
    cell = {}
    for sv in ("AI", "Mixed"):
        v = [r for r in go if r["seed_verdict"] == sv]
        c = collections.Counter(r["verdict"] for r in v)
        k, tot = c["Human"], len(v)
        cell[sv] = (k, tot - k)
        lo, hi = wilson(k, tot)
        print(f"  {sv:<7s} {tot:>4d} {c['AI']:>5d} {c['Mixed']:>6d} "
              f"{c['Human']:>6d} {f'{100*k/tot:.1f}% [{100*lo:.0f},{100*hi:.0f}]':>18s}")
    p = fisher(cell["AI"][0], cell["AI"][1], cell["Mixed"][0],
               cell["Mixed"][1])
    print(f"\n  Fisher exact on reaching Human: p = {p:.3f}")
    print("  NOTE: the superseded '22% vs 76%' counted 'not confidently AI'")
    print("  as success, which scores a Mixed seed that STAYED Mixed as an")
    print("  evasion. Like-for-like, the gap is directional and not")
    print("  significant per variant.")

    # ---- the second headline: per-target, best method only ---------------
    #
    # The pooled per-variant rate above is deliberately conservative: it
    # averages two superseded searches into the denominator and asks how often
    # a RANDOM attempt succeeds. That is the wrong question for an adversary,
    # who does not care how many drafts they discard -- only whether the speech
    # they wanted through got through.
    #
    # This is the same data asked the other way: taking only the FINAL search
    # per chamber, on what fraction of TARGETS did at least one variant reach a
    # clean Human verdict? It is the figure a fresh study replicating our best
    # method should expect to reproduce, so it is reported alongside.
    # THE DENOMINATOR IS TARGETS SEARCHED, NOT TARGETS THAT YIELDED.
    # The search only submits a variant to Pangram if its Opus proxy score
    # drops below 50. Sixteen targets across the three searches ran four to
    # six full rounds and never produced anything under that gate. They are
    # attack FAILURES -- an adversary who cannot produce a candidate their own
    # proxy will submit has not walked that speech past anything -- so they
    # belong in the denominator. Counting only targets that yielded makes the
    # rate conditional on the attack having already half-succeeded, and
    # inflated the headline from 22.5% to 24.6%.
    SEARCH = {"NB v3 contrastive": "bypass_v3.json",
              "GO all-31 uniform": "gov_bypass_all.json",
              "GO Opus-selected": "gov_bypass_v3.json"}

    def searched(run):
        f = os.path.join(HERE, SEARCH[run])
        if not os.path.exists(f):
            return None
        return len(json.load(open(f))["state"])

    print("\nPER TARGET, FINAL SEARCH PER CHAMBER ONLY")
    print("(at least one variant reaching Human; denominator is targets")
    print("SEARCHED, including those that never cleared the submission gate)\n")
    print(f"  {'run':<20s} {'searched':>9s} {'zero-yield':>11s} "
          f"{'label':>16s} {'strict':>16s}")
    tt = hh = ss = 0
    for run in ["NB v3 contrastive", "GO all-31 uniform"]:
        t = collections.defaultdict(list)
        for r in rows:
            if r["run"] == run:
                t[r["seg_id"]].append(r)
        n = searched(run) or len(t)
        k = sum(1 for v in t.values()
                if any(x["verdict"] == "Human" for x in v))
        st = sum(1 for v in t.values() if any(x["strict"] for x in v))
        tt += n; hh += k; ss += st
        print(f"  {run:<20s} {n:>9d} {n - len(t):>11d} "
              f"{f'{k}/{n} = {100*k/n:.1f}%':>16s} "
              f"{f'{st}/{n} = {100*st/n:.1f}%':>16s}")
    lo, hi = wilson(hh, tt)
    slo, shi = wilson(ss, tt)
    print(f"  {'POOLED':<20s} {tt:>9d} {'':>11s} "
          f"{f'{hh}/{tt} = {100*hh/tt:.1f}%':>16s} "
          f"{f'{ss}/{tt} = {100*ss/tt:.1f}%':>16s}")
    print(f"    label  [{100*lo:.1f}, {100*hi:.1f}]   "
          f"strict [{100*slo:.1f}, {100*shi:.1f}]")
    print("  The two chambers agree within their intervals despite")
    print("  contradicting each other on WHICH edits work (see")
    print("  BYPASS_METHODOLOGY.md) -- the rate transfers, the playbook")
    print("  does not.")

    print("\nTARGETS THE SEARCH COULD NOT MOVE")
    print("  The only direct evidence in the study of text that resisted the")
    print("  attack. Best proxy score reached, against a submission gate of")
    print("  < 50 and a 3x re-score sd of ~2.4:\n")
    tot_s = tot_z = 0
    for run, f in SEARCH.items():
        fp = os.path.join(HERE, f)
        if not os.path.exists(fp):
            continue
        d = json.load(open(fp))
        kept = set(x["seg_id"] for x in d["kept"])
        z = [(s, d["state"][s]["rounds"], d["state"][s]["best"])
             for s in d["state"] if s not in kept]
        tot_s += len(d["state"]); tot_z += len(z)
        print(f"  {run}: {len(z)} of {len(d['state'])} searched")
        for s, r, b in sorted(z, key=lambda x: x[2]):
            print(f"      {s:<24s} {r} rounds, best {b:.1f}")
    print(f"\n  {tot_z} of {tot_s} searched targets ({100*tot_z/tot_s:.0f}%) "
          f"yielded nothing submittable.")
    print("  Caveat that cuts the other way: the four Government Orders")
    print("  near-misses sit at 50.0-51.7 against a gate of < 50 and a")
    print("  re-score sd of ~2.4, so their exclusion is closer to a coin flip")
    print("  than a demonstration that the text resists rewriting. Their best")
    print("  variants were discarded rather than stored, so the question")
    print("  cannot be settled from this run.")

    # per-text, conditional on the search budget
    print("\nPER TEXT, ALL RUNS AND SEED TYPES (conditional on ~6 rounds x 3")
    print("variants -- a property of the search budget, not of the detector)\n")
    for run in ["NB v3 contrastive", "GO all-31 uniform"]:
        v = [r for r in rows if r["run"] == run]
        for sv in (["AI"] if run.startswith("NB") else ["AI", "Mixed"]):
            t = collections.defaultdict(list)
            for r in v:
                if r["seed_verdict"] == sv:
                    t[r["seg_id"]].append(r["verdict"])
            if not t:
                continue
            k = sum(1 for l in t.values() if "Human" in l)
            lo, hi = wilson(k, len(t))
            print(f"  {run:<20s} seed {sv:<6s} {k:>2d}/{len(t):<3d} = "
                  f"{100*k/len(t):>5.1f}% [{100*lo:.0f}, {100*hi:.0f}]")

    print(f"\nSPECIFICITY FOR CONTRAST: 0 AI labels in 1,260 pre-AI controls")
    print(f"  (see prevalence_report.py). The reversals above are movements")
    print(f"  INTO a class the detector otherwise reaches 0/1,260 times.")


if __name__ == "__main__":
    main()
