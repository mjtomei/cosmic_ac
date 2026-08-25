#!/usr/bin/env python3
"""§4.2's length-quartile contrast and weighting comparison, on the pooled
prevalence sample (review CP3: the earlier 9.4%/5.8%/0.6pp figures were
computed on a different scope). One source: banded_prevalence.load()."""
import banded_prevalence as B
rows=[r for r in B.load() if r[1]=="prev"]
rows.sort(key=lambda r:r[3]); q=len(rows)//4
lo,hi=rows[:q],rows[-q:]
w=lambda rs:100*sum(r[3]*r[5] for r in rs)/sum(r[3] for r in rs)
b=lambda rs:100*sum(1 for r in rs if r[4])/len(rs)
print(f"shortest quartile: {w(lo):.1f}% word-weighted, {b(lo):.1f}% binary-segment")
print(f"longest quartile:  {w(hi):.1f}% word-weighted, {b(hi):.1f}% binary-segment")
print(f"segment-weighted binary {100*sum(1 for r in rows if r[4])/len(rows):.2f}% | "
      f"segment-weighted fraction {100*sum(r[5] for r in rows)/len(rows):.2f}% | "
      f"word-weighted {100*sum(r[3]*r[5] for r in rows)/sum(r[3] for r in rows):.2f}%")
