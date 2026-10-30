"""Relatório de evidências da execução (HTML standalone, galeria por ação, IDs EV-Axxx-nn estáveis).

Portado de brasil/entregas/_fonte/build_relatorio_evidencias.py (aprovado e enviado na v1.7, 27/10/2026).
O que era fixo do BR veio para o conteúdo: META, EVIDENCIAS.rodadas/fora/mascara/como_ler/avisos.

Numeração EV por ação: rodada a rodada na ordem em que aparecem no catálogo (a original, sem rodada, primeiro);
dentro de cada rodada, prints antes de dados. Rodada nova entra no fim e não renumera o que já foi enviado.
"""
import base64
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

from comum import SKILL, ev_id

IMG_EXT = {".png", ".jpg", ".jpeg"}
CRIT = {"ALTA": ("alta", "Alta"), "MÉDIA": ("media", "Média"), "BAIXA": ("baixa", "Baixa")}
COMO_LER_PADRAO = [
    ["ID estável", "Cada evidência tem um código EV-Axxx-nn, o mesmo citado na apresentação. O link direto `#EV-Axxx-nn` abre o print."],
    ["Prints", "Miniaturas por ação. Clique para ampliar; ← → passa só entre os prints daquela ação; clique na imagem para ver em tamanho real; Esc fecha."],
    ["Dados", "Consultas de API, exports do GTM e diffs ficam em blocos que abrem com um clique, com o trecho que prova o ponto."],
    ["Fato e leitura", "A legenda descreve só o que se vê. \"O que prova\" liga ao critério da ação. O impacto no negócio fica no bloco da ação, separado do fato."],
    ["Cadeia de custódia", "Cada evidência traz fonte, data, quem coletou (Monks), o nome do arquivo original e os 12 primeiros caracteres do SHA-256. O original fica guardado pela Monks."],
    ["Dados sensíveis", "Testes feitos com dados fictícios. Tokens de API, e-mails e IDs reais não aparecem: citamos só a existência ou mascaramos."],
]


def t(s):
    """Escapa e marca termos técnicos curtos entre crases como <code>."""
    s = html.escape(str(s or ""), quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def t_rico(s):
    """t() + **negrito** (só nos avisos)."""
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t(s))


def gerar(root, C, CAT, D):
    """Devolve (doc, ref_deck, resumo, ev_mapa). ref_deck: ação → faixa EV (o deck cita); ev_mapa: EV → arquivo."""
    META = C["META"]
    E = C["EVIDENCIAS"]
    FONTE = root / "entregas/_fonte"
    CACHE = FONTE / "prints_evidencias"
    RET = {r["id"]: r for r in C["RETESTE"]}
    FORA = E.get("fora", {})
    MASCARA = {k: [tuple(r) for r in v] for k, v in E.get("mascara", {}).items()}
    RODADAS = E.get("rodadas", {})
    REL = META.get("rel_tecnico", "relatório técnico")

    def jpg(src, lado, q):
        """Converte/redimensiona com sips (macOS) e devolve data URI; cache por hash do arquivo + parâmetros."""
        CACHE.mkdir(exist_ok=True)
        h = hashlib.sha1(src.read_bytes() + f"{lado}/{q}".encode()).hexdigest()[:16]
        out = CACHE / f"{h}.jpg"
        if not out.exists():
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q), "-Z", str(lado),
                            str(src), "--out", str(out)], check=True, capture_output=True)
        return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()

    def mascarada(rel, src):
        """Imagem já tarjada (cache). Gerar uma tarja nova exige Pillow no Python que roda o build."""
        if rel not in MASCARA:
            return src
        CACHE.mkdir(exist_ok=True)
        h = hashlib.sha1(src.read_bytes() + repr(MASCARA[rel]).encode()).hexdigest()[:16]
        out = CACHE / f"m_{h}.png"
        if not out.exists():
            from PIL import Image, ImageDraw, ImageFont
            im = Image.open(src).convert("RGB")
            d = ImageDraw.Draw(im)
            for r in MASCARA[rel]:
                d.rounded_rectangle(r, radius=6, fill=(12, 13, 13))
                fs = max(11, int((r[3] - r[1]) * .5))
                d.text((r[0] + 10, (r[1] + r[3]) / 2), "mascarado", fill=(255, 196, 9), anchor="lm",
                       font=ImageFont.load_default(size=fs))
            im.save(out)
        return out

    def dims(src):
        r = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(src)], capture_output=True, text=True).stdout
        w = re.search(r"pixelWidth: (\d+)", r)
        hh = re.search(r"pixelHeight: (\d+)", r)
        return (int(w.group(1)), int(hh.group(1))) if w and hh else (0, 0)

    def chip_crit(c):
        k, l = CRIT.get(c, ("baixa", c))
        return f'<span class="crit {k}">{l}</span>'

    def chip_st(s):
        k, l = C["STATUS"][s]
        return f'<span class="st {k}">{html.escape(l)}</span>'

    ACOES_EV = [a for a in C["ACOES"] if a["id"] in CAT]
    GAL, REF_DECK, EV_MAPA = {}, {}, {}
    cont = {"prints": 0, "dados": 0}

    def eh_print(i):
        p = root / i["arquivo"]
        return i.get("tipo") == "print" and p.suffix.lower() in IMG_EXT and p.exists()

    def bloco_acao(a):
        c = CAT[a["id"]]
        itens = [i for i in c.get("itens", []) if not i.get("obsoleta") and i["arquivo"] not in FORA]
        prints, dados = [], []
        rodadas = list(dict.fromkeys(i.get("rodada") for i in itens))
        itens = [i for r in rodadas for g in (True, False) for i in itens if i.get("rodada") == r and eh_print(i) == g]
        for n, it in enumerate(itens, 1):
            it = dict(it, ev=ev_id(a["id"], n))
            EV_MAPA[it["ev"]] = it["arquivo"]
            p = root / it["arquivo"]
            it["sha"] = hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.exists() else "arquivo ausente"
            if eh_print(it):
                if it["arquivo"] in MASCARA:
                    it["legenda"] = it.get("legenda", "") + " Valores identificadores tarjados nesta cópia; o original fica com a Monks."
                prints.append((it, mascarada(it["arquivo"], p)))
            else:
                dados.append(it)
        cont["prints"] += len(prints)
        cont["dados"] += len(dados)
        gid = a["id"]
        GAL[gid] = []
        thumbs = {}
        for k, (it, p) in enumerate(prints):
            w, hgt = dims(p)
            GAL[gid].append(dict(ev=it["ev"], src=jpg(p, 2000, 80), t=it["titulo"], l=it.get("legenda", ""),
                                 p=it.get("prova", ""), f=it.get("fonte", ""), d=it.get("data", ""), h=it["sha"], a=Path(it["arquivo"]).name))
            thumbs.setdefault(it.get("rodada"), []).append(f"""
<li><button type="button" class="th" data-g="{gid}" data-i="{k}" id="{it['ev']}"
  aria-label="Ampliar {it['ev']}: {html.escape(it['titulo'], quote=True)}">
  <img src="{jpg(p, 640, 72)}" alt="{html.escape(it.get('legenda', ''), quote=True)}" loading="lazy" width="{min(w, 640) if w else 320}" height="{round(hgt * min(w, 640) / w) if w else 200}">
  <span class="th-z" aria-hidden="true">⤢</span>
</button>
<div class="th-c"><b class="mono">{it['ev']}</b> {t(it['titulo'])}<span class="th-p">{t(it.get('prova', ''))}</span></div></li>""")
        linhas = {}
        for it in dados:
            trecho = f'<pre>{t(it["trecho"])}</pre>' if it.get("trecho") else ""
            num = f'<p class="num">{t(it["resumo_numerico"])}</p>' if it.get("resumo_numerico") else ""
            linhas.setdefault(it.get("rodada"), []).append(f"""
<details class="dado" id="{it['ev']}">
<summary><b class="mono">{it['ev']}</b><span class="dt-t">{t(it['titulo'])}</span><span class="tag">{t(it.get('tipo', 'dado'))}</span></summary>
<div class="dado-b">
<p>{t(it.get('legenda', ''))}</p>{num}
<p class="prova"><b>O que prova:</b> {t(it.get('prova', ''))}</p>
{trecho}
<p class="src">{t(it.get('fonte', ''))} · {t(it.get('data', ''))} · coletado por Monks · arquivo <code>{t(Path(it['arquivo']).name)}</code> · SHA-256 <code>{it['sha']}</code></p>
</div></details>""")
        todos = [it for it, _ in prints] + dados
        if todos:
            evs = [x["ev"] for x in todos]
            faixa = evs[0] if len(evs) == 1 else f"{evs[0]} a {evs[-1].rsplit('-', 1)[1]}"
            REF_DECK[a["id"]] = dict(faixa=faixa, prints=len(prints), dados=len(dados))
        ret = RET.get(a["id"])
        ret_html = ""
        if ret:
            res = ret["resultado"]
            res = f"Aguardando publicação {D.ART['pela']} {D.NOME}" if res.startswith("PLACEHOLDER_") else res
            ret_html = f'<div class="ret"><b>Critério de pronto (reteste na live)</b><span>{t(ret["criterio"])}</span><i>{t(res)}</i></div>'

        def grupo(r):
            th, ln = thumbs.get(r, []), linhas.get(r, [])
            g = (f'<h4>Prints <span class="cnt">{len(th)}</span><span class="hint">clique para ampliar e navegar com ← →</span></h4>'
                 f'<ul class="gal">{"".join(th)}</ul>') if th else ""
            d = (f'<h4>Dados e registros <span class="cnt">{len(ln)}</span></h4>{"".join(ln)}') if ln else ""
            if r is None:
                return g + d
            return (f'<div class="rodada"><p class="rod-t"><b>Rodada {t(r)}</b> {t(RODADAS.get(r, ""))}</p>{g}{d}</div>') if (g or d) else ""
        galeria = "".join(grupo(r) for r in rodadas)
        vazio = "" if todos else f'<p class="vazio">{t(c.get("resumo", ""))}</p>'
        k_crit = CRIT.get(a["crit"], ("baixa",))[0]
        return f"""
<article class="card" id="{a['id']}" data-crit="{k_crit}" data-st="{a['status']}">
<header class="card-h">
  <span class="cid">{a['id']}</span><span class="ach">{a['achado']}</span>{chip_crit(a['crit'])}{chip_st(a['status'])}
  <span class="dtc">{t(a.get('data') or '')}</span>
</header>
<h3>{t(a['titulo'])}</h3>
{'' if not todos else f'<p class="resumo">{t(c.get("resumo", ""))}</p>'}
<dl class="abn">
  <div><dt>O que acontecia</dt><dd>{t(a['antes'])}</dd></div>
  <div><dt>O que fizemos</dt><dd>{t(a['feito'] or '—')}</dd></div>
  <div><dt>O que muda para o negócio</dt><dd>{t(a['negocio'])}</dd></div>
</dl>
{f'<p class="met"><b>Como coletamos:</b> {t(c.get("metodo", ""))}</p>' if c.get("metodo") and todos else ''}
{galeria}{vazio}
{ret_html}
<p class="prox"><b>Próximo passo:</b> {t(a['proximo'])}</p>
</article>"""

    secoes, toc = [], []
    for f in C["FASES"]:
        acs = [a for a in ACOES_EV if a["fase"] == f["id"]]
        if not acs:
            continue
        corpo = "".join(bloco_acao(a) for a in acs)
        sid = f"fase-{f['id'].lower()}"
        secoes.append(f'<section class="sec" id="{sid}"><h2>{f["nome"]} · {t(f["tema"])}</h2>'
                      f'<p class="sub">Janela {t(f["janela"])} · {len(acs)} ações</p>{corpo}</section>')
        toc.append(f'<li><a href="#{sid}">{f["nome"]} · {t(f["tema"])}</a><ol>'
                   + "".join(f'<li><a href="#{a["id"]}">{a["id"]} · {t(a["titulo"])}</a></li>' for a in acs) + "</ol></li>")

    rast = []
    for a in ACOES_EV:
        r = REF_DECK.get(a["id"])
        evc = (f'<a href="#{a["id"]}" class="mono">{r["faixa"]}</a><span class="sm">{r["prints"]} print(s) · {r["dados"]} dado(s)</span>'
               if r else f'<span class="sm">sem arquivo · {"aguardando próximos passos" if a["status"] == "espera" else "decisão pendente"}</span>')
        rel = a.get("rel", a["achado"])
        rast.append(f'<tr><td class="mono"><a href="#{a["id"]}">{a["id"]}</a></td><td>{t(a["titulo"])}</td>'
                    f'<td class="mono">{t(rel)}</td><td>{chip_crit(a["crit"])}</td><td>{chip_st(a["status"])}</td><td>{evc}</td></tr>')
    n_acoes_com = sum(1 for a in ACOES_EV if a["id"] in REF_DECK)

    avisos, toc_av = [], []
    for av in E.get("avisos", []):
        itens = "\n".join(f"<li>{t_rico(x)}</li>" for x in av.get("itens", []))
        avisos.append(f"""<section class="sec" id="{av['id']}">
<h2>{t(av['titulo'])}</h2>
<p class="sub">{t(av.get('sub', ''))}</p>
<div class="aviso">
<p>{t_rico(av.get('texto', ''))}</p>
{f'<ul>{chr(10)}{itens}{chr(10)}</ul>' if itens else ''}
</div>
</section>""")
        toc_av.append(f'<li><a href="#{av["id"]}">{t(av.get("toc", av["titulo"]))}</a></li>')

    css = (SKILL / "assets/evidencias.css.tpl").read_text(encoding="utf-8").format(
        FONTS=D.FONTS, REP_LIGHT=D.REP_LIGHT, REP_DARK=D.REP_DARK, LOGO_CSS=D.LOGO_CSS, DISPLAY=D.DISPLAY,
        Y=D.Y, ON=D.ON, ON_M=D.ON_M, ESCURO=D.ESCURO, LG_CAB=D.lg_vars("cabecalho_evidencias"), LG_PRINT=D.lg_vars("impressao"))
    js = (SKILL / "assets/evidencias.js").read_text(encoding="utf-8")
    kpi = [(str(n_acoes_com), "ações com evidência anexada"), (str(cont["prints"]), "prints (Preview, plataformas, UI)"),
           (str(cont["dados"]), "registros de dados (API, JSON, diffs)"), (META.get("periodo_coleta", "—"), "período de coleta")]
    kpis = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{t(l)}</div></div>' for v, l in kpi)
    como = "\n".join(f"<li><b>{t(b)}</b>{t(x)}</li>" for b, x in E.get("como_ler", COMO_LER_PADRAO))
    pais = META.get("pais_curto", META["cc"].upper())
    coleta = META.get("coleta", "Monks · Tag Assistant, Tag Manager API, GA4 Admin/Data API, interfaces das plataformas")

    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml;base64,{D.b64(D.FAVICON)}">
<title>Evidências da execução · {t(D.NOME)} {t(pais)}</title>
<style>{css}</style>
</head>
<body>{D.SYMBOLS}
<div class="layout">
<nav class="toc" aria-label="Sumário"><ol>
<li><a href="#s-intro">Como ler este relatório</a></li>
<li><a href="#s-rast">Rastreabilidade</a></li>
{''.join(toc)}
{''.join(toc_av)}
</ol></nav>
<main>
<header class="doc">
<div class="doc-brand">{D.BRAND}</div>
<span class="kick">Auditoria de mensuração · execução do plano de ação</span>
<h1>Relatório de <span class="hl">evidências</span></h1>{D.SMILE}
<div class="metagrid">
<div><b>Versão</b> {t(META['versao'])} · {t(META['atualizado'])}</div>
<div><b>Escopo</b> {t(META['escopo'])}</div>
<div><b>Base</b> {t(META['diagnostico'])}</div>
<div><b>Coleta</b> {t(coleta)}</div>
</div>
<span class="conf">{t(META['confidencialidade'])}</span>
</header>

<section class="sec" id="s-intro">
<h2>Como ler este relatório</h2>
<p class="sub">Acompanha a apresentação da execução. Lá está o que fizemos e o que muda; aqui está a prova de cada ação.</p>
<div class="kpis">{kpis}</div>
<div class="chain" aria-label="Cadeia de rastreabilidade"><span>Achado SF-xxx</span><i>→</i><span>Ação A-xxx</span><i>→</i><span>Evidência EV-Axxx-nn</span><i>→</i><span>Critério de pronto</span></div>
<ul class="how">
{como}
</ul>
</section>

<section class="sec" id="s-rast">
<h2>Rastreabilidade</h2>
<p class="sub">Uma linha por ação: o achado e a evidência E-xx do {t(REL)}, e as evidências da execução neste relatório.</p>
<div class="tw"><table><thead><tr><th>Ação</th><th>O quê</th><th>Achado · {t(META.get('rel_tecnico_curto', REL))}</th><th>Crit.</th><th>Status</th><th>Evidências</th></tr></thead>
<tbody>{''.join(rast)}</tbody></table></div>
</section>

{''.join(secoes)}

{''.join(avisos)}

<footer class="brandfoot" aria-label="{t(D.NOME)} e Monks">{D.BRAND}<span class="f">{t(META['titulo'])} · {t(META['versao'])} · {t(META['atualizado'])}</span></footer>
</main>
</div>
<button type="button" class="themebtn" aria-label="Alternar tema claro/escuro">◐ Tema</button>

<dialog class="lb" id="lb" aria-labelledby="lb-t">
<div class="lb-w">
<div class="lb-top"><span class="lb-ev"></span><span class="lb-n" aria-live="polite"></span>
<button type="button" class="lb-b lb-x" aria-label="Fechar (Esc)">✕</button></div>
<div class="lb-stage">
<button type="button" class="lb-b lb-prev" aria-label="Evidência anterior (←)">←</button>
<img alt="">
<button type="button" class="lb-b lb-next" aria-label="Próxima evidência (→)">→</button>
</div>
<div class="lb-cap"><div class="lb-dots"></div><h5 id="lb-t"></h5><p class="lg"></p><p class="pv"><b>O que prova:</b> <span></span></p><p class="sr"></p></div>
</div>
</dialog>
<script type="application/json" id="gal-data">{json.dumps(GAL, ensure_ascii=False).replace('</', '<\\/')}</script>
<script>{js}</script>
</body>
</html>"""
    resumo = dict(acoes=n_acoes_com, prints=cont["prints"], dados=cont["dados"])
    return doc, REF_DECK, resumo, EV_MAPA
