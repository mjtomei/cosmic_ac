#!/usr/bin/env python3
r"""Post-process pandoc's LaTeX (_body_pandoc.tex) into body.tex.

The canonical source is ../S10-WRITEUP-DRAFT.md; build_body.sh runs pandoc then
this. The draft bakes section numbers into heading text ("4.6b What ...") and
refers to sections as literal "§4.6b". Once LaTeX auto-numbers, every literal
number is wrong, so this:

  1. strips the baked-in number from each heading and gives it a SEMANTIC label
     (sec:occupation, not 46b-...), so LaTeX numbers and cleveref links them;
  2. rewrites internal §N / §N.M refs to \cref{...} and Appendix refs to
     Appendix~\ref{...} (cross-document refs like "METHODOLOGY §6.1c" and the
     external "Table 23" of the Pangram report are left as literal text);
  3. wraps the three figures in float environments with captions and labels,
     and points prose at them with \cref;
  4. inserts \appendix before the first appendix so A-D number as letters.

Idempotence is not required: it always runs on fresh pandoc output.
"""
import re, sys

SRC, DST = "_body_pandoc.tex", "body.tex"

# slug (pandoc's) -> semantic label
LABELS = {
 "1-the-question-and-why-it-needs-two-instruments":"sec:intro",
 "2-data":"sec:data",
 "21-two-contamination-hazards-both-found-by-looking":"sec:hazards",
 "3-method":"sec:method",
 "31-the-calibration-that-carries-the-argument":"sec:calibration-method",
 "32-detector-and-a-defect-worth-recording":"sec:detector",
 "33-why-the-frequency-arm-is-descriptive-not-inferential":"sec:freq-descriptive",
 "34-instruments-retired-and-why":"sec:retired",
 "4-results":"sec:results",
 "41-calibration-1260--1260":"sec:calibration",
 "42-prevalence-90-of-words-with-an-elevenfold-spread":"sec:prevalence",
 "43-genre-drafting-concentrates-in-scripted-business":"sec:genre",
 "44-the-opus-screen-tracks-pangram":"sec:screen-pangram",
 "45-the-register-shift-starts-in-199496-decades-before-the-machines":"sec:register-shift",
 "45a-the-climb-is-everywhere-except-the-united-states":"sec:climb-geography",
 "46-a-generational-gradient-net-of-calendar-drift":"sec:generational",
 "46a-class-and-the-register-jointly-significant-individually-noisy--and-education-is-not-it":"sec:class",
 "all-four-predictors-at-once":"sub:four-predictors",
 "class-the-provincial-estimates-retained-as-the-discovery-record-see-the-panel-result-above":"sub:class-provincial",
 "education-the-provincial-ladder-did-not-replicate-see-above":"sub:education-provincial",
 "the-shape-has-a-name--held-now-as-hypothesis-not-finding":"sub:shape-name",
 "flight-class-i-avoids-the-words-that-became-common":"sub:flight",
 "prominence-a-gradient-in-the-provinces-an-arc-in-the-national-chambers":"sub:prominence-class",
 "word-mix-the-effects-live-in-rate-not-vocabulary--and-machine-text-sits-outside-the-geometry":"sub:wordmix",
 "limits-and-they-are-real":"sub:class-limits",
 "46b-what-the-class-shape-was-occupation-pre-registered-and-run":"sec:occupation",
 "47-the-register-is-a-post-training-artifact":"sec:posttraining",
 "47a-coverage-post-training-moves-the-models-vocabulary-onto-hansards":"sec:coverage",
 "48-permeation-detector-independent-and-small-but-positive":"sec:permeation",
 "49-quality-better-formed-not-worse-engaged--and-evadable-under-effort":"sec:quality",
 "5-limits":"sec:limits",
 "6-policy-context":"sec:policy",
 "7-related-work":"sec:related",
 "8-discussion-detection-as-a-norms-instrument-and-what-to-measure-instead":"sec:discussion",
 "81-the-limit":"sec:disc-limit",
 "82-where-the-norms-argument-actually-lands":"sec:disc-norms",
 "83-the-substitution-and-why-our-null-is-the-argument-for-it":"sec:disc-substitution",
 "84-where-text-is-a-proxy-for-a-persons-internal-state":"sec:disc-proxy",
 "85-measuring-the-human-contribution-against-an-automated-counterpart":"sec:disc-human",
 "86-future-work":"sec:future",
 "appendix-a--null-results":"app:null",
 "appendix-b--superseded-analyses":"app:superseded",
 "appendix-c--replication-and-reproducibility":"app:repro",
 "c1-cross-route-reproduction-of-the-detector":"sec:cross-route",
 "c2-independent-re-analysis":"sec:reanalysis",
 "c3-bypass-sample-selection":"sec:bypass-sample",
 "c4-artifacts":"sec:artifacts",
 "appendix-d--robustness-and-sensitivity-checks":"app:robustness",
 "d1-the-judge-leakage-control-documented-run-not-adopted":"sec:judge-leakage",
 "d2-prominence-wikipedia-article-length-on-the-full-panel":"sec:prominence-full",
 "d3-prominence-in-buckets-which-is-how-it-should-be-read":"sec:prominence-buckets",
 "d4-is-the-cohort-gradient-ministerial-office":"sec:cohort-ministerial",
}

# §N / §N.M  ->  label   (only these resolve; anything else is left literal)
NUMMAP = {
 "1":"sec:intro","2":"sec:data","2.1":"sec:hazards","3":"sec:method",
 "3.1":"sec:calibration-method","3.2":"sec:detector","3.3":"sec:freq-descriptive",
 "3.4":"sec:retired","4":"sec:results","4.1":"sec:calibration","4.2":"sec:prevalence",
 "4.3":"sec:genre","4.4":"sec:screen-pangram","4.5":"sec:register-shift",
 "4.5a":"sec:climb-geography","4.6":"sec:generational","4.6a":"sec:class",
 "4.6b":"sec:occupation","4.7":"sec:posttraining","4.7a":"sec:coverage",
 "4.8":"sec:permeation","4.9":"sec:quality","5":"sec:limits","6":"sec:policy",
 "7":"sec:related","8":"sec:discussion","8.1":"sec:disc-limit","8.2":"sec:disc-norms",
 "8.3":"sec:disc-substitution","8.4":"sec:disc-proxy","8.5":"sec:disc-human","8.6":"sec:future",
}
APPMAP = {
 "A":"app:null","B":"app:superseded","C":"app:repro","D":"app:robustness",
 "C.1":"sec:cross-route","C.2":"sec:reanalysis","C.3":"sec:bypass-sample","C.4":"sec:artifacts",
 "D.1":"sec:judge-leakage","D.2":"sec:prominence-full","D.3":"sec:prominence-buckets",
 "D.4":"sec:cohort-ministerial",
}
FIGLABEL = {"class_by_era_grouped.png":"fig:class-era","altitude_u.png":"fig:altitude",
            "bypass_search.png":"fig:bypass"}

NUMSTRIP = re.compile(r'^(?:Appendix\s+[A-D]\s+---\s+|(?:[0-9]+(?:\.[0-9]+[a-z]?)?|[A-D]\.[0-9]+[a-z]?)\.?\s+)')

def transform_headings(t):
    pat = re.compile(r'\\hypertarget\{([^}]*)\}\{%\n\\(section|subsection|subsubsection)\{((?:[^{}]|\{[^{}]*\})*)\}\\label\{\1\}\}')
    def repl(m):
        slug, level, title = m.group(1), m.group(2), m.group(3)
        title = NUMSTRIP.sub('', title)
        if slug == "abstract":
            return r'\section*{Abstract}'
        lab = LABELS.get(slug)
        if not lab:
            sys.stderr.write("WARN: no label for slug %r\n" % slug)
            return "\\%s{%s}" % (level, title)
        return "\\%s{%s}\\label{%s}" % (level, title, lab)
    t, n = pat.subn(repl, t)
    sys.stderr.write("headings transformed: %d\n" % n)
    return t

def grab(t, i):
    """t[i] must be '{'; return (inner, index-after-matching-'}')."""
    assert t[i] == '{'
    d, j = 0, i
    while j < len(t):
        if t[j] == '{': d += 1
        elif t[j] == '}':
            d -= 1
            if d == 0: return t[i+1:j], j+1
        j += 1
    raise ValueError("unbalanced")

def wrap_figures(t):
    for fn, lab in FIGLABEL.items():
        m = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{' + re.escape(fn) + r'\}', t)
        if not m:
            sys.stderr.write("WARN: figure not found: %s\n" % fn); continue
        start = m.start()
        k = m.end()
        while k < len(t) and t[k] in ' \n\t': k += 1
        if not t.startswith('\\emph{', k):
            sys.stderr.write("WARN: no caption after %s\n" % fn); continue
        cap, k = grab(t, k + len('\\emph'))
        # optional trailing "†\footnote{...}" -> inline as a parenthetical
        k2 = k
        while k2 < len(t) and t[k2] in ' \n\t': k2 += 1
        foot = ""
        mfoot = re.match(r'(?:†\s*)?\\footnote', t[k2:])
        if mfoot:
            bstart = k2 + t[k2:].index('{', 0)
            fc, k = grab(t, bstart)
            foot = " (" + fc.strip() + ")"
        env = ("\\begin{figure}[htbp]\n\\centering\n"
               "\\includegraphics[width=0.85\\linewidth]{%s}\n"
               "\\caption{%s%s}\n\\label{%s}\n\\end{figure}" % (fn, cap.strip(), foot, lab))
        t = t[:start] + env + t[k:]
    return t

def replace_section_refs(t):
    def repl(m):
        num = m.group(1)
        lab = NUMMAP.get(num)
        return ("\\cref{%s}" % lab) if lab else m.group(0)
    return re.sub(r'§(\d+(?:\.\d+[a-z]?)?)', repl, t)

def replace_appendix_refs(t):
    def repl(m):
        key = m.group(1) + (m.group(2) or "")
        lab = APPMAP.get(key)
        return ("Appendix~\\ref{%s}" % lab) if lab else m.group(0)
    return re.sub(r'Appendix~?\s*([A-D])((?:\.[0-9]+[a-z]?))?', repl, t)

def figure_ref_anchors(t):
    subs = [
      (r"sits\s+above\s+class\s+I\s+in\s+all\s+seven\s+half-decades",
       r"\g<0> (\\cref{fig:class-era})"),
      (r"carry\s+the\s+claim\.",
       r"carry the claim; \\cref{fig:altitude} plots both ladders."),
      (r"The\s+figure\s+below\s+lays\s+out\s+the\s+loop\.",
       r"\\Cref{fig:bypass} lays out the loop."),
    ]
    for a, b in subs:
        t, n = re.subn(a, b, t, count=1)
        if n != 1: sys.stderr.write("WARN: fig-anchor %r subs=%d\n" % (a, n))
    return t

def insert_appendix(t):
    needle = "\\section{Null results}\\label{app:null}"
    if needle in t:
        t = t.replace(needle, "\\appendix\n\n" + needle, 1)
    else:
        sys.stderr.write("WARN: app:null heading not found for \\appendix\n")
    return t

def main():
    t = open(SRC, encoding="utf-8").read()
    t = transform_headings(t)
    t = wrap_figures(t)
    t = figure_ref_anchors(t)
    t = replace_section_refs(t)
    t = replace_appendix_refs(t)
    t = insert_appendix(t)
    open(DST, "w", encoding="utf-8").write(t)
    sys.stderr.write("wrote %s (%d chars)\n" % (DST, len(t)))

main()
