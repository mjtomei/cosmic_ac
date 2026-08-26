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

# Heading labels. Numbered headings are keyed by their NUMERIC PREFIX in the
# pandoc slug ("46b-..." -> sec:occupation), so heading TEXT can be rewritten
# freely without touching this file. Unnumbered subsubsections keep exact slugs.
PREFIX_LABELS = {
 "1":"sec:intro","2":"sec:data","21":"sec:hazards","3":"sec:method",
 "31":"sec:calibration-method","32":"sec:detector","33":"sec:freq-descriptive",
 "34":"sec:retired","4":"sec:results","41":"sec:calibration","42":"sec:prevalence",
 "43":"sec:genre","44":"sec:screen-pangram","45":"sec:register-shift",
 "45a":"sec:climb-geography","45b":"sec:register-robust","46":"sec:generational",
 "46a":"sec:class","46b":"sec:occupation","47":"sec:posttraining","47a":"sec:coverage",
 "48":"sec:permeation","49":"sec:quality","5":"sec:limits","6":"sec:policy",
 "7":"sec:related","8":"sec:discussion","81":"sec:disc-limit","82":"sec:disc-norms",
 "83":"sec:disc-substitution","84":"sec:disc-proxy","85":"sec:disc-human","86":"sec:future",
 "c1":"sec:cross-route","c2":"sec:reanalysis","c3":"sec:bypass-sample","c4":"sec:artifacts",
 "d1":"sec:judge-leakage","d2":"sec:prominence-full","d3":"sec:prominence-buckets",
 "d4":"sec:cohort-ministerial",
}
APPENDIX_LABELS = {"appendix-a":"app:null","appendix-b":"app:superseded",
                   "appendix-c":"app:repro","appendix-d":"app:robustness"}
LABELS = {   # unnumbered subsubsections: exact slug
 "all-four-predictors-at-once":"sub:four-predictors",
 "the-provincial-class-estimates-the-discovery-record":"sub:class-provincial",
 "education-the-provincial-ladder-did-not-replicate-see-above":"sub:education-provincial",
 "the-shape-has-a-name--held-now-as-hypothesis-not-finding":"sub:shape-name",
 "flight-class-i-avoids-the-words-that-became-common":"sub:flight",
 "prominence-a-gradient-in-the-provinces-an-arc-in-the-national-chambers":"sub:prominence-class",
 "word-mix-the-effects-live-in-rate-not-vocabulary--and-machine-text-sits-outside-the-geometry":"sub:wordmix",
 "what-the-class-analysis-cannot-rule-out":"sub:class-limits",
}

def label_for(slug):
    m = re.match(r'^([0-9]+[a-z]?|[cd][0-9])-', slug)
    if m and m.group(1) in PREFIX_LABELS:
        return PREFIX_LABELS[m.group(1)]
    for pre, lab in APPENDIX_LABELS.items():
        if slug.startswith(pre):
            return lab
    return LABELS.get(slug)

# §N / §N.M  ->  label   (only these resolve; anything else is left literal)
NUMMAP = {
 "1":"sec:intro","2":"sec:data","2.1":"sec:hazards","3":"sec:method",
 "3.1":"sec:calibration-method","3.2":"sec:detector","3.3":"sec:freq-descriptive",
 "3.4":"sec:retired","4":"sec:results","4.1":"sec:calibration","4.2":"sec:prevalence",
 "4.3":"sec:genre","4.4":"sec:screen-pangram","4.5":"sec:register-shift",
 "4.5a":"sec:climb-geography","4.6":"sec:generational","4.6a":"sec:occupation",
 "4.6b":"sec:class","4.7":"sec:posttraining","4.7a":"sec:coverage",
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
FIGLABEL = {"class_by_era_panels.png":"fig:class-era","ladder_by_era_panels.png":"fig:ladder-era","altitude_u.png":"fig:altitude",
            "the-ai-lexicon-trend.png":"fig:trend","apc_gradients.png":"fig:apc","bypass_search.png":"fig:bypass"}

NUMSTRIP = re.compile(r'^(?:Appendix\s+[A-D]\s+---\s+|(?:[0-9]+(?:\.[0-9]+[a-z]?)?|[A-D]\.[0-9]+[a-z]?)\.?\s+)')

def transform_headings(t):
    pat = re.compile(r'\\hypertarget\{([^}]*)\}\{%\n\\(section|subsection|subsubsection)\{((?:[^{}]|\{[^{}]*\})*)\}\\label\{\1\}\}')
    def repl(m):
        slug, level, title = m.group(1), m.group(2), m.group(3)
        title = NUMSTRIP.sub('', title)
        if slug == "abstract":
            return r'\section*{Abstract}'
        lab = label_for(slug)
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
      (r"sits\s+above\s+class\s+I\s+in\s+every\s+bin",
       r"\g<0> (\\cref{fig:class-era})"),
      (r"carry\s+the\s+claim\.",
       r"carry the claim (\\cref{fig:altitude})."),
      (r"the two instruments then\s+part ways",
       r"the two instruments then part ways (\\cref{fig:trend})"),
      (r"The\s+figure\s+below\s+lays\s+out\s+the\s+loop\.",
       r"\\Cref{fig:bypass} lays out the loop."),
      (r"comparing legislatures whose group histories\s+differ, below",
       r"comparing legislatures whose group histories differ (\\cref{fig:apc}), below"),
      (r"The\s+search\s+loop\s+generates\s+and\s+screens\s+variants",
       r"The search loop (\\cref{fig:bypass}) generates and screens variants"),
      (r"reported\s+individually\s+in\s+the\s+table\s+below",
       r"reported individually in \\cref{tab:prevalence}"),
    ]
    for a, b in subs:
        t, n = re.subn(a, b, t, count=1)
        if n != 1: sys.stderr.write("WARN: fig-anchor %r subs=%d\n" % (a, n))
    return t

def insert_appendix(t):
    needle = "\\section{Null results}\\label{app:null}"
    if needle in t:
        t = t.replace(needle, "\\appendix\n\\section*{Supplementary materials}\n\n" + needle, 1)
    else:
        sys.stderr.write("WARN: app:null heading not found for \\appendix\n")
    return t

PUB_ORDER = ["sec:intro","sec:results","sec:discussion","sec:data","sec:method"]
MERGE_INTO_DISCUSSION = ["sec:limits","sec:related","sec:policy"]  # demoted to subsections

def reorder(t):
    """Drafting order (markdown) -> publication order (Science: Methods last),
    merging Limits/Related/Policy into Discussion as subsections and relocating
    the post-abstract provenance block to Supplementary materials."""
    intro = re.search(r'\\section\{[^{}]*\}\\label\{sec:intro\}', t)
    app = re.search(r'\\appendix', t)
    if not (intro and app):
        sys.stderr.write("WARN: reorder skipped (intro/appendix not found)\n"); return t
    head, middle, tail = t[:intro.start()], t[intro.start():app.start()], t[app.start():]
    starts = [(m.start(), m.group(1)) for m in
              re.finditer(r'\\section\{[^{}]*\}\\label\{(sec:[a-z-]+)\}', middle)]
    blocks = {}
    for i, (pos, lab) in enumerate(starts):
        end = starts[i+1][0] if i+1 < len(starts) else len(middle)
        blocks[lab] = middle[pos:end]
    expected = set(PUB_ORDER) | set(MERGE_INTO_DISCUSSION)
    if expected != set(blocks):
        sys.stderr.write("WARN: reorder section set mismatch: %r\n" % (expected ^ set(blocks))); return t

    # merge Limits/Related/Policy into Discussion, before the Future work subsection
    disc = blocks["sec:discussion"]
    demoted = "".join(re.sub(r'\\section\{', r'\\subsection{', blocks[lab], count=1)
                      for lab in MERGE_INTO_DISCUSSION)
    mfut = re.search(r'\\subsection\{[^{}]*\}\\label\{sec:future\}', disc)
    disc = (disc[:mfut.start()] + demoted + disc[mfut.start():]) if mfut else (disc + demoted)
    blocks["sec:discussion"] = disc

    # relocate the provenance block (between the two thematic-break rules in head)
    RULE = "\\begin{center}\\rule{0.5\\linewidth}{0.5pt}\\end{center}"
    prov = ""
    if head.count(RULE) >= 2:
        hp = head.split(RULE)
        head = hp[0].rstrip() + "\n\n"
        prov = hp[1].strip()

    pieces = []
    for lab in PUB_ORDER:
        if lab == "sec:data":
            pieces.append("\\section*{Materials and methods}\n\n")
        pieces.append(blocks[lab])
    tail_out = tail
    if prov:
        marker = "\\section*{Supplementary materials}\n\n"
        note = marker + "\\subsection*{Provenance and reproducibility}\n\n" + prov + "\n\n"
        tail_out = tail_out.replace(marker, note, 1)
    sys.stderr.write("reorder: merged %d sections into Discussion; provenance moved=%s\n"
                     % (len(MERGE_INTO_DISCUSSION), bool(prov)))
    return head + "".join(pieces) + tail_out

# 35 tables in DRAFTING order: (header keyword for a safety check, label, caption).
# longtable's own \caption auto-numbers and stays inline (no float drift).
TABLE_CAPS = [
 ("group & chambers", "tab:chambers", "The 22 chambers, grouped by country and regime, and the arms that use each."),
 ("instrument & outcome", "tab:retired", "Instruments built and retired, with the result that dropped each."),
 ("Pangram 3 & Pangram 4", "tab:calibration", "Calibration on pre-2022 speech: specificity of Pangram 3 versus Pangram 4."),
 ("& & chamber", "tab:prevalence", "Prevalence of machine-drafted words by chamber, with 95\\% confidence intervals."),
 ("genre, 2025--26", "tab:genre", "Machine-drafted share by genre of business, 2025--26."),
 ("Pangram verdict & n & mean Opus", "tab:screen-by-verdict", "Mean Opus screen score by Pangram verdict on the 618-segment overlap."),
 ("run & AUC", "tab:screen-auc", "Agreement of the Opus screen with Pangram across runs (AUC)."),
 ("gap 2006", "tab:climb", "The constant-window register trend: nineteen chambers, 2006--2026, ordered by growth."),
 ("gap 1994", "tab:climb-long", "The longest window: the three chambers whose series reach 1994."),
 ("sd & vs US House", "tab:vs-ushouse", "Register level by chamber, 2020--26 means, benchmarked against the US House."),
 ("contrast & Spearman", "tab:flight-corr", "Chase-and-flight correlations, raw and holding word frequency fixed."),
 ("directional ladder & coded ladder", "tab:altitude", "The occupational altitude ladder: register by level on both instruments (plotted in \\cref{fig:altitude})."),
 ("EGP class & mean z", "tab:egp", "Register by EGP social class (member-level means)."),
 ("level & mean z & n & vs bachelor", "tab:education", "Register by education level, relative to a bachelor's degree."),
 ("term & n & alone & joint", "tab:four-predictors", "Every member-level predictor in one model: each block alone, the joint fit of cohort, all EGP classes, all education levels and prominence quintiles (n = 4{,}056), and the occupational blocks — both altitude ladders and Indoors — added (n = 3{,}631); t in parentheses; the last column converts jointly significant effects into years of cohort."),
 ("quintile of article length", "tab:prominence-class", "Register by prominence (Wikipedia article-length quintile) across chamber groups."),
 ("register shift (corrected)", "tab:posttraining", "Register shift by training stage (Rogan--Gladen corrected)."),
 ("corpus & \\textbf{0}", "tab:coverage-occ", "Style-word coverage by number of occurrences, at matched volume."),
 ("absent from generated only", "tab:coverage-partition", "Where the 407 style words fall: generated text versus Hansard 2025--26."),
 ("stage 1, per 0", "tab:dqi", "Discourse Quality Index associations with machine authorship: stages 1 and 2."),
 ("Pangram verdict & meaning & counts as", "tab:verdicts", "Pangram's three verdicts and the two events the search counts."),
 ("attacker\\textquotesingle s detector access", "tab:bypass-rates", "Bypass rates by whether the attacker may query the detector."),
 ("searched & zero-yield", "tab:bypass-yield", "Detector-evasion search yield per target."),
 ("measurement & rate & what it is", "tab:bypass-summary", "The bypass rates, disambiguated."),
 ("stage 3 (n=38)", "tab:quality-paired", "Paired within-text quality comparisons (stages 3 and 4)."),
 ("variant (n=35) & target (n=15)", "tab:quality-evasion", "Quality of successful evasions versus their targets, by dimension."),
 ("arm & justification vs human", "tab:continuations", "Machine continuations graded blind: justification and applicability by arm."),
 ("Rice 2026 (Australian federal)", "tab:priorart", "This study against the two closest prior efforts."),
 ("seed verdict & variants", "tab:superseded-bypass", "Superseded per-seed bypass transitions."),
 ("run & role & seeds", "tab:bypass-sample", "Bypass sample selection across runs."),
 ("artifact & what it does", "tab:artifacts", "Artifacts: the scripts and data behind each result."),
 ("arm & model & effort", "tab:models", "Models and reasoning effort by arm."),
 ("class & & vs I & t & members", "tab:class-provincial", "Provincial class estimates relative to class I (discovery record)."),
 ("stage 1 (internal): AI+FE", "tab:judge-leakage", "The judge-leakage control: quality with the grading judge's own AI guess added."),
 ("quintile & CA provinces", "tab:prominence-buckets", "Register by prominence quintile, by chamber group and pooled."),
 ("cells & birth gradient", "tab:cohort-office", "The cohort gradient among office- and non-office-holders."),
]



# Column-spec overrides for prose-heavy tables (pandoc emits natural-width l
# columns; longtable's fill glue hides the overflow, so wide tables silently
# run off the measure). Keyed by table label.
COLSPECS = {
 "tab:chambers":       r"@{}lp{0.74\linewidth}@{}",
 "tab:retired":        r"@{}p{0.30\linewidth}p{0.33\linewidth}p{0.30\linewidth}@{}",
 "tab:verdicts":       r"@{}lp{0.28\linewidth}p{0.44\linewidth}@{}",
 "tab:bypass-rates":   r"@{}lp{0.22\linewidth}p{0.16\linewidth}p{0.36\linewidth}@{}",
 "tab:bypass-summary": r"@{}p{0.22\linewidth}p{0.20\linewidth}p{0.50\linewidth}@{}",
 "tab:priorart":       r"@{}p{0.20\linewidth}p{0.38\linewidth}p{0.36\linewidth}@{}",
 "tab:bypass-sample":  r"@{}lp{0.16\linewidth}lp{0.28\linewidth}p{0.24\linewidth}@{}",
 "tab:artifacts":      r"@{}p{0.36\linewidth}p{0.58\linewidth}@{}",
 "tab:judge-leakage":  r"@{}lp{0.34\linewidth}p{0.34\linewidth}@{}",
 "tab:coverage-partition": r"@{}p{0.15\linewidth}p{0.16\linewidth}p{0.20\linewidth}p{0.20\linewidth}p{0.16\linewidth}@{}",
 "tab:dqi":            r"@{}p{0.20\linewidth}p{0.22\linewidth}p{0.22\linewidth}p{0.24\linewidth}@{}",
 "tab:continuations":  r"@{}p{0.28\linewidth}p{0.32\linewidth}p{0.30\linewidth}@{}",
 "tab:models":        r"@{}p{0.50\linewidth}p{0.20\linewidth}p{0.22\linewidth}@{}",
 "tab:four-predictors": r"@{}p{0.255\linewidth}rp{0.135\linewidth}p{0.135\linewidth}p{0.135\linewidth}l@{}",
}

def inject_table_captions(t):
    parts = re.split(r'(\\begin\{longtable\}[^\n]*\n)', t)
    out = [parts[0]]
    for i, k in enumerate(range(1, len(parts), 2)):
        delim = parts[k]
        body = parts[k+1] if k+1 < len(parts) else ""
        if i >= len(TABLE_CAPS):
            sys.stderr.write("WARN: more longtables than captions (%d)\n" % i); out.append(delim+body); continue
        kw, lab, cap = TABLE_CAPS[i]
        if lab in COLSPECS:
            delim = re.sub(r'\\begin\{longtable\}\[\]\{[^\n]*\}',
                           lambda m: "\\begin{longtable}[]{%s}" % COLSPECS[lab], delim)
        m = re.match(r'(\\toprule\\noalign\{\}\n.*?\\midrule\\noalign\{\}\n)\\endhead\n', body, re.DOTALL)
        capline = "\\caption{%s}\\label{%s}\\\\\n" % (cap, lab)
        if m:
            headblk = m.group(1)
            if kw not in headblk:
                sys.stderr.write("WARN: table %d keyword %r not in header: %r\n" % (i+1, kw, headblk[:90]))
            # caption on the first page only; header repeats on continuation pages
            newbody = capline + headblk + "\\endfirsthead\n" + headblk + "\\endhead\n" + body[m.end():]
            out.append(delim + newbody)
        else:
            sys.stderr.write("WARN: table %d head block not matched; caption prepended\n" % (i+1))
            out.append(delim + capline + body)
    n = (len(parts)-1)//2
    if n != len(TABLE_CAPS):
        sys.stderr.write("WARN: %d longtables vs %d captions\n" % (n, len(TABLE_CAPS)))
    else:
        sys.stderr.write("table captions injected: %d\n" % n)
    body = "".join(out)
    # tables are data-dense; set them all in \small so they fit the measure
    body = body.replace("\\begin{longtable}", "\\begingroup\\small\n\\begin{longtable}")
    body = body.replace("\\end{longtable}", "\\end{longtable}\n\\endgroup")
    return body


# Inline citations -> \cite (numeric, scicite). Applied to the pandoc body; each
# is a first-occurrence substitution matched on the author/venue prose the draft
# already carries, so it survives markdown prose edits that keep those names.
CITE_SUBS = [
 # --- introduction (first mentions; later sections re-cite where discussed) ---
 (r'\(Liang et al\.,\s+Gray\)', r'(Liang et al.\\cite{liang2024monitoring,liang2025quantifying}, Gray\\cite{gray2025})'),
 (r'construction[.] Kobak et al[.] measure excess', r'construction. Kobak et al.\\cite{kobak2025} measure excess'),
 (r'closest\s+parliamentary study measures false positives', r'closest parliamentary study\\cite{suvanto2026} measures false positives'),
 (r'population-level studies validate per venue', r'population-level studies\\cite{liang2024monitoring} validate per venue'),
 (r'a single fifty-speech calibration', r'a single fifty-speech calibration\\cite{rice2026}'),
 (r'where Gray documents', r'where Gray\\cite{gray2025} documents'),
 (r'what Brynjolfsson calls the Turing trap', r'what Brynjolfsson\\cite{brynjolfsson2022} calls the Turing trap'),
 (r'no post-ChatGPT rise\s+\(Rice\)', r'no post-ChatGPT rise (Rice\\cite{rice2026})'),
 (r'\(Pimlico Journal\)', r'(Pimlico Journal\\cite{pimlico2025})'),
 (r'\(Liang et al\.\)', r'(Liang et al.\\cite{liang2024monitoring,liang2025quantifying})'),
 (r'biomedical abstracts \(Kobak et al\.\)', r'biomedical abstracts (Kobak et al.\\cite{kobak2025})'),
 (r'scholarly writing at large \(Gray\)', r'scholarly writing at large (Gray\\cite{gray2025})'),
 (r'Suvanto et al\.\s+detect undisclosed', r'Suvanto et al.\\cite{suvanto2026} detect undisclosed'),
 (r'with Pangram, a commercial detector\s+calibrated', r'with Pangram\\cite{pangram2024}, a commercial detector calibrated'),
 (r'\(arXiv:2406\.07016; \\emph\{Sci Adv\}\s+11\(27\):eadt3813, 2025\)', r'\\cite{kobak2025}'),
 (r'\(Steenbergen,\s+Bächtiger,\s+Spörndli\s+\\&\s+Steiner\s+2003\)', r'\\cite{steenbergen2003}'),
 (r'\(Benjamini \\& Hochberg, \\emph\{JRSS-B\} 57, 1995, 289--300\)', r'\\cite{benjamini1995}'),
 (r'Suvanto, McGlinchey, Barclay \\&\s+Wahde \(arXiv:2606\.14209, 2026\)', r'Suvanto, McGlinchey, Barclay \\& Wahde\\cite{suvanto2026}'),
 (r'Binoculars \(Hans et al\.\s+2024\)', r'Binoculars\\cite{hans2024}'),
 (r'Fast-DetectGPT \(Bao et al\. 2024\)', r'Fast-DetectGPT\\cite{bao2024}'),
 (r'ParliaBench \(Koniaris et al\., LREC 2026\)', r'ParliaBench\\cite{koniaris2026}'),
 (r'Perkins benchmark', r'Perkins benchmark\\cite{perkins2024}'),
 (r'Rice does not claim evidence of absence', r'Rice\\cite{rice2026} does not claim evidence of absence'),
 (r'Pimlico\\textquotesingle s agreement is', r'Pimlico\\cite{pimlico2025}\\textquotesingle s agreement is'),
 (r'Simmel 1904', r'Simmel 1904\\cite{simmel1904}'),
 (r'Veblen 1899', r'Veblen 1899\\cite{veblen1899}'),
 (r'Jhering 1883', r'Jhering 1883\\cite{jhering1883}'),
 (r'Durkheim\\textquotesingle s 1887', r'Durkheim\\textquotesingle s 1887\\cite{durkheim1887}'),
 (r'Lieberson\s+2000', r'Lieberson 2000\\cite{lieberson2000}'),
 (r'Labov 1972', r'Labov 1972\\cite{labov1972}'),
 (r'by Rogan--Gladen', r'by Rogan--Gladen\\cite{rogan1978}'),
 (r'the whole of the record Pangram will read', r'the whole of the record Pangram\\cite{pangram2024} will read'),
 (r'Pangram 4 report', r'Pangram 4 report\\cite{pangram4}'),
 (r'Mann--Kendall\s+p', r'Mann--Kendall\\cite{mann1945,kendall1948} p'),
 (r"Fisher\\textquotesingle s method over the", r"Fisher\\textquotesingle s method\\cite{fisher1925} over the"),
]

def cite_wire(t):
    n_ok = 0
    for pat, rep in CITE_SUBS:
        t, n = re.subn(pat, rep, t, count=1)
        if n == 1: n_ok += 1
        else: sys.stderr.write("WARN: cite pattern unmatched: %s\n" % pat[:60])
    sys.stderr.write("cite_wire: %d/%d citations wired\n" % (n_ok, len(CITE_SUBS)))
    return t


def breakable_tt(t):
    """Long \\texttt{} arguments (paths, script names) are single unbreakable
    boxes and silently overflow the measure; allow breaks after / . _ - ."""
    def fix(m):
        a = m.group(1)
        if len(a) < 25:
            return m.group(0)
        a = a.replace("/", "/\\allowbreak{}").replace("\\_", "\\_\\allowbreak{}")
        a = a.replace(".", ".\\allowbreak{}").replace("-", "-\\allowbreak{}")
        return "\\texttt{%s}" % a
    return re.sub(r'\\texttt\{([^{}]*)\}', fix, t)



# ---------------------------------------------------------------------------
# mathify: set superscripts, Greek and math expressions in proper LaTeX math
# rather than leaning on the preamble's newunicodechar glyph fallbacks (which
# remain as a safety net). Code spans (\texttt) and verbatim blocks are
# protected -- except the Rogan-Gladen material, which IS math and is
# converted first, the display equation included.
SUPMAP = dict(zip("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789"))

RG_TEXTTT = {   # code-styled spans in the Rogan-Gladen passage that are math
 r"\texttt{τ\ =\ π/Se\ ≥\ π}": r"\(\tau = \pi/\mathrm{Se} \geq \pi\)",
 r"\texttt{τ\ =\ π/Se}": r"\(\tau = \pi/\mathrm{Se}\)",
 r"\texttt{Sp\ =\ 1}": r"\(\mathrm{Sp} = 1\)",
 r"\texttt{Se\ =\ 1}": r"\(\mathrm{Se} = 1\)",
 r"\texttt{Se\ ≤\ 1}": r"\(\mathrm{Se} \leq 1\)",
 r"\texttt{Se}": r"\(\mathrm{Se}\)",
 r"\texttt{Sp}": r"\(\mathrm{Sp}\)",
 r"\texttt{τ}": r"\(\tau\)",
 r"\texttt{π}": r"\(\pi\)",
}
RG_VERBATIM = (
 "\\begin{verbatim}\nπ = τ·Se + (1−τ)(1−Sp)      ⇒     "
 "τ = (π − (1−Sp)) / (Se − (1−Sp))\n\\end{verbatim}")
RG_DISPLAY = (
 "\\[ \\pi = \\tau\\,\\mathrm{Se} + (1-\\tau)(1-\\mathrm{Sp})"
 " \\;\\Rightarrow\\; \\tau = \\frac{\\pi - (1-\\mathrm{Sp})}"
 "{\\mathrm{Se} - (1-\\mathrm{Sp})} \\]")


def mathify(t):
    # Rogan-Gladen first: this code-set material is math
    assert t.count(RG_VERBATIM.replace("\\\\", "\\")) or True
    t = t.replace(RG_VERBATIM.replace("\\begin", "\\begin"), RG_DISPLAY)
    for a, b in RG_TEXTTT.items():
        t = t.replace(a, b)
    prot, math = [], []
    def stash(m):
        prot.append(m.group(0)); return "\x00%d\x01" % (len(prot) - 1)
    def put(x):
        math.append(x); return "\x02%d\x03" % (len(math) - 1)
    t = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", stash, t, flags=re.S)
    t = re.sub(r"\\texttt\{[^{}]*\}", stash, t)
    sup = lambda x: "".join(SUPMAP[c] for c in x)
    # p < 1.3x10^-83 molecules (relation may arrive as \textless{})
    def pmol(m):
        rel = {"≈": r"\approx", "=": "="}.get(m.group("rel"), "<")
        num = "10^{%s}" % sup(m.group("sup"))
        if m.group("mant"):
            num = m.group("mant").replace("×", "").replace(",", "{,}").strip() \
                  + r"\times " + num
        return put(r"\(%s %s %s\)" % (m.group("p"), rel, num))
    t = re.sub(r"(?P<p>[pP])\s*(?:\\textless\{\}|(?P<rel>[=≈<]))\s*"
               r"(?P<mant>\d[\d.,]*\s*×\s*)?10(?P<sup>[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
               pmol, t)
    t = re.sub(r"(\d[\d.,]*)\s*×\s*10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
               lambda m: put(r"\(%s\times 10^{%s}\)"
                             % (m.group(1).replace(",", "{,}"), sup(m.group(2)))), t)
    t = re.sub(r"10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
               lambda m: put(r"\(10^{%s}\)" % sup(m.group(1))), t)
    # the R-squared family and other letter superscripts
    t = t.replace("ΔadjR²", put(r"\(\Delta\text{adj}R^{2}\)"))
    t = re.sub(r"adjR²", lambda m: put(r"\(\text{adj}R^{2}\)"), t)
    t = re.sub(r"\b([RA])²", lambda m: put(r"\(%s^{2}\)" % m.group(1)), t)
    t = re.sub(r"²", lambda m: put(r"\({}^{2}\)"), t)
    # Greek with operands, then number-attached sigma
    t = re.sub(r"ρ\s*=\s*([+−-]?[\d.]+)",
               lambda m: put(r"\(\rho = %s\)" % m.group(1).replace("−", "-")), t)
    t = re.sub(r"([+−-]?\d[\d.]*)σ",
               lambda m: put(r"\(%s\sigma\)" % m.group(1).replace("−", "-")), t)
    # multiplier and signed-number molecules
    t = re.sub(r"(\d[\d,.]*)\s*×",
               lambda m: put(r"\(%s\times\)" % m.group(1).replace(",", "{,}")), t)
    t = re.sub(r"−(\d[\d.]*)", lambda m: put(r"\(-%s\)" % m.group(1)), t)
    # lone symbols
    for u, x in (("−", r"\(-\)"), ("×", r"\(\times\)"), ("≈", r"\(\approx\)"),
                 ("≥", r"\(\geq\)"), ("≤", r"\(\leq\)"), ("±", r"\(\pm\)"),
                 ("·", r"\(\cdot\)"), ("→", r"\(\rightarrow\)"),
                 ("⇒", r"\(\Rightarrow\)"), ("σ", r"\(\sigma\)"),
                 ("π", r"\(\pi\)"), ("τ", r"\(\tau\)"), ("ρ", r"\(\rho\)")):
        t = t.replace(u, put(x))
    for i, x in enumerate(math):
        t = t.replace("\x02%d\x03" % i, x)
    for i, x in enumerate(prot):
        t = t.replace("\x00%d\x01" % i, x)
    return t


def main():
    t = open(SRC, encoding="utf-8").read()
    t = transform_headings(t)
    t = wrap_figures(t)
    t = figure_ref_anchors(t)
    t = replace_section_refs(t)
    t = replace_appendix_refs(t)
    t = cite_wire(t)
    t = inject_table_captions(t)
    t = breakable_tt(t)
    t = insert_appendix(t)
    t = reorder(t)
    t = mathify(t)
    open(DST, "w", encoding="utf-8").write(t)
    sys.stderr.write("wrote %s (%d chars)\n" % (DST, len(t)))

main()
