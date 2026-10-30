"""Gera o relatório técnico e a apresentação executiva de um país a partir de <pais>/entregas/_fonte/conteudo.json.

Uso:
  python3 build.py <pasta-do-pais>                 # valida, gera os 2 HTML base e as cópias -design
  python3 build.py <pasta-do-pais> --entrega v1.0  # idem + copia as versões -design para entregas/entrega-cliente-<hoje>_v1.0/
  python3 build.py <pasta-do-pais> --forcar        # gera mesmo com ERRO na validação (só para rascunho)

O país fica dentro da pasta do cliente, que tem cliente.json e design-system/<marca>/marca.json (Etapa 0 da skill).
Saída em <pais>/entregas/: relatorio-tecnico-<slug>-<cc>[-design].html e apresentacao-executiva-<slug>-<cc>[-design].html.
O que vai ao cliente é sempre a cópia -design (identidade do cliente + assinatura Monks).
"""
import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pais")
    ap.add_argument("--entrega", help="versão, ex.: v1.0")
    ap.add_argument("--forcar", action="store_true")
    a = ap.parse_args()
    root = Path(a.pais).resolve()
    import cliente
    CL = cliente.configurar_design(root)
    import deck
    import design
    import relatorio
    import validar

    C = json.load(open(root / "entregas/_fonte/conteudo.json", encoding="utf-8"))
    erros, avisos = validar.validar(root, C)
    for x in avisos:
        print("AVISO", x)
    for x in erros:
        print("ERRO ", x)
    if erros and not a.forcar:
        sys.exit(f"{len(erros)} erro(s) no conteúdo: corrija ou use --forcar para rascunho")

    cc = C["META"]["cc"].lower()
    ent = root / "entregas"
    sl = CL["slug"]
    rel, rel_d = ent / f"relatorio-tecnico-{sl}-{cc}.html", ent / f"relatorio-tecnico-{sl}-{cc}-design.html"
    dk, dk_d = ent / f"apresentacao-executiva-{sl}-{cc}.html", ent / f"apresentacao-executiva-{sl}-{cc}-design.html"

    doc, anx = relatorio.gerar(root, C)
    rel.write_text(doc, encoding="utf-8")
    print(f"relatório: {rel.name} · {rel.stat().st_size / 1e6:.1f} MB · {len(anx.items)} anexos ({anx.total_mb():.1f} MB) · segredos mascarados: {len(anx.secrets)}")
    doc, slides, n_corpo = deck.gerar(root, C)
    dk.write_text(doc, encoding="utf-8")
    print(f"deck: {dk.name} · {len(slides)} slides ({n_corpo} no corpo + {len(slides) - n_corpo} no apêndice)")
    for n, apx, tit in slides:
        print(f"  {n:>2}{' A' if apx else '  '} {tit}")

    src, out = design.relatorio(rel, rel_d)
    print(f"design relatório: texto visível idêntico: {design.texto(src) == design.texto(out)}")
    src, out = design.deck(dk, dk_d, C["META"]["escopo_curto"])
    print(f"design deck: {dk_d.name} ok")

    if a.entrega:
        pasta = ent / f"entrega-cliente-{datetime.date.today().isoformat()}_{a.entrega}"
        pasta.mkdir(parents=True, exist_ok=True)
        shutil.copy(rel_d, pasta / rel.name)
        shutil.copy(dk_d, pasta / dk.name)
        print(f"entrega: {pasta}")


if __name__ == "__main__":
    main()
