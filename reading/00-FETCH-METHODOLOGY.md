# Fetch methodology — canonical rules for acquisition sweeps

Distilled from every sweep since 2026-07; workflow prompts should reference or
inline this file rather than re-deriving technique. Updated when a new failure
mode or technique is proven.

## The order of operations (per target)

1. **Resolve identity FIRST.** Full citation + DOI before any fetch attempt.
   No identity → run reverse resolution: Crossref filter query from whatever
   is known (journal ISSN + volume + page; title fragment + year; author +
   venue). Publisher URLs usually encode identity — OUP embeds
   `vol/issue/page`, JSTOR stables are `10.2307/<stable>`, Springer/Wiley
   embed the DOI. **A miss recorded without a DOI is not a result; it is an
   unresolved lead and must be flagged as such.** (Root cause of the
   Alonso-Matouschek escape: URL-only MISS shelved in July; the LSE green
   copy sat in OpenAlex the whole time.)
2. **OA indexes before fetching anything:** Unpaywall v2 (by DOI) and OpenAlex
   `locations[]` (landing + pdf urls, repository copies). These are unmetered
   or nearly so. Semantic Scholar as third opinion.
3. **Distinguish CHECKED-AND-ABSENT from CHECK-FAILED.** A 429/quota-out is
   not a negative. Record `oa_status: unknown (rate-limited)` and retry later
   — never let an infrastructure failure become "no OA copy exists." Verify
   claimed-free hints too (a Beheim oa_hint asserted the Nature VoR was free;
   it was not).
4. **Author-side routes** when indexes say closed: institutional repository
   guessed from author affiliation (LSE eprints, ANU, DASH, eScholarship,
   DiVA, PURE instances), personal sites live AND via Wayback CDX (dead
   pages: Norenzayan's UBC, Johnson's squatted domain, Copp's Weebly),
   academia.edu asset-scrape (page images at attachments.academia-assets.com
   rebuild into a PDF — Ulrich, Velasquez 2003).
5. **Aggregators and mirrors:** national OJS hosts (tidsskrift.dk, RACO.cat,
   Dialnet, redalyc/scielo), Europe PMC render endpoint (beats Cloudflare on
   RoyalSoc/PNAS/Wiley VoRs), DSpace/Omeka bitstream APIs, `lawcat`-style
   catalogs, govinfo for anything a committee ever printed (public domain),
   IA serials microfilm (`sim_<journal>_<year>` — but PAR stops at 1961;
   check coverage before promising).
6. **Anthology/reprint route** for pre-1990 classics: Google Books
   SearchWithinVolume on a distinctive phrase locates which readers carry the
   piece; IA loans API (`is_lendable`, not just item existence) gives real
   borrowability. Negative control the scan first — a zero-hit phrase search
   on one Google volume means an index gap, not absence (that step caught the
   Price "rather more than" misquote).
7. **Browser-hardness ladder:** curl w/ UA → headless Chromium → **headless
   Firefox (clears Cloudflare where Chromium fails: HathiTrust, T&F, Wiley)**
   → warmed sessions → Wayback Save-Page-Now (archive.org's egress beats
   IP-scoped WAF blocks) → EBSCO-style response sniffing with service workers
   blocked (viewer Download buttons often never fire download events).
   **Never automate past a CAPTCHA** — that is the stop line; route to
   Matthew's browser with exact URLs and VERIFIED IDs.
8. **Never construct IDs from patterns.** The one bad JPASS download came
   from a pattern-guessed JSTOR stable ID. Resolve IDs from Crossref/OpenAlex
   or the target site's own search; when handing a human a download list,
   every ID must be verified, and say "confirm title on screen before
   downloading."

## Verification (unchanged, mandatory)

%PDF magic + early-page title/author match against the resolved identity;
record the VERSION (VoR / accepted / preprint / WP) and never cite one
version's pagination as another's; page-1 provenance stamps on rendered HTML;
filenames tell the truth (rename stand-ins for what they actually are).

## Ledger hygiene

Every target ends in exactly one state: FETCHED (with version), LOCATED-NEEDS-
HUMAN (with the specific action and verified ID), CHECKED-AND-ABSENT (with
which indexes said so), or UNRESOLVED-IDENTITY / CHECK-FAILED (retry queue —
never silently dropped). Re-hunts read the prior ledger and skip exhausted
angles by name.
