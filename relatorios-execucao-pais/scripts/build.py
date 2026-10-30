"""Gera o relatório de evidências e o deck de execução de um país a partir de <pais>/entregas/_fonte/execucao.json.

Ordem fixa: valida → evidências (define as faixas EV) → deck (cita as faixas) → cópia -design do deck.

Uso:
  python3 build.py <pasta-do-pais>                        # gera em <pais>/entregas/
  python3 build.py <pasta-do-pais> --saida <dir>          # rascunho fora do vault (não toca em entregas/)
  python3 build.py <pasta-do-pais> --entrega v1.8 [--incluir arq ...]
        # idem + congela entregas/entrega-cliente-<hoje>_v1.8/ (deck -design com o nome simples, evidências e os
        # arquivos de --incluir) e grava os EV enviados em _fonte/ev_registro.json
  python3 build.py <pasta-do-pais> --registrar            # só grava o registro de EV (semear o que já foi enviado)
  --forcar                                                # gera mesmo com ERRO (só rascunho; nunca com --entrega)

O que vai ao cliente: apresentacao-execucao-<slug>-<cc>-design.html (copiada sem o -design) e
relatorio-evidencias-execucao-<slug>-<cc>.html, que já sai com a identidade do cliente (cliente.json → marca.json).
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

import deck
import evidencias
from comum import carregar, design, fonte, nomes
from validar import conferir_registro, registro, validar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pais")
    ap.add_argument("--saida")
    ap.add_argument("--entrega")
    ap.add_argument("--incluir", nargs="*", default=[])
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    if a.forcar and a.entrega:
        sys.exit("--forcar não combina com --entrega")

    root, C, CAT = carregar(a.pais)
    E, A = validar(root, C, CAT)
    for x in A:
        print("AVISO", x)
    D = design(root)
    N = nomes(C)
    out = Path(a.saida).resolve() if a.saida else root / "entregas"
    out.mkdir(parents=True, exist_ok=True)

    doc, ref_ev, res, ev_mapa = evidencias.gerar(root, C, CAT, D)
    E += conferir_registro(root, ev_mapa)
    for x in E:
        print("ERRO ", x)
    if E and not a.forcar:
        sys.exit(f"{len(E)} erro(s): corrija o conteúdo (ou --forcar com --saida para rascunho)")
    p_ev = out / N["ev"]
    p_ev.write_text(doc, encoding="utf-8")
    print(f"evidências: {p_ev} · {len(doc) / 1e6:.1f} MB · {res['acoes']} ações · {res['prints']} prints · {res['dados']} dados")

    doc, slides, n_corpo = deck.gerar(root, C, ref_ev, N["ev"])
    p_dk, p_dd = out / N["deck"], out / N["deck_d"]
    p_dk.write_text(doc, encoding="utf-8")
    D.deck(p_dk, p_dd, C["META"]["escopo_curto"])
    print(f"deck: {p_dd} · {len(slides)} slides ({n_corpo} no corpo + {len(slides) - n_corpo} no apêndice)")
    for n, apx, tit in slides:
        print(f"  {n:>2}{' A' if apx else '  '} {tit}")

    if a.entrega or a.registrar:
        reg = registro(root)
        reg.update(ev_mapa)
        (fonte(root) / "ev_registro.json").write_text(json.dumps(dict(sorted(reg.items())), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"registro de EV: {len(reg)} evidências marcadas como enviadas")
    if a.entrega:
        if a.saida:
            sys.exit("--entrega grava na pasta do país; rode sem --saida")
        if a.entrega != C["META"]["versao"]:
            print(f"AVISO --entrega {a.entrega} diferente de META.versao {C['META']['versao']}")
        pasta = root / "entregas" / f"entrega-cliente-{datetime.date.today().isoformat()}_{a.entrega}"
        pasta.mkdir(parents=True, exist_ok=True)
        shutil.copy(p_dd, pasta / N["deck"])
        shutil.copy(p_ev, pasta / N["ev"])
        for x in a.incluir:
            px = Path(x) if Path(x).is_absolute() else root / x
            shutil.copy(px, pasta / px.name)
        print(f"entrega: {pasta}")
        for f in sorted(pasta.iterdir()):
            print(f"  {f.name}")


if __name__ == "__main__":
    main()
