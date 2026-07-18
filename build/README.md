# build/ — figure + PDF pipeline

Regenerate everything:

    bash build/build.sh

Requires Python 3 with `matplotlib`, `markdown`, and `weasyprint`
(`pip install matplotlib markdown weasyprint`). WeasyPrint needs the system
Pango/cairo libraries; on macOS: `brew install pango`.

| Script | Produces | Layout in PDF |
|---|---|---|
| fig1_effort.py        | the-performance-commons-figure.png   (Figure 1) | full-width |
| fig2_coordination.py  | the-performance-commons-figure-2.png (Figure 2) | full-width |
| fig3_demand.py        | the-performance-commons-figure-3.png (Figure 3) | single-column |
| fig4_phase.py         | the-performance-commons-figure-4.png (Figure 4) | single-column |
| fig5_trend.py         | the-performance-commons-figure-5.png (Figure 5) | full-width |
| render_twocol.py      | the-performance-commons-2col.pdf | — |

`render_twocol.py <in.md> <out.pdf>` builds the two-column academic layout.
Which figures render single-column vs full-width is set by `fig_class()` inside it
(currently: figure-3 and figure-4 are single-column; everything else spans both columns).
Colour theme: navy #15324f, slate #5f7081, grey #9aa7b4, fill #2a4a6b.
