"""Peças comuns do motor da execução: leitura do conteúdo e do catálogo, contagens por fase e nomes dos arquivos.

O conteúdo de um país fica em <pais>/entregas/_fonte/execucao.json (esquema em references/conteudo-execucao.md)
e o catálogo de evidências em <pais>/entregas/_fonte/evidencias_execucao_*.json (uma chave por ação).
Caminhos de arquivo no conteúdo e no catálogo são relativos à pasta do país.
"""
import json
import os
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
AUDITORIA = SKILL.parent / "auditoria-mensuracao-pais"  # CSS/JS do deck, design.py e cliente.py vêm de lá (fonte única)
sys.path.append(str(AUDITORIA / "scripts/motor"))  # no fim: validar.py/comum.py daqui têm prioridade
import cliente as _cliente  # noqa: E402

CL = {}  # cliente.json do país carregado (preenchido por carregar)

STATUS_PADRAO = {
    "concluida": ["st-ok", "✓ Concluída"],
    "publicar": ["st-pub", "◐ Validada · falta publicar"],
    "andamento": ["st-parc", "◐ Em andamento"],
    "decisao": ["st-dec", "◇ Decisão do cliente"],
    "espera": ["st-pend", "‖ Em espera"],
    "revisao": ["st-dec", "↺ Achado revisado"],
    "nao": ["st-pend", "○ Não iniciada"],
}


def status_padrao():
    """Rótulos de status; o de decisão leva o nome do cliente (◇ Decisão Smart Fit)."""
    st = {k: list(v) for k, v in STATUS_PADRAO.items()}
    if CL.get("nome"):
        st["decisao"][1] = f"◇ Decisão {CL['nome']}"
    return st


CRITS = ("ALTA", "MÉDIA", "BAIXA")
PH_RE = re.compile(r"PLACEHOLDER_[A-Za-z0-9_]*")


def fonte(root):
    return Path(root) / "entregas/_fonte"


def carregar(pais):
    """Devolve (root, C, CAT). CAT junta todos os evidencias_execucao_*.json da pasta _fonte."""
    root = Path(pais).resolve()
    CL.clear()
    CL.update(_cliente.carregar(root))
    arq = fonte(root) / "execucao.json"
    if not arq.exists():
        sys.exit(f"conteúdo não encontrado: {arq}")
    C = json.loads(arq.read_text(encoding="utf-8"))
    C.setdefault("STATUS", status_padrao())
    for k in ("PEDIDOS", "RETESTE"):
        C.setdefault(k, [])
    C.setdefault("DECK", {"slides": []})
    C.setdefault("EVIDENCIAS", {})
    CAT = {}
    for p in sorted(fonte(root).glob("evidencias_execucao_*.json")):
        CAT.update(json.loads(p.read_text(encoding="utf-8")))
    return root, C, CAT


def arquivos_catalogo(root):
    return sorted(fonte(root).glob("evidencias_execucao_*.json"))


def nomes(C):
    cc = C["META"]["cc"].lower()
    return {
        "deck": f"apresentacao-execucao-{CL['slug']}-{cc}.html",
        "deck_d": f"apresentacao-execucao-{CL['slug']}-{cc}-design.html",
        "ev": f"relatorio-evidencias-execucao-{CL['slug']}-{cc}.html",
    }


def design(root):
    """Importa o design.py da skill de auditoria apontando para a marca do cliente (cliente.json → marca.json)."""
    _cliente.configurar_design(root)
    import design as D
    D.ART = _cliente.artigos(CL)
    return D


def da_fase(C, f):
    return [a for a in C["ACOES"] if a["fase"] == f]


def contagens(C):
    """Números para os títulos: {F1_total}, {F1_concluida}, {F1_prontas}, {F2_andaram}, {pedidos}, {publicacoes}…"""
    c = {"acoes": len(C["ACOES"]), "pedidos": len(C["PEDIDOS"]),
         "publicacoes": sum(p["o"].startswith("Publicar") for p in C["PEDIDOS"])}
    for f in C["FASES"]:
        acs = da_fase(C, f["id"])
        fid = f["id"]
        c[f"{fid}_total"] = len(acs)
        for s in C["STATUS"]:
            c[f"{fid}_{s}"] = sum(a["status"] == s for a in acs)
        c[f"{fid}_prontas"] = sum(a["status"] in ("concluida", "publicar") for a in acs)
        c[f"{fid}_andaram"] = sum(a["status"] not in ("nao", "espera") for a in acs)
    return c


TOKEN_RE = re.compile(r"\{(\w+)(?:\|([^|{}]*)\|([^{}]*))?\}")


def preencher(s, cnt):
    """{chave} vira o número; {chave|singular|plural} vira a forma certa para o número."""
    if not s:
        return s

    def sub(m):
        k = m.group(1)
        if k not in cnt:
            raise KeyError(f"contagem desconhecida no título: {{{k}}} (disponíveis: {', '.join(sorted(cnt))})")
        n = cnt[k]
        if m.group(2) is None:
            return str(n)
        return m.group(2) if n == 1 else m.group(3)
    return TOKEN_RE.sub(sub, s)


def ev_id(aid, n):
    return f"EV-{aid.replace('-', '')}-{n:02d}"
