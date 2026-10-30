"""Configuração do cliente: lê <cliente>/cliente.json (a pasta-mãe dos países) e aponta o design para a marca.

Cada cliente é uma pasta com cliente.json, design-system/<marca>/marca.json e uma pasta por país.
Esquema e exemplo em references/cliente-schema.md. A Etapa 0 da skill cria os dois arquivos.
"""
import json
import os
import re
import sys
from pathlib import Path

PADRAO = {
    "prefixo": "XX",
    "dominios_internos": [],
    "acessos_protegidos": {},
    "conta_auditoria": "",
    "projeto_cota": "",
    "gmp_org": "",
    "genero": "f",
    "teste": {"marcador": "Data Test"},
}


def raiz(pais):
    return Path(pais).resolve().parent


def carregar(pais):
    """cliente.json da pasta-mãe do país, com os padrões preenchidos."""
    arq = raiz(pais) / "cliente.json"
    if not arq.exists():
        sys.exit(f"cliente.json não encontrado em {arq.parent}: rode a Etapa 0 da skill (identidade e configuração do cliente)")
    c = {**PADRAO, **json.loads(arq.read_text(encoding="utf-8"))}
    for k in ("nome", "slug", "marca"):
        if not c.get(k):
            sys.exit(f"cliente.json sem '{k}'")
    return c


def configurar_design(pais):
    """Define MARCA_DIR para o design.py e devolve o cliente."""
    c = carregar(pais)
    d = raiz(pais) / c["marca"]
    if not (d / "marca.json").exists():
        sys.exit(f"marca.json não encontrado em {d}: rode a Etapa 0 (identidade do cliente)")
    os.environ["MARCA_DIR"] = str(d)
    return c


def id_achado_re(prefixo):
    """Padrão dos IDs de achado do cliente (ex.: SF-PII-04)."""
    return rf"{re.escape(prefixo)}-(?:FIN|DUP|INT|PII|PERF|GOV)-\d{{2}}"


def email_ok_re(c):
    """E-mails que podem aparecer no texto: Monks, domínios internos do cliente e fictícios."""
    doms = ["monks\\.com", "example\\.com", "teste[a-z]*\\.com"] + [re.escape(d) for d in c["dominios_internos"]]
    return re.compile(r"@(" + "|".join(doms) + r")$", re.I)


def artigos(c):
    """Concordância com o nome do cliente: genero "f" (a Smart Fit) ou "m" (o Itaú)."""
    a = "a" if c.get("genero", "f") == "f" else "o"
    return {"a": a, "da": "d" + a, "com_a": "com " + a, "para_a": "para " + a, "pela": "pel" + a}
