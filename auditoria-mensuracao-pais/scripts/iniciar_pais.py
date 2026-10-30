"""Etapa 0: prepara a pasta de um país para a auditoria (idempotente; não sobrescreve nada que já exista, exceto os coletores).

O país fica dentro da pasta do cliente (<cliente>/<pais>/), que deve ter cliente.json e design-system/<marca>/marca.json
(criados na Etapa 0 · identidade e configuração do cliente; ver references/identidade-cliente.md e cliente-schema.md).

Uso: python3 iniciar_pais.py <pasta-do-pais> --cc mx --nome "México"
  - cria o esqueleto (achados, checklists, entregas/_fonte, evidencias/{gtm,ga4,gmp,chrome,_uso_ativos}, historico-mensagens, jira, scripts)
  - copia os coletores canônicos da skill para <pais>/scripts/ (sobrescreve: a skill é a fonte)
  - cria PEDIDO.md: o pedido do cliente (<cliente>/PEDIDO.md, se existir), senão o de um país irmão, senão o modelo da skill
  - cria auditoria-estado.md
"""
import argparse
import datetime
import json
import re
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
PASTAS = ["achados", "checklists", "entregas/_fonte", "entregas/_rascunhos", "evidencias/gtm", "evidencias/ga4", "evidencias/gmp",
          "evidencias/chrome", "evidencias/_uso_ativos", "historico-mensagens", "jira", "scripts"]


def pedido(p, nome):
    """Texto do PEDIDO.md e de onde veio."""
    cli = p.parent / "PEDIDO.md"
    if cli.exists():
        return f"> Pedido do cliente (`../PEDIDO.md`), aplicado a {nome}.\n\n" + cli.read_text(), "pedido do cliente"
    for irmao in sorted(p.parent.glob("*/PEDIDO.md")):
        if irmao.parent != p:
            s = irmao.read_text()
            if s.startswith("> "):  # já é cópia de outro país: usa só o corpo
                s = s.split("\n\n", 1)[-1]
            return (f"> Mesmo pedido de `../{irmao.parent.name}/PEDIDO.md`. Confira os nomes de país no texto.\n\n" + s,
                    f"cópia de {irmao.parent.name}")
    return (SKILL / "assets/pedido-modelo.md").read_text().replace("{PAIS}", nome), "modelo da skill (confirmar com o cliente)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pais")
    ap.add_argument("--cc", required=True)
    ap.add_argument("--nome", required=True)
    a = ap.parse_args()
    p = Path(a.pais).resolve()
    cfg = p.parent / "cliente.json"
    cliente = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
    for d in PASTAS:
        (p / d).mkdir(parents=True, exist_ok=True)
    copiados = []
    for f in sorted((SKILL / "scripts/coletores").glob("*.py")):
        shutil.copy(f, p / "scripts" / f.name)
        copiados.append(f.name)
    ped = p / "PEDIDO.md"
    origem = "já existia"
    if not ped.exists():
        txt, origem = pedido(p, a.nome)
        ped.write_text(txt)
    est = p / "auditoria-estado.md"
    if not est.exists():
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        modelo = (SKILL / "references/estado.md").read_text()
        corpo = modelo.split("```markdown\n", 1)[1].rsplit("```", 1)[0]
        corpo = corpo.replace("<País>", a.nome).replace("AAAA-MM-DD HH:MM", agora).replace("AAAA-MM-DD", agora[:10])
        corpo = re.sub(r"<Cliente>", cliente.get("nome", "<Cliente>"), corpo)
        est.write_text(corpo)
    print(f"{p.name}: esqueleto ok · coletores: {', '.join(copiados)} · PEDIDO.md: {origem} · estado: {est.name}")
    if not cliente:
        print(f"ATENÇÃO: {cfg} não existe. Faça a Etapa 0 · identidade e configuração do cliente antes de coletar.")


if __name__ == "__main__":
    main()
