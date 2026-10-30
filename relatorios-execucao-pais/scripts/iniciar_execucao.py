"""Cria o execucao.json de um país a partir do plano de ação aprovado (conteudo.json da auditoria).

Todas as ações nascem "nao" (não iniciada), com o critério de pronto do plano no RETESTE e um deck mínimo
(capa, onde estamos, um quadro por fase, pedidos, como vamos provar, índice). Vitrines e "resposta em uma página"
entram quando houver ação concluída para mostrar. Textos marcados com [preencher] precisam de revisão.
Não sobrescreve um execucao.json existente.

Uso:  python3 iniciar_execucao.py <pasta-do-pais>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "auditoria-mensuracao-pais/scripts/motor"))
from cliente import carregar as carregar_cliente  # noqa: E402

LEI = {"br": "LGPD", "mx": "dado pessoal"}
TEMAS = {"F1": "Segurança, {lei} e acessos", "F2": "Integridade dos dados, custo 360 e ativos", "F3": "Performance, limpeza e governança contínua"}
HORIZ = {"Now": "F1", "Next": "F2", "Later": "F3"}


def main():
    root = Path(sys.argv[1]).resolve()
    dest = root / "entregas/_fonte/execucao.json"
    if dest.exists():
        sys.exit(f"já existe: {dest} (edite em vez de recriar)")
    A = json.loads((root / "entregas/_fonte/conteudo.json").read_text(encoding="utf-8"))
    M = A["META"]
    nome = carregar_cliente(root)["nome"]
    cc = M["cc"].lower()
    ach = {x["id"]: x for x in A["ACHADOS"]}
    ev_de = {}
    for x in A["ACHADOS"]:
        ev_de[x["id"]] = ", ".join(x.get("evid", [])[:2]) if isinstance(x.get("evid"), list) else str(x.get("evid", ""))
    rel = f"relatório técnico {M.get('versao', '')}".strip()
    lei = M.get("lei_dados", LEI.get(cc, "dado pessoal")).split()[0]
    fases_meta = M.get("fases", {})
    FASES = [{"id": f, "nome": f"Fase {f[1]}", "tema": TEMAS[f].format(lei=lei),
              "janela": fases_meta.get(h, "").split("·")[-1].strip() or "[preencher]"} for h, f in HORIZ.items()]
    ACOES, RET = [], []
    for a in A["ACOES"]:
        sf = a["achados"][0]
        x = ach.get(sf, {})
        ACOES.append(dict(
            id=a["id"], fase=HORIZ.get(a.get("horizonte"), "F1"), achado=sf, crit=x.get("crit", "MÉDIA"),
            titulo=x.get("curto") or a["oque"][:70],
            antes=x.get("condicao", "[preencher: o que acontecia, com o número do diagnóstico]"),
            feito="", negocio=x.get("efeito", "[preencher]"), status="nao",
            proximo=f"Owner: {a.get('A', '[preencher]')}", evid="", data="",
            rel=f"{sf} · {ev_de.get(sf, '')}".rstrip(" ·")))
        if a.get("pronto"):
            RET.append(dict(id=a["id"], criterio=a["pronto"], resultado=f"PLACEHOLDER_reteste_{a['id'].lower().replace('-', '')}"))
    pais = M.get("pais", cc.upper())
    META = dict(cc=cc.upper(), pais=pais, pais_curto=cc.upper(),
                titulo=f"Auditoria de mensuração {nome} {cc.upper()}: execução do plano de ação",
                capa_titulo=f"Auditoria {nome} {cc.upper()}: o que já mudou e o que muda para o negócio",
                autores="Monks", versao="v0.1", atualizado=M.get("data_doc", "[preencher]"),
                escopo=M.get("escopo", "[preencher]"), escopo_curto=M.get("escopo_curto", "[preencher]"),
                confidencialidade=f"Confidencial · uso interno {nome} e Monks",
                diagnostico=f"diagnóstico aprovado em [preencher] ({rel})",
                rel_tecnico=rel, rel_tecnico_curto=f"relatório {M.get('versao', '')}".strip(), periodo_coleta="[preencher]")
    S = [dict(tipo="capa", notas="Este deck acompanha a execução do plano aprovado. Cada ação aparece com o que acontecia, o que fizemos (com evidência) e o que muda para o negócio.",
              fonte="Plano de ação e evidências da execução", ids="—"),
         dict(tipo="fases", titulo="Fase 1: {F1_concluida} das {F1_total} ações concluídas", kicker="Onde estamos",
              notas="Visão das três fases.", fonte="Status por ação do plano de ação", ids="—")]
    for f in FASES:
        S.append(dict(tipo="quadro", fase=f["id"], xl=sum(a["fase"] == f["id"] for a in ACOES) > 9,
                      titulo=f"{f['nome']} ação a ação: {{{f['id']}_concluida}} de {{{f['id']}_total}} concluídas",
                      kicker=f"{f['nome']} · {f['tema']}", notas="", fonte="Status por ação do plano de ação"))
    S += [dict(tipo="pedidos", titulo="Com {pedidos} passos de vocês, as 3 fases fecham", kicker="O que depende de vocês",
               notas="Fechamos com o pedido concreto, em ordem de prioridade.", fonte="Plano de ação"),
          dict(tipo="reteste", titulo="Depois da publicação, cada correção só fecha quando o mesmo teste do achado passar na live",
               kicker="Como vamos provar", notas="Nenhuma ação fecha por declaração.", fonte="Definição de pronto do plano de ação"),
          dict(tipo="indice", fases=[f["id"] for f in FASES], titulo="Índice de evidências da execução", apendice=True)]
    out = dict(META=META, FASES=FASES, ACOES=ACOES, PEDIDOS=[], RETESTE=RET, DECK=dict(slides=S),
               EVIDENCIAS=dict(rodadas={}, fora={}, mascara={}, avisos=[]))
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {dest} · {len(ACOES)} ações ({', '.join(f'{f['id']}={sum(a['fase'] == f['id'] for a in ACOES)}' for f in FASES)}) · {len(RET)} critérios de pronto")


if __name__ == "__main__":
    main()
