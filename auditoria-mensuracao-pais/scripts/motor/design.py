"""Gera cópias *-design.html das entregas com a identidade do cliente + assinatura Monks.

Os originais não são alterados: o script lê cada HTML, injeta um <style id="sf-design"> depois do
CSS original (fontes em base64, tokens, componentes) e acrescenta logos SVG inline.
Texto, números e estrutura de achados ficam iguais; só entram spans/elementos decorativos.

Nasceu do aplicar_design.py da Smart Fit BR (design aprovado em 14/10/2026). Tudo o que é da marca do cliente vem
do manifesto <cliente>/design-system/<marca>/marca.json (pasta em MARCA_DIR, definida por cliente.py); a Monks vem
de assets/monks/ da própria skill. Esquema do manifesto em references/identidade-cliente.md.
(Os nomes internos sf-design, lg-sf e sf-brand e os comentários CSS ficaram da Smart Fit e valem para qualquer cliente;
não mude os comentários: eles vão para o HTML e quebram a comparação byte a byte com o BR.)
"""
import os
import base64
import json
import re
from pathlib import Path

MARCA = Path(os.environ["MARCA_DIR"])  # <cliente>/design-system/<marca>
MK = Path(__file__).resolve().parents[2] / "assets/monks"
M = json.loads((MARCA / "marca.json").read_text(encoding="utf-8"))
NOME = M["nome"]
COR = M["cores"]
Y, Y2, ON, ON_M, ESCURO = COR["destaque"], COR["destaque_2"], COR["sobre_destaque"], COR["sobre_destaque_suave"], COR["fundo_escuro"]
TK = M["tokens"]


def b64(p):
    return base64.b64encode(p.read_bytes()).decode()


def paths(svg_file):
    return re.findall(r'\sd="([^"]+)"', svg_file.read_text())


def lg_vars(modo, sep=";"):
    """Cores das partes do logo do cliente num modo (claro, escuro, impressao), no formato --var:cor."""
    return sep.join(f"--{k}:{v}" for k, v in M["logo"]["cores"][modo].items())


# --- Fontes -------------------------------------------------------------------
def _face(f):
    ur = f";unicode-range:{f['unicode_range']}" if f.get("unicode_range") else ""
    return (f'@font-face{{font-family:"{f["familia"]}";src:url(data:font/woff2;base64,{b64(MARCA / f["arquivo"])}) '
            f'format("woff2");font-weight:{f["peso"]};font-style:{f.get("estilo", "normal")};font-display:block{ur}}}')


FONTS = "\n" + "\n".join(_face(f) for f in M["fontes"]) + "\n"
DISPLAY = M["fonte_display"] + ",Arial,sans-serif"
SANS = M["fonte_texto"] + ',system-ui,-apple-system,"Segoe UI",Roboto,sans-serif'
SANS_REL = M["fonte_texto"] + ',system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif'

# --- Logos (cores por classe, controladas por --lg-*) ---------------------------
# Cada parte do logo do cliente é um <path> cuja cor vem de uma custom property (marca.json → logo.partes),
# para trocar as cores conforme o fundo. A Monks é sempre o .monks mono (--lg-mk).
_lg = M["logo"]
_cl = paths(MARCA / _lg["arquivo"])
_mk = paths(MK / "logos/dot-monks-logo.preto.svg")
# Definidos uma vez (<symbol>) e reutilizados com <use>; as cores entram por herança de custom properties.
SYMBOLS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
           f'<symbol id="lg-sf" viewBox="{_lg["viewbox"]}">'
           + "".join(f'<path style="fill:var(--{p["var"]})" d="{_cl[p["path"]]}"/>' for p in _lg["partes"])
           + '</symbol>'
           '<symbol id="lg-mk" viewBox="0 0 99 21">'
           + "".join(f'<path style="fill:var(--lg-mk)" d="{d}"/>' for d in _mk) + "</symbol></svg>")
LOGO_SF = f'<svg class="lg-sf" viewBox="{_lg["viewbox"]}" role="img" aria-label="{NOME}"><use href="#lg-sf"/></svg>'
LOGO_MK = '<svg class="lg-mk" viewBox="0 0 99 21" role="img" aria-label="Monks"><use href="#lg-mk"/></svg>'
_orn = M.get("ornamento")
SMILE = (f'<svg class="smile" viewBox="{_orn["viewbox"]}" aria-hidden="true">'
         f'<path d="{paths(MARCA / _orn["arquivo"])[_orn.get("path", 0)]}"/></svg>') if _orn else ""
BRAND = f'{LOGO_SF}<span class="lg-rule" aria-hidden="true"></span>{LOGO_MK}'
FAVICON = MARCA / M["favicon"]

LOGO_CSS = f"""
.lg-rule{{display:inline-block;width:1px;align-self:stretch;background:var(--lg-rule)}}
.smile path{{fill:{Y}}}
"""

# --- Paleta comum ---------------------------------------------------------------
# Criticidade: sólido (chip, texto preto) Alta #EF4343 5,55:1 · Média #FF5400 6,52:1 · Baixa #45B2FF 9,07:1.
# Claro: Alta #A50F17 sobre #FDE3E3 6,44:1 (o #F68E8E sugerido dá só 3,42:1) · Média #A12F0B/#FFECD3 6,22:1 ·
# Baixa #084072/#B8DFFF 7,57:1. Escuro: #F68E8E 8,5:1 · #FF8A4D 8,3:1 · #8CCBFF 11,2:1 sobre #0C0D0D.

# =================================================================================
# DECK
# =================================================================================
DECK_TOKENS_LIGHT = TK["deck_claro"]
DECK_TOKENS_DARK = TK["deck_escuro"]

DECK_CSS = f"""
{FONTS}
:root{{{DECK_TOKENS_LIGHT}
  --display:{DISPLAY};
  --sans:{SANS};
}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{DECK_TOKENS_DARK}}}}}
:root[data-theme="dark"]{{{DECK_TOKENS_DARK}}}
{LOGO_CSS}
body{{font-weight:500}}
::selection{{background:{Y}4d}}

/* títulos: Muscle Display, caixa alta, entrelinha apertada, última palavra com marca-texto amarelo */
h2{{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:50px;line-height:.98;letter-spacing:0}}
.apx h2{{font-size:42px}}
h2 .hl{{background:linear-gradient(transparent 46%,var(--y) 46%,var(--y) 84%,transparent 84%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 .06em}}
:root[data-theme="dark"] h2 .hl{{background:none;color:var(--y);padding:0}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) h2 .hl{{background:none;color:var(--y);padding:0}}}}
.kicker{{font-family:var(--display);font-size:20px;color:var(--ink);letter-spacing:.06em;font-weight:700}}
.kicker::before{{content:"";flex:0 0 44px;height:12px;border-radius:9999px;background:var(--y)}}
.apx-tag{{border-radius:9999px;padding:4px 14px;font-size:16px}}
.lead{{font-weight:700}}
.qb h3,.panel-t,.rcol h3,.dod h3,.rub-side h3{{font-family:var(--display);font-weight:700}}
.sf .pg{{font-family:var(--display);font-weight:700;font-size:20px}}
.sf>span:first-child{{white-space:normal;font-size:15px;line-height:1.25;display:block;max-height:57px;overflow:hidden}}
.sf-brand{{display:flex;align-items:center;gap:14px;flex:0 0 auto;margin-left:auto}}
.sf-brand .lg-sf{{height:24px;width:auto}}.sf-brand .lg-mk{{height:12px;width:auto}}.sf-brand .lg-rule{{height:22px;align-self:center}}

/* chips de criticidade: pílula sólida, texto preto, rótulo sempre presente */
.chip{{border:0;border-radius:9999px;color:#000!important;font-family:var(--display);font-weight:700;letter-spacing:.05em;padding:5px 14px}}
.c-alta{{background:var(--f-alta)}}.c-media{{background:var(--f-media)}}.c-baixa{{background:var(--f-baixa)}}
.st,.lbl{{border-radius:9999px}}

/* cards: chapados, raio 24 */
.quote,.steps li,.kpi,.dec,.panel,.qb,.declist li{{border:0;border-radius:24px;background:var(--card)}}
.inv div,.rc,.hop,.callout,.anpd{{border:0;border-radius:16px}}
.inv div{{background:var(--card)}}
.quote{{box-shadow:inset 10px 0 0 var(--y)}}
.qn{{font-family:var(--display);font-weight:700;font-size:26px;color:var(--ink)}}
.steps li::before{{font-family:var(--display);background:var(--bg);color:var(--ink)}}
.steps li.on{{border:0;background:var(--y);--ink:{ON};--muted:{ON_M};color:{ON}}}
.steps li.on::before{{background:{ON};color:var(--y)}}
.drow{{border:0;border-radius:24px}}
.dprazo b{{background:var(--y,{Y});color:{ON};border-radius:9999px;font-family:var(--display)}}
.drow b{{font-family:var(--display);font-weight:700}}
.steps b,.dec b,.declist b{{font-family:var(--display);font-weight:700}}
.kpi b,.kpi.big b,.inv b{{font-family:var(--display);font-weight:700;letter-spacing:0;color:var(--ink)}}
.kpi.big{{border-top:0;box-shadow:inset 0 10px 0 var(--y)}}
.kpi.big.crit-a{{box-shadow:inset 0 10px 0 var(--f-alta)}}
.bluf-fix{{background:var(--y);border-radius:24px;--ink:{ON};--muted:{ON_M};--card:#fff;color:{ON}}}
.bluf-fix>b{{font-family:var(--display);font-weight:700;color:{ON}}}
.bluf-fix .mono{{color:{ON}}}
.dod{{border-radius:24px}}
.dn{{background:var(--y);color:{ON};font-family:var(--display)}}
.qb{{box-shadow:inset 8px 0 0 var(--y);border-left:0}}
.qb-m{{box-shadow:inset 8px 0 0 var(--f-alta)}}.qb-f{{box-shadow:inset 8px 0 0 var(--f-ok)}}
.hop{{border-left:0;box-shadow:inset 8px 0 0 var(--line);background:var(--card)}}.hop.bad{{box-shadow:inset 8px 0 0 var(--f-alta)}}
.callout{{border-left:0;box-shadow:inset 8px 0 0 var(--f-media)}}
.rcol{{border-radius:24px;background:var(--card)}}
.rcol-now h3{{color:var(--alta)}}
.rc{{background:var(--bg)}}
.gloss dt{{font-family:var(--display);font-weight:700;color:var(--ink)}}
.ph{{border-radius:4px}}

/* tabelas no padrão da comparativa de /planos */
.tbl th{{font-family:var(--display);font-weight:700;color:var(--ink);letter-spacing:.04em}}
.tbl td{{border-bottom-color:var(--rule)}}
.meta dt{{font-family:var(--display);font-weight:700}}

/* gráficos: total = preto, série neutra = grafite, perda/risco = vermelho Alta, destaque/base verificável = amarelo de marca.
   Azul fica reservado à criticidade Baixa. */
.chart text{{font-family:var(--sans)}}
.chart .v,.chart .marco-t{{font-family:var(--display);font-weight:700}}
.chart .ref{{fill:var(--muted)}}
.bar-total{{fill:var(--bar-total)}}
.bar-final{{fill:var(--y);stroke:var(--bar-stroke);stroke-width:2}}
.bar-neg,.bar-hi,.seg-hi{{fill:var(--f-alta)}}
.bar-lo{{fill:var(--bar-neutral)}}
.seg-mid{{fill:var(--f-media);opacity:1}}
.seg-lo{{fill:var(--bar-neutral);opacity:.55}}
.chart .seg-pct{{fill:#000}}
.s-ok{{background:var(--f-ok)}}.s-md{{background:var(--f-media)}}.s-al{{background:var(--f-alta)}}.s-al2{{background:#a50f17}}.s-lo{{background:var(--bar-neutral)}}
.sg b{{color:#000;font-family:var(--display)}}.s-al2 b,.s-lo b{{color:#fff}}
.sw{{border-radius:9999px}}

/* capa: hero preto com amarelo */
.slide.dark{{{lg_vars("escuro")};--lg-mk:#ffffff;--lg-rule:#515252}}
.capa-wrap{{background:none;position:relative;padding:72px 110px 64px}}
.capa-wrap::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:12px;background:linear-gradient(90deg,{Y} 0%,{Y2} 100%)}}
.capa-brand{{display:flex;align-items:center;gap:22px;margin-bottom:22px}}
.capa-brand .lg-sf{{height:46px;width:auto}}.capa-brand .lg-mk{{height:16px;width:auto}}.capa-brand .lg-rule{{height:38px;align-self:center}}
.capa-top{{font-family:var(--sans);font-weight:500;font-size:16px;letter-spacing:.1em}}
.capa-kicker{{color:var(--y);font-family:var(--display);font-weight:700;font-size:18px;letter-spacing:.14em;margin-bottom:26px}}
.capa-h{{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:84px;line-height:.9;letter-spacing:0;max-width:1180px;color:#fff}}
.capa-h .hl{{color:var(--y)}}
.capa .smile{{display:block;width:220px;height:auto;margin:20px 0 0 580px}}
.capa-mid{{flex:1 1 auto;display:flex;flex-direction:column;min-height:0}}
.capa-h{{margin-top:auto}}
.capa-sub{{margin-top:44px;font-size:22px}}
.capa-meta{{border-top-color:#3a3b3b;margin-top:auto;margin-bottom:44px;padding-top:22px;gap:56px}}
.capa-meta dt{{font-family:var(--display);font-weight:700;font-size:14px}}
.capa-meta dd{{font-size:18px;color:var(--capa-muted)}}
.capa-bot{{font-size:14px;color:#8a8a8a}}
.capa-print{{font-family:var(--sans);font-size:13px}}

.notes{{background:rgba(12,13,13,.96);border-radius:24px}}
.notes b{{color:var(--y);font-family:var(--display)}}
#bar{{background:var(--y)}}

@media print{{
  :root:root:root:root{{{DECK_TOKENS_LIGHT} --stage:#ffffff}}
  h2 .hl{{background:linear-gradient(transparent 46%,{Y} 46%,{Y} 84%,transparent 84%)!important;color:inherit!important;padding:0 .06em!important}}
}}
"""


# Edições de conteúdo da capa, aprovadas em 13/10/2026 no BR (só na cópia -design):
# rótulo repetia o título; instruções de navegação vão para as notas; escopo detalhado já está no slide de cobertura.
def editar_capa(s, escopo):
    s, n1 = re.subn(r'\s*<p class="capa-kicker">.*?</p>', "", s, count=1)
    m = re.search(r'\s*<span class="capa-print">(.*?)</span>', s)
    n2 = 0
    if m:
        s = s.replace(m.group(0), "", 1)
        i = s.index('<aside class="notes">')  # notas do slide 1
        j = s.index("</aside>", i)
        s = s[:j] + f"<p>{m.group(1)} · F tela cheia</p>" + s[j:]
        n2 = 1
    s, n3 = re.subn(r'(<div><dt>Escopo</dt><dd>).*?(</dd></div>)', lambda m: m.group(1) + escopo + m.group(2), s, count=1)
    assert (n1, n2, n3) == (1, 1, 1), (n1, n2, n3)
    return s


# Atalho F: alterna tela cheia (Esc também sai). O motor original já reescala o deck no resize.
FULLSCREEN_JS = """<script>
document.addEventListener('keydown',function(e){
  if(e.metaKey||e.ctrlKey||e.altKey||(e.key!=='f'&&e.key!=='F')) return;
  var d=document, el=d.documentElement;
  var on=d.fullscreenElement||d.webkitFullscreenElement;
  e.preventDefault();
  if(on){(d.exitFullscreen||d.webkitExitFullscreen).call(d);}
  else{(el.requestFullscreen||el.webkitRequestFullscreen).call(el);}
});
</script>"""


def deck(origem, destino, escopo_curto):
    src = editar_capa(Path(origem).read_text(), escopo_curto)
    s = src.replace("</style>", "</style>\n<style id=\"sf-design\">" + DECK_CSS + "</style>", 1)

    # última palavra do título de cada slide (h2 sem classe) com marca-texto
    def hl(m):
        inner = m.group(1)
        mm = re.search(r"(\s)([^\s<>]+)$", inner)
        if not mm:
            return m.group(0)
        return f"<h2>{inner[:mm.start()]}{mm.group(1)}<span class=\"hl\">{mm.group(2)}</span></h2>"
    s = re.sub(r"<h2>(.*?)</h2>", hl, s)

    # capa
    s = s.replace('<div class="capa-top">', f'<div class="capa-top"><div class="capa-brand">{BRAND}</div>', 1)
    s = re.sub(r'(<h1 class="capa-h">.*?)(\S+)</h1>', lambda m: f'{m.group(1)}<span class="hl">{m.group(2)}</span></h1>{SMILE}', s, count=1)
    # rodapé de cada slide: logo do cliente | .monks ao lado da paginação
    s = s.replace('<span class="pg">', f'<span class="sf-brand" aria-hidden="true">{BRAND}</span><span class="pg">')
    s = s.replace('<link rel="icon" href="data:,">',
                  '<link rel="icon" href="data:image/svg+xml;base64,' + b64(FAVICON) + '">', 1)
    s = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + SYMBOLS, s, count=1)
    s = s.replace("</body>", FULLSCREEN_JS + "</body>", 1)
    Path(destino).write_text(s)
    return src, s


# =================================================================================
# RELATÓRIO
# =================================================================================
REP_LIGHT = TK["rel_claro"]
REP_DARK = TK["rel_escuro"]
REP_HEADER_VARS = TK["rel_cabecalho"]

REP_CSS = f"""
{FONTS}
:root{{{REP_LIGHT};--display:{DISPLAY};--fx-alta:#ef4343;--fx-media:#ff5400;--fx-baixa:#45b2ff}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{REP_DARK}}}}}
:root[data-theme="dark"]{{{REP_DARK}}}
{LOGO_CSS}
body{{font-family:{SANS_REL};line-height:1.6}}
::selection{{background:{Y}4d}}
h1,h2,h3,h4,h5{{font-family:var(--display);font-weight:700;letter-spacing:0}}
h2{{text-transform:uppercase;font-size:28px;line-height:1}}
h3{{line-height:1.2}}
a{{color:var(--accent);text-decoration-color:var(--link-u);text-decoration-thickness:2px;text-underline-offset:2px}}
.layout{{max-width:1280px}}
nav.toc a[aria-current="true"]{{border-left-color:{Y};border-left-width:3px}}

header.doc{{background:{ESCURO};border:0;border-radius:36px;padding:36px 44px;color:#fff;{REP_HEADER_VARS}}}
.doc-brand{{display:flex;flex-wrap:wrap;align-items:center;gap:20px;margin-bottom:26px}}
.doc-brand .lg-sf{{height:40px;width:auto}}.doc-brand .lg-mk{{height:15px;width:auto}}.doc-brand .lg-rule{{height:32px;align-self:center}}
header.doc h1{{text-transform:uppercase;font-size:48px;line-height:.88;margin:10px 0 0}}
header.doc h1 .hl{{color:{Y}}}
header.doc .smile{{display:block;width:150px;height:auto;margin:12px 0 4px}}
.conf{{border-radius:16px}}

section.sec{{border:0;border-radius:24px}}
.kpi{{border:0;border-radius:24px;background:var(--bg);padding:18px 20px}}
.kpi .v{{font-family:var(--display);font-size:32px}}
#s1 .kpi:first-child{{background:{Y};--ink:{ON};--muted:{ON_M};--accent:{ON};--link-u:{ON};color:{ON}}}
thead th{{background:transparent;color:var(--ink);font-weight:700;border-bottom:2px solid var(--ink)}}
th,td{{border-bottom-color:var(--rule)}}
.crit{{font-family:var(--display);font-size:13px;color:#000!important;border-radius:9999px;padding:3px 11px}}
.crit.alta{{background:var(--fx-alta)}}.crit.media{{background:var(--fx-media)}}.crit.baixa{{background:var(--fx-baixa)}}
.chip,.btn,.eid{{border-radius:9999px}}
.chip[aria-pressed="true"]{{background:{Y};border-color:{Y};color:{ON};font-weight:700}}
article.card{{border:0;border-radius:24px;background:var(--bg);box-shadow:inset 8px 0 0 var(--fx-baixa);padding:22px 26px 22px 34px}}
article.card[data-crit="alta"]{{box-shadow:inset 8px 0 0 var(--fx-alta)}}article.card[data-crit="media"]{{box-shadow:inset 8px 0 0 var(--fx-media)}}
.cid{{font-family:var(--display);font-size:15px}}
dl.anat dt{{font-family:var(--display);color:var(--ink)}}
.imp,dd.done,.note,pre,.cov div,.tf{{border-radius:16px}}
.cov div,.hz{{border:0}}.hz{{border-radius:24px}}
.tf{{border:0}}
.chart .b-b{{fill:var(--chart-main)}}.chart .b-a{{fill:var(--fx-alta)}}.chart .vl{{font-family:var(--display)}}
.spark{{color:var(--chart-main)}}
figure.shot img{{border-radius:16px}}
.brandfoot{{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin-top:20px;padding-top:18px;border-top:1px solid var(--line)}}
.brandfoot .lg-sf{{height:28px;width:auto}}.brandfoot .lg-mk{{height:11px;width:auto}}.brandfoot .lg-rule{{height:22px;align-self:center}}
@media (max-width:900px){{header.doc{{border-radius:24px}}header.doc h1{{font-size:34px}}}}
@media print{{
:root:root:root{{{REP_LIGHT}}}
header.doc{{background:#fff;color:#000;border:1px solid #bbb;--ink:#000;--muted:#515252;--crit-alta:#a50f17;--crit-alta-bg:#fde3e3;{lg_vars("impressao")};--lg-mk:#2d2d2d;--lg-rule:#bfbfbf}}
header.doc h1 .hl{{color:inherit;background:linear-gradient(transparent 60%,{Y} 60%,{Y} 94%,transparent 94%)}}
article.card{{border:1px solid #bbb}}
}}
"""


def relatorio(origem, destino):
    src = Path(origem).read_text()
    s = src.replace("</style>", "</style>\n<style id=\"sf-design\">" + REP_CSS + "</style>", 1)
    s = s.replace('<header class="doc">', f'<header class="doc"><div class="doc-brand">{BRAND}</div>', 1)
    s = re.sub(r'(<header class="doc">.*?<h1>.*?)(\S+)</h1>',
               lambda m: f'{m.group(1)}<span class="hl">{m.group(2)}</span></h1>{SMILE}', s, count=1, flags=re.S)
    i = s.rfind("</main>")
    s = s[:i] + f'<footer class="brandfoot" aria-label="{NOME} e Monks">{BRAND}</footer>' + s[i:]
    s = s.replace("<title>", '<link rel="icon" href="data:image/svg+xml;base64,'
                  + b64(FAVICON) + '">\n<title>', 1)
    s = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + SYMBOLS, s, count=1)
    Path(destino).write_text(s)
    return src, s


def texto(html):
    """Texto visível normalizado, para provar que o conteúdo não mudou."""
    html = re.sub(r"<style.*?</style>|<script.*?</script>|<svg.*?</svg>", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()
