"""Deck vivo da execução (slides 16:9, mesmo CSS/JS do deck de diagnóstico aprovado).

Portado de brasil/entregas/_fonte/build_deck_execucao.py (v1.7, 27/10/2026). Os slides deixaram de estar no código:
a sequência fica em DECK.slides do execucao.json, um item por slide, na ordem. Tipos em references/conteudo-execucao.md:
capa · fases · bluf · quadro · vitrine · pedidos · tres_blocos · reteste · indice · prints.
Títulos aceitam contagens: {F1_concluida}, {F2_publicar|está pronta|estão prontas}… (comum.contagens).
"""
import base64
import html
import re

from comum import AUDITORIA, CL, SKILL, PH_RE, contagens, da_fase, preencher

def _id_re():
    return re.compile(r"\b((?:" + re.escape(CL.get("prefixo", "SF")) + r"-[A-Z]+|A|D)-[A-Z0-9]+)")
CRIT = {"ALTA": ("alta", "▲ ALTA"), "MÉDIA": ("media", "■ MÉDIA"), "BAIXA": ("baixa", "▼ BAIXA")}


def t(s):
    """Escapa; PLACEHOLDER_* vira o marcador "após a publicação"; `x` vira <code>; IDs sem quebra de linha."""
    if s is None:
        return ""
    s = str(s)
    out, last = [], 0
    for m in PH_RE.finditer(s):
        out.append(html.escape(s[last:m.start()]))
        out.append('<span class="ph">após a publicação</span>')
        last = m.end()
    out.append(html.escape(s[last:]))
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", "".join(out))
    return _id_re().sub(r'<span class="nw">\1</span>', s)


def gerar(root, C, ref_ev, nome_ev):
    """Devolve (doc, [(n, apêndice, título)], n_corpo). ref_ev vem do relatório de evidências (gerar antes)."""
    META = C["META"]
    ACO = {a["id"]: a for a in C["ACOES"]}
    CNT = contagens(C)
    REL = META.get("rel_tecnico", "relatório técnico")
    REL = REL[0].upper() + REL[1:]
    EV_REL = "Relatório de evidências"

    def chip(crit):
        cls, lab = CRIT[crit]
        return f'<span class="chip c-{cls}">{lab}</span>'

    def st(s):
        cls, lab = C["STATUS"][s]
        return f'<span class="st {cls}">{lab}</span>'

    def conta(f, *sts):
        return sum(1 for a in da_fase(C, f) if a["status"] in sts)

    def p(s):
        return preencher(s, CNT)

    def ref_ev_txt(a):
        r = ref_ev.get(a["id"])
        return f'{EV_REL} · {r["faixa"]}' if r else ""

    def ref(a):
        partes = [x for x in (ref_ev_txt(a), a.get("onde")) if x]
        if a.get("rel"):
            partes.append(f'{REL} · {a["rel"]}')
        return " · ".join(partes) or a.get("evid", "")

    def ref_html(a):
        partes = []
        if a["id"] in ref_ev:
            partes.append(f'<a class="evl" href="{nome_ev}#{a["id"]}">{t(ref_ev_txt(a))}</a>')
        partes += [t(x) for x in (a.get("onde"), f'{REL} · {a["rel"]}' if a.get("rel") else "") if x]
        return " · ".join(partes) or t(a.get("evid", ""))

    def img_src(a):
        return "data:image/jpeg;base64," + base64.b64encode((root / a["print"]).read_bytes()).decode()

    specs = C["DECK"]["slides"]
    # nº do slide onde aparece o print de cada ação (o índice do apêndice cita)
    PRINT_SLIDE = {}
    for n, s in enumerate(specs, 1):
        if s["tipo"] == "vitrine" and len(s["acoes"]) == 1 and ACO[s["acoes"][0]].get("print"):
            PRINT_SLIDE[s["acoes"][0]] = n
        elif s["tipo"] == "prints":
            for i in s["acoes"]:
                if ACO[i].get("print"):
                    PRINT_SLIDE[i] = n

    # ---------------------------------------------------------------- tipos de slide
    def s_capa(s):
        corpo = f"""
<div class="capa-wrap">
  <div class="capa-top">{t(META['autores'])} · {t(META['versao'])} · atualizado em {t(META['atualizado'])}</div>
  <div class="capa-mid">
    <p class="capa-kicker">Execução do plano de ação</p>
    <h1 class="capa-h">{t(META['capa_titulo'])}</h1>
    <p class="capa-sub">{t(META.get('capa_sub', 'Acompanhamento das fases 1 a 3 · a partir do ' + META['diagnostico']))}</p>
    <dl class="capa-meta">
      <div><dt>Escopo</dt><dd>{t(META['escopo'])}</dd></div>
      <div><dt>Atualizado</dt><dd>{t(META['atualizado'])}</dd></div>
      <div><dt>Versão</dt><dd>{t(META['versao'])}</dd></div>
    </dl>
  </div>
  <div class="capa-bot">
    <span>{t(META['confidencialidade'])}</span>
    <span class="capa-print">Navegar: ← → · N notas · A apêndice</span>
  </div>
</div>"""
        return dict(titulo=META["titulo"], corpo=corpo, cls="dark capa")

    def s_fases(s):
        rot = {"fb-ok": "concluídas", "fb-pub": "validadas, falta publicar", "fb-dec": "em decisão ou revisão",
               "fb-and": "em andamento", "fb-nao": "em espera ou não iniciadas"}
        cards = []
        for f in C["FASES"]:
            n = len(da_fase(C, f["id"])) or 1
            seg = {"fb-ok": conta(f["id"], "concluida"), "fb-pub": conta(f["id"], "publicar"),
                   "fb-dec": conta(f["id"], "decisao", "revisao"), "fb-and": conta(f["id"], "andamento"),
                   "fb-nao": conta(f["id"], "nao", "espera")}
            barra = "".join(f'<i class="{c}" style="width:{v / n * 100:.1f}%"></i>' for c, v in seg.items() if v)
            lst = "".join(f'<li><i class="sw {c}" aria-hidden="true"></i><b>{seg[c]}</b>{r}</li>' for c, r in rot.items())
            on = " on" if f["id"] == s.get("destaque", C["FASES"][0]["id"]) else ""
            cards.append(f'<div class="fase{on}"><div class="fase-h"><b>{f["nome"]}</b><span>{f["janela"]}</span></div>'
                         f'<p>{t(f["tema"])} · {len(da_fase(C, f["id"]))} ações</p><div class="fbar" role="img" aria-label="{f["nome"]}: distribuição por status">{barra}</div>'
                         f'<ul class="fcount">{lst}</ul></div>')
        return dict(corpo=f'<div class="fases">{"".join(cards)}</div>')

    def s_bluf(s):
        k = "\n  ".join(f'<div class="kpi big {x.get("tom", "ok")}"><b>{t(x["v"])}</b><span>{t(x["l"])}'
                    f'{"<br><small>" + t(x["sub"]) + "</small>" if x.get("sub") else ""}</span><em>{t(x.get("ids", ""))}</em></div>'
                    for x in s["kpis"])
        fx = s.get("destaque")
        fix = ""
        if fx:
            lis = "\n    ".join(f'<li><span class="mono">{t(i["mono"])}</span> {t(i["txt"])}{" <em>(" + t(i["em"]) + ")</em>" if i.get("em") else ""}</li>'
                          for i in fx.get("itens", []))
            nota = f'\n  <p class="foot-note">{t(fx["nota"])}</p>' if fx.get("nota") else ""
            fix = f"""
<div class="bluf-fix">
  <b>{t(fx['titulo'])}</b>
  <ul>
    {lis}
  </ul>{nota}
</div>"""
        return dict(corpo=f'\n<div class="kpis4">\n  {k}\n</div>{fix}')

    def s_quadro(s):
        acs = da_fase(C, s["fase"])
        if s.get("colunas") == "hoje":
            cab = "<th>Ação</th><th>O que muda</th><th>Hoje</th><th>Para o negócio</th><th>Status</th>"
            lin = "".join(f'<tr><td class="mono">{a["id"]}</td><td>{t(a["titulo"])}</td><td>{t(a["antes"])}</td><td>{t(a["negocio"])}</td><td>{st(a["status"])}</td></tr>' for a in acs)
        else:
            cab = "<th>Ação</th><th>O que muda</th><th>Criticidade</th><th>Status</th><th>Próximo passo</th>"
            lin = "".join(f'<tr><td class="mono">{a["id"]}</td><td>{t(a["titulo"])}</td><td>{chip(a["crit"])}</td><td>{st(a["status"])}</td>'
                          f'<td class="px">{t(a["proximo"])}</td></tr>' for a in acs)
        cls = "tbl board board-xl" if s.get("xl") else "tbl board"
        return dict(corpo=f'<table class="{cls}"><thead><tr>{cab}</tr></thead><tbody>{lin}</tbody></table>',
                    ids=", ".join(a["id"] for a in acs))

    def s_vitrine(s):
        blocos = []
        for i in s["acoes"]:
            a = ACO[i]
            blocos.append(f"""
<div class="feito">
  <div class="qb qb-m"><h3>{a['id']} · O que acontecia</h3><p>{t(a['antes'])}</p></div>
  <div class="qb"><h3>O que fizemos</h3><p>{t(a['feito'])}</p></div>
  <div class="qb qb-f"><h3>O que muda para o negócio</h3><p>{t(a['negocio'])}</p></div>
</div>
<div class="feito-pe">{st(a['status'])}<span>{t(a['proximo'])}</span><span class="ref">{ref_html(a)}</span></div>""")
        extra = ""
        if s.get("numeros"):
            extra = '<div class="kpis4 nums">' + "".join(
                f'<div class="kpi{" ok" if x.get("ok") else ""}"><b>{t(x["v"])}</b><span>{t(x["l"])}</span></div>' for x in s["numeros"]) + "</div>"
        shot = ""
        a0 = ACO[s["acoes"][0]]
        if len(s["acoes"]) == 1 and a0.get("print"):
            shot = (f'<figure class="shot"><img src="{img_src(a0)}" alt="{html.escape(a0["legenda"], quote=True)}">'
                    f'<figcaption><b>Evidência · {a0["id"]}</b>{t(a0["legenda"])}</figcaption></figure>')
        return dict(corpo="".join(blocos) + extra + shot,
                    fonte=" · ".join(ref(ACO[i]) for i in s["acoes"]),
                    ids=", ".join(f'{ACO[i]["id"]}, {ACO[i]["achado"]}' for i in s["acoes"]))

    def s_pedidos(s):
        def lin(k, x):
            det = f'<small>{t(x["nome"])}</small>' if x.get("nome") else ""
            return (f'<tr><td class="c"><span class="dn sm">{k + 1}</span></td><td><b>{t(x["o"])}</b>{det}</td>'
                    f'<td class="mono">{t(x["fecha"])}</td></tr>')
        ped = "".join(lin(k, x) for k, x in enumerate(C["PEDIDOS"]))
        return dict(corpo=f'<table class="tbl ped"><thead><tr><th>#</th><th>O que precisamos</th><th>Fecha</th></tr></thead><tbody>{ped}</tbody></table>',
                    ids=", ".join(x["fecha"] for x in C["PEDIDOS"]))

    def s_tres_blocos(s):
        cls = ["qb qb-m", "qb", "qb qb-f"]
        b = "\n".join(f'  <div class="{cls[k]}"><h3>{t(x["h"])}</h3><p>{t(x["p"])}</p></div>' for k, x in enumerate(s["blocos"]))
        pe = ""
        if s.get("pe"):
            pe = f'\n<div class="feito-pe">{st(s["pe"]["status"])}<span>{t(s["pe"]["txt"])}</span></div>'
        return dict(corpo=f'<div class="feito">\n{b}\n</div>{pe}')

    def s_reteste(s):
        ret = "".join(f'<tr><td class="mono">{r["id"]}</td><td>{t(r["criterio"])}</td><td>{t(r["resultado"])}</td></tr>' for r in C["RETESTE"])
        dod = s.get("dod", "versão nomeada com o ID da ação · testada em Preview e na live com o roteiro do achado · evidência salva com o ID · sem regressão no funil, 1 purchase por transação e nenhum dado pessoal.")
        return dict(corpo=f"""<table class="tbl prova"><thead><tr><th>Ação</th><th>Pronto quando…</th><th>Resultado do reteste</th></tr></thead><tbody>{ret}</tbody></table>
<p class="dod-l" style="margin-top:10px;font-size:15px;color:var(--mut,#9aa0a6)"><b>Definição de pronto (todas as ações):</b> {t(dod)}</p>""",
                    ids=", ".join(r["id"] for r in C["RETESTE"]))

    def onde_ver(a):
        partes = []
        if a["id"] in ref_ev:
            partes.append(f'<a class="evl" href="{nome_ev}#{a["id"]}">{t(ref_ev[a["id"]]["faixa"])}</a>')
        if a["id"] in PRINT_SLIDE:
            partes.append(f'print no slide {PRINT_SLIDE[a["id"]]}')
        if a.get("onde"):
            partes.append(t(a["onde"]))
        return " · ".join(partes) or "—"

    def s_indice(s):
        ev = []
        for f in C["FASES"]:
            acs = [a for a in da_fase(C, f["id"]) if f["id"] in s["fases"] and (a.get("evid") or a["id"] in ref_ev)]
            if not acs:
                continue
            ev.append(f'<tr class="grp"><td colspan="6">{f["nome"]} · {t(f["tema"])}</td></tr>')
            ev += [f'<tr><td class="mono">{a["id"]}</td><td>{t(a["titulo"])}</td><td>{st(a["status"])}</td>'
                   f'<td class="dt">{t(a.get("data") or "—")}</td><td class="ov">{onde_ver(a)}</td><td class="ov mono">{t(a.get("rel", a["achado"]))}</td></tr>' for a in acs]
        return dict(corpo=f'<table class="tbl evt"><thead><tr><th>Ação</th><th>O quê</th><th>Status</th><th>Data</th><th>Relatório de evidências · onde ver</th><th>{t(REL)}</th></tr></thead><tbody>{"".join(ev)}</tbody></table>',
                    kicker="Evidências", ids="—",
                    fonte=f"{EV_REL} da execução (EV-Axxx-nn, arquivo {nome_ev}) e {META.get('rel_tecnico', 'relatório técnico')} (E-xx = índice de evidências do relatório técnico)",
                    notas="Cada linha diz onde conferir: a evidência EV no relatório de evidências da execução, que abre os prints em galeria, o print neste deck, o que vocês abrem direto (workspace no GTM, planilha) e o achado com a evidência E-xx no relatório técnico.")

    def s_prints(s):
        acs = [i for i in s["acoes"] if ACO[i].get("print")]
        figs = "".join(f'<figure><img src="{img_src(ACO[i])}" alt="{html.escape(ACO[i]["legenda"], quote=True)}">'
                       f'<figcaption><b>{i}</b>{t(ACO[i]["legenda"])}</figcaption></figure>' for i in acs)
        return dict(corpo=f'<div class="shots2">{figs}</div>', ids=", ".join(acs))

    TIPOS = dict(capa=s_capa, fases=s_fases, bluf=s_bluf, quadro=s_quadro, vitrine=s_vitrine, pedidos=s_pedidos,
                 tres_blocos=s_tres_blocos, reteste=s_reteste, indice=s_indice, prints=s_prints)

    SLIDES = []
    for s in specs:
        gerado = TIPOS[s["tipo"]](s)
        sl = dict(titulo="", corpo="", notas="", fonte="", ids="", cls="", kicker="")
        sl.update(gerado)
        for k in ("titulo", "notas", "fonte", "ids", "kicker"):  # o conteúdo manda sobre o padrão do tipo
            if s.get(k) is not None:
                sl[k] = s[k]
        sl["titulo"] = p(sl["titulo"])
        sl["notas"] = p(sl["notas"])
        sl["apendice"] = bool(s.get("apendice"))
        SLIDES.append(sl)

    n_corpo = next((k for k, s in enumerate(SLIDES) if s["apendice"]), len(SLIDES))
    total = len(SLIDES)
    secs = []
    for n, s in enumerate(SLIDES, 1):
        titulo_plano = re.sub(r"\s+", " ", s["titulo"])
        aria = html.escape(f"{n} de {total}: {titulo_plano}", quote=True)
        cls = "slide " + s["cls"] + (" apx" if s["apendice"] else "")
        first_apx = ' data-first-apx="1"' if s["apendice"] and (n - 1) == n_corpo else ""
        tag_apx = '<span class="apx-tag">Apêndice</span>' if s["apendice"] else ""
        kicker = f'<p class="kicker">{tag_apx}<span>{t(s["kicker"])}</span></p>' if (s["kicker"] or tag_apx) else ""
        if "capa" in s["cls"]:
            h2 = f'<h2 class="sr">{t(s["titulo"])}</h2>'
        else:
            h2 = f'<header class="sh">{kicker}<h2>{t(s["titulo"])}</h2></header>'
        notas = f'<aside class="notes"><b>Notas do apresentador</b><p>{t(s["notas"])}</p></aside>' if s["notas"] else ""
        rod = (f'<footer class="sf"><span>Fonte: {t(s["fonte"])} · atualizado {META["atualizado"]}'
               f'{" · IDs citados: " + t(s["ids"]) if s["ids"] and s["ids"] != "—" else ""}</span><span class="pg">{n} / {total}</span></footer>')
        secs.append(f'<section class="{cls.strip()}" role="group" aria-roledescription="slide" aria-label="{aria}" id="s{n}"{first_apx}>'
                    f'{h2}<div class="content">{s["corpo"]}</div>{rod}{notas}</section>')

    css = (AUDITORIA / "assets/deck.css").read_text(encoding="utf-8") + (SKILL / "assets/deck-execucao.css").read_text(encoding="utf-8")
    js = (AUDITORIA / "assets/deck.js").read_text(encoding="utf-8")
    pais = META.get("pais_curto", META["cc"].upper())
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Execução {html.escape(CL["nome"])} {html.escape(pais)}</title>
<meta name="description" content="{html.escape(META['titulo'])} · {html.escape(META['versao'])} · {html.escape(META['atualizado'])}">
<link rel="icon" href="data:,">
<style>{css}</style>
</head>
<body>
<main id="deck" aria-label="Apresentação executiva da execução">
{''.join(secs)}
</main>
<div id="bar" aria-hidden="true"></div>
<div id="cnt" aria-live="polite"></div>
<script>{js}</script>
</body>
</html>
"""
    return doc, [(n, s["apendice"], s["titulo"]) for n, s in enumerate(SLIDES, 1)], n_corpo
