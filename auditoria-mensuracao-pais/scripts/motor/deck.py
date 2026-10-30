"""Apresentação executiva 16:9 (motor e sequência aprovados no BR em 14/10/2026), gerada só a partir do conteudo.json.

Corpo: capa · o que combinamos · pedido → entrega · resposta em uma página · decisões (prévia) · cobertura e método ·
matriz · [slide da receita] · vitrines (achados com "vitrine": true) · [slides extras] · plano · como vamos provar ·
decisões e insumos. Apêndice: demais achados · a validar · dependências · rubrica · índice de evidências · glossário.
Teclas: ← → espaço · N notas · A apêndice · T tema · F tela cheia (na cópia -design).
"""
import datetime
import html
import re
from pathlib import Path

from cliente import artigos, carregar as carregar_cliente
from comum import CRIT_ORD, PILARES_PADRAO, bloco, blocos, esc, fmt_fn, txt

ASSETS = Path(__file__).resolve().parents[2] / "assets"
CRIT = {"ALTA": ("alta", "▲ ALTA"), "MÉDIA": ("media", "■ MÉDIA"), "BAIXA": ("baixa", "▼ BAIXA")}
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def t(s):
    return txt(s, links=False, nw=True)


def chip(c):
    cls, lab = CRIT[c]
    return f'<span class="chip c-{cls}">{lab}</span>'


def nivel(n):
    return {3: "3 · Alto", 2: "2 · Médio", 1: "1 · Baixo"}[n]


def curta(s, lim=86):
    s = s.split(";")[0].strip()
    if len(s) > lim:
        s = re.sub(r"\s*\([^)]*\)", "", s)
    while len(s) > lim and ", " in s:
        s = s.rsplit(", ", 1)[0]
    if s.count("(") > s.count(")"):
        s = s.rsplit("(", 1)[0].rstrip()
    return s


def gerar(root, C):
    M = C["META"]
    moeda = M.get("moeda", "R$")
    CL = carregar_cliente(root)
    cliente = M.get("cliente", CL["nome"])
    ART = artigos(CL)
    PIL = C.get("PILARES", PILARES_PADRAO)
    ACH = {a["id"]: a for a in C["ACHADOS"]}
    EVI = {e["id"]: e for e in C["EVIDENCIAS"]}
    ACO = {a["id"]: a for a in C["ACOES"]}
    NOT = C.get("NOTAS", {})
    PER = M.get("periodo_curto", M["periodo"])
    SL = []

    def add(titulo, corpo, notas="", fonte="", ids="", cls="", kicker="", apendice=False, periodo=None):
        SL.append(dict(titulo=titulo, corpo=corpo, notas=notas, fonte=fonte, ids=ids, cls=cls, kicker=kicker, apendice=apendice, periodo=periodo))

    # 1 · capa
    titulo_capa = M.get("titulo_deck", M["titulo"])
    capa = f"""
<div class="capa-wrap">
  <div class="capa-top">{t(M['autores'])} · {t(M['rodada'])} · {t(M['versao'])}</div>
  <div class="capa-mid">
    <p class="capa-kicker">Auditoria de mensuração</p>
    <h1 class="capa-h">{t(titulo_capa)}</h1>
    <p class="capa-sub">Dados de {t(M['periodo'])} · extraídos em {t(M['extraido'])}</p>
    <dl class="capa-meta">
      <div><dt>Escopo</dt><dd>{t(M['escopo'])}</dd></div>
      <div><dt>Data</dt><dd>{t(M['data_doc'])}{f" · reunião de {t(M['reuniao'])}" if M.get('reuniao') else ""}</dd></div>
      <div><dt>Versão</dt><dd>{t(M['rodada'])} · {t(M['versao'])}</dd></div>
    </dl>
  </div>
  <div class="capa-bot">
    <span>{t(M['confidencialidade'])}</span>
    <span class="capa-print">Imprimir: margens Nenhuma, gráficos de segundo plano ligado · Navegar: ← → · N notas · A apêndice</span>
  </div>
</div>"""
    add(titulo_capa, capa, cls="dark capa", notas=NOT.get("capa", "Recorte, período dos dados e o combinado: tudo o que mostramos tem evidência rastreável no relatório técnico, pelo mesmo ID."),
        fonte="Tag Manager API v2, GA Admin API e Data API, Chrome DevTools", ids="—")

    # 2 · o que combinamos
    if C.get("REUNIAO") or C.get("COMBINADO"):
        quotes = "".join(f'<blockquote class="quote"><span class="qn">{k + 1}</span>{t(q)}</blockquote>' for k, q in enumerate(C.get("REUNIAO", [])))
        steps = "".join(f'<li class="{"on" if s.get("on") else ""}"><b>{t(s["titulo"])}</b><span>{t(s["texto"])}</span></li>' for s in C.get("COMBINADO", []))
        add(M.get("titulo_combinado", "Combinamos começar pela conta principal, com evidência e impacto no negócio em cada achado"), f"""
<div class="two">
  <div><p class="lead">O que vocês pediram, nas palavras de vocês:</p><div class="quotes">{quotes}</div></div>
  <div><p class="lead">O que combinamos fazer:</p><ol class="steps">{steps}</ol></div>
</div>""", kicker=f"O que combinamos{' em ' + M['reuniao'] if M.get('reuniao') else ''}", notas=NOT.get("combinado", ""), fonte="Reunião de alinhamento", ids="—")

    # 3 · RTM
    cont = {s: sum(1 for r in C["RTM"] if r["status"] == s) for s in ("Atendido", "Parcial", "Pendente")}
    stc = {"Atendido": ("st-ok", "✓ Atendido"), "Parcial": ("st-parc", "◐ Parcial"), "Pendente": ("st-pend", "○ Pendente")}
    linhas = "".join(f'<tr><td class="mono">{t(r["id"])}</td><td>{t(r["pedido"])}</td><td class="mono sm">{t(r["onde"])}</td><td><span class="st {stc[r["status"]][0]}">{stc[r["status"]][1]}</span></td></tr>' for r in C["RTM"])
    add(M.get("titulo_rtm", f"{cont['Atendido']} dos {len(C['RTM'])} itens do pedido estão atendidos" + (f"; {cont['Parcial']} parciais" if cont["Parcial"] else "") + (f" e {cont['Pendente']} pendentes" if cont["Pendente"] else "")), f"""
<div class="rtm-wrap">
  <div class="rtm-sum">
    <div class="kpi"><b>{cont['Atendido']}</b><span>✓ Atendido</span></div>
    <div class="kpi"><b>{cont['Parcial']}</b><span>◐ Parcial<br><small>{t(M.get('nota_parcial', 'conta principal coberta; demais ativos na próxima rodada'))}</small></span></div>
    <div class="kpi"><b>{cont['Pendente']}</b><span>○ Pendente<br><small>{t(M.get('nota_pendente', ''))}</small></span></div>
  </div>
  <table class="tbl rtm"><thead><tr><th>ID</th><th>Pedido</th><th>Onde está atendido</th><th>Status</th></tr></thead><tbody>{linhas}</tbody></table>
</div>""", kicker="Pedido → entrega", notas=NOT.get("rtm", "Matriz de rastreabilidade: cada item do pedido oficial aponta para onde está atendido."),
        fonte="Pedido oficial × esta entrega (matriz completa no relatório técnico)", ids=f"{C['RTM'][0]['id']} a {C['RTM'][-1]['id']}")

    # 4 · BLUF
    S = C.get("SUMARIO", {})
    kp = "".join(f'<div class="kpi big{" crit-a" if k.get("crit") else ""}"><b>{t(k["v"])}</b><span>{t(k["l"])}{("<br><small>" + t(k["d"]) + "</small>") if k.get("d") else ""}</span><em>{t(k.get("s", ""))}</em></div>' for k in S.get("kpis", [])[:4])
    dst = S.get("destaque")
    bluf_fix = ""
    if dst:
        itens = "".join(f'<li><span class="mono">{x}</span> {t(curta(ACO[x]["oque"]))} <em>({" · ".join(ACO[x]["achados"])} · esforço {ACO[x]["esforco"]})</em></li>' for x in dst.get("acoes", []) if x in ACO)
        bluf_fix = f'<div class="bluf-fix"><b>{t(dst["titulo"])}</b><ul>{itens}</ul>{('<p class="foot-note">' + t(dst["nota"]) + "</p>") if dst.get("nota") else ""}</div>'
    add(S.get("titulo_deck", S.get("resposta_curta", "Resposta em uma página")), f'<div class="kpis4">{kp}</div>{bluf_fix}', kicker="Resposta em uma página",
        notas=NOT.get("bluf", S.get("resposta_curta", "")), fonte=S.get("fonte", "GA Data API, Tag Manager API, Chrome DevTools"), ids=", ".join(S.get("top", [])))

    # 5 · decisões (prévia)
    if C.get("DECISOES"):
        dec = "".join(f'<div class="drow"><span class="dn">{k + 1}</span><b>{t(x["d"])}</b><p class="dwhy">{t(x["porque"])}</p><p class="drisk">{t(x["senao"])}</p></div>' for k, x in enumerate(C["DECISOES"]))
        prazo = ""
        if M.get("decisoes_ate"):
            dd = datetime.datetime.strptime(M["decisoes_ate"], "%d/%m/%Y")
            prazo = f'<div class="dprazo"><span class="dprazo-k">Prazo</span><b>{DIAS[dd.weekday()]}, {t(M["decisoes_ate"])}</b><span>{t(M.get("prazo_texto", "para começar a fase 1 do plano"))}</span></div>'
        add(f"Precisamos de {len(C['DECISOES'])} decisões" + (f" até {M['decisoes_ate']}" if M.get("decisoes_ate") else "") + " para executar o plano",
            f'<div class="dgrid"><div class="dhead"><span></span><span>Decisão</span><span>Por quê</span><span>Se não decidirmos</span></div>{dec}</div>{prazo}',
            kicker="Decisões pedidas (prévia)", notas=NOT.get("decisoes", "Antecipamos o que vamos pedir no fim, para vocês ouvirem o resto já com isso em mente."), fonte="Plano de ação (relatório técnico §8)", ids="—")

    # 6 · cobertura e método
    CB = C.get("COBERTURA", {})
    inv = "".join(f'<div><b>{t(x["v"])}</b><span>{t(x["l"])}</span></div>' for x in CB.get("itens", []))
    ok = "".join(f'<li><span class="ok">✓</span><span>{t(v["item"])}</span><em class="mono">{t(v["evid"])}</em></li>' for v in C.get("VERIFICADO_OK", []))
    add(CB.get("titulo_deck", "Lemos 100% da conta principal, percorremos o funil e mapeamos acessos e uso de todos os ativos"), f"""
<div class="two w46">
  <div><p class="lead">O que lemos (somente leitura, via API e navegador)</p><div class="inv">{inv}</div></div>
  <div><p class="lead">O que verificamos e está OK</p><ul class="oklist">{ok}</ul></div>
</div>""", kicker="Cobertura e método", notas=NOT.get("cobertura", "Primeiro o que olhamos e o que está funcionando, para ficar claro que não é uma lista só de problemas."),
        fonte="Tag Manager API v2, GA Admin/Data API, Chrome DevTools", ids=", ".join(sorted({v["evid"] for v in C.get("VERIFICADO_OK", [])})))

    # 7 · matriz
    achs = sorted(C["ACHADOS"], key=lambda a: (CRIT_ORD[a["crit"]], -a["I"], -a["P"]))
    cnt = {c: sum(1 for a in achs if a["crit"] == c) for c in CRIT_ORD}
    app = {p: sum(1 for a in achs if a["crit"] == "ALTA" and a["pilar"] == p) for p in PIL}
    ptop = max(app, key=app.get)
    hm = []
    for a in achs:
        cells = "".join(f'<td class="hm s{a["scores"][p]}{" dom" if p == a["pilar"] else ""}">{nivel(a["scores"][p])}{" ◆" if p == a["pilar"] else ""}</td>' for p in ("FIN", "INT", "PG"))
        hm.append(f'<tr><td class="mono">{a["id"]}</td><td>{t(a["curto"])}</td>{cells}<td class="mono c">{a["I"]}×{a["P"]}</td><td>{chip(a["crit"])}</td></tr>')
    av = C.get("A_VALIDAR", [])
    add(M.get("titulo_matriz", f"{len(achs)} achados, {cnt['ALTA']} em Alta" + (f": {app[ptop]} deles em {PIL[ptop]}" if cnt["ALTA"] else "")), f"""
<table class="tbl heat{" heat-xl" if len(achs) > 18 else ""}"><thead><tr><th>ID</th><th>Achado</th><th>{PIL['FIN']}</th><th>{PIL['INT']}</th><th>{PIL['PG']}</th><th>I×P</th><th>Criticidade</th></tr></thead><tbody>{''.join(hm)}</tbody></table>
<p class="legend">Célula = impacto no pilar (1 Baixo · 2 Médio · 3 Alto). ◆ = pilar dominante. Criticidade = I × P + modificadores (dado pessoal/credencial, lance de mídia); rubrica no apêndice.{f" Itens “a validar” ({av[0]['id']}..{av[-1]['id']}) ficam fora da matriz." if av else ""}</p>""",
        kicker="Matriz de criticidade", notas=NOT.get("matriz", f"São {len(achs)} achados, {cnt['ALTA']} em Alta e {cnt['MÉDIA']} em Média, nos três pilares do pedido. Vocês conseguem refazer a conta: impacto vezes abrangência, mais os modificadores."),
        fonte="Rubrica I×P (apêndice) aplicada aos achados do relatório técnico", ids="—")

    # 8 · slide da receita (opcional)
    MO = C.get("MONEY")
    if MO:
        p1, p2 = MO["principal"], MO.get("lateral")
        w1 = bloco({"tipo": "waterfall", "itens": p1["itens"], "fmt": p1.get("fmt", "moeda"), "legenda": p1["titulo"], "w": 1060, "h": 640}, root, moeda, deck=True)
        side = ""
        if p2:
            w2 = bloco({"tipo": "waterfall", "itens": p2["itens"], "fmt": p2.get("fmt", "compacto"), "legenda": p2["titulo"], "w": 640, "h": 480, "compacto": True}, root, moeda, deck=True)
            side = f'<div class="panel side"><p class="panel-t">{t(p2["titulo"])}</p>{w2}{('<p class="small">' + t(p2["nota"]) + "</p>") if p2.get("nota") else ""}</div>'
        add(MO["titulo"], f'<div class="money"><div class="panel"><p class="panel-t">{t(p1["titulo"])}</p>{w1}</div>{side}</div>',
            kicker=MO.get("kicker", "Receita reportada × verificável"), notas=MO.get("notas", ""), fonte=MO.get("fonte", "GA Data API"), ids=MO.get("ids", "—"))

    # vitrines
    def meta_achado(a, extra=""):
        ac = ACO.get(a["acao"], {})
        mods = "; ".join(a.get("mods") or []) or "—"
        return f"""
<dl class="meta">
  <div><dt>ID</dt><dd class="mono">{a['id']}</dd></div>
  <div><dt>Criticidade</dt><dd>{chip(a['crit'])} <span class="mono">I={a['I']} ({t(PIL[a['pilar']])}) × P={a['P']}</span></dd></div>
  <div><dt>Modificadores</dt><dd>{t(mods)}</dd></div>
  <div><dt>Confiança</dt><dd>{t(a['conf'])}</dd></div>
  <div><dt>Evidências</dt><dd class="mono">{' · '.join(a['evid'])}</dd></div>
  <div><dt>Ação</dt><dd><span class="mono">{t(a['acao'])}</span> · {t(ac.get('fase', ''))} · esforço {t(ac.get('esforco', ''))} · A: {t(ac.get('A', ''))}</dd></div>
  {extra}
</dl>"""

    def tres(a):
        d = a["deck"]
        return f"""
<div class="q3">
  <div class="qb"><h3>O que acontece</h3><p>{t(d['oque'])}</p></div>
  <div class="qb qb-m"><h3>Quanto custa ou distorce</h3><p>{t(d['quanto'])}</p>{f'<p class="refmk">{t(d["nota_quanto"])}</p>' if d.get("nota_quanto") else ""}</div>
  <div class="qb qb-f"><h3>O que fazer</h3><p>{t(d['fazer'])}</p></div>
</div>"""

    def fonte_achado(a):
        return ", ".join(dict.fromkeys(EVI[e]["tipo"] for e in a["evid"] if e in EVI))

    vit = [a for a in C["ACHADOS"] if a.get("vitrine")]
    vit.sort(key=lambda a: a.get("ordem_vitrine", 99))
    for n, a in enumerate(vit, 1):
        d = a["deck"]
        g = d.get("grafico")
        painel = (f'<p class="panel-t">{t(d.get("grafico_titulo", ""))}</p>' if d.get("grafico_titulo") else "") + (bloco(g, root, moeda, deck=True) if g else "")
        add(d.get("titulo", a["titulo"]), f'<div class="vit">{tres(a)}<div class="vit-side">{painel}{meta_achado(a)}</div></div>',
            kicker=f"Achado {n} · " + re.sub(r"^Achado \d+ · ", "", d.get("kicker", PIL[a["pilar"]])), notas=d.get("notas", ""), fonte=fonte_achado(a),
            ids=", ".join([a["id"], *a["evid"], a["acao"]]), periodo=d.get("periodo"))

    for x in C.get("SLIDES_EXTRA", []):
        add(x["titulo"], blocos(x.get("blocos"), root, moeda, deck=True), kicker=x.get("kicker", ""), notas=x.get("notas", ""), fonte=x.get("fonte", ""), ids=x.get("ids", "—"),
            apendice=x.get("apendice", False), periodo=x.get("periodo"))

    # plano
    cols = []
    for hz, rot in M["fases"].items():
        cards = "".join(
            f'<div class="rc"><div class="rc-h"><span class="mono">{x["id"]}</span><span class="mono rc-a">{" · ".join(x["achados"])}</span><span class="ef">esforço {x["esforco"]}</span></div>'
            f'<p>{t(curta(x["oque"], 58))} <span class="rc-own">· A: {t(x["A"])}</span></p></div>' for x in C["ACOES"] if x["horizonte"] == hz)
        nz = sum(1 for x in C["ACOES"] if x["horizonte"] == hz)
        cols.append(f'<div class="rcol rcol-{hz.lower()}"><h3>{t(rot)} <small>{nz} ações</small></h3>{cards}</div>')
    n_now = sum(1 for x in C["ACOES"] if x["horizonte"] == "Now")
    add(M.get("titulo_plano", f"Na {M['fases']['Now']}, {n_now} ações atacam o que tem mais risco; o plano inteiro tem {len(C['ACOES'])} ações com dono e critério de pronto"),
        f'<div class="road">{"".join(cols)}</div>', kicker="Plano de ação", notas=NOT.get("plano", "Cada ação tem um único responsável (A), esforço P, M ou G e um critério de pronto escrito como teste."),
        fonte="Plano de ação (relatório técnico §8)", ids=f"{C['ACOES'][0]['id']}..{C['ACOES'][-1]['id']}")

    # como vamos provar
    ex_ids = C.get("PROVA") or [x["id"] for x in C["ACOES"] if x["horizonte"] == "Now"][:5]
    ex = "".join(f'<tr><td class="mono">{x}</td><td class="mono">{" · ".join(ACO[x]["achados"])}</td><td>{t(curta(ACO[x]["oque"], 60))}</td><td><b>{t(ACO[x]["pronto"])}</b></td><td class="sm">{t(ACO[x]["metodo"])}</td></tr>' for x in ex_ids if x in ACO)
    dod = "".join(f"<li>{t(x)}</li>" for x in C.get("DOD", []))
    add("Cada correção só fecha quando o mesmo teste que provou o problema passar", f"""
<table class="tbl prova"><thead><tr><th>Ação</th><th>Achado</th><th>O quê</th><th>Pronto quando…</th><th>Mesmo método do achado</th></tr></thead><tbody>{ex}</tbody></table>
<div class="dod"><h3>Definição de pronto (vale para todas as ações)</h3><ol>{dod}</ol></div>""", kicker="Como vamos provar",
        notas=NOT.get("prova", "Nenhuma ação fecha por declaração: o critério de pronto é o mesmo teste que encontrou o problema."), fonte="Plano de ação e DoD (relatório técnico §8)", ids=", ".join(ex_ids))

    # decisões e insumos
    dec2 = "".join(f'<li><span class="dn sm">{k + 1}</span><div><b>{t(x["d"])}</b><small>Se não: {t(x["senao"])}</small></div></li>' for k, x in enumerate(C.get("DECISOES", [])))
    perg = "".join(f'<tr><td class="c">{p["n"]}</td><td>{t(p["q"])}</td><td class="mono sm">{t(p["fecha"])}</td></tr>' for p in C.get("PERGUNTAS", []))
    ate = f" até {M['decisoes_ate']}" if M.get("decisoes_ate") else ""
    add(f"Decidir{ate}: {len(C.get('DECISOES', []))} decisões e {len(C.get('PERGUNTAS', []))} respostas fecham os números em aberto e destravam o plano", f"""
<div class="two w38">
  <div><p class="lead">Decidir{t(ate)}</p><ol class="declist">{dec2}</ol></div>
  <div><p class="lead">Insumos que precisamos de vocês</p><table class="tbl perg"><thead><tr><th>#</th><th>Pergunta</th><th>O que fecha</th></tr></thead><tbody>{perg}</tbody></table></div>
</div>""", kicker="Decisões e próximos passos", notas=NOT.get("fecho", "Fechamos com o pedido concreto: decisões e respostas que transformam estimativas em números fechados."),
        fonte="Plano de ação e perguntas (relatório técnico)", ids="—")

    # ------------------------------------------------------------ apêndice
    n_corpo = len(SL)
    vit_ids = {a["id"] for a in vit}
    for a in achs:
        if a["id"] in vit_ids:
            continue
        ac = ACO.get(a["acao"], {})
        ev = "".join(f'<li><span class="mono">{e}</span> {t(EVI[e]["tipo"])}</li>' for e in a["evid"] if e in EVI)
        extra = f'<div><dt>Pronto quando</dt><dd>{t(ac.get("pronto", a.get("pronto", "")))}</dd></div>'
        add(a["deck"].get("titulo", a["titulo"]), f'<div class="vit ap">{tres(a)}<div class="vit-side">{meta_achado(a, extra)}<ul class="evl">{ev}</ul></div></div>',
            kicker=f"{a['id']} · {PIL[a['pilar']]}", apendice=True, notas=a["deck"].get("notas", ""), fonte=fonte_achado(a), ids=", ".join([a["id"], *a["evid"], a["acao"]]))

    if av:
        rows = "".join(f'<tr><td class="mono">{t(v["id"])}</td><td><b>{t(v["item"])}</b></td><td>{t(v["porque"])}</td><td>{t(v["como"])}</td></tr>' for v in av)
        add(f"{len(av)} pontos ainda a validar ficam fora da matriz até termos a prova", f"""
<table class="tbl aval{" aval-xl" if len(av) > 6 else ""}"><thead><tr><th>ID</th><th>Item</th><th>Por que importa</th><th>Como validar</th></tr></thead><tbody>{rows}</tbody></table>
<p class="legend">Confiança Baixa (inferido da configuração, sem reprodução nem dado de API) não entra na matriz executiva. Cada item vira achado ou é descartado na próxima rodada.</p>""",
            kicker="A validar", apendice=True, fonte="Tag Manager API, GA Data API, Chrome DevTools", ids=", ".join(v["id"] for v in av))

    if C.get("DEPENDENCIAS"):
        dp = "".join(f'<tr><td class="mono">{t(x["id"])}</td><td><b>{t(x["item"])}</b></td><td>{t(x["porque"])}</td><td class="mono sm">{t(x["destrava"])}</td></tr>' for x in C["DEPENDENCIAS"])
        add(f"{len(C['DEPENDENCIAS'])} dependências {ART["com_a"]} {cliente} destravam achados e ações em aberto", f"""
<table class="tbl aval dep"><thead><tr><th>ID</th><th>O que precisamos de vocês</th><th>Por que</th><th>O que destrava</th></tr></thead><tbody>{dp}</tbody></table>
<p class="legend">“Remover” e “Desativar” são sempre recomendação: nada sai sem a validação de vocês.</p>""", kicker="Dependências", apendice=True, fonte="Relatório técnico §8 (Dependências)", ids="—")

    from comum import MATRIZ
    rows = "".join(f'<tr><th>I = {i}</th>' + "".join(f'<td class="mx">{chip(MATRIZ[(i, p)])}</td>' for p in (1, 2, 3)) + "</tr>" for i in (3, 2, 1))
    lei = M.get("lei_dados", "lei de proteção de dados")
    add("A criticidade sai de uma conta que vocês conseguem refazer: impacto × abrangência, mais modificadores declarados", f"""
<div class="two w50">
  <div>
    <p class="lead">Impacto (I) × Probabilidade/abrangência (P)</p>
    <table class="tbl rub"><thead><tr><th></th><th>P = 1<br><small>raro</small></th><th>P = 2<br><small>condição comum</small></th><th>P = 3<br><small>todo o tráfego / já nos dados</small></th></tr></thead><tbody>{rows}</tbody></table>
    <p class="small">I = o <b>maior</b> impacto entre os 3 pilares (não a média); o pilar desse impacto é o pilar dominante do achado.</p>
  </div>
  <div class="rub-side">
    <h3>Impacto 3 (Alto), por pilar</h3>
    <ul>
      <li><b>Financeiro:</b> gasto evitável relevante na cota 360 ou no sGTM, ou sinal errado alimentando lance de mídia.</li>
      <li><b>Integridade:</b> distorção ≥ 5% em receita/conversões, evento de funil ausente ou duplicado, ou dado pessoal enviado a terceiros.</li>
      <li><b>Performance &amp; Governança:</b> token em texto aberto, acesso indevido, CWV ruim no checkout, publicação sem controle.</li>
    </ul>
    <h3>Modificadores (só para cima, sempre justificados)</h3>
    <ul>
      <li><b>+1 nível</b> se há risco de dado pessoal ({t(lei)}) ou credencial exposta.</li>
      <li><b>+1 nível</b> se o dado alimenta automação de lance (key event importado no Ads/Meta).</li>
    </ul>
    <h3>Confiança (metadado, não nota)</h3>
    <p>Alta = reproduzido + dado de API · Média = só um dos dois · Baixa = inferido da configuração → vai para “a validar”.</p>
  </div>
</div>""", kicker="Rubrica de criticidade", apendice=True, fonte="Metodologia (relatório técnico §4)", ids="—")

    ei = "".join(f'<tr><td class="mono">{e["id"]}</td><td>{t(e["titulo"])}{" <em>(restrito)</em>" if e.get("restrito") else ""}</td><td>{t(e["tipo"])}</td><td>{t(e["periodo"])}</td><td>{t(e["extraido"])}</td></tr>' for e in C["EVIDENCIAS"])
    add(f"{len(C['EVIDENCIAS'])} evidências sustentam os achados, cada uma com fonte, período e data de extração", f"""
<table class="tbl evt{" evt-xl" if len(C["EVIDENCIAS"]) > 20 else ""}"><thead><tr><th>ID</th><th>Evidência</th><th>Fonte</th><th>Período</th><th>Extraído</th></tr></thead><tbody>{ei}</tbody></table>
<p class="legend">Arquivos brutos anexados no relatório técnico. “Restrito” = contém credenciais ou dados da compra de teste; valores redigidos nas entregas.</p>""",
        kicker="Índice de evidências", apendice=True, fonte="Tag Manager API, GA Admin/Data API, Chrome DevTools", ids=f"{C['EVIDENCIAS'][0]['id']}..{C['EVIDENCIAS'][-1]['id']}")

    gl = C.get("GLOSSARIO", [])
    if gl:
        g = "".join(f"<div><dt>{t(k)}</dt><dd>{t(v)}</dd></div>" for k, v in gl[:10])
        add(f"Glossário: os {min(len(gl), 10)} termos técnicos usados nesta apresentação", f'<dl class="gloss">{g}</dl>', kicker="Glossário", apendice=True, fonte="Documentação pública Google, Meta e Apple", ids="—")

    # ------------------------------------------------------------ HTML
    tot = len(SL)
    secs = []
    for n, s in enumerate(SL, 1):
        aria = html.escape(f"{n} de {tot}: {re.sub(r'\s+', ' ', s['titulo'])}", quote=True)
        cls = "slide " + s["cls"] + (" apx" if s["apendice"] else "")
        first_apx = ' data-first-apx="1"' if s["apendice"] and (n - 1) == n_corpo else ""
        tag_apx = '<span class="apx-tag">Apêndice</span>' if s["apendice"] else ""
        kicker = f'<p class="kicker">{tag_apx}{t(s["kicker"])}</p>' if (s["kicker"] or tag_apx) else ""
        h2 = f'<h2 class="sr">{t(s["titulo"])}</h2>' if "capa" in s["cls"] else f'<header class="sh">{kicker}<h2>{t(s["titulo"])}</h2></header>'
        notas = f'<aside class="notes"><b>Notas do apresentador</b><p>{t(s["notas"])}</p></aside>' if s["notas"] else '<aside class="notes"><b>Notas do apresentador</b><p>—</p></aside>' if "capa" in s["cls"] else ""
        ids = f" · IDs citados: {t(s['ids'])}" if s["ids"] and s["ids"] != "—" else ""
        rod = f'<footer class="sf"><span>Fonte: {t(s["fonte"])} · período {t(s["periodo"] or PER)} · extraído {t(M["extraido"])}{ids}</span><span class="pg">{n} / {tot}</span></footer>'
        secs.append(f'<section class="{cls.strip()}" role="group" aria-roledescription="slide" aria-label="{aria}" id="s{n}"{first_apx}>{h2}<div class="content">{s["corpo"]}</div>{rod}{notas}</section>')
    css = (ASSETS / "deck.css").read_text()
    js = (ASSETS / "deck.js").read_text()
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auditoria {esc(cliente)} {esc(M.get('cc', '').upper())}</title>
<meta name="description" content="{esc(M['titulo'])} · {esc(M['rodada'])} {esc(M['versao'])} · {esc(M['data_doc'])}">
<link rel="icon" href="data:,">
<style>{css}</style>
</head>
<body>
<main id="deck" aria-label="Apresentação executiva">
{''.join(secs)}
</main>
<div id="bar" aria-hidden="true"></div>
<div id="cnt" aria-live="polite"></div>
<script>{js}</script>
</body>
</html>
"""
    return doc, [(n, s["apendice"], s["titulo"]) for n, s in enumerate(SL, 1)], n_corpo
