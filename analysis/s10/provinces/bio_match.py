#!/usr/bin/env python3
"""S10 bios: match the Hansard speaker roster to the Wikipedia/Wikidata candidate
pool and emit member_bios.json + member_bios_summary.txt.

Conservative by construction: any roster entry whose surname resolves to more
than one plausible candidate after era- and gender-filtering is left unmatched
(match_confidence "none", all fields null) rather than guessed.
"""
import json, os, re, sys, unicodedata, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bio_fetch_pool import TERMS  # noqa

BODY = {
    "ON": "Legislative Assembly of Ontario", "AB": "Legislative Assembly of Alberta",
    "MB": "Legislative Assembly of Manitoba", "BC": "Legislative Assembly of British Columbia",
    "SK": "Legislative Assembly of Saskatchewan",
    "PE": "Legislative Assembly of Prince Edward Island",
    "NS": "Nova Scotia House of Assembly", "NL": "Newfoundland and Labrador House of Assembly",
}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("-", " ").replace("'", " ").replace("’", " ").replace(".", " ")
    return re.sub(r"\s+", " ", s).strip()


def strip_paren(t):
    return re.sub(r"\s*\(.*\)$", "", t)


NAME_NOISE = {"jr", "sr", "ii", "iii", "dr", "hon", "mr", "mrs", "ms", "miss", "mme", "mlle", "m"}


def toks(s):
    return [t for t in norm(strip_paren(s)).split() if t not in NAME_NOISE]


# ---------------------------------------------------------------- occupation
OCC_MAP = [
    ("law", ["lawyer", "jurist", "barrister", "solicitor", "attorney", "judge", "notary",
             "prosecutor", "legal"]),
    ("health", ["physician", "nurse", "surgeon", "dentist", "pharmacist", "veterinarian",
                "psychologist", "psychiatrist", "chiropractor", "paramedic", "optometrist",
                "midwife", "therapist", "medical"]),
    ("education", ["teacher", "professor", "educator", "academic", "lecturer",
                   "schoolteacher", "principal", "researcher", "historian", "scientist",
                   "economist", "sociologist", "university teacher", "mathematician"]),
    ("communications-PR-journalism", ["journalist", "broadcaster", "writer", "author",
                                      "editor", "publisher", "radio personality",
                                      "television presenter", "news presenter", "columnist",
                                      "public relations", "communication", "reporter",
                                      "announcer", "actor", "musician", "photographer"]),
    ("agriculture", ["farmer", "rancher", "agronomist", "agriculturalist", "fisher",
                     "fisherman", "forester", "agricultural"]),
    ("trades-labour", ["electrician", "carpenter", "plumber", "welder", "miner",
                       "mechanic", "machinist", "steelworker", "truck driver",
                       "trade unionist", "labor union", "labour union", "millwright",
                       "construction worker", "pipefitter", "ironworker"]),
    ("public-service", ["civil servant", "public servant", "police officer", "firefighter",
                        "soldier", "military officer", "diplomat", "bureaucrat",
                        "correctional officer", "military personnel"]),
    ("NGO-advocacy", ["activist", "trade union", "social worker", "community organizer",
                      "advocate", "philanthropist", "clergy", "priest", "minister of religion",
                      "pastor", "missionary", "rabbi"]),
    ("business", ["businessperson", "entrepreneur", "merchant", "manager", "executive",
                  "accountant", "banker", "realtor", "real estate", "insurance",
                  "consultant", "engineer", "financier", "restaurateur", "hotelier",
                  "salesperson", "contractor", "business"]),
]
IGNORE_OCC = {"politician", "political scientist", "statesperson", "civil rights advocate"}

CAT_OCC = [  # enwiki category fragments -> coarse category
    ("law", ["lawyers", "jurists", "judges", "king's counsel", "queen's counsel"]),
    ("health", ["physicians", "nurses", "surgeons", "dentists", "pharmacists",
                "veterinarians", "psychologists"]),
    ("education", ["educators", "schoolteachers", "academics", "academic staff",
                   "university and college faculty", "economists", "historians"]),
    ("communications-PR-journalism", ["journalists", "broadcasters", "writers",
                                      "television personalities", "radio personalities",
                                      "newspaper editors", "musicians"]),
    ("agriculture", ["farmers", "ranchers", "fishers", "agriculturalists"]),
    ("trades-labour", ["trade unionists", "miners", "electricians", "carpenters"]),
    ("public-service", ["civil servants", "police officers", "firefighters",
                        "military personnel", "diplomats"]),
    ("NGO-advocacy", ["activists", "social workers", "clergy", "priests",
                      "philanthropists", "religious leaders", "pastors"]),
    ("business", ["businesspeople", "business people", "chief executives",
                  "accountants", "engineers", "real estate"]),
]


def occ_category(occs, cats):
    low = [o.lower() for o in occs if o and o.lower() not in IGNORE_OCC]
    for cat, keys in OCC_MAP:
        for o in low:
            if any(k in o for k in keys):
                return cat, o
    cl = [c.lower() for c in cats
          if not re.search(r"ministers? of|minister for|members of the executive council|"
                           r"premiers of|leaders of|speakers of|mayors of|councillors|"
                           r"candidates|mlas|mpps|mhas|political part|deaths|births|"
                           r"people from|politicians from|alumni", c.lower())]
    for cat, keys in CAT_OCC:
        for c in cl:
            if any(k in c for k in keys):
                # "Canadian abortion-rights activists" -> "abortion-rights activist"
                txt = re.sub(r"^(canadian|women|men|21st-century|20th-century|"
                             r"british columbia|nova scotia|newfoundland and labrador|"
                             r"prince edward island|ontario|alberta|manitoba|"
                             r"saskatchewan)\s+", "", c).strip()
                txt = re.sub(r"s$", "", txt) if txt.endswith("s") else txt
                return cat, (txt or c)
    if low:
        return "other", low[0]
    return None, None


# ---------------------------------------------------------------- education
DEG_LEVEL = [
    ("professional", ["juris doctor", "bachelor of laws", "llb", "ll.b", "doctor of medicine",
                      "bachelor of medicine", "doctor of dental", "bachelor of engineering",
                      "doctor of veterinary", "bachelor of education"]),
    ("graduate", ["doctor of philosophy", "ph.d", "phd", "master of", "magister",
                  "doctorate", "doctor of science", "licentiate", "master's",
                  "llm", "ll.m", "mba", "doctor of"]),
    ("bachelor", ["bachelor", "b.a", "bsc", "b.sc", "baccalaureate", "artium baccalaureus",
                  "undergraduate"]),
    ("secondary", ["high school diploma", "secondary"]),
]


def edu_level(degrees):
    dl = [d.lower() for d in degrees if d]
    for lvl, keys in DEG_LEVEL:
        if any(any(k in d for k in keys) for d in dl):
            return lvl
    return None


PARTY_CAT = re.compile(
    r"^(.*?)\s+(MLAs|MPPs|MHAs|MNAs)$")


def year_of(iso):
    if not iso:
        return None
    m = re.match(r"^(-?\d{1,6})-", iso)
    if not m:
        return None
    y = int(m.group(1))
    return y if 1800 < y < 2015 else None



PARTICLES = {"de", "van", "von", "der", "den", "del", "di", "da", "la", "le", "du",
             "st", "ste", "mac", "mc", "o", "d", "al", "des", "dos", "ten", "ter"}
ROLE_PREFIX = {"member", "mla", "mha", "mpp", "mna", "hon", "honourable", "rev",
               "reverend", "dr", "mr", "mrs", "ms", "miss", "mme", "mlle", "m",
               "sir", "madam", "chair", "deputy"}
NON_MEMBER = {"lieutenant governor", "the speaker", "speaker", "clerk", "sergeant at arms",
              "mr speaker", "madam speaker", "an hon member", "some hon members",
              "the chair", "the deputy speaker", "unidentified"}


def roster_tokens(name):
    """Hansard speaker string -> name tokens.

    Distinguishes a middle initial ("Kathleen O. Wynne") from an apostrophe
    particle ("Christopher d'Entremont") using the punctuation, which plain
    normalisation destroys; drops role prefixes and nickname parentheticals.
    """
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\([^)]*\)", " ", s)                 # "jennifer (jennie) stevens"
    s = re.sub(r"\b([a-z])\.", " ", s)               # middle / leading initials with a dot
    initial_dot = bool(re.search(r"\b[a-z]\.", name.lower()))
    t = [x for x in re.sub(r"[^a-z]+", " ", s).split() if x]
    while t and t[0] in ROLE_PREFIX:
        t = t[1:]
    return t


def roster_initial(name):
    """Leading single-letter initial, if the raw string had one ('D. Routley')."""
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().strip()
    m = re.match(r"^([a-z])\.", s)
    return m.group(1) if m else None


def given_compatible(a, b):
    """roster given name a vs candidate given name b, nickname/initial tolerant."""
    if not a or not b:
        return False
    if a == b:
        return True
    if len(a) == 1 and b.startswith(a):
        return True
    if len(b) == 1 and a.startswith(b):
        return True
    if len(a) >= 3 and b.startswith(a):
        return True
    if len(b) >= 3 and a.startswith(b):
        return True
    return False


def ends_with(cand_toks, sur_toks):
    return len(cand_toks) >= len(sur_toks) and cand_toks[-len(sur_toks):] == sur_toks



# ------------------------------------------------------- infobox enrichment
DEG_ABBR = [   # case-SENSITIVE: degree post-nominals are capitalised
    ("professional", r"\b(LL\.?B|J\.?D|M\.?D|D\.?D\.?S|D\.?V\.?M|B\.?Ed|B\.?Eng|B\.?Arch)\b"),
    ("graduate", r"\b(Ph\.?D|D\.?Phil|M\.?A|M\.?Sc|M\.?B\.?A|M\.?Ed|M\.?P\.?A|M\.?S\.?W|"
                 r"M\.?Div|LL\.?M|M\.?Eng|M\.?Comm|MPP\b(?!s))\b"),
    ("bachelor", r"\b(B\.?A|B\.?Sc|B\.?Comm|BComm|B\.?B\.?A|B\.?F\.?A|B\.?Sc\.?N|"
                 r"B\.?S\.?W|B\.?N|B\.?P\.?E)\b"),
]
DEG_WORD = [   # case-insensitive spelled-out forms
    ("professional", r"\b(bachelor of laws|juris doctor|doctor of medicine|law degree|"
                     r"doctor of dental|bachelor of education|doctor of veterinary|"
                     r"bachelor of engineering|medical degree|called to the bar)\b"),
    ("graduate", r"\b(doctor of philosophy|doctorate|master(?:'s)? (?:degree|of)|"
                 r"master of business administration|graduate degree|"
                 r"postgraduate degree)\b"),
    ("bachelor", r"\b(bachelor(?:'s)? (?:degree|of)|undergraduate degree|"
                 r"baccalaureate)\b"),
]


def degree_level_from_text(txt):
    """Highest attested level; abbreviations matched case-sensitively so that
    'Manitoba' cannot be read as an M.A."""
    if not txt:
        return None, None
    for lvl, pat in DEG_ABBR:
        m = re.search(pat, txt)
        if m:
            return lvl, m.group(0)
    for lvl, pat in DEG_WORD:
        m = re.search(pat, txt, re.I)
        if m:
            return lvl, m.group(0)
    return None, None


FIELD_FROM_DEGREE = [
    ("law", r"LL\.?B|LL\.?M|J\.?D\b|[Bb]achelor of [Ll]aws|[Jj]uris [Dd]octor|law degree"),
    ("medicine", r"\bM\.?D\b|[Dd]octor of [Mm]edicine|medical degree"),
    ("dentistry", r"D\.?D\.?S|[Dd]octor of [Dd]ental"),
    ("veterinary medicine", r"D\.?V\.?M|[Dd]octor of [Vv]eterinary"),
    ("education", r"B\.?Ed|M\.?Ed|[Bb]achelor of [Ee]ducation"),
    ("engineering", r"B\.?Eng|M\.?Eng|[Bb]achelor of [Ee]ngineering"),
    ("business/commerce", r"M\.?B\.?A|B\.?Comm|BComm|B\.?B\.?A|"
                          r"[Bb]usiness [Aa]dministration|[Cc]ommerce"),
    ("nursing", r"B\.?Sc\.?N|B\.?N\b|[Nn]ursing"),
    ("social work", r"M\.?S\.?W|B\.?S\.?W|[Ss]ocial [Ww]ork"),
    ("public administration", r"M\.?P\.?A\b|[Pp]ublic [Aa]dministration"),
    ("divinity", r"M\.?Div|[Dd]ivinity|[Tt]heology"),
    ("architecture", r"B\.?Arch|[Aa]rchitecture"),
]


def field_from_degree(*texts):
    t = " ".join(x for x in texts if x)
    if not t:
        return None
    for f, pat in FIELD_FROM_DEGREE:
        if re.search(pat, t):
            return f
    return None


def infobox_birth_year(v):
    if not v or v.strip().startswith("|"):
        return None
    m = re.search(r"\{\{\s*[Bb]irth (?:date|year)[^|}]*\|\s*(?:df=\w+\|)?\s*(\d{4})", v)
    if m:
        y = int(m.group(1))
        return y if 1850 < y < 2010 else None
    m = re.search(r"[Bb]irth based on age as of date\|\s*(\d{1,3})\s*\|\s*(\d{4})", v)
    if m:
        y = int(m.group(2)) - int(m.group(1))
        return y if 1850 < y < 2010 else None
    m = re.search(r"\b(18\d{2}|19\d{2}|200\d)\b", v)
    if m:
        return int(m.group(1))
    return None


def clean_ib(v):
    if not v or v.strip().startswith("|"):
        return None
    v = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", " ", v, flags=re.S)
    v = re.sub(r"\{\{\s*(?:[Pp]lainlist|[Uu]bl|[Hh]list|[Ff]latlist|[Cc]omma separated entries|"
               r"[Uu]nbulleted list|[Nn]owrap)\s*\|?", " ", v)
    v = re.sub(r"\{\{[^}]*\}\}|\}\}|\{\{", " ", v)
    v = v.replace("|", ", ")
    v = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", v)
    v = re.sub(r"<[^>]+>|\n\*|\n", ", ", v)
    v = re.sub(r"[\[\]']", " ", v)
    v = re.sub(r"\s*,\s*,+", ", ", v)
    v = re.sub(r"\s+", " ", v).strip(" ,;")
    # a leaked sentence is not an occupation value
    if not v or re.search(r"\b(is|was) an? \b", v) or len(v) > 120:
        return None
    return v


def main():
    roster = json.load(open(os.path.join(HERE, "member_roster.json")))
    catpool = json.load(open(os.path.join(HERE, "wikipedia_category_pool.json")))
    artpool = json.load(open(os.path.join(HERE, "wikipedia_pool_raw.json")))
    pagecats = json.load(open(os.path.join(HERE, "page_categories.json")))
    infoboxes = json.load(open(os.path.join(HERE, "page_infoboxes.json")))
    prose_p = os.path.join(HERE, "page_prose.json")
    prose = json.load(open(prose_p)) if os.path.exists(prose_p) else {}
    t2q = json.load(open(os.path.join(HERE, "title_qids.json")))
    for p in artpool:
        t2q.update(artpool[p])
    bios = json.load(open(os.path.join(HERE, "pool_bios_raw.json")))
    terms = json.load(open(os.path.join(HERE, "pool_terms_raw.json")))
    p39 = json.load(open(os.path.join(HERE, "wikidata_raw.json")))
    p39_by_qid = {}
    for prov, rows in p39.items():
        for r in rows:
            p39_by_qid[(prov, r["qid"])] = r
    links_by_art = json.load(open(os.path.join(HERE, "wikipedia_links_by_article.json")))
    # title -> set of (prov, y0, y1)
    art_windows = collections.defaultdict(set)
    for k, titles in links_by_art.items():
        prov, art = k.split("||")
        w = TERMS[prov][art]
        for t in titles:
            art_windows[t].add((prov, w[0], w[1]))

    # ------------------------------------------------ build candidate records
    cands = collections.defaultdict(list)
    for prov in catpool:
        titles = set(catpool[prov]) | set(artpool.get(prov, {}).keys())
        c21 = set(catpool[prov])   # from 21st/20th cat harvest (both centuries)
        for t in sorted(titles):
            cats = pagecats.get(t, [])
            ib = infoboxes.get(t, {})
            pr_txt = prose.get(t, "")
            qid = t2q.get(t)
            b = bios.get(qid, {}) if qid else {}
            # birth year: wikidata first, enwiki "NNNN births" category second
            by, by_src = year_of(b.get("dob")), None
            if by:
                by_src = "wikidata:P569"
            else:
                for c in cats:
                    m = re.match(r"^(\d{4}) births$", c)
                    if m:
                        by, by_src = int(m.group(1)), "enwiki:category"
                        break
                if not by:
                    y = infobox_birth_year(ib.get("birth_date"))
                    if y:
                        by, by_src = y, "enwiki:infobox"
                if not by and pr_txt:
                    mm = re.search(r"\(born[^)]{0,80}?\b(18\d\d|19\d\d|200\d)\b", pr_txt)
                    if not mm:
                        mm = re.search(r"\bborn (?:on |in )?(?:[A-Z][a-z]+ \d{1,2}, )?"
                                       r"\b(18\d\d|19\d\d|200\d)\b", pr_txt)
                    if mm:
                        yy = int(mm.group(1))
                        if 1850 < yy < 2010:
                            by, by_src = yy, "enwiki:prose"
            # gender
            g = (b.get("gender") or "").lower() or None
            if g in ("male", "female"):
                pass
            elif any(c.lower().startswith("women ") or " women " in c.lower() for c in cats):
                g = "female"
            else:
                g = g or None
            # party
            party = None
            for c in cats:
                m = PARTY_CAT.match(c)
                if m and "candidates" not in c.lower():
                    party = m.group(1)
                    break
            if not party and b.get("parties"):
                party = b["parties"][0]
            occ_cat, occ_txt = occ_category(b.get("occupations", []), cats)
            ib_occ = clean_ib(ib.get("occupation")) or clean_ib(ib.get("profession"))
            if ib_occ and (occ_cat in (None, "other")):
                c2, t2 = occ_category([x.strip() for x in re.split(r"[,;/]", ib_occ)], [])
                if c2:
                    occ_cat, occ_txt = c2, ib_occ
                elif not occ_txt:
                    occ_cat, occ_txt = "other", ib_occ
            if ib_occ and not occ_txt:
                occ_txt = ib_occ
            lvl = edu_level(b.get("degrees", []))
            edu_txt = " ; ".join(x for x in (clean_ib(ib.get("education")),
                                             clean_ib(ib.get("alma_mater"))) if x) or None
            deg_txt = None
            if not lvl:
                lvl, deg_txt = degree_level_from_text(
                    " ".join([ib.get("education") or "", ib.get("alma_mater") or ""]))
            if not lvl and pr_txt:
                lvl, deg_txt = degree_level_from_text(pr_txt)
                if lvl:
                    edu_src_prose = True
            alma = b.get("almas", []) or ([edu_txt] if edu_txt else [])
            edu_src = None
            if b.get("degrees") and edu_level(b["degrees"]):
                edu_src = "wikidata:P512"
            elif lvl:
                edu_src = ("enwiki:infobox"
                           if degree_level_from_text(" ".join([ib.get("education") or "",
                                                               ib.get("alma_mater") or ""]))[0]
                           else "enwiki:prose")
            # service window
            wins = {(y0, y1) for (pv, y0, y1) in art_windows.get(t, set()) if pv == prov}
            # explicit century flags
            body = BODY[prov]
            c20 = ("20th-century members of the " + body) in cats
            c21f = ("21st-century members of the " + body) in cats
            # first elected
            fe = None
            pr = p39_by_qid.get((prov, qid)) if qid else None
            if pr and pr.get("term_start"):
                fe = year_of(pr["term_start"])
            if not fe and qid in terms:
                ys = [year_of(x["start"]) for x in terms[qid]
                      if x.get("start") and x.get("pos") and body.lower() in (x["pos"] or "").lower()]
                ys = [y for y in ys if y]
                if ys:
                    fe = min(ys)
            fe_src = "wikidata:P39-start" if fe else None
            fe_lb = False
            if not fe and wins and not c20:
                # lower bound: earliest legislature (2003+) they are listed in, and
                # they carry no 20th-century membership category
                fe = min(w[0] for w in wins)
                fe_src = "inferred:earliest-legislature-listed (lower bound)"
                fe_lb = True
            cands[prov].append({
                "title": t, "qid": qid, "name": (b.get("label") or strip_paren(t)),
                "toks": toks(b.get("label") or t), "birth_year": by, "birth_year_source": by_src,
                "gender": g, "party": party, "occ_cat": occ_cat, "occ_txt": occ_txt,
                "occupations": b.get("occupations", []), "edu_level": lvl, "edu_source": edu_src, "edu_text": edu_txt,
                "edu_field": field_from_degree(deg_txt, ib.get("education"),
                                               " ".join(b.get("degrees", []))),
                "postsec": bool(b.get("almas") or clean_ib(ib.get("alma_mater"))
                                or clean_ib(ib.get("education"))
                                or (pr_txt and re.search(
                                    r"\b(graduat\w+ from|attended|studied at|degree from|"
                                    r"alumn\w+ of)\b.{0,60}?"
                                    r"(University|College|Polytechnic|Institute|School of)",
                                    pr_txt))),
                "degrees": b.get("degrees", []) or ([deg_txt] if deg_txt else []),
                "almas": alma,
                "fields": b.get("fields", []), "windows": sorted(wins),
                "c20": c20, "c21": c21f, "in_catpool": t in c21,
                "fe": fe, "fe_src": fe_src, "fe_lb": fe_lb,
                "url": ("https://en.wikipedia.org/wiki/" + t.replace(" ", "_")),
            })

    # ------------------------------------------------ matching
    HON_F = {"ms", "mrs", "miss", "mme", "mlle"}
    HON_M = {"mr", "m"}
    out, unmatched_reason = [], collections.Counter()
    diag = []
    for m in roster:
        prov = m["prov"]
        if norm(m["name"]) in NON_MEMBER:
            continue
        rt = roster_tokens(m["name"])
        y0 = int(m["first_seen"][:4]); y1 = int(m["last_seen"][:4])
        hg = set()
        for f in m["printed_forms"]:
            h = norm(f).split()[0] if norm(f) else ""
            if h in HON_F:
                hg.add("female")
            elif h in HON_M:
                hg.add("male")
        hint = list(hg)[0] if len(hg) == 1 else None

        # dedupe candidate pool by qid / normalised name
        pool, seen = [], set()
        for c in cands[prov]:
            k = c["qid"] or ("t:" + c["title"])
            if k in seen:
                continue
            seen.add(k)
            pool.append(c)

        init = roster_initial(m["name"])
        kind, C = None, []
        if init and len(rt) >= 1:
            sur = rt if len(rt) >= 1 else rt
            C = [c for c in pool if ends_with(c["toks"], sur) and c["toks"]
                 and c["toks"][0].startswith(init)]
            kind = "initial+surname" if C else None
        if not C and len(rt) >= 2:
            # given name + longest matching surname suffix
            for k in range(len(rt) - 1, 0, -1):
                sur = rt[-k:]
                C = [c for c in pool if ends_with(c["toks"], sur) and c["toks"]
                     and given_compatible(rt[0], c["toks"][0])]
                if C:
                    kind = "full"
                    break
        if not C:
            for sur in ([rt] if len(rt) == 1 else [rt, rt[1:], rt[-1:]]):
                C = [c for c in pool if ends_with(c["toks"], sur)]
                if C:
                    break
            kind = "surname" if len(rt) == 1 else "surname-fallback"
        if not C and len(rt) >= 2:
            # last resort: every roster token present in the candidate's name
            C = [c for c in pool if set(rt) <= set(c["toks"])]
            kind = "token-subset"

        def era_ok(c):
            if c["windows"]:
                return any(w0 - 1 <= y1 and w1 + 1 >= y0 for w0, w1 in c["windows"])
            return c["c21"]
        E = [c for c in C if era_ok(c)]
        C2 = E if E else ([c for c in C if c["c21"]] or C)

        used_gender = False
        if len(C2) > 1 and hint:
            G = [c for c in C2 if c["gender"] == hint]
            if G and len(G) < len(C2):
                C2, used_gender = G, True
        if len(C2) > 1:
            S = [c for c in C2 if c["windows"] and
                 any(w0 <= y1 and w1 >= y0 for w0, w1 in c["windows"])]
            if len(S) == 1:
                C2 = S
        # a surname-fallback from a full roster name must not contradict the honorific
        if kind in ("surname-fallback", "token-subset") and len(C2) == 1 and hint and \
                C2[0]["gender"] and C2[0]["gender"] != hint:
            C2 = []

        def by_plausible(byv):
            """A sitting member must have been >=18 at first_seen and <=92 at last."""
            return byv is not None and (y0 - byv) >= 18 and (y1 - byv) <= 92

        rec = {"prov": prov, "name": m["name"], "words": m["words"],
               "first_seen": m["first_seen"], "last_seen": m["last_seen"]}
        if len(C2) == 1:
            c = C2[0]
            window_hit = bool(c["windows"]) and any(
                w0 <= y1 and w1 >= y0 for w0, w1 in c["windows"])
            if kind in ("full", "initial+surname"):
                conf = "high"
            elif kind == "surname" and window_hit:
                conf = "high"
            elif kind in ("surname-fallback", "token-subset") and window_hit:
                conf = "medium"
            elif c["c21"]:
                conf = "medium"
            else:
                conf = "low"
            if used_gender and conf == "high":
                conf = "medium"
            rec["match_kind"] = kind
            rec.update({
                "matched_name": c["name"], "wikidata_qid": c["qid"],
                "birth_year": c["birth_year"] if by_plausible(c["birth_year"]) else None,
                "birth_year_source": (c["birth_year_source"]
                                      if by_plausible(c["birth_year"]) else None),
                "birth_year_rejected": (None if by_plausible(c["birth_year"])
                                        else c["birth_year"]),
                "year_first_elected": None, "gender": c["gender"] or hint,
                "gender_source": "wikidata/enwiki" if c["gender"] else
                                 ("hansard-honorific" if hint else None),
                "party": c["party"],
                "prior_occupation": c["occ_txt"], "occupation_category": c["occ_cat"],
                "education_level": c["edu_level"],
                "education_source": c["edu_source"],
                "postsecondary_attested": c["postsec"],
                "education_text": c["edu_text"],
                "education_field": ((c["fields"] or None) and c["fields"][0])
                                   or c["edu_field"],
                "degrees": c["degrees"], "alma_maters": c["almas"],
                "source_url": c["url"], "match_confidence": conf, "n_candidates": 1})
            rec["year_first_elected"] = c["fe"]
            rec["year_first_elected_source"] = c["fe_src"]
            rec["year_first_elected_is_lower_bound"] = c["fe_lb"]
        else:
            rec.update({
                "matched_name": None, "wikidata_qid": None, "birth_year": None,
                "birth_year_source": None, "birth_year_rejected": None,
                "year_first_elected": None,
                "gender": hint, "gender_source": "hansard-honorific" if hint else None,
                "party": None, "prior_occupation": None, "occupation_category": None,
                "education_level": None, "education_source": None, "education_text": None,
                "postsecondary_attested": None,
                "education_field": None, "degrees": [],
                "alma_maters": [], "source_url": None,
                "match_confidence": "none", "n_candidates": len(C2),
                "year_first_elected_source": None,
                "year_first_elected_is_lower_bound": None})
            unmatched_reason["ambiguous (%d candidates)" % min(len(C2), 5) if C2 else "no candidate"] += 1
            diag.append((prov, m["name"], len(C2), [c["name"] for c in C2[:6]]))
        out.append(rec)

    cnt = collections.Counter((r["prov"], r["wikidata_qid"]) for r in out if r["wikidata_qid"])
    for r in out:
        r["person_row_count"] = cnt.get((r["prov"], r["wikidata_qid"]), None)

    # -------- Manitoba Legislative Assembly bios (DOB + first-election dates)
    mbp = os.path.join(HERE, "mb_legislature_bios.json")
    if os.path.exists(mbp):
        mb = json.load(open(mbp))
        by_key = collections.defaultdict(list)
        for r in mb:
            by_key[(norm(r["surname"]).split()[-1])].append(r)
        n_dob = n_fe = 0
        for rec in out:
            if rec["prov"] != "MB":
                continue
            if rec["birth_year"] and rec["year_first_elected"]:
                continue
            key_name = rec.get("matched_name") or rec["name"]
            kt = toks(key_name)
            if not kt:
                continue
            C = [r for r in by_key.get(kt[-1], [])
                 if r["first_elected"] and r["first_elected"] <= 2019]
            if len(kt) >= 2:
                G = [r for r in C if given_compatible(kt[0], norm(r["given"]).split()[0])]
                if G:
                    C = G
            # must plausibly still be sitting during the Hansard window
            y1 = int(rec["last_seen"][:4])
            C = [r for r in C if r["first_elected"] <= y1]
            if len(C) != 1:
                continue
            r = C[0]
            if not rec["birth_year"] and r["dob"]:
                rec["birth_year"] = r["dob"]
                rec["birth_year_source"] = "mb-legislature:MLA-biographies"
                n_dob += 1
            if not rec["year_first_elected"] and r["first_elected"]:
                rec["year_first_elected"] = r["first_elected"]
                rec["year_first_elected_source"] = "mb-legislature:MLA-biographies"
                n_fe += 1
            if not rec["party"]:
                rec["party"] = r["party"]
        print("MB legislature merge: +%d birth years, +%d first-elected" % (n_dob, n_fe))

    json.dump(out, open(os.path.join(HERE, "member_bios.json"), "w"), indent=1)
    json.dump(diag, open(os.path.join(HERE, "bio_unmatched_diag.json"), "w"), indent=1)
    # quick coverage print
    for prov in sorted({r["prov"] for r in out}):
        R = [r for r in out if r["prov"] == prov]
        f = lambda k: sum(1 for r in R if r.get(k) is not None)
        print("%s n=%3d matched=%3d birth=%3d elected=%3d occ=%3d edu=%3d party=%3d gender=%3d" % (
            prov, len(R), sum(1 for r in R if r["match_confidence"] != "none"),
            f("birth_year"), f("year_first_elected"), f("occupation_category"),
            f("education_level"), f("party"), f("gender")))


if __name__ == "__main__":
    main()
