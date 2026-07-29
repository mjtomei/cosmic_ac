# NB Hansard corpus (for study S10)

`nb-hansard-index.json` — the 38 published sittings of the 61st Legislature,
2nd Session (Oct 2025 – May 2026), as [date, PDF URL] pairs scraped from
legnb.ca. Re-download with any HTTP client; ~39 MB total.

`nb-hansard-59th-index.json` — all 60 sittings of the 59th Legislature
(2018–2020, sessions 1–3), scraped 2026-07-29: the pre-ChatGPT control pool.
Listing pages are JS-rendered; pattern is
`legnb.ca/en/house-business/hansard/{legislature}/{session}` (58/3 onward),
PDFs under `legnb.ca/content/house_business/{leg}/{ses}/hansard/`.

Measured (2026-07-29 full extraction, `analysis/s10/`): **1,889,991 words
bilingual, 869k English** (of which ~709k speaker-authored — the two-column
record puts the language as spoken in the LEFT column, translation right).
The earlier 1,604,993-word figure undercounted: **six of the 38 PDFs are
truncated on the server itself** (curl-confirmed content-length; sittings
09, 14, 15, 28, 30, 33) and were only partially readable then. pikepdf
recovers them fully (xref rebuild); see `analysis/s10/README.md`.

Note: publication lags. As of 2026-07-29 the index ends at May 14, 2026, while
Bills 46/47 (Energy Sector Consumer Advocate Act) were introduced May 26 — so
the sitting containing the Bill Oliver speech is not yet public. Unlisted
transcripts are available on request from the Hansard Office
(leghaninfo@legnb.ca, 506-453-2531).
