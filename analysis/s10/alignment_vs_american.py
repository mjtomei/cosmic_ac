#!/usr/bin/env python3
"""Does post-training move a model toward American parliamentary English?

THE HYPOTHESIS (Matthew's, 2026-08-13)

Alignment and the American experiment are argued to be the same optimization
run on different substrates. Speech optimized for approval across a
heterogeneous audience that must be kept in coalition converges on a
characteristic register: hedged, inclusive, aggregative, reluctant to alienate.
The United States ran that process on people for two centuries; RLHF runs it on
models in weeks. On this account models do not sound American because they were
trained on American text -- they sound American because the same pressure
produces the same speech, and the pre-LLM global drift toward that register is
soft power exporting the human version of it.

THE TEST

If it is right, the vocabulary shift that post-training induces in a model
should resemble the vocabulary difference that already separated American from
British legislative speech BEFORE any LLM existed.

  pref(w)  = log( P(w | instruct) / P(w | base) )        our generations
  amer(w)  = log( P(w | US 2006-2010) / P(w | UK 2006-2010) )   real Hansard

A positive rank correlation between them is the prediction. The window is
2006-2010: pre-transformer, and early enough that the UK's own climb has barely
begun, so `amer` measures a difference between two human traditions rather than
a difference in how far each has already drifted.

THREE CONTROLS, BECAUSE THE NAIVE VERSION WOULD PASS ON ARTIFACTS

  SPELLING. -ize/-ise, -or/-our, -er/-re. Models trained mostly on American text
  prefer American spellings, and American Hansard uses them; that correlation is
  real and utterly uninteresting. Both members of every detected pair are
  dropped, and the test is reported with and without the filter so the size of
  the artifact is visible rather than assumed away.

  FREQUENCY. Both quantities are log ratios of small counts, so rare words carry
  more noise and can manufacture correlation through shared denominators. The
  partial correlation holds log corpus frequency fixed.

  OTHER ANGLOPHONES. If pref correlates just as well with log(Canada/UK) and
  log(Australia/UK), then the finding is "post-training moves away from British
  usage", not "toward American usage". Canada is the interesting middle case:
  North American, and on the hypothesis it should sit between the two.

THE HEADLINE IS THE UNFILTERED STRATUM (Matthew's call, 2026-08-13)

An earlier version reported a topic-filtered stratum as primary, on the grounds
that words like `programs`, `coordination` and `percent` are subject matter
rather than register. That was wrong twice over. Most of those words are
generic managerial English, not American institutions -- and the diffusion of
managerial vocabulary from American into British usage IS the hypothesis, so
filtering it out assumes the conclusion. Topical influence carried by soft
power is the same finding, not a confound.

So `all words` is the reported result. The narrower strata below it are
robustness checks and are read as such: they show how much of the correlation
survives progressively harsher filtering, which is worth knowing, but none of
them is the measurement. The one genuinely artifactual contrast -- US/UK
spelling and one-word orthographic forms like `percent` for "per cent" -- is
reported as its own stratum so the size of that artifact is visible.

WHAT A PASS WOULD AND WOULD NOT SHOW

It would show that the direction post-training pushes vocabulary coincides with
the direction that already separated two human legislatures. It would NOT
establish the causal story -- a shared cause (both trained on, or influenced by,
the same American-dominated written corpus) predicts the same correlation. The
honest claim available from this design is compatibility, plus a measured effect
size, not confirmation.

Usage: python alignment_vs_american.py [--min-count 20] [--procs 8]
"""
import argparse
import glob
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rlhf_pref_analyze as A          # noqa: E402
import rlhf_pref_scale as S            # noqa: E402

TOKEN_RE = re.compile(r"[a-z']+")
OUT = os.path.join(HERE, "alignment_vs_american.json")
YEARS = ("2006", "2007", "2008", "2009", "2010")

GROUPS = {
    "US": ["us/segments_us_house.jsonl", "us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl"],
    "CA": ["provinces/segments_ab.jsonl", "provinces/segments_bc.jsonl",
           "provinces/segments_on.jsonl", "provinces/segments_mb.jsonl",
           "provinces/segments_ns.jsonl", "provinces/segments_nl.jsonl",
           "provinces/segments_sk.jsonl"],
    "AU": ["provinces/segments_aus_nsw.jsonl", "provinces/segments_aus_vic.jsonl",
           "provinces/segments_aus_qld.jsonl", "provinces/segments_aus_wa.jsonl",
           "provinces/segments_aus_sa.jsonl"],
}

# US/UK spelling pairs: transform applied to the AMERICAN form gives the British
SPELL = [(re.compile(r"ize$"), "ise"), (re.compile(r"izes$"), "ises"),
         (re.compile(r"ized$"), "ised"), (re.compile(r"izing$"), "ising"),
         (re.compile(r"ization$"), "isation"), (re.compile(r"izations$"), "isations"),
         (re.compile(r"yze$"), "yse"), (re.compile(r"yzed$"), "ysed"),
         (re.compile(r"or$"), "our"), (re.compile(r"ors$"), "ours"),
         (re.compile(r"ter$"), "tre"), (re.compile(r"ters$"), "tres"),
         (re.compile(r"og$"), "ogue"), (re.compile(r"ogs$"), "ogues"),
         (re.compile(r"ense$"), "ence"), (re.compile(r"eled$"), "elled"),
         (re.compile(r"eling$"), "elling"), (re.compile(r"eler$"), "eller")]

# One-word American renderings of two-word British forms. These are
# orthographic, not lexical: UK Hansard writes "per cent", so "percent" scores
# as maximally American while carrying no register information at all.
ORTHOGRAPHIC = {"percent", "anymore", "awhile", "everyday", "someday"}


def british_variants(vocab):
    """Candidate British spellings of every American form in vocab."""
    out = set()
    for w in vocab:
        for pat, rep in SPELL:
            if pat.search(w):
                out.add(pat.sub(rep, w))
    return out


def spelling_pairs(vocab, attested):
    """Both members of every US/UK spelling pair.

    The first version tested the British form for membership of the GENERATED
    vocabulary, which is the wrong set: a model that prefers American spelling
    rarely emits the British form, so the pair went undetected and the American
    member stayed in the test. It found 16 pairs. Attestation is a property of
    the real corpora, so `attested` is the UK Hansard counter -- the British
    form only has to exist in British Hansard, which is exactly the condition
    that makes the pair a spelling difference rather than a lexical one."""
    out = set()
    for w in vocab:
        for pat, rep in SPELL:
            if pat.search(w):
                b = pat.sub(rep, w)
                if attested.get(b, 0) > 0:
                    out.add(w)
                    out.add(b)
    return out


def _count(job):
    files, need = job
    c, n = Counter(), 0
    pre = tuple(f'"{y}-'.encode() for y in YEARS)
    for f in files:
        with open(os.path.join(HERE, f), "rb") as fh:
            for line in fh:
                if not any(p in line for p in pre):
                    continue
                d = json.loads(line)
                if not d.get("scoreable") or d.get("translated"):
                    continue
                if (d.get("date") or "")[:4] not in YEARS:
                    continue
                t = TOKEN_RE.findall(d["text"].lower())
                n += len(t)
                for w in t:
                    if w in need:
                        c[w] += 1
    return c, n


def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            m = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[o[k]] = m
            i = j + 1
        return r
    x, y = rk(a), rk(b)
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if not sx or not sy:
        return 0.0
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sx * sy)


def partial(a, b, ctrl):
    rab, rac, rbc = spearman(a, b), spearman(a, ctrl), spearman(b, ctrl)
    d = math.sqrt(max(1e-12, (1 - rac ** 2) * (1 - rbc ** 2)))
    return (rab - rac * rbc) / d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-count", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()

    # ---- pref(w) from the generations, families balanced ----
    base_c, base_n, inst_c, inst_n, fams = Counter(), 0, Counter(), 0, []
    have = sorted((len(json.load(open(os.path.join(HERE, "rlhf_gen",
                                                   f"{f}_base.json"))))
                   for f, _, _ in S.PAIRS
                   if os.path.exists(os.path.join(HERE, "rlhf_gen",
                                                  f"{f}_base.json"))),
                  reverse=True)
    bal = have[1] if len(have) > 1 else have[0]
    for fam, _, _ in S.PAIRS:
        bp = os.path.join(HERE, "rlhf_gen", f"{fam}_base.json")
        ip = os.path.join(HERE, "rlhf_gen", f"{fam}_instruct.json")
        if not (os.path.exists(bp) and os.path.exists(ip)):
            continue
        bg, ig = json.load(open(bp)), json.load(open(ip))
        if min(len(bg), len(ig)) < bal:
            continue
        bg, ig = bg[:bal], ig[:bal]
        keep = [i for i in range(bal) if not A.META.search(ig[i][:300])
                and not A.META.search(bg[i][:300])]
        bc, bn = A.counts([bg[i] for i in keep])
        ic, inn = A.counts([ig[i] for i in keep])
        base_c += bc; base_n += bn
        inst_c += ic; inst_n += inn
        fams.append(f"{fam}({bal})")

    vocab = {w for w in set(base_c) | set(inst_c)
             if w.isalpha() and len(w) >= 4
             and base_c[w] + inst_c[w] >= a.min_count}
    style = set(A.load_style())
    # count the British variants too, so spelling pairs can be detected on
    # attestation in real Hansard rather than on the generated vocabulary
    need = vocab | british_variants(vocab) | style
    print(f"families {', '.join(fams)}; {len(vocab):,} words with "
          f">={a.min_count} generated occurrences\n")

    # ---- real-corpus counts, 2006-2010 ----
    jobs = [(f, need) for f in GROUPS.values()]
    names = list(GROUPS)
    with Pool(min(a.procs, len(jobs))) as pool:
        res = pool.map(_count, jobs)
    C = {names[i]: res[i][0] for i in range(len(names))}
    N = {names[i]: res[i][1] for i in range(len(names))}
    for k in names:
        print(f"  {k}: {N[k]/1e6:>7.1f}M words {YEARS[0]}-{YEARS[-1]}")

    # keep words attested in both reference corpora, so the ratio is a
    # comparison rather than a pseudocount artifact
    words = sorted(w for w in vocab if C["US"][w] > 0 and C["UK"][w] > 0)
    spell = spelling_pairs(set(words), C["UK"])
    print(f"\n  {len(words):,} words attested in both US and UK; "
          f"{len(spell)} are US/UK spelling variants")

    def lr(w, x, y):
        return math.log(((C[x][w] + 0.5) / N[x]) / ((C[y][w] + 0.5) / N[y]))

    def pref(w):
        return math.log(((inst_c[w] + 0.5) / inst_n)
                        / ((base_c[w] + 0.5) / base_n))

    results = {}
    nospell = [w for w in words if w not in spell and w not in ORTHOGRAPHIC]
    # PRIMARY STRATUM. Requiring the word to be well attested in BOTH corpora
    # is symmetric and does not beg the question: it removes referents one
    # legislature simply does not have (foley, suvs, gubernatorial) while
    # keeping every managerial word both use (programs, coordination,
    # cooperation). An earlier version restricted to Kobak style words instead,
    # which cut 4,797 words to 146 and destroyed the test's power to protect
    # against a dozen -- and it also begged the question, since diffusion of
    # managerial vocabulary from American into British usage IS the hypothesis,
    # not a confound to be filtered out.
    shared = [w for w in nospell if C["US"][w] >= 20 and C["UK"][w] >= 20]
    # Robustness. The top of the joint ranking is still institution-heavy
    # (senate, congress, federal, dollars), which clear a >=20 bar because UK
    # Hansard does mention American institutions occasionally. If the
    # correlation is carried by that tail it is not a register finding, so:
    # drop the most US-skewed and most UK-skewed tenth, and separately raise
    # the attestation bar tenfold. A broad register shift survives both.
    _sk = sorted(shared, key=lambda w: lr(w, "US", "UK"))
    trimmed = _sk[len(_sk) // 10: -len(_sk) // 10]
    strict = [w for w in nospell if C["US"][w] >= 200 and C["UK"][w] >= 200]
    for label, ws in (("all words", words),
                      ("spelling + orthographic removed", nospell),
                      ("PRIMARY: attested >=20 in both", shared),
                      ("robustness: middle 80% by US/UK skew", trimmed),
                      ("robustness: attested >=200 in both", strict),
                      ("Kobak style words only", [w for w in nospell if w in style])):
        if len(ws) < 30:
            print(f"\n=== {label}: only {len(ws)} words, skipped ===")
            continue
        p = [pref(w) for w in ws]
        freq = [math.log(C["UK"][w] + C["US"][w] + 1) for w in ws]
        row = {"n_words": len(ws)}
        print(f"\n=== {label} (n = {len(ws):,}) ===")
        print(f"  {'contrast':<26s} {'Spearman':>9s} {'partial|freq':>13s}")
        for x, y in (("US", "UK"), ("CA", "UK"), ("AU", "UK"), ("US", "CA")):
            v = [lr(w, x, y) for w in ws]
            r, pr = spearman(p, v), partial(p, v, freq)
            row[f"{x}_vs_{y}"] = {"spearman": r, "partial": pr}
            print(f"  pref vs log({x}/{y}){'':<8s} {r:>+9.4f} {pr:>+13.4f}")
        results[label] = row

        # permutation null on the headline contrast
        v = [lr(w, "US", "UK") for w in ws]
        rng = random.Random(11)
        obs = spearman(p, v)
        null = []
        for _ in range(200):
            q = p[:]
            rng.shuffle(q)
            null.append(spearman(q, v))
        null.sort()
        pv = sum(1 for x in null if abs(x) >= abs(obs)) / len(null)
        row["perm_p"] = pv
        print(f"  permutation p (US/UK, 200 shuffles): {pv:.3f}")

    # Is the US the outlier, or is every anglophone legislature equidistant?
    # Mean |log ratio| over the shared vocabulary is a plain lexical divergence.
    print("\n\nLEXICAL DIVERGENCE BETWEEN LEGISLATURES, 2006-2010")
    print("  mean |log frequency ratio| over the primary stratum "
          f"({len(shared):,} words)\n")
    pairs = [("US","UK"),("US","CA"),("US","AU"),("UK","CA"),("UK","AU"),("CA","AU")]
    div = {}
    for x, y in pairs:
        d = sum(abs(lr(w, x, y)) for w in shared) / len(shared)
        div[f"{x}-{y}"] = d
        print(f"  {x}-{y}   {d:.4f}")
    results["divergence"] = div
    us = [div[k] for k in div if k.startswith("US")]
    non = [div[k] for k in div if not k.startswith("US")]
    print(f"\n  mean involving US: {sum(us)/len(us):.4f}   "
          f"not involving US: {sum(non)/len(non):.4f}")

    # what post-training adds that is most American
    sc = sorted(shared, key=lambda w: -(pref(w) + lr(w, "US", "UK")))
    print("\n  most instruct-preferred AND most American (spelling excluded):")
    print("    " + ", ".join(sc[:30]))
    results["top_joint"] = sc[:60]
    results["families"] = fams
    results["corpus_words"] = N
    json.dump(results, open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
