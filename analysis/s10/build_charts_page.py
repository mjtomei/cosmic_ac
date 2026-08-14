#!/usr/bin/env python3
"""Render the S10 distribution and trend charts to a self-contained HTML page.

Reads the three built artifacts -- occurrence_trends.json,
length_distributions.json, rlhf_pref_final.json -- and writes s10_charts.html
with the data embedded, so the page is reproducible from the repository and
carries no external dependency.

Usage: python build_charts_page.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import banded_prevalence as BP          # noqa: E402

OUT = os.path.join(HERE, "s10_charts.html")

# chambers with an uninterrupted download window, so a line is a trend rather
# than a picture of the sampling schedule
CONTINUOUS = ["UK", "US-House", "US-Senate", "CA-FED", "IE"]

AI_MARKS = [(2017, "Transformer"), (2018, "Smart Compose"), (2019, "GPT-2"),
            (2020, "GPT-3"), (2021, "Copilot"), (2022, "ChatGPT")]


def stats():
    rows = BP.load()
    prev = [r for r in rows if r[1] == "prev"]
    ctl = [r for r in rows if r[1] == "ctl"]
    out = {}
    for band in ("short", "long"):
        s = [r for r in prev if r[2] == band]
        n, k, sr, w, wk, wr = BP.rate(s)
        out[band] = {"n": n, "k": k, "seg": sr, "words": w, "word": wr}
    n, k, sr, w, wk, wr = BP.rate(prev)
    out["all"] = {"n": n, "k": k, "seg": sr, "words": w, "word": wr}
    n, k, sr, w, wk, wr = BP.rate(ctl)
    out["ctl"] = {"n": n, "k": k, "seg": sr, "words": w, "word": wr}
    return out


def main():
    trends = json.load(open(os.path.join(HERE, "occurrence_trends.json")))
    trends.pop("_META", None)                     # 377 words we do not plot
    lengths = json.load(open(os.path.join(HERE, "length_distributions.json")))
    align = json.load(open(os.path.join(HERE, "rlhf_pref_final.json")))
    freq = json.load(open(os.path.join(HERE, "style_word_frequency.json")))
    aishare_p = os.path.join(HERE, "ai_share_by_chamber.json")
    aishare = json.load(open(aishare_p)) if os.path.exists(aishare_p) else None
    data = {"trends": trends, "lengths": lengths, "align": align, "freq": freq,
            "aishare": aishare,
            "stats": stats(), "continuous": CONTINUOUS, "marks": AI_MARKS}
    html = TEMPLATE.replace("__DATA__", json.dumps(data))
    open(OUT, "w").write(html)
    print(f"wrote {os.path.basename(OUT)} ({os.path.getsize(OUT)/1024:.0f} KB)")


TEMPLATE = r"""<title>Legislative Register Drift</title>
<style>
:root{
  --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e;
  --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,.10);
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4;
  --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --good:#006300; --crit:#d03b3b;
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --page:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7;
  --muted:#898781; --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,.10);
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --good:#0ca30c; --crit:#d03b3b;
}}
:root[data-theme="dark"]{
  --page:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink2:#c3c2b7;
  --muted:#898781; --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,.10);
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181;
  --s6:#008300; --s7:#9085e9; --s8:#e66767;
  --good:#0ca30c; --crit:#d03b3b;
}
*{box-sizing:border-box}
body{background:var(--page); color:var(--ink); margin:0;
  font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;}
.wrap{max-width:1120px; margin:0 auto; padding:40px 22px 90px;}
h1{font-size:30px; line-height:1.2; margin:0 0 6px; letter-spacing:-.02em}
h2{font-size:20px; margin:52px 0 4px; letter-spacing:-.01em}
h3{font-size:15px; margin:30px 0 4px; color:var(--ink)}
p{color:var(--ink2); margin:8px 0}
.lede{font-size:16px; max-width:74ch}
.note{font-size:13.5px; color:var(--muted); max-width:82ch; margin:6px 0 0}
.card{background:var(--surface); border:1px solid var(--ring); border-radius:12px;
  padding:18px 18px 10px; margin:16px 0;}
.tiles{display:grid; grid-template-columns:repeat(auto-fit,minmax(178px,1fr)); gap:12px; margin:18px 0}
.tile{background:var(--surface); border:1px solid var(--ring); border-radius:12px; padding:14px 15px}
.tile .v{font-size:26px; font-weight:640; letter-spacing:-.02em; display:block}
.tile .k{font-size:12.5px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em}
.tile .s{font-size:12.5px; color:var(--ink2); margin-top:3px}
.legend{display:flex; flex-wrap:wrap; gap:8px 16px; margin:2px 0 8px; font-size:13px; color:var(--ink2)}
.legend span{display:inline-flex; align-items:center; gap:6px}
.sw{width:11px;height:11px;border-radius:3px;flex:none}
.sm{display:grid; grid-template-columns:repeat(auto-fill,minmax(196px,1fr)); gap:10px}
.smc{background:var(--surface); border:1px solid var(--ring); border-radius:9px; padding:8px 8px 2px}
.smt{font-size:12px; font-weight:600; margin:0 0 1px}
.smx{font-size:11px; color:var(--muted); margin:0}
.scroll{overflow-x:auto}
svg{display:block; max-width:100%}
table{border-collapse:collapse; font-size:13px; width:100%; margin-top:8px}
th,td{text-align:right; padding:4px 9px; border-bottom:1px solid var(--grid);
  font-variant-numeric:tabular-nums; white-space:nowrap}
th:first-child,td:first-child{text-align:left; font-variant-numeric:normal}
th{color:var(--muted); font-weight:600}
details{margin:10px 0}
summary{cursor:pointer; font-size:13px; color:var(--ink2)}
.tip{position:fixed; pointer-events:none; background:var(--surface);
  border:1px solid var(--ring); border-radius:8px; padding:7px 10px; font-size:12.5px;
  box-shadow:0 4px 18px rgba(0,0,0,.16); opacity:0; transition:opacity .1s; z-index:9;
  font-variant-numeric:tabular-nums; max-width:280px}
.warn{border-left:3px solid var(--crit); padding-left:12px; margin:14px 0}
</style>

<div class="wrap" id="root"></div>
<div class="tip" id="tip"></div>

<script>
const D = __DATA__;
const NS = "http://www.w3.org/2000/svg";
const CSS = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const SER = ["--s1","--s2","--s3","--s4","--s5","--s6","--s7","--s8"];
const tip = document.getElementById("tip");
const el = (t,a={},kids=[])=>{const e=document.createElementNS(NS,t);
  for(const k in a) e.setAttribute(k,a[k]); kids.forEach(k=>e.appendChild(k)); return e;};
const h = (t,a={},kids=[])=>{const e=document.createElement(t);
  for(const k in a){ if(k==="html") e.innerHTML=a[k]; else if(k==="text") e.textContent=a[k];
    else e.setAttribute(k,a[k]); }
  (Array.isArray(kids)?kids:[kids]).forEach(k=>k&&e.appendChild(k)); return e;};
const fmt = (n,d=0)=>n.toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d});

function showTip(evt, html){ tip.innerHTML=html; tip.style.opacity=1;
  const p=12, w=tip.offsetWidth, hh=tip.offsetHeight;
  let x=evt.clientX+p, y=evt.clientY+p;
  if(x+w>innerWidth-8) x=evt.clientX-w-p;
  if(y+hh>innerHeight-8) y=evt.clientY-hh-p;
  tip.style.left=x+"px"; tip.style.top=y+"px"; }
const hideTip = ()=>tip.style.opacity=0;

/* ---------- line chart: series of [x, y|null]; null breaks the line ---------- */
function lineChart(opts){
  const W=opts.width||1040, H=opts.height||330, compact=opts.compact;
  const M = compact ? {t:8,r:8,b:20,l:34} : {t:14,r:opts.padRight||96,b:30,l:56};
  const iw=W-M.l-M.r, ih=H-M.t-M.b;
  const xs=opts.series.flatMap(s=>s.points.map(p=>p[0]));
  const ys=opts.series.flatMap(s=>s.points.filter(p=>p[1]!=null).map(p=>p[1]));
  if(!ys.length) return h("div");
  const x0=opts.xMin!=null?opts.xMin:Math.min(...xs), x1=opts.xMax!=null?opts.xMax:Math.max(...xs);
  let y0=opts.yMin!=null?opts.yMin:Math.min(...ys), y1=opts.yMax!=null?opts.yMax:Math.max(...ys);
  if(opts.zero) y0=0;
  const pad=(y1-y0)*.10||1; y1+=pad; y0=opts.zero?0:y0-pad;
  const X=v=>M.l+(v-x0)/((x1-x0)||1)*iw, Y=v=>M.t+ih-(v-y0)/((y1-y0)||1)*ih;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,width:W,height:H,role:"img"});

  const ticks=(lo,hi,n)=>{const raw=(hi-lo)/n, m=Math.pow(10,Math.floor(Math.log10(raw)));
    const st=[1,2,2.5,5,10].map(k=>k*m).find(k=>k>=raw)||10*m;
    const out=[]; for(let v=Math.ceil(lo/st)*st; v<=hi; v+=st) out.push(v); return out;};
  for(const t of ticks(y0,y1,compact?3:5)){
    svg.appendChild(el("line",{x1:M.l,x2:M.l+iw,y1:Y(t),y2:Y(t),stroke:CSS("--grid"),"stroke-width":1}));
    svg.appendChild(el("text",{x:M.l-7,y:Y(t)+4,"text-anchor":"end",
      fill:CSS("--muted"),"font-size":compact?9:11},[document.createTextNode(fmt(t))]));
  }
  const xt = opts.xTicks || ticks(x0,x1,compact?3:8).map(v=>Math.round(v));
  for(const t of xt){ if(t<x0||t>x1) continue;
    svg.appendChild(el("text",{x:X(t),y:H-(compact?7:10),"text-anchor":"middle",
      fill:CSS("--muted"),"font-size":compact?9:11},[document.createTextNode("'"+String(t).slice(2))]));
  }
  svg.appendChild(el("line",{x1:M.l,x2:M.l+iw,y1:M.t+ih,y2:M.t+ih,stroke:CSS("--axis"),"stroke-width":1}));

  (opts.marks||[]).forEach(([yr,lab])=>{ if(yr<x0||yr>x1) return;
    svg.appendChild(el("line",{x1:X(yr),x2:X(yr),y1:M.t,y2:M.t+ih,stroke:CSS("--grid"),
      "stroke-width":1,"stroke-dasharray":"3 3"}));
    /* The six AI landmarks fall in six consecutive years, so horizontal
       labels pile on top of each other on any axis longer than a decade.
       Set them vertical, hanging from the top of the plot along their own
       rule, where they cannot collide with each other or with the data. */
    if(!compact){ const lx=X(yr)+11, ly=M.t+4;
      svg.appendChild(el("text",{x:lx,y:ly,fill:CSS("--muted"),"font-size":10,
        "text-anchor":"start",transform:`rotate(90 ${lx} ${ly})`},
        [document.createTextNode(lab)])); }
  });

  const lbl=[];
  opts.series.forEach((s,i)=>{
    const col = s.color || CSS(SER[i%8]);
    let d="", pen=false;
    s.points.forEach(([px,py])=>{ if(py==null){pen=false; return;}
      d += (pen?" L":" M")+X(px)+" "+Y(py); pen=true; });
    svg.appendChild(el("path",{d:d.trim(),fill:"none",stroke:col,
      "stroke-width":compact?1.5:2,"stroke-linejoin":"round","stroke-linecap":"round"}));
    const last=[...s.points].reverse().find(p=>p[1]!=null);
    if(!compact && last && opts.directLabels!==false){
      // collect for a de-collision pass; series whose final values are close
      // together would otherwise print their labels on top of each other
      lbl.push({x:X(last[0])+7, y:Y(last[1])+4,
                col:(s.labelColor||col), name:s.name});
    }
    if(!compact) s.points.forEach(([px,py])=>{ if(py==null) return;
      const c=el("circle",{cx:X(px),cy:Y(py),r:8,fill:"transparent"});
      c.addEventListener("mousemove",e=>showTip(e,
        `<b>${s.name}</b><br>${px}: ${fmt(py,opts.dp||0)}${opts.unit||""}`));
      c.addEventListener("mouseleave",hideTip); svg.appendChild(c);
      svg.appendChild(el("circle",{cx:X(px),cy:Y(py),r:2.6,fill:col}));
    });
  });
  // de-collide end labels: sort by y and enforce a minimum vertical spacing
  lbl.sort((a,b)=>a.y-b.y);
  const MINGAP=13;
  for(let i=1;i<lbl.length;i++)
    if(lbl[i].y-lbl[i-1].y<MINGAP) lbl[i].y=lbl[i-1].y+MINGAP;
  const over=lbl.length?lbl[lbl.length-1].y-(M.t+ih):0;
  if(over>0) lbl.forEach(l=>l.y-=over);
  lbl.forEach(l=>svg.appendChild(el("text",{x:l.x,y:l.y,fill:l.col,
    "font-size":11.5,"font-weight":620},[document.createTextNode(l.name)])));

  if(compact){ const r=el("rect",{x:M.l,y:M.t,width:iw,height:ih,fill:"transparent"});
    r.addEventListener("mousemove",e=>{ const bb=svg.getBoundingClientRect();
      const vx=(e.clientX-bb.left)*(W/bb.width);
      const yr=Math.round(x0+(vx-M.l)/iw*(x1-x0));
      const rows=opts.series.map(s=>{const p=s.points.find(p=>p[0]===yr);
        return p&&p[1]!=null?`${s.name}: <b>${fmt(p[1],opts.dp||0)}</b>`:null;}).filter(Boolean);
      if(rows.length) showTip(e,`<b>${yr}</b><br>`+rows.join("<br>")); else hideTip(); });
    r.addEventListener("mouseleave",hideTip); svg.appendChild(r); }
  return svg;
}

/* ---------- step chart over ordered bins ---------- */
function stepChart(opts){
  const W=opts.width||1040, H=opts.height||300, compact=opts.compact;
  const M = compact?{t:8,r:8,b:30,l:32}:{t:14,r:16,b:46,l:52};
  const iw=W-M.l-M.r, ih=H-M.t-M.b, n=opts.labels.length, bw=iw/n;
  const y1=Math.max(...opts.series.flatMap(s=>s.values))*1.1||1;
  const Y=v=>M.t+ih-v/y1*ih;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,width:W,height:H,role:"img"});
  for(let k=0;k<=4;k++){ const v=y1*k/4;
    svg.appendChild(el("line",{x1:M.l,x2:M.l+iw,y1:Y(v),y2:Y(v),stroke:CSS("--grid"),"stroke-width":1}));
    svg.appendChild(el("text",{x:M.l-7,y:Y(v)+4,"text-anchor":"end",fill:CSS("--muted"),
      "font-size":compact?9:11},[document.createTextNode(fmt(v,0)+"%")]));
  }
  opts.labels.forEach((lb,i)=>{ if(compact && i%3) return;
    svg.appendChild(el("text",{x:M.l+bw*(i+.5),y:H-(compact?8:26),"text-anchor":"middle",
      fill:CSS("--muted"),"font-size":compact?8.5:10,
      transform:compact?"":`rotate(-40 ${M.l+bw*(i+.5)} ${H-26})`},[document.createTextNode(lb)]));
  });
  if(!compact) svg.appendChild(el("text",{x:M.l+iw/2,y:H-4,"text-anchor":"middle",
    fill:CSS("--muted"),"font-size":11},[document.createTextNode("words per item")]));
  svg.appendChild(el("line",{x1:M.l,x2:M.l+iw,y1:M.t+ih,y2:M.t+ih,stroke:CSS("--axis"),"stroke-width":1}));
  opts.series.forEach((s,i)=>{
    const col=s.color||CSS(SER[i%8]); let d="";
    s.values.forEach((v,j)=>{ const x=M.l+bw*j, y=Y(v);
      d += (j?" L":"M")+x+" "+y+" L"+(x+bw)+" "+y; });
    svg.appendChild(el("path",{d,fill:"none",stroke:col,"stroke-width":compact?1.5:2,
      "stroke-linejoin":"round"}));
  });
  const r=el("rect",{x:M.l,y:M.t,width:iw,height:ih,fill:"transparent"});
  r.addEventListener("mousemove",e=>{ const bb=svg.getBoundingClientRect();
    const j=Math.floor(((e.clientX-bb.left)*(W/bb.width)-M.l)/bw);
    if(j<0||j>=n) return hideTip();
    showTip(e,`<b>${opts.labels[j]} words</b><br>`+opts.series.map(s=>
      `${s.name}: <b>${fmt(s.values[j],1)}%</b>`).join("<br>")); });
  r.addEventListener("mouseleave",hideTip); svg.appendChild(r);
  return svg;
}

function legend(names,cols){ return h("div",{class:"legend"},
  names.map((n,i)=>h("span",{},[ (()=>{const s=h("span",{class:"sw"});
    s.style.background=cols?cols[i]:CSS(SER[i%8]); return s;})(),
    h("span",{text:n}) ]))); }

function table(head, rows){
  const t=h("table",{},[h("thead",{},[h("tr",{},head.map(x=>h("th",{text:x})))])]);
  t.appendChild(h("tbody",{},rows.map(r=>h("tr",{},r.map(x=>h("td",{text:String(x)}))))));
  return h("div",{class:"scroll"},[t]);
}
const details=(s,node)=>h("details",{},[h("summary",{text:s}),node]);

/* ------------------------------- build page ------------------------------- */
const R=document.getElementById("root");
const add=(...n)=>n.forEach(x=>R.appendChild(x));
const binLabels=(()=>{const e=D.lengths.edges,o=["<"+e[0]];
  for(let i=0;i<e.length-1;i++) o.push(e[i]+"–"+(e[i+1]-1));
  o.push(e[e.length-1]+"+"); return o;})();
const pct=hist=>{const s=hist.reduce((a,b)=>a+b,0)||1; return hist.map(c=>100*c/s);};

add(h("h1",{text:"Legislative Register Drift"}));
add(h("p",{class:"lede",html:"Word-count distributions for the generated corpus and the real record, "+
  "and the Kobak instrument-vocabulary rate per chamber per year. Everything here is "+
  "computed by <code>length_distributions.py</code> and <code>occurrence_trends.py</code> "+
  "from the tracked corpora; hover any chart for values."}));

/* -- stat tiles -- */
const S=D.stats, A=D.align;
const uk=D.trends.UK, ukF=uk[uk.length-1], uk94=uk.find(r=>r.year===1994);
const tiles=[
  ["Prevalence, word-weighted", (100*S.all.word).toFixed(2)+"%",
   `${fmt(S.all.words)} words scored, both bands`],
  ["Pre-AI controls", "0", `of ${fmt(S.ctl.words)} words flagged`],
  ["Short band 50–119w", (100*S.short.word).toFixed(2)+"%", "vs "+(100*S.long.word).toFixed(2)+"% long band"],
  ["Alignment excess", "+"+A.by_checkpoint.find(r=>r.n===1600).excess_well_measured.toFixed(3),
   "well-measured, 3 families @1600"],
  ["UK gap, 1994→2026", fmt(uk94.gap)+" → "+fmt(ukF.gap),
   (ukF.gap/uk94.gap).toFixed(1)+"× over 32 years"],
];
add(h("div",{class:"tiles"},tiles.map(([k,v,s])=>h("div",{class:"tile"},[
  h("span",{class:"k",text:k}),h("span",{class:"v",text:v}),h("div",{class:"s",text:s})]))));

/* ====================== A. STYLE-WORD FREQUENCY ====================== */
add(h("h2",{text:"A. Do the style words actually show up?"}));
add(h("p",{html:"§4.7's excess runs over Kobak's <b>"+D.freq.style_n+"</b> style words, and only "+
  "about half appear in the generated corpus. The standing defence is that the list came from "+
  "PubMed abstracts and is partly out-of-domain for legislatures. This is that defence tested "+
  "against the distribution rather than a presence count — every corpus truncated to the same "+
  "<b>"+fmt(D.freq.target_words)+" words</b>, base and instruct counted separately."}));

const FC=D.freq.corpora, fnames=Object.keys(FC);
add(h("div",{class:"card"},[
  h("h3",{text:"How many style words occur this often, at matched volume"}),
  legend(fnames),
  stepChart({labels:D.freq.bins,
    series:fnames.map(n=>({name:n,values:FC[n].hist.map(v=>100*v/D.freq.style_n)}))}),
]));
add(details("Table: number of style words per occurrence bin",
  table(["corpus","words",...D.freq.bins],
    fnames.map(n=>[n,fmt(FC[n].words),...FC[n].hist]))));

const gb=FC["generated BASE"], gi=FC["generated INSTRUCT"], hz=FC["Hansard 2025-26"].hist[0];
add(h("div",{class:"warn"},[h("p",{html:"<b>The shapes are not the same, so the defence only "+
  "half holds.</b> At equal volume Hansard leaves <b>"+hz+"</b> of the "+D.freq.style_n+
  " words unused; base generation leaves <b>"+gb.hist[0]+"</b> and instruct <b>"+gi.hist[0]+
  "</b>. The generated corpus has the fatter zero bin, so part of the missing coverage is a "+
  "property of the generation, not of the word list."})]));

const ov=gb.overlap, ov2=gi.overlap;
add(h("div",{class:"tiles"},[
  ["Absent from both", ov.absent_both, "genuinely out-of-domain"],
  ["Absent from base only", ov.absent_generated_only, "real usage the model missed"],
  ["Absent from instruct only", ov2.absent_generated_only, "post-training closes the gap"],
  ["Present in both", ov.present_both, "base vs Hansard 2025–26"],
].map(([k,v,s])=>h("div",{class:"tile"},[h("span",{class:"k",text:k}),
  h("span",{class:"v",text:String(v)}),h("div",{class:"s",text:s})]))));
add(h("p",{class:"note",html:"Only <b>"+ov.absent_both+"</b> of "+D.freq.style_n+
  " words are absent from both corpora — that is the true out-of-domain share, well under the "+
  "111 a presence count implied. The words real legislators used in 2025–26 that our models "+
  "never produced are the archetypal ones: <i>"+
  ov.generated_only_examples.slice(0,10).join(", ")+"</i>. Our 8B open models are not the "+
  "source of that register; post-training moves them toward it ("+ov.absent_generated_only+
  " → "+ov2.absent_generated_only+" missing), but does not close it."}));

/* ============================ B. LENGTH ============================ */
add(h("h2",{text:"B. How long is a piece of text?"}));
add(h("p",{html:"Two caps dominate these distributions and both are ours. Generated text stops at "+
  `<b>${D.lengths.new_tokens} new tokens</b>, so it is truncated from above; Hansard segments are `+
  "packer output capped at <b>360 words</b> with a 50-word floor. A turn is the only natural unit here."}));

const mAll=D.lengths.models, cAll=D.lengths.chambers;
const cmp=[
  {name:"Generated · base", values:pct(mAll["ALL/base"].hist)},
  {name:"Generated · instruct", values:pct(mAll["ALL/instruct"].hist)},
  {name:"Hansard segments", values:pct(cAll._ALL.segments_scoreable.hist)},
  {name:"Hansard turns", values:pct(cAll._ALL.turns.hist)},
];
add(h("div",{class:"card"},[
  h("h3",{text:"Generated text against the real record"}),
  legend(cmp.map(s=>s.name)),
  stepChart({labels:binLabels,series:cmp}),
]));
add(h("p",{class:"note",html:"The generated corpus is a <b>spike</b>: "+
  fmt(pct(mAll["ALL/instruct"].hist)[9],0)+"% of instruct outputs land in the 300–359 bin. "+
  "Real speech is long-tailed — "+fmt(pct(cAll._ALL.turns.hist)[0],0)+
  "% of turns are under 25 words and "+fmt(pct(cAll._ALL.turns.hist).slice(10).reduce((a,b)=>a+b,0),0)+
  "% run past 360. Base models also produce a low shoulder the instruct models do not, "+
  "which is the base model emitting almost nothing before the cap binds."}));
add(details("Table: % of items per bin",
  table(["series",...binLabels], cmp.map(s=>[s.name,...s.values.map(v=>v.toFixed(1))]))));

add(h("h3",{text:"Each model, base against instruct"}));
add(h("div",{class:"sm"}, Object.keys(mAll).filter(k=>!k.startsWith("ALL/")).map(k=>{
  const st=mAll[k].stats;
  return h("div",{class:"smc"},[h("p",{class:"smt",text:k}),
    h("p",{class:"smx",text:`n=${fmt(st.n)} · median ${st.median} · mean ${st.mean.toFixed(0)}`}),
    stepChart({labels:binLabels,series:[{name:k,values:pct(mAll[k].hist),
      color:CSS(k.endsWith("/base")?"--s1":"--s2")}],compact:true,width:210,height:112})]);
})));
add(h("p",{class:"note",html:"Blue is base, orange is instruct. Every base model carries the "+
  "short shoulder; no instruct model does."}));

add(h("h3",{text:"Each chamber, scoreable segments"}));
add(h("div",{class:"sm"}, Object.keys(cAll).filter(k=>k!=="_ALL").sort().map(k=>{
  const st=cAll[k].segments_scoreable.stats, tt=cAll[k].turns.stats;
  return h("div",{class:"smc"},[h("p",{class:"smt",text:k}),
    h("p",{class:"smx",text:`median ${st.median}w · turns ${tt.median}w`}),
    stepChart({labels:binLabels,series:[
      {name:"segments",values:pct(cAll[k].segments_scoreable.hist),color:CSS("--s3")},
      {name:"turns",values:pct(cAll[k].turns.hist),color:CSS("--s5")}],
      compact:true,width:210,height:112})]);
})));
add(h("p",{class:"note",html:"Aqua is packed segments, magenta is whole turns. The chambers "+
  "differ enormously: US Senate segments have a median of "+
  cAll["US-Senate"].segments_scoreable.stats.median+" words against UK Commons’ "+
  cAll.UK.segments_scoreable.stats.median+"."}));

/* ============================ B. TRENDS ============================ */
add(h("h2",{text:"C. Instrument vocabulary over time"}));
add(h("p",{html:"Kobak style-word occurrences per 100k words, against the median of 200 "+
  "frequency- and dispersion-matched placebo sets. The <b>gap</b> between them is the quantity "+
  "of interest: if instrument and placebo rise together, ordinary vocabulary change explains it."}));

add(h("div",{class:"card"},[
  h("h3",{text:"UK Commons, 1985–2026 — the only chamber with deep history"}),
  legend(["Instrument (377 Kobak style words)","Matched placebo (median of 200)"]),
  lineChart({series:[
    {name:"instrument",points:uk.map(r=>[r.year,r.instrument_per100k])},
    {name:"placebo",points:uk.map(r=>[r.year,r.placebo_per100k])}],
    marks:D.marks, height:300, unit:"/100k", padRight:76}),
  h("h3",{text:"…and the gap between them"}),
  lineChart({series:[{name:"gap",points:uk.map(r=>[r.year,r.gap])}],
    marks:D.marks, height:250, zero:true, unit:"/100k", padRight:46, directLabels:false}),
]));
add(h("p",{class:"note",html:"The placebo is flat across forty-one years, so the instrument's "+
  "rise is specific to those words. But the shape is a <b>U</b> that bottoms out in "+
  "1994 — long before any transformer — and climbs steadily from the mid-1990s. "+
  "There is no visible break at 2022. 2023 is absent: it was deliberately excluded as the "+
  "ChatGPT transition year and is being backfilled."}));

const contin=D.continuous.filter(c=>D.trends[c]);
const yrs=[]; for(let y=2006;y<=2026;y++) yrs.push(y);
const pts=(ch,key)=>yrs.map(y=>{const r=D.trends[ch].find(r=>r.year===y);
  return [y, r?r[key]:null];});
add(h("div",{class:"card"},[
  h("h3",{text:"All continuously-covered chambers, 2006–2026 (gap per 100k)"}),
  legend(contin),
  lineChart({series:contin.map(c=>({name:c,points:pts(c,"gap")})),
    marks:D.marks, height:340, xMin:2006, xMax:2026, unit:"/100k"}),
]));
add(h("div",{class:"warn"},[h("p",{html:"<b>The UK trend does not replicate.</b> "+
  "US House and Senate are flat across the whole twenty years — the House sits at "+
  fmt(D.trends["US-House"][0].gap)+" in 2006 and "+
  fmt(D.trends["US-House"][D.trends["US-House"].length-1].gap)+" in 2026 — while the UK "+
  "roughly doubles. The US chambers start far <i>above</i> where the UK ends, so the "+
  "picture is the UK converging upward on a level the US already held in 2006, not a "+
  "common machine-driven shift. Ireland rises; federal Canada does not."})]));

/* -- one chart: national chambers + word-weighted regional aggregates -- */
add(h("h3",{text:"Eight series: national chambers and regional aggregates"}));
add(h("p",{class:"note",html:"Twenty-two lines is past what colour can carry, so the "+
  "eight states and provinces of each federation are collapsed into one "+
  "<b>word-weighted</b> series apiece — weighting by words rather than by chamber so a "+
  "large legislature is not given the same say as a small one. Each aggregate is a "+
  "<b>balanced panel</b>: only years where every member is present, because a group "+
  "average whose membership changes between years is a picture of coverage rather than "+
  "a trend. Members with gaps are excluded and named, and remain available individually "+
  "below — PEI from the Canadian group (bot-blocked, 12 years missing), South Australia "+
  "from the Australian (Wayback gaps in 2012, 2013, 2015), and Northern Ireland from the "+
  "devolved (the Assembly did not sit for two multi-year stretches)."}));
const GRP = [
  ["UK", D.trends["UK"], "UK Commons"],
  ["US-House", D.trends["US-House"], "US House"],
  ["US-Senate", D.trends["US-Senate"], "US Senate"],
  ["CA-FED", D.trends["CA-FED"], "Canada federal"],
  ["IE", D.trends["IE"], "Ireland"],
  ["_GRP_CA_PROV", D.trends["_GRP_CA_PROV"], "CA provinces (7)"],
  ["_GRP_AUS_STATE", D.trends["_GRP_AUS_STATE"], "AUS states (5)"],
  ["_GRP_UK_DEVOLVED", D.trends["_GRP_UK_DEVOLVED"], "UK devolved (2)"],
].filter(g=>g[1] && g[1].length);
const yrsG=[]; for(let y=1985;y<=2026;y++) yrsG.push(y);
const grpSeries = GRP.map(([k,rows,lab],i)=>({name:lab,
  points:yrsG.map(y=>{const r=rows.find(r=>r.year===y); return [y, r?r.gap:null];}),
  color:CSS(SER[i%8])}));
add(h("div",{class:"card"},[
  legend(GRP.map(g=>g[2]), GRP.map((g,i)=>CSS(SER[i%8]))),
  lineChart({series:grpSeries, marks:D.marks, height:420,
             xMin:1985, xMax:2026, unit:"/100k", padRight:120}),
]));
add(details("Table: gap per 100k, eight series",
  table(["series", ...yrsG.filter(y=>y>=2006).map(String)],
    GRP.map(([k,rows,lab])=>[lab, ...yrsG.filter(y=>y>=2006).map(y=>{
      const r=rows.find(r=>r.year===y); return r?fmt(r.gap):"—";})]))));
add(h("p",{class:"note",html:"The three aggregates all climb — CA provinces ×1.24, "+
  "AUS states ×1.27, UK devolved ×1.64 — and the devolved legislatures, which start "+
  "lowest of anything on the chart, climb fastest. The two US series remain the "+
  "flattest long runs."}));

/* -- 5-year moving average of the eight aggregated series -- */
add(h("h3",{text:"Five-year moving average"}));
add(h("p",{class:"note",html:"The eight series above, smoothed with a centred five-year "+
  "mean. Smoothing is not cosmetic here: US House alone swings between 1,660 and 2,074 "+
  "across the series, a range wider than most of the differences between chambers, so "+
  "year-to-year comparison reads noise as signal. A window needs at least <b>three of "+
  "its five years</b> present, so a series with a gap thins rather than interpolating "+
  "across it, and the two-year skirts at each end are dropped rather than computed from "+
  "a half-window."}));
const MA=(pts,win)=>{const h=Math.floor(win/2);
  return pts.map((p,i)=>{
    const s=pts.slice(Math.max(0,i-h), i+h+1).filter(x=>x[1]!=null);
    if(s.length<3||i<h||i>pts.length-1-h) return [p[0],null];
    return [p[0], s.reduce((a,x)=>a+x[1],0)/s.length];});};
const smoothed = GRP.map(([k,rows,lab],i)=>({name:lab,
  points:MA(yrsG.map(y=>{const r=rows.find(r=>r.year===y); return [y, r?r.gap:null];}),5),
  color:CSS(SER[i%8])}));
add(h("div",{class:"card"},[
  legend(GRP.map(g=>g[2]), GRP.map((g,i)=>CSS(SER[i%8]))),
  lineChart({series:smoothed, marks:D.marks, height:400,
             xMin:1987, xMax:2024, unit:"/100k", padRight:120}),
]));
add(h("p",{class:"note",html:"Smoothed, the shape is a <b>convergence that narrows from "+
  "below</b>: the spread between series is wide through the 2000s and tight by the 2020s, "+
  "and it closes because the low starters climb while the two US lines stay roughly "+
  "level. The crossings visible in the raw chart are mostly US House oscillation — on a "+
  "five-year mean only the Canadian provinces sit clearly above it."}));

/* -- the same series with machine-written text removed -- */
if (D.aishare) {
add(h("h3",{text:"With machine-written text removed"}));
add(h("p",{class:"note",html:"The detector covers 2025\u201326 only, so this differs "+
  "from the chart above in those two years and is identical everywhere else. For each "+
  "chamber the 2025 and 2026 points are scaled by its own measured machine share of "+
  "<b>occurrences</b>, which is not the same as its share of words: machine-written text "+
  "carries the instrument at <b>4,231 per 100k against human text's 3,470</b>, a ratio of "+
  "1.22\u00d7, so a chamber that is 9.0% machine by words is 10.6% machine by "+
  "occurrences. Chamber shares run from 2.2% (US Senate) to 23.2% (NSW). Dashed "+
  "segments are the corrected years."}));
const yrsH=[]; for(let y=1985;y<=2026;y++) yrsH.push(y);
const adj=(ch)=>{const s=D.aishare.share_occurrences[ch]||0;
  return yrsH.map(y=>{const r=(D.trends[ch]||[]).find(r=>r.year===y);
    if(!r) return [y,null];
    return [y, (y>=2025) ? r.gap*(1-s) : r.gap];});};
const HL=[["UK","UK Commons"],["US-House","US House"],["US-Senate","US Senate"],
          ["CA-FED","Canada federal"],["IE","Ireland"]].filter(x=>D.trends[x[0]]);
add(h("div",{class:"card"},[
  legend(HL.map(x=>x[1]), HL.map((x,i)=>CSS(SER[i%8]))),
  lineChart({series:HL.map(([k,lab],i)=>({name:lab,points:adj(k),color:CSS(SER[i%8])})),
             marks:D.marks, height:380, xMin:1985, xMax:2026, unit:"/100k", padRight:120}),
]));
add(details("Table: 2025\u201326 before and after removing machine text",
  table(["chamber","machine % of words","machine % of occurrences","2026 gap","2026 human-only"],
    Object.keys(D.aishare.share_occurrences).sort().map(ch=>{
      const s=D.aishare.share_occurrences[ch];
      const r=(D.trends[ch]||[]).find(r=>r.year===2026);
      const sw=D.aishare.share_words?D.aishare.share_words[ch]:null;
      return [ch, sw!=null?(100*sw).toFixed(1)+"%":"\u2014", (100*s).toFixed(1)+"%",
              r?fmt(r.gap):"\u2014", r?fmt(r.gap*(1-s)):"\u2014"];}))));
add(h("div",{class:"warn"},[h("p",{html:"<b>The rise survives removing every "+
  "machine-written word.</b> The largest correction on the chart is NSW at 23.2% of "+
  "occurrences, and even there the 2026 human-only figure sits well above that "+
  "chamber's 2006 level. The thirty-year climb is a fact about human speech: it "+
  "began in 1994, and subtracting the machine text that exists now does not "+
  "reach back far enough to explain it."})]));
}

add(h("h3",{text:"Every chamber, same axes"}));
add(h("p",{class:"note",html:"Lines break at missing years rather than interpolating. The "+
  "states and provinces were downloaded in two five-year windows (2006–2010, 2015–2019) plus "+
  "2025–2026, so their gaps are the sampling schedule, not the record."}));
const chs=Object.keys(D.trends).filter(k=>!k.startsWith("_")).sort();
const gmin=Math.min(...chs.flatMap(c=>D.trends[c].filter(r=>r.year>=2006).map(r=>r.gap)));
const gmax=Math.max(...chs.flatMap(c=>D.trends[c].filter(r=>r.year>=2006).map(r=>r.gap)));
add(h("div",{class:"sm"}, chs.map(c=>{
  const rows=D.trends[c].filter(r=>r.year>=2006);
  const first=rows[0], last=rows[rows.length-1];
  const dl=last&&first?((last.gap-first.gap)>=0?"+":"")+fmt(last.gap-first.gap):"";
  return h("div",{class:"smc"},[h("p",{class:"smt",text:c}),
    h("p",{class:"smx",text:`${first?first.year:""}–${last?last.year:""} · Δ ${dl}`}),
    lineChart({series:[{name:c,points:pts(c,"gap")}],compact:true,width:210,height:118,
      xMin:2006,xMax:2026,yMin:gmin,yMax:gmax})]);
})));

add(details("Table: gap per 100k by chamber and year",
  table(["chamber",...yrs.map(String)],
    chs.map(c=>[c,...yrs.map(y=>{const r=D.trends[c].find(r=>r.year===y);
      return r?fmt(r.gap):"—";})]))));

add(h("h2",{text:"D. What the record actually covers"}));
add(table(["chamber","first","last","years","missing"],
  chs.map(c=>{const ys=D.trends[c].map(r=>r.year); const set=new Set(ys);
    const miss=[]; for(let y=Math.min(...ys);y<=Math.max(...ys);y++) if(!set.has(y)) miss.push(y);
    return [c,Math.min(...ys),Math.max(...ys),ys.length,
      miss.length?(miss.length>6?miss.length+" years":miss.join(", ")):"—"];})));
add(h("p",{class:"note",html:"Every gap above is a property of what was downloaded, not of the "+
  "legislature. 2023 is missing almost everywhere because the study design excluded it as a "+
  "washout year between the 2018–2022 and 2024–2026 windows."}));
</script>
"""

if __name__ == "__main__":
    main()
