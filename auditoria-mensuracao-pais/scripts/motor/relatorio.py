"""Relatório técnico HTML standalone (estrutura aprovada no BR em 14/10/2026), gerado só a partir do conteudo.json.

Seções: 1 Sumário · 2 Pedido → onde está atendido · 3 Escopo e método · 4 Metodologia de criticidade ·
5 Inventário e cobertura · 6 Matriz · 7 Achados (cartões por pilar) · 8 Plano de ação + dependências ·
9 Reteste · 10 Apêndices (a validar, perguntas, índice de evidências com anexos embutidos, glossário, changelog).
"""
import json
import os
from pathlib import Path

import anexos as AX
from cliente import artigos, carregar as carregar_cliente
from comum import (CRIT_CLS, CRIT_ICON, CRIT_ORD, MATRIZ, PIL_CURTO, PILARES_PADRAO, blocos, esc, f_dec, paras, tabela, txt)

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def badge(crit):
    return f'<span class="crit {CRIT_CLS[crit]}">{CRIT_ICON[crit]} {crit}</span>'


def stamp(C, eid):
    ev = next((x for x in C["EVIDENCIAS"] if x["id"] == eid), None)
    if not ev:
        return ""
    return f'<p class="stamp">{eid} · {esc(ev["tipo"])} · período {esc(ev["periodo"])} · extraído {esc(ev["extraido"])}</p>'


def query_block(C, eid):
    ev = next((x for x in C["EVIDENCIAS"] if x["id"] == eid), None)
    if not ev or not ev.get("query"):
        return ""
    q = json.dumps(ev["query"], ensure_ascii=False, indent=2)
    return f'<details class="raw"><summary>Consulta {eid} ({esc(ev["tipo"])})</summary><pre>{esc(q)}</pre></details>'


def card(C, a, root, moeda):
    PIL = C.get("PILARES", PILARES_PADRAO)
    acao = next((x for x in C["ACOES"] if x["id"] == a["acao"]), {})
    obs = "".join(f"<tr><td>{txt(o)}</td><td>{txt(s)}</td></tr>" for o, s in a.get("obs_esp", []))
    fontes = " · ".join(f'<a href="{esc(u)}" rel="noopener">{esc(n)}</a>' for n, u in a.get("fontes", [])) or "—"
    mods = "; ".join(a.get("mods") or []) or "nenhum"
    evs = " ".join(f'<a class="eid" href="#{x}">{x}</a>' for x in a["evid"])
    imp = a["impacto"]
    tec = blocos(a.get("tecnico"), root, moeda) + "".join(query_block(C, e) for e in a["evid"])
    contorno = a.get("rec_contorno") or "—"
    return f'''
<article class="card" id="{a['id']}" data-crit="{CRIT_CLS[a['crit']]}" data-pilar="{a['pilar'].lower()}">
 <header>
  <div class="cardtop"><span class="cid">{a['id']}</span>{badge(a['crit'])}<span class="pil">Pilar: {esc(PIL[a['pilar']])}</span><span class="st">Status: {esc(a.get('status', 'Aberto'))}</span></div>
  <h3>{esc(a['titulo'])}</h3>
  <p class="calc"><b>I={a['I']}</b> ({esc(PIL_CURTO[a['pilar']])}) · <b>P={a['P']}</b> · Modificadores: {esc(mods)} → <b>{a['crit']}</b> · Confiança: {esc(a['conf'])}</p>
  <p class="ativo"><b>Ativo:</b> {txt(a['ativo'], links=False)}</p>
 </header>
 <dl class="anat">
  <dt>Condição</dt><dd>{txt(a['condicao'])}</dd>
  {f'<dt>Atualização</dt><dd class="rev">{txt(a["revisao"])}</dd>' if a.get('revisao') else ''}
  <dt>Observado × esperado</dt><dd><div class="tw"><table class="oe"><thead><tr><th scope="col">Observado</th><th scope="col">Esperado</th></tr></thead><tbody>{obs}</tbody></table></div></dd>
  <dt>Critério</dt><dd>{txt(a['criterio'])} <span class="src">Fonte: {fontes}</span></dd>
  <dt>Causa</dt><dd>{txt(a['causa'])}</dd>
  <dt>Efeito no negócio</dt><dd>{txt(a['efeito'])}</dd>
  <dt>Impacto</dt><dd><div class="imp"><p><b>Fórmula:</b> <code>{esc(imp['formula'])}</code></p><p><b>Resultado:</b> {txt(imp['valor'])}</p><p><b>Premissa:</b> {txt(imp['premissa'])}</p></div></dd>
  <dt>Evidência</dt><dd>{evs}</dd>
  <dt>Reproduzir</dt><dd><ol>{''.join(f'<li>{txt(s)}</li>' for s in a['reproduzir'])}</ol></dd>
  <dt>Recomendação</dt><dd><p><b>Raiz:</b> {txt(a['rec_raiz'])}</p>{'' if contorno == '—' else f'<p><b>Contorno:</b> {txt(contorno)}</p>'}</dd>
  <dt>Pronto quando</dt><dd class="done">{txt(a['pronto'])}</dd>
  <dt>Ação</dt><dd><a href="#{acao.get('id', '')}">{acao.get('id', '—')}</a> · A: {esc(acao.get('A', ''))} · R: {esc(acao.get('R', ''))} · Esforço: {esc(acao.get('esforco', ''))} · Fase: {esc(acao.get('fase', ''))}</dd>
 </dl>
 {f'<details class="tech" open><summary>Evidência técnica</summary>{tec}</details>' if tec else ''}
</article>'''


def heatmap(C):
    PIL = C.get("PILARES", PILARES_PADRAO)
    head = '<tr><th scope="col">Achado</th>' + "".join(f'<th scope="col">{esc(PIL[p])}</th>' for p in ("FIN", "INT", "PG")) + '<th scope="col">Criticidade</th></tr>'
    body = ""
    for a in sorted(C["ACHADOS"], key=lambda x: (CRIT_ORD[x["crit"]], x["id"])):
        cells = ""
        for p in ("FIN", "INT", "PG"):
            s = a["scores"][p]
            dom = " dom" if p == a["pilar"] else ""
            cells += f'<td class="hm s{s}{dom}">{["", "baixo", "médio", "alto"][s]}{" ●" if dom else ""}</td>'
        body += f'<tr><th scope="row"><a href="#{a["id"]}">{a["id"]}</a> {esc(a["curto"])}</th>{cells}<td>{badge(a["crit"])}</td></tr>'
    return f'<div class="tw"><table class="heat"><caption>Impacto por pilar (1–3); ● = pilar dominante do cartão</caption><thead>{head}</thead><tbody>{body}</tbody></table></div>'


def ixp(C):
    grid = {}
    for a in C["ACHADOS"]:
        grid.setdefault((a["I"], a["P"]), []).append(a)
    h = ('<div class="tw"><table class="ixp"><caption>Matriz I × P (célula = nível base, antes dos modificadores)</caption><thead><tr><th scope="col">I \\ P</th>'
         '<th scope="col">P1 raro</th><th scope="col">P2 condição comum</th><th scope="col">P3 sempre / já nos dados</th></tr></thead><tbody>')
    for i in (3, 2, 1):
        h += f'<tr><th scope="row">I{i}</th>'
        for p in (1, 2, 3):
            ids = " ".join(f'<a href="#{a["id"]}">{a["id"]}</a>' for a in grid.get((i, p), []))
            b = MATRIZ[(i, p)]
            h += f'<td class="cell {CRIT_CLS[b]}"><span class="lvl">{CRIT_ICON[b]} {b}</span><br>{ids}</td>'
        h += "</tr>"
    return h + "</tbody></table></div>"


def evid_index(C, ANX):
    body = []
    for ev in C["EVIDENCIAS"]:
        lis = []
        for f in ANX.by_ev[ev["id"]]:
            it = ANX.items[f]
            mk = f' <span class="mk">· {it["masked"]} credencial(is) mascarada(s)</span>' if it["masked"] else ""
            lis.append(f'<li>{ANX.link(f, "abrir")} <code>{esc(f)}</code> <span class="sz">{f_dec(it["size"] / 1024, 0)} KB · sha256:{it["sha"][:16]}…</span>{mk}</li>')
        fl = f'<ul class="evfiles">{"".join(lis)}</ul>' if lis else f"<code>{esc(ev['arquivo'])}</code> <span class=\"tbd\">arquivo não encontrado</span>"
        if len(lis) > 6:
            fl = f"<details><summary>{len(lis)} arquivos anexados</summary>{fl}</details>"
        restr = ' <span class="restr">acesso restrito</span>' if ev.get("restrito") else ""
        body.append([f'<span id="{ev["id"]}">{ev["id"]}</span>', esc(ev["titulo"]) + restr, esc(ev["tipo"]), esc(ev["periodo"]), esc(ev["extraido"]), fl])
    return tabela(["ID", "Evidência", "Fonte", "Período", "Extraído", "Arquivos anexados (abrir · tamanho original · hash)"], body, cls="evx", html_celulas=True)


def plan(C):
    hz = C["META"]["fases"]
    A = {a["id"]: a for a in C["ACHADOS"]}
    cols = ""
    for h in ("Now", "Next", "Later"):
        items = "".join(f'<li><a href="#{x["id"]}">{x["id"]}</a> {txt(x["oque"], links=False)} <span class="meta">A: {esc(x["A"])} · {x["esforco"]}</span></li>' for x in C["ACOES"] if x["horizonte"] == h)
        cols += f'<div class="hz"><h4>{esc(hz[h])}</h4><ul>{items}</ul></div>'
    rows = []
    for x in C["ACOES"]:
        crits = [A[f]["crit"] for f in x["achados"] if f in A]
        crit = min(crits, key=lambda c: CRIT_ORD[c]) if crits else "BAIXA"
        rows.append([f'<span id="{x["id"]}">{x["id"]}</span>', " ".join(f'<a href="#{f}">{f}</a>' for f in x["achados"]), badge(crit), txt(x["oque"]), esc(x["R"]),
                     f"<b>{esc(x['A'])}</b>", esc(x.get("C", "")), x["esforco"], esc(x["fase"]), txt(x.get("dep", "—")), txt(x["pronto"]), txt(x["metodo"])])
    return (f'<div class="roadmap">{cols}</div>' + tabela(["Ação", "Achados", "Crit.", "O que fazer (raiz)", "R", "A (único)", "C", "Esforço", "Fase", "Depende de", "Critério de pronto (teste)", "Método"],
                                                         rows, cls="plan", legenda="Backlog de ações (RACI com um único A)", html_celulas=True))


def gerar(root, C):
    M = C["META"]
    moeda = M.get("moeda", "R$")
    CL = carregar_cliente(root)
    cliente = M.get("cliente", CL["nome"])
    ART = artigos(CL)
    PIL = C.get("PILARES", PILARES_PADRAO)
    A = C["ACHADOS"]
    ANX = AX.Anexos(str(root), C["EVIDENCIAS"])
    cnt = {k: sum(1 for a in A if a["crit"] == k) for k in ("ALTA", "MÉDIA", "BAIXA")}
    cross = {(c, p): sum(1 for a in A if a["crit"] == c and a["pilar"] == p) for c in cnt for p in PIL}
    inv_secs = C.get("INVENTARIO", {}).get("secoes", [])

    toc = [("s1", "1. Sumário executivo"), ("s2", "2. Pedido → onde está atendido"), ("s3", "3. Escopo, cobertura e método"), ("s4", "4. Metodologia de criticidade"),
           ("s5", "5. Inventário e cobertura"), ("s6", "6. Matriz de Criticidade"), ("s7", "7. Achados detalhados"), ("s8", "8. Plano de ação"), ("s9", "9. Reteste"), ("s10", "10. Apêndices")]
    subs = {"s5": [(f"s5-{k + 1}", f"5.{k + 1} {s['titulo']}") for k, s in enumerate(inv_secs)] + [("s5-ok", f"5.{len(inv_secs) + 1} Verificado e OK")],
            "s7": [("s7-fin", "7.1 Financeiro"), ("s7-int", "7.2 Integridade"), ("s7-pg", "7.3 Performance & Gov.")], "s8": [("s8-dep", "Dependências")]}
    tochtml = "".join(f'<li><a href="#{i}">{t}</a>' + ("<ol>" + "".join(f'<li><a href="#{j}">{esc(u)}</a></li>' for j, u in subs[i]) + "</ol>" if i in subs else "") + "</li>" for i, t in toc)

    S = C.get("SUMARIO", {})
    kpis = blocos([{"tipo": "kpis", "itens": S.get("kpis", [])}], root, moeda) if S.get("kpis") else ""
    tops = "".join(f'<li>{badge(a["crit"])} <a href="#{a["id"]}">{a["id"]}</a> {esc(a["titulo"])}</li>' for a in A if a["id"] in S.get("top", []))
    nows = "".join(f'<li><a href="#{x["id"]}">{x["id"]}</a> {txt(x["oque"], links=False)} (A: {esc(x["A"])}, esforço {x["esforco"]})</li>' for x in C["ACOES"] if x["horizonte"] == "Now")
    crossrows = [[esc(PIL[p])] + [str(cross[(c, p)]) for c in ("ALTA", "MÉDIA", "BAIXA")] for p in PIL] + [["<b>Total</b>"] + [f"<b>{cnt[c]}</b>" for c in ("ALTA", "MÉDIA", "BAIXA")]]
    s1 = f'''<section class="sec" id="s1"><h2>1. Sumário executivo</h2>
<p><b>Resposta curta:</b> {txt(S.get("resposta_curta", ""))}</p>{kpis}
<h3>Achados mais críticos</h3><ul>{tops}</ul>
{tabela(["Pilar", "▲ ALTA", "■ MÉDIA", "▼ BAIXA"], crossrows, legenda=f"{len(A)} achados por criticidade × pilar dominante", html_celulas=True)}
<h3>Ações da {esc(M["fases"]["Now"])}</h3><ol>{nows}</ol>
{"".join(paras(p) for p in S.get("paragrafos", []))}
{f'<p class="note">{txt(S["nota_escopo"])}</p>' if S.get("nota_escopo") else ""}</section>'''

    rtm = tabela(["ID", "Pedido (PEDIDO.md)", "Onde está atendido", "Status", "Observação"],
                 [[r["id"], esc(r["pedido"]), txt(r["onde"]), f'<span class="st-{r["status"]}">{r["status"]}</span>', txt(r["nota"])] for r in C["RTM"]], html_celulas=True)
    reun = "".join(f"<li>{txt(x)}</li>" for x in C.get("REUNIAO", []))
    s2 = f'''<section class="sec" id="s2"><h2>2. O que foi pedido e onde está atendido</h2>
{f"<p>{'Alinhamento de ' + esc(M['reuniao']) + ': o' if M.get('reuniao') else 'No alinhamento, o'} cliente pediu</p><ul>{reun}</ul>" if reun else ""}
{paras(M.get("combinado", "Combinado: começar pela conta principal, validar o formato e depois escalar para os demais ativos."))}{rtm}</section>'''

    E = C.get("ESCOPO", {})
    s3 = f'''<section class="sec" id="s3"><h2>3. Escopo, cobertura e método</h2>
<div class="tw"><table class="kv"><tbody>
<tr><td>Ativos</td><td>{txt(M['escopo'])}</td></tr>
<tr><td>Fontes</td><td>{txt(E.get('fontes', ''))}</td></tr>
<tr><td>Período dos dados</td><td>{esc(M['periodo'])} · extração em {esc(M['extraido'])}</td></tr>
<tr><td>Limitações</td><td>{txt(E.get('limitacoes', ''))}</td></tr>
<tr><td>Fora desta rodada</td><td>{txt(E.get('fora', '—'))}</td></tr>
</tbody></table></div></section>'''

    s4 = f'''<section class="sec" id="s4"><h2>4. Metodologia de criticidade</h2>
<p><b>Passo 1 — Impacto (I), 1 a 3, por pilar.</b> O impacto do achado é o <b>maior</b> entre os três pilares do pedido; esse pilar vira o pilar do cartão.</p>
{tabela(["Nível", PIL["FIN"], PIL["INT"], PIL["PG"]], [
        ["3 Alto", "Gasto evitável relevante em cota 360 ou infra sGTM; sinal errado alimentando lance de mídia", "Receita/conversões distorcidas ≥ 5%; purchase ausente/duplicado; dado pessoal enviado a terceiros", "Token em texto aberto; acesso indevido; CWV acima de “bom” no checkout; publicação sem controle"],
        ["2 Médio", "Custo evitável moderado ou localizado", "Distorção 1–5% ou em parâmetro secundário (items, currency)", "Container sobrecarregado; nomenclatura que impede manutenção; CWV “precisa melhorar”"],
        ["1 Baixo", "Custo marginal", "Distorção < 1% ou cosmética", "Higiene (pastas, nomes, sobras)"]])}
<p><b>Passo 2 — Probabilidade/Abrangência (P).</b> 3 = em todo o tráfego do fluxo ou já presente nos dados da API; 2 = sob condição comum (um navegador, app × web, adicional marcado); 1 = raro.</p>
<p><b>Passo 3 — Matriz I × P</b> (ver <a href="#s6">seção 6</a>). <b>Passo 4 — Modificadores (só para cima):</b> +1 nível para risco de dado pessoal ({esc(M.get("lei_dados", "lei de proteção de dados"))}) ou credencial exposta; +1 se o dado alimenta lance de mídia. Nunca rebaixar sem registrar “risco aceito por &lt;nome&gt;, &lt;data&gt;”. <b>Passo 5 — Confiança</b> (metadado): Alta = reproduzido + dado da API; Média = um dos dois; Baixa = inferido da configuração → vai para “A validar”.</p></section>'''

    cov = "".join(f'<div><span class="ok">✓ OK</span> <b>{esc(x["item"])}</b><br>{txt(x["detalhe"])} <a href="#{x["evid"]}">{x["evid"]}</a></div>' for x in C.get("VERIFICADO_OK", []))
    secs5 = "".join(f'<h3 id="s5-{k + 1}">5.{k + 1} {esc(s["titulo"])}</h3>{blocos(s.get("blocos"), root, moeda)}{"".join(stamp(C, e) for e in s.get("evid", []))}' for k, s in enumerate(inv_secs))
    s5 = f'''<section class="sec" id="s5"><h2>5. Inventário e cobertura</h2>{secs5}
<h3 id="s5-ok">5.{len(inv_secs) + 1} Grade de cobertura: verificado e OK</h3><div class="cov">{cov}</div></section>'''

    s6 = f'''<section class="sec" id="s6"><h2>6. Matriz de Criticidade</h2>
<p>{cnt['ALTA']} Alta, {cnt['MÉDIA']} Média, {cnt['BAIXA']} Baixa. A ordem de execução está no plano de ação.</p>{heatmap(C)}{ixp(C)}</section>'''

    chips = ('<span class="lbl">Criticidade</span>' + "".join(f'<button class="chip" data-k="crit" data-v="{v}" aria-pressed="false">{CRIT_ICON[k]} {k}</button>' for k, v in (("ALTA", "alta"), ("MÉDIA", "media"), ("BAIXA", "baixa")))
             + '<span class="lbl">Pilar</span>' + "".join(f'<button class="chip" data-k="pilar" data-v="{p.lower()}" aria-pressed="false">{esc(PIL_CURTO[p])}</button>' for p in PIL)
             + '<button class="btn" id="clear">Limpar</button><button class="btn" id="openall">Expandir tudo</button><button class="btn" id="closeall">Recolher tudo</button><span id="live" aria-live="polite"></span>')
    s7 = (f'<section class="sec" id="s7"><h2>7. Achados detalhados</h2><p>Cada cartão segue condição → critério → causa → efeito → evidência → reprodução → recomendação → pronto quando. '
          f'Dados extraídos em {esc(M["extraido"])}; período {esc(M["periodo"])}.</p><div class="filters noprint" role="group" aria-label="Filtros">{chips}</div>')
    for gid, gt, p in (("s7-fin", "7.1 " + PIL["FIN"], "FIN"), ("s7-int", "7.2 " + PIL["INT"], "INT"), ("s7-pg", "7.3 " + PIL["PG"], "PG")):
        s7 += f'<h2 id="{gid}" style="margin-top:28px">{esc(gt)}</h2>' + "".join(card(C, a, root, moeda) for a in sorted([a for a in A if a["pilar"] == p], key=lambda x: (CRIT_ORD[x["crit"]], x["id"])))
    s7 += "</section>"

    dod = "".join(f"<li>{txt(x)}</li>" for x in C.get("DOD", []))
    deps = tabela(["ID", f"O que precisamos {ART['da']} {cliente}", "Por que", "O que destrava", "Status"],
                  [[f'<span id="{d["id"]}">{d["id"]}</span>', esc(d["item"]), txt(d["porque"]), txt(d["destrava"]), esc(d.get("status", "Aberta"))] for d in C.get("DEPENDENCIAS", [])], html_celulas=True)
    s8 = f'''<section class="sec" id="s8"><h2>8. Plano de ação</h2>{paras(M.get("plano_intro", ""))}
{plan(C)}<h3>Definition of Done (vale para toda ação)</h3><ol>{dod}</ol>
<h3 id="s8-dep">Dependências {ART["com_a"]} {esc(cliente)}</h3><p>O que precisamos para fechar achados e destravar ações. “Remover” e “Desativar” são sempre recomendação sujeita à validação.</p>{deps}</section>'''

    ACO = {x["id"]: x for x in C["ACOES"]}
    RT = {r["achado"]: r for r in C.get("RETESTE", [])}
    s9 = f'''<section class="sec" id="s9"><h2>9. Reteste</h2><p>Um achado só fecha quando o teste do “pronto quando” passa com o mesmo método da evidência.</p>
{tabela(["Achado", "Crit.", "Status", "Data do reteste", "Método", "Resultado"],
        [[f'<a href="#{a["id"]}">{a["id"]}</a>', badge(a["crit"]), esc(RT.get(a["id"], {}).get("status", a.get("status", "Aberto"))), esc(RT.get(a["id"], {}).get("data", "—")),
          txt(ACO.get(a["acao"], {}).get("metodo", "—")), txt(RT.get(a["id"], {}).get("resultado", "—"))] for a in sorted(A, key=lambda x: (CRIT_ORD[x["crit"]], x["id"]))], html_celulas=True)}</section>'''

    val = tabela(["ID", "Item", "Por que importa", "Como fechar"], [[v["id"], esc(v["item"]), txt(v["porque"]), txt(v["como"])] for v in C.get("A_VALIDAR", [])], html_celulas=True)
    perg = "".join(f'<li>{txt(p["q"])} <span class="src">Fecha: {txt(p["fecha"])}</span></li>' for p in C.get("PERGUNTAS", []))
    s10 = f'''<section class="sec" id="s10"><h2>10. Apêndices</h2>
<h3 id="s10-validar">10.1 A validar (fora da matriz)</h3>{val}
<h3>10.2 Perguntas {ART["para_a"]} {esc(cliente)}</h3><ol>{perg}</ol>
<h3 id="s10-evid">10.3 Índice de evidências</h3><p>Todos os arquivos de evidência citados estão <b>anexados dentro deste HTML</b> ({len(ANX.items)} arquivos): “abrir” mostra a imagem ou o JSON completo, com busca, e “Baixar” salva o arquivo. Não é preciso ter a pasta <code>evidencias/</code>. O hash SHA-256 (16 primeiros caracteres) é o do arquivo bruto original. Capturas viraram JPEG, sem outra alteração; nos JSON, valores de token e chave de API foram substituídos por “[MASCARADO]”.</p>{evid_index(C, ANX)}
<h3>10.4 Glossário</h3>{tabela(["Termo", "Significado"], [[esc(a), txt(b)] for a, b in C.get("GLOSSARIO", [])], html_celulas=True)}
<h3>10.5 Changelog</h3>{tabela(["Versão", "Data", "Mudança"], [[esc(a), esc(b), txt(c)] for a, b, c in C.get("CHANGELOG", [])], html_celulas=True)}</section>'''

    head = f'''<header class="doc"><p style="margin:0;font-size:13px;color:var(--muted)">{esc(M['rodada'])} · Relatório técnico · {esc(M['versao'])}</p><h1>{esc(M['titulo'])}</h1>
<div class="metagrid"><div><b>Data:</b> {esc(M['data_doc'])}</div><div><b>Período dos dados:</b> {esc(M['periodo'])}</div><div><b>Extração:</b> {esc(M['extraido'])}</div><div><b>Autoria:</b> {esc(M['autores'])}</div><div style="grid-column:1/-1"><b>Escopo:</b> {txt(M['escopo'], links=False)}</div></div>
<p class="conf">{esc(M['confidencialidade'])}</p></header>'''
    css = AX.CSS + (ASSETS / "relatorio.css").read_text()
    js = AX.JS + (ASSETS / "relatorio.js").read_text()
    doc = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório Técnico {esc(cliente)} {esc(M.get("cc", "").upper())}</title><meta name="description" content="{esc(M['titulo'])}: achados com evidência, Matriz de Criticidade e plano de ação.">
<style>{css}</style></head><body><div class="layout"><nav class="toc" aria-label="Sumário"><ol>{tochtml}</ol></nav><main>{head}{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}{s9}{s10}
<p style="font-size:12px;color:var(--muted)">{esc(M['titulo'])} · {esc(M['versao'])} · {esc(M['data_doc'])} · dados {esc(M['periodo'])}</p></main></div><script>{js}</script>{ANX.blocks()}</body></html>'''
    return doc, ANX
