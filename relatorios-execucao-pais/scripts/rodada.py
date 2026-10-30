"""Registra uma rodada de evidências no catálogo do país (idempotente).

Substitui os scripts evidencias_execucao_<ddmm>.py do BR: em vez de um script por rodada, um JSON por rodada,
guardado em <pais>/entregas/_fonte/rodadas/<AAAA-MM-DD>.json (formato em references/conteudo-execucao.md).

  {"rodada": "29/10", "rotulo": "· depois da publicação do ws 777: reteste na live",
   "acoes": {"A-028": {"fase": "F3", "itens": [{"tipo": "print", "arquivo": "evidencias/…", "titulo": "…",
                                               "legenda": "…", "prova": "…", "fonte": "…", "data": "29/10/2026"}]},
             "A-032": {"fase": "F3", "nova": true, "resumo": "…", "metodo": "…", "itens": [...]}}}

- Ação que já tem itens: os itens entram com "rodada" = a data da rodada, no fim da ação (EV já enviados não mudam).
- Ação nova ("nova": true, nada enviado ainda): os itens entram como bloco original (sem rodada).
- Rodar de novo com o mesmo arquivo troca os itens daquela rodada, sem duplicar.

Uso:  python3 rodada.py <pasta-do-pais> <rodada.json>
"""
import json
import sys
from pathlib import Path

from comum import carregar, fonte
from validar import registro

PADRAO = dict(trecho="", resumo_numerico="", sensivel="", obsoleta=False)


def main():
    root, C, _ = carregar(sys.argv[1])
    R = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    rod = R["rodada"]
    reg = registro(root)
    fases = {f["id"] for f in C["FASES"]}
    acoes = {a["id"] for a in C["ACOES"]}
    cats, arqs = {}, {}
    for aid, n in R["acoes"].items():
        if aid not in acoes:
            sys.exit(f"{aid} não está em ACOES do execucao.json: cadastre a ação antes")
        if n["fase"] not in fases:
            sys.exit(f"{aid}: fase {n['fase']} inválida")
        p = fonte(root) / f"evidencias_execucao_{n['fase']}.json"
        arqs[n["fase"]] = p
        cat = cats.setdefault(n["fase"], json.loads(p.read_text(encoding="utf-8")) if p.exists() else {})
        nova = bool(n.get("nova"))
        if nova and any(ev.startswith(f"EV-{aid.replace('-', '')}-") for ev in reg):
            sys.exit(f"{aid} já tem EV enviado ao cliente: não pode ser 'nova'; tire o 'nova' para entrar como rodada")
        c = cat.setdefault(aid, {"resumo": "", "metodo": "", "itens": []})
        for k in ("resumo", "metodo"):
            if n.get(k):
                c[k] = n[k]
        if nova:
            c["itens"] = [i for i in c["itens"] if i.get("rodada") is not None]
        else:
            c["itens"] = [i for i in c["itens"] if i.get("rodada") != rod]
        for i in n["itens"]:
            if not (root / i["arquivo"]).exists():
                sys.exit(f"{aid}: arquivo ausente {i['arquivo']}")
            item = dict(PADRAO, **i)
            item["rodada"] = None if nova else rod
            c["itens"].append(item)
        if nova:  # bloco original antes das rodadas posteriores
            c["itens"].sort(key=lambda i: i.get("rodada") is not None)
    for f, p in arqs.items():
        p.write_text(json.dumps(cats[f], ensure_ascii=False, indent=1), encoding="utf-8")
    if R.get("rotulo"):
        arq = fonte(root) / "execucao.json"
        C2 = json.loads(arq.read_text(encoding="utf-8"))
        C2.setdefault("EVIDENCIAS", {}).setdefault("rodadas", {})[rod] = R["rotulo"]
        arq.write_text(json.dumps(C2, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK:", {aid: len(n["itens"]) for aid, n in R["acoes"].items()}, "· rodada", rod)


if __name__ == "__main__":
    main()
