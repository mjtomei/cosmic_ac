# S10 power expansion: more legislators, more legislatures

**2026-08-14, planned with Matthew.** The class/education/prominence results
(§4.6a, VECTOR-ANALYSIS.md) are limited by member-level n, not by corpus
size: class III rests on 29 members, VIIab on 16, secondary education on 40,
and the AI-usage-by-class table's largest cell is 181 segments. The plan is to
expand POWER — members with covariates — not merely words.

## Execute after the Claude-trace workflow returns

## Tier 1: covariates for corpora we already hold (no new downloads)

The cheapest power is sitting in chambers whose text is already extracted but
whose members were never bio-joined:

| chamber | corpus in repo | why the join is easy |
|---|---|---|
| US House 1994-2026 | `us/segments_us_house.jsonl` | Biographical Directory of Congress: birth year, occupation, education for EVERY member in structured form; CongressBios/unitedstates datasets |
| US Senate 1994-2026 | `us/segments_us_senate.jsonl` | same |
| UK Commons 1985-2026 | `uk/segments_uk_deep.jsonl` | TheyWorkForYou/mySociety IDs; extensive published member data |
| Dáil Éireann | `ie/segments_ie_en.jsonl` | Oireachtas member API |
| CA federal | `ca/segments_ca2.jsonl` | PARLINFO: full biographical records |
| AUS states ×5, SCO, WAL, NI | already extracted | parliament member pages, varying quality |
| New Brunswick | pilot corpus | CAN provincial pattern established |

The US join alone should several-fold the member count and — critically for
the small classes — Congress historically carries far more farmers, manual and
routine-non-manual backgrounds than eight Canadian provinces do. It also
enables the AI-by-class question in the highest-prevalence chamber (US House
12.1%).

Method per chamber: same as the CA pass. Speaker-key → member join first
(the BC/SK/NL lesson: use each source's own key field); occupation strings
through the SAME double-blind coding workflow (append to
`occupation_strings.json`, rerun; same rubric, agreement rate reported);
education to the same six levels; birth year; Wikipedia QID → article length
via `wiki_depth.py` (already generic).

## Tier 2: new chambers chosen for class composition, not size

The binding cells are III (routine non-manual) and VIIab (manual). Choose
chambers that add THOSE members:

- **US state legislatures** (citizen legislatures: part-time, low-pay —
  far more trades, clerical, farm members than professional parliaments).
  Openstates has structured member data + transcripts for many.
- **NZ Parliament** (Hansard quality high, member data good).
- **Remaining CA provinces/territories**: QC (English segments only, small),
  YT/NT/NU (tiny but cheap).

## Tier 3: the checks the new power must fund

Committed alongside the expansion, because they are what the current results
lack:

1. **Cluster-robust standard errors by member** for every §4.6a regression.
   Three prior incidents of unclustered inference flattering a result.
2. **Cluster bootstrap on AI-usage-by-class** (currently 27-segment cells).
3. **Pre-registered volume threshold** for the chase-and-flight correlation:
   fix the cut on pre-2023 data, test on post.
4. **Primary-text verification** of the §4.6a citation set (Labov, Simmel,
   Veblen, Jhering, Lieberson, Bourdieu, Owens & Baker).
5. **Equalizer tracking**: the class gradient in §4.6a re-estimated yearly;
   the hypothesis predicts compression as prevalence rises.

## Order

1. US House + Senate covariates (biggest single win, structured source).
2. UK Commons.
3. Cluster-robust re-estimation of everything on the enlarged panel.
4. CA federal, IE, AUS states.
5. Tier 2 chambers as needed for the thin classes specifically.
