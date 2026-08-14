#!/usr/bin/env python3
"""Build length-banded corpora for the permeation test.

THE ARGUMENT THIS SERVES

The lexicon result shows AI-preferred vocabulary rising. The obvious reading
is that members are pasting machine drafts. The alternative -- and the more
consequential one -- is that the machine register has permeated how people
write and speak generally, so it shows up even in text nobody drafted with a
model. Direct drafting is a story about a few hundred legislators; permeation
is a story about mass indirect behaviour change.

Separating them needs text that is measurably NOT machine-drafted. We now
have it. Pangram adjudicated 120 randomly drawn 50-119 word segments from
2025-26 across three parliaments and returned **1 AI** (0.8%, Wilson upper
bound 4.6%). The same detector returns 17.5% on the 120-360 word band of the
same corpora, so this is a property of the stratum, not of a blind detector.

So: run the frozen protocol, unmodified, on the short band alone. If
AI-preferred vocabulary still rises there against its own frequency-matched
placebo null, the rise cannot be explained by machine drafting of those
segments, because those segments are essentially not machine-drafted.

The long band is emitted too, as a dose-response contrast: if permeation is
real the short band should show a rise; if drafting were the whole story the
short band should show none and the long band all of it.

Bands are defined identically in both eras and segmentation is date-blind,
so the split cannot itself manufacture a difference between periods.

Usage: python permeation_strata.py            # build the files
       then: bash permeation_run.sh           # run the frozen protocol
"""
import json
import os

SHORT_MIN, SHORT_MAX = 50, 120     # [50, 120)
CORPORA = {
    "nb": ("segments.jsonl", "New Brunswick"),
    "ie": ("ie/segments_ie_en.jsonl", "Dail Eireann"),
    "ca": ("ca/segments_ca_en.jsonl", "Canada House of Commons"),
    "uk": ("uk/segments_uk.jsonl", "UK House of Commons"),
}
OUT = "permeation"


def keep(d):
    """Member-authored, scoreable, in one of the protocol windows."""
    if not d.get("scoreable") or d.get("translated"):
        return False
    if d.get("orig_frac", 1.0) <= 0.5:
        return False
    return d["date"] <= "2022-12-31" or d["date"] >= "2024-01-01"


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            print(f"  skip {code}: {path} missing")
            continue
        fh = {b: open(f"{OUT}/{code}_{b}.jsonl", "w") for b in ("short", "long")}
        n = {b: [0, 0] for b in fh}          # [segments, words] per band
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            b = "short" if SHORT_MIN <= d["n_words"] < SHORT_MAX else "long"
            fh[b].write(line)
            n[b][0] += 1
            n[b][1] += d["n_words"]
        for f in fh.values():
            f.close()
        for b in ("short", "long"):
            rows.append((code, name, b, n[b][0], n[b][1]))
            print(f"  {code}_{b}: {n[b][0]:>7,} segments  {n[b][1]:>11,} words")

    with open(f"{OUT}/bands.json", "w") as f:
        json.dump([{"code": c, "name": nm, "band": b, "segments": s, "words": w}
                   for c, nm, b, s, w in rows], f, indent=1)

    # emit the driver so the protocol itself stays untouched and frozen
    with open("permeation_run.sh", "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write("# Frozen protocol v1.0, unmodified, per length band.\n")
        f.write("# Corpus name seeds the RNG, so each band gets its own\n")
        f.write("# independent placebo draw -- bands are not sharing a null.\n")
        f.write("set -e\n")
        for c, nm, b, s, w in rows:
            if s < 200:
                f.write(f'echo "skip {c}_{b}: only {s} segments"\n')
                continue
            f.write(f'python3 run_protocol.py "{nm} {b}-band" '
                    f'perm_{c}_{b} {OUT}/{c}_{b}.jsonl\n')
    os.chmod("permeation_run.sh", 0o755)
    print("\nwrote permeation_run.sh")


if __name__ == "__main__":
    main()
