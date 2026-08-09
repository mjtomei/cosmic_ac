# Capital-cycle model artifacts

Reproducible artifacts behind the companion report **"Assets, Rents, and the Socialized
Buildout"** (2nd ed., 2026-08-04) — `assets-rents-socialized-buildout-2e.pdf` at repo
root. Satisfies the repo convention that every novel number gets an in-repo artifact
(the first edition's numbers had none). Handoff context: `HANDOFF-capital-cycle-2e.md`
in this directory.

## Files

| File | Feeds | What it computes |
|---|---|---|
| `build_report_v2.py` | The report PDF itself | **Canonical source of the report's text.** Edit this, run it, never edit the PDF. Deps: `reportlab` only (pypdf unneeded). Writes to `../../assets-rents-socialized-buildout-2e.pdf`. QA per repo convention: `pdftoppm -png -r 80` and view pages. |
| `ai_stock.py` | Report §3, Tables 1–2 | Vintage capital-stock model: gross → net stock (low/central/high), competitive-cost repricing, rent capitalization + required rent flows at three market-value attributions. |
| `gdp_req.py` | Report §5, Tables 3–4 | Revenue-requirement inversion: required after-tax profit → external revenue at three margins → share of world/US GDP; breakeven floor; labor-substitution decomposition. |
| `recognition_halflife.py` | Candidate for outline IV.3 (continuous-socialization bullet) | Recognition half-life: years for each era's own books to amortize half a capital vintage's cost. Railroads 1865–1900: **never** (RRB/betterment accounting — 100% storable; depreciation mandates arrived 1907/1943/1983); telecom 1996–2002: ~8–10y as booked (and booked slow: WorldCom fiber 40y→25y restated; WilTel wtd-avg 21y→15y at fresh start; GX plant 17.9% depreciated when impaired 74%); AI 2023–26: **~3.5y** (14.4%/yr) on the era's own schedule. Every share/life sourced in `VERIFICATION.md` (ICC/Fishlow/Ulmer; FCC SOCC/ARMIS + FCC 99-397; EDGAR verbatim; report Appendix A). The quantitative form of "this cycle socializes continuously": the first buildout whose accounting clock outruns its bubble. |

## Key assumptions (full text in report Appendices A–B)

**ai_stock.py** — Vintage gross AI-attributable capex 2023→H1-2026 (central: 65/185/460/370
$B), from big-4 disclosed capex ($226B 2024 → $410B 2025 → ~$725B guided 2026) times an
AI share rising ~50–55% → ~75% (CreditSights), plus Oracle/neoclouds/xAI/China/sovereign.
Asset mix and straight-line lives: IT 62% at 5y, power/cooling infra 23% at 15y,
shell+land 15% at 30y; mid-year convention. The 5-year IT life is corroborated by
Amazon's Jan-2025 reversion of a subset of server lives from six years to five, citing
the pace of AI hardware development ($1.4B depreciation cost). Add-ons (net, central):
upstream fab plant AI-allocated $125B, power/grid $65B, model IP at cost ex-compute
$55B. Competitive-cost adjustment: accelerators+networking = 75% of IT stock repriced
to 45% of paid price (competitive-margin replacement); other IT to 75%; infra/shell at
cost. Rent flows: required flow = rent capitalization × (r−g) growing (r=8%, g=3%),
× r flat, × (r+d) decaying (d=10%). Sensitivity: moving every vintage to its high case
plus Nvidia's implied IT share to 55% raises central net stock ~$200B; rent
capitalization moves <2% (dominated by the market-value term).

**gdp_req.py** — Required after-tax profit = required rent flow ($18T attribution case)
+ 8% normal return on a projected 2030 net stock of ~$5T (Goldman's $5.3T big-four
capex 2025–30 plus the rest of the ecosystem, net of depreciation). External revenue =
profit / consolidated net margin at 12/20/30%. GDP bases: world ~$135T, US ~$35T
nominal 2030 (~5%/yr from ~$118T / ~$30.5T in 2026, IMF-consistent). Breakeven floor =
depreciation on the 2030 stock (~$940B/yr at the Appendix A mix, net-to-gross ~0.77)
+ operations (~$275B) + tax-adjusted cost of capital (~$480B) ≈ $1.7T/yr ≈ 1.3% of
2030 world GDP. Labor decomposition: revenue R = capture share × labor cost addressed;
at 30% capture, R of $4.0/5.5/7.0T implies 19/26/33% of global labor income (labor
share 53% of world GDP).

## Provenance classes (report's Data Provenance note is the authority)

1. **Reported** — company disclosures and named third-party research (hyperscaler
   capex/guidance, Nvidia/TSMC, Gartner, PitchBook, CNBC/WSJ/FT on the Situational
   Awareness unwind, Microsoft FQ4-2026).
2. **Estimated by the authors** — AI-attribution shares, the vintage model and all of
   Tables 1–4, competitive-cost repricing, external AI revenue ($300–400B), rent
   composition, labor arithmetic.
3. **Historical literature** — railway/railroad/telecom records, cited in the report's
   Sources. **Caution:** per-name July-2026 long/short returns, 19th-c. express-company
   financials, and the Moody's/Bain figures currently ride on the report's ref [28]
   (Stansberry/Porter & Co.), a marketing document. **Never cite [28] as an authority
   in paper text** — re-anchor to primaries first (see handoff §5 for the target list
   and `VERIFICATION.md` in this directory, if present, for pass results).
