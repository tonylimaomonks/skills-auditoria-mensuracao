
{FONTS}
:root{{{REP_LIGHT};--display:{DISPLAY};--fx-alta:#ef4343;--fx-media:#ff5400;--fx-baixa:#45b2ff;--y:{Y}}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{REP_DARK}}}}}
:root[data-theme="dark"]{{{REP_DARK}}}
{LOGO_CSS}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "DM Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-weight:500}}
::selection{{background:{Y}4d}}
h1,h2,h3,h4{{font-family:var(--display);font-weight:700;letter-spacing:0}}
h2{{text-transform:uppercase;font-size:28px;line-height:1;margin:0 0 6px}}
h3{{font-size:22px;line-height:1.15;margin:6px 0 10px;text-transform:uppercase}}
h4{{font-size:15px;text-transform:uppercase;letter-spacing:.04em;margin:22px 0 10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
code,pre,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
code{{background:var(--code);padding:1px 5px;border-radius:6px;font-size:.86em;word-break:break-word}}
pre{{background:var(--code);padding:12px 14px;border-radius:16px;overflow:auto;white-space:pre;font-size:12.5px;line-height:1.45;max-height:460px;margin:10px 0}}
a{{color:var(--accent);text-decoration-color:var(--link-u);text-decoration-thickness:2px;text-underline-offset:2px}}
a:focus-visible,button:focus-visible,summary:focus-visible{{outline:3px solid var(--y);outline-offset:2px}}
.layout{{display:flex;gap:32px;max-width:1320px;margin:0 auto;padding:0 24px}}
nav.toc{{position:sticky;top:0;align-self:flex-start;width:260px;flex:none;max-height:100vh;overflow:auto;padding:24px 0;font-size:14px}}
nav.toc ol{{list-style:none;padding:0;margin:0}}nav.toc li{{margin:2px 0}}nav.toc li li{{padding-left:12px;font-size:13px}}
nav.toc a{{color:var(--muted);text-decoration:none;display:block;padding:3px 8px;border-left:3px solid transparent}}
nav.toc a[aria-current="true"]{{color:var(--ink);border-left-color:var(--y);font-weight:700}}
main{{flex:1;min-width:0;padding:24px 0 80px}}
header.doc{{background:{ESCURO};border-radius:36px;padding:36px 44px;color:#fff;margin-bottom:24px;--ink:#fff;--muted:#bfbfbf;{LG_CAB};--lg-mk:#fff;--lg-rule:#515252}}
.doc-brand{{display:flex;flex-wrap:wrap;align-items:center;gap:20px;margin-bottom:26px}}
.doc-brand .lg-sf{{height:40px;width:auto}}.doc-brand .lg-mk{{height:15px;width:auto}}.doc-brand .lg-rule{{height:32px;align-self:center}}
header.doc .kick{{font-family:var(--display);text-transform:uppercase;letter-spacing:.08em;color:{Y};font-size:15px}}
header.doc h1{{text-transform:uppercase;font-size:48px;line-height:.9;margin:10px 0 0}}
header.doc h1 .hl{{color:{Y}}}
header.doc .smile{{display:block;width:150px;height:auto;margin:12px 0 4px}}
.metagrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px 24px;margin-top:16px;font-size:14px;color:#bfbfbf}}
.metagrid b{{color:#fff}}
.conf{{margin-top:16px;font-size:13px;padding:8px 14px;border-radius:16px;background:#3d1214;color:#f68e8e;display:inline-block}}
section.sec{{background:var(--paper);border-radius:24px;padding:28px 32px;margin-bottom:24px}}
.sub{{color:var(--muted);margin:0 0 18px;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:16px 0}}
.kpi{{border-radius:24px;background:var(--bg);padding:18px 20px}}
.kpi:first-child{{background:var(--y);color:{ON};--muted:{ON_M}}}
.kpi .v{{font-family:var(--display);font-size:34px;line-height:1}}.kpi .l{{font-size:13px;color:var(--muted);margin-top:6px}}
.how{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:14px 0 0;padding:0;list-style:none}}
.how li{{background:var(--bg);border-radius:16px;padding:14px 16px;font-size:14px}}
.how b{{font-family:var(--display);display:block;text-transform:uppercase;font-size:14px;margin-bottom:4px}}
.chain{{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:16px 0 4px;font-size:14px}}
.chain span{{background:var(--bg);border-radius:9999px;padding:4px 14px;font-weight:700}}.chain i{{font-style:normal;color:var(--muted)}}
.tw{{overflow-x:auto;margin:10px 0}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{border-bottom:1px solid var(--rule);padding:8px 9px;text-align:left;vertical-align:top}}
thead th{{font-size:12px;text-transform:uppercase;letter-spacing:.03em;border-bottom:2px solid var(--ink)}}
td .sm{{display:block;font-size:12px;color:var(--muted)}}
.crit{{display:inline-block;font-family:var(--display);font-size:13px;color:#000;border-radius:9999px;padding:3px 11px;white-space:nowrap}}
.crit.alta{{background:var(--fx-alta)}}.crit.media{{background:var(--fx-media)}}.crit.baixa{{background:var(--fx-baixa)}}
.st{{display:inline-block;font-size:12.5px;font-weight:700;border-radius:9999px;padding:3px 11px;white-space:nowrap}}
.st-ok{{background:var(--ok-soft);color:var(--ok)}}.st-pub{{background:var(--accent-soft);color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--y)}}
.st-dec,.st-parc{{background:var(--crit-media-bg);color:var(--crit-media)}}.st-pend{{background:var(--s1);color:var(--muted);box-shadow:inset 0 0 0 1px var(--rule)}}
article.card{{border-radius:24px;background:var(--bg);box-shadow:inset 8px 0 0 var(--fx-baixa);padding:22px 26px 22px 34px;margin:0 0 18px;scroll-margin-top:16px}}
article.card[data-crit="alta"]{{box-shadow:inset 8px 0 0 var(--fx-alta)}}article.card[data-crit="media"]{{box-shadow:inset 8px 0 0 var(--fx-media)}}
.card-h{{display:flex;flex-wrap:wrap;align-items:center;gap:8px}}
.cid{{font-family:var(--display);font-size:17px}}.ach{{font-family:ui-monospace,Menlo,monospace;font-size:13px;color:var(--muted)}}
.dtc{{margin-left:auto;font-size:13px;color:var(--muted)}}
.resumo{{font-weight:700;margin:0 0 12px}}
dl.abn{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0}}
dl.abn div{{background:var(--paper);border-radius:16px;padding:12px 14px}}
dl.abn div:last-child{{box-shadow:inset 0 5px 0 var(--y)}}
dl.abn dt{{font-family:var(--display);text-transform:uppercase;font-size:13px;margin-bottom:4px}}
dl.abn dd{{margin:0;font-size:14px;line-height:1.5}}
.met,.prox{{font-size:14px;margin:12px 0 0}}.met b,.prox b{{font-weight:700}}
.cnt{{font-family:var(--display);background:var(--ink);color:var(--bg);border-radius:9999px;padding:1px 9px;font-size:12px}}
.hint{{font-family:"DM Sans",system-ui,sans-serif;text-transform:none;letter-spacing:0;font-weight:500;font-size:12.5px;color:var(--muted)}}
ul.gal{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}}
ul.gal li{{display:flex;flex-direction:column;gap:6px;min-width:0}}
button.th{{position:relative;display:block;width:100%;aspect-ratio:16/10;padding:0;border:0;border-radius:16px;overflow:hidden;cursor:zoom-in;background:var(--paper);box-shadow:0 0 0 1px var(--line);transition:transform .18s ease,box-shadow .18s ease}}
button.th img{{width:100%;height:100%;object-fit:cover;object-position:top left;display:block;transition:transform .25s ease}}
button.th:hover,button.th:focus-visible{{transform:scale(1.04);box-shadow:0 0 0 3px var(--y),0 12px 28px rgba(0,0,0,.22);z-index:2}}
button.th:hover img{{transform:scale(1.06)}}
.th-z{{position:absolute;right:8px;bottom:8px;background:{ON};color:{Y};border-radius:9999px;width:28px;height:28px;display:grid;place-items:center;font-size:15px;opacity:.85}}
.th-c{{font-size:13px;line-height:1.35}}.th-c b{{font-size:11.5px;color:var(--muted);display:block}}
.th-p{{display:block;color:var(--muted);font-size:12.5px;margin-top:2px}}
details.dado{{background:var(--paper);border-radius:16px;margin:8px 0;scroll-margin-top:16px}}
details.dado summary{{cursor:pointer;padding:11px 14px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;list-style:none}}
details.dado summary::-webkit-details-marker{{display:none}}
details.dado summary::before{{content:"+";font-family:var(--display);width:16px}}details.dado[open] summary::before{{content:"−"}}
details.dado summary b{{font-size:12px;color:var(--muted)}}.dt-t{{flex:1;min-width:200px;font-weight:700}}
.tag{{font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;background:var(--bg);border-radius:9999px;padding:1px 9px;color:var(--muted)}}
.dado-b{{padding:0 16px 12px 40px;font-size:14px}}.dado-b p{{margin:6px 0}}
.num{{font-family:var(--display);font-size:16px}}.prova b{{font-weight:700}}.src{{font-size:12.5px;color:var(--muted)}}
.ret{{margin-top:16px;background:var(--paper);border-radius:16px;padding:12px 14px;display:grid;grid-template-columns:auto 1fr;gap:4px 14px;font-size:14px;box-shadow:inset 0 0 0 1.5px var(--y)}}
.ret b{{grid-row:span 2;font-family:var(--display);text-transform:uppercase;font-size:13px;max-width:170px}}.ret i{{color:var(--muted)}}
.rodada{{margin-top:22px;border-top:2px dashed var(--rule);padding-top:4px}}
.rod-t{{margin:14px 0 0;font-size:14px;color:var(--muted)}}.rod-t b{{font-family:var(--display);text-transform:uppercase;background:var(--y);color:{ON};border-radius:9999px;padding:2px 12px;margin-right:6px}}
.aviso{{background:var(--bg);border-radius:24px;padding:20px 24px;box-shadow:inset 8px 0 0 var(--muted)}}.aviso ul{{margin:8px 0 0;padding-left:20px;font-size:14.5px}}.aviso li{{margin:4px 0}}
.vazio{{background:var(--paper);border-radius:16px;padding:12px 14px;font-size:14px;color:var(--muted);margin-top:14px}}
.brandfoot{{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin-top:20px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}}
.brandfoot .lg-sf{{height:28px;width:auto}}.brandfoot .lg-mk{{height:11px;width:auto}}.brandfoot .lg-rule{{height:22px;align-self:center}}
.brandfoot span.f{{margin-left:auto}}
.themebtn{{position:fixed;right:16px;bottom:16px;z-index:5;border:0;border-radius:9999px;background:var(--ink);color:var(--bg);font:inherit;font-size:13px;padding:7px 14px;cursor:pointer}}

/* galeria (lightbox) */
dialog.lb{{width:100vw;height:100vh;max-width:none;max-height:none;margin:0;padding:0;border:0;background:rgba(8,8,8,.97);color:#fff}}
body:has(dialog[open]){{overflow:hidden}}
dialog.lb::backdrop{{background:rgba(0,0,0,.7)}}
.lb-w{{display:grid;grid-template-rows:auto 1fr auto;height:100%}}
.lb-top{{display:flex;align-items:center;gap:14px;padding:12px 18px;font-size:14px}}
.lb-top .lb-ev{{font-family:var(--display);color:{Y};font-size:16px}}.lb-top .lb-n{{color:#bfbfbf}}
.lb-top .lb-x{{margin-left:auto}}
.lb-b{{background:#232424;color:#fff;border:0;border-radius:9999px;width:44px;height:44px;font-size:20px;cursor:pointer;display:grid;place-items:center;font-family:var(--display)}}
.lb-b:hover{{background:{Y};color:{ON}}}.lb-b:disabled{{opacity:.3;cursor:default;background:#232424;color:#fff}}
.lb-stage{{position:relative;display:flex;align-items:center;justify-content:center;min-height:0;padding:0 72px;touch-action:pan-y}}
.lb-stage img{{max-width:100%;max-height:100%;object-fit:contain;border-radius:12px;background:#fff;box-shadow:0 20px 60px rgba(0,0,0,.5);cursor:zoom-in}}
.lb-stage img.z{{max-width:none;max-height:none;cursor:zoom-out}}
.lb-stage.zoom{{overflow:auto;display:block;padding:0 72px}}
.lb-prev,.lb-next{{position:absolute;top:50%;transform:translateY(-50%);z-index:2}}.lb-prev{{left:16px}}.lb-next{{right:16px}}
.lb-cap{{padding:14px 24px 18px;max-width:1100px;margin:0 auto;width:100%;font-size:14.5px;line-height:1.5}}
.lb-cap h5{{font-family:var(--display);text-transform:uppercase;font-size:18px;margin:0 0 4px}}
.lb-cap p{{margin:3px 0;color:#dbdbdb}}.lb-cap .pv b{{color:{Y}}}.lb-cap .sr{{color:#a3a3a3;font-size:12.5px}}
.lb-dots{{display:flex;gap:6px;justify-content:center;padding-bottom:6px}}
.lb-dots button{{width:9px;height:9px;border-radius:9999px;border:0;background:#515252;padding:0;cursor:pointer}}.lb-dots button[aria-current="true"]{{background:{Y};width:22px}}

@media (max-width:980px){{nav.toc{{display:none}}dl.abn{{grid-template-columns:1fr}}}}
@media (max-width:640px){{.layout{{padding:0 12px}}header.doc{{border-radius:24px;padding:24px}}header.doc h1{{font-size:32px}}section.sec{{padding:20px 16px}}article.card{{padding:18px 16px 18px 24px}}.lb-stage{{padding:0 8px}}.lb-prev,.lb-next{{top:auto;bottom:-52px}}.lb-cap{{padding-top:60px}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;scroll-behavior:auto!important}}}}
@media print{{
:root:root:root{{{REP_LIGHT}}}
nav.toc,.themebtn,dialog.lb,.th-z,.hint{{display:none!important}}
body{{background:#fff}}header.doc{{background:#fff;color:#000;border:1px solid #bbb;{LG_PRINT};--lg-mk:#2d2d2d}}.metagrid,.metagrid b{{color:#000}}
section.sec{{padding:0}}article.card{{break-inside:avoid;border:1px solid #bbb}}details.dado .dado-b{{display:block}}
button.th{{aspect-ratio:auto}}button.th img{{height:auto;object-fit:contain}}
}}
