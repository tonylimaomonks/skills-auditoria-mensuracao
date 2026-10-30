"""Confere o conteudo.json antes do build: estrutura, rastreabilidade, rubrica, segredos e dado pessoal.

Uso: python3 validar.py <pasta-do-pais>     (código de saída 1 se houver ERRO)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anexos import resolve  # noqa: E402
import comum  # noqa: E402
from cliente import carregar as carregar_cliente, email_ok_re  # noqa: E402
from comum import MATRIZ, PH_RE, PILARES_PADRAO, SOBE  # noqa: E402

OBRIG = ["META", "ACHADOS", "ACOES", "EVIDENCIAS", "RTM"]
META_OBRIG = ["pais", "cc", "titulo", "rodada", "versao", "data_doc", "periodo", "extraido", "escopo", "escopo_curto", "autores", "confidencialidade", "fases", "moeda"]
ACH_OBRIG = ["id", "pilar", "scores", "I", "P", "crit", "conf", "titulo", "curto", "ativo", "evid", "condicao", "obs_esp", "criterio", "causa", "efeito",
             "impacto", "reproduzir", "rec_raiz", "pronto", "acao", "deck"]
ACO_OBRIG = ["id", "achados", "oque", "R", "A", "esforco", "horizonte", "pronto", "metodo", "fase"]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CURP = re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d\b")
TOKEN = re.compile(r"\bEAA[A-Za-z0-9]{30,}|\b[A-Za-z0-9_\-]{40,}\b")


def textos(o, caminho=""):
    if isinstance(o, str):
        yield caminho, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from textos(v, f"{caminho}.{k}" if caminho else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from textos(v, f"{caminho}[{i}]")


def validar(root, C):
    erros, avisos = [], []
    CL = carregar_cliente(root)
    comum.configurar_ids(CL["prefixo"])
    EMAIL_OK = email_ok_re(CL)
    for k in OBRIG:
        if k not in C:
            erros.append(f"falta a chave {k}")
    if erros:
        return erros, avisos
    M = C["META"]
    for k in META_OBRIG:
        if k not in M:
            erros.append(f"META.{k} ausente")
    PIL = C.get("PILARES", PILARES_PADRAO)
    ach = {a.get("id"): a for a in C["ACHADOS"]}
    aco = {a.get("id"): a for a in C["ACOES"]}
    evi = {e.get("id"): e for e in C["EVIDENCIAS"]}
    conhecidos = set(ach) | set(aco) | set(evi) | {x["id"] for k in ("DEPENDENCIAS", "A_VALIDAR", "RTM") for x in C.get(k, [])}

    for a in C["ACHADOS"]:
        aid = a.get("id", "?")
        for k in ACH_OBRIG:
            if k not in a:
                erros.append(f"{aid}: campo {k} ausente")
        if any(k not in a for k in ("scores", "I", "P", "pilar", "crit")):
            continue
        if a["pilar"] not in PIL:
            erros.append(f"{aid}: pilar {a['pilar']} inválido")
        if max(a["scores"].values()) != a["I"]:
            erros.append(f"{aid}: I={a['I']} diferente do maior score por pilar {a['scores']}")
        if a["scores"].get(a["pilar"]) != a["I"]:
            avisos.append(f"{aid}: o pilar {a['pilar']} não é o de maior impacto")
        base = MATRIZ.get((a["I"], a["P"]))
        teto = base
        for _ in a.get("mods") or []:
            teto = SOBE[teto]
        ordem = ["BAIXA", "MÉDIA", "ALTA"]
        if base and a["crit"] not in ordem[ordem.index(base): ordem.index(teto) + 1] and not a.get("risco_aceito"):
            erros.append(f"{aid}: crit {a['crit']} fora do intervalo da rubrica (base {base}, com {len(a.get('mods') or [])} modificador(es) até {teto}); se rebaixou, registre risco_aceito")
        for e in a.get("evid", []):
            if e not in evi:
                erros.append(f"{aid}: evidência {e} não está em EVIDENCIAS")
        if a.get("acao") not in aco:
            erros.append(f"{aid}: ação {a.get('acao')} não está em ACOES")
        for k in ("oque", "quanto", "fazer"):
            if k not in a.get("deck", {}):
                erros.append(f"{aid}: deck.{k} ausente")
        if "baixa" in str(a.get("conf", "")).lower()[:6]:
            avisos.append(f"{aid}: confiança Baixa deveria ir para A_VALIDAR, fora da matriz")
        imp = a.get("impacto", {})
        for k in ("formula", "valor", "premissa"):
            if not imp.get(k):
                erros.append(f"{aid}: impacto.{k} vazio (regra: nenhum achado sem impacto quantificado com premissa)")
    for x in C["ACOES"]:
        for k in ACO_OBRIG:
            if k not in x:
                erros.append(f"{x.get('id', '?')}: campo {k} ausente")
        for f in x.get("achados", []):
            if f not in ach:
                erros.append(f"{x['id']}: achado {f} inexistente")
        if x.get("horizonte") not in M.get("fases", {}) and x.get("horizonte") != "Fora":
            erros.append(f"{x['id']}: horizonte {x.get('horizonte')} não está em META.fases")
    usadas = ({e for a in C["ACHADOS"] for e in a.get("evid", [])} | {v.get("evid") for v in C.get("VERIFICADO_OK", [])}
              | {e for s in C.get("INVENTARIO", {}).get("secoes", []) for e in s.get("evid", [])})
    for e in C["EVIDENCIAS"]:
        for k in ("id", "titulo", "tipo", "arquivo", "periodo", "extraido"):
            if k not in e:
                erros.append(f"{e.get('id', '?')}: campo {k} ausente")
        if "arquivo" in e and not resolve(str(root), e):
            erros.append(f"{e['id']}: nenhum arquivo encontrado para '{e['arquivo']}' (caminho relativo à pasta do país)")
        if e.get("id") not in usadas:
            avisos.append(f"{e.get('id')}: evidência não citada por nenhum achado nem no verificado OK")
    for r in C["RTM"]:
        if r.get("status") not in ("Atendido", "Parcial", "Pendente"):
            erros.append(f"{r.get('id')}: status {r.get('status')} inválido")
    vit = [a for a in C["ACHADOS"] if a.get("vitrine")]
    if not 3 <= len(vit) <= 14:
        avisos.append(f"{len(vit)} vitrines no deck (o BR teve 14 no corpo; abaixo de 3 a apresentação fica rasa)")

    for cam, s in textos(C):
        if cam.startswith(("EVIDENCIAS", "INVENTARIO")) and ("arquivo" in cam):
            continue
        for m in comum.ID_RE.findall(s):
            if m.startswith((CL["prefixo"] + "-", "A-", "E-", "D-", "V-")) and m not in conhecidos and not cam.startswith("CHANGELOG"):
                avisos.append(f"{cam}: cita {m}, que não existe no conteúdo")
        if PH_RE.search(s):
            avisos.append(f"{cam}: PLACEHOLDER pendente")
        for em in EMAIL.findall(s):
            if not EMAIL_OK.search(em):
                erros.append(f"{cam}: e-mail '{em}' no texto (só e-mails corporativos ou fictícios podem aparecer)")
        if CPF.search(s) or CURP.search(s):
            erros.append(f"{cam}: parece documento pessoal (CPF/CURP) no texto")
        if TOKEN.search(s) and "http" not in s:
            avisos.append(f"{cam}: sequência longa que pode ser token/segredo: confira antes de enviar")
    return erros, sorted(set(avisos))


def main():
    root = os.path.abspath(sys.argv[1])
    C = json.load(open(os.path.join(root, "entregas/_fonte/conteudo.json")))
    erros, avisos = validar(root, C)
    for a in avisos:
        print("AVISO", a)
    for e in erros:
        print("ERRO ", e)
    print(f"{len(erros)} erro(s), {len(avisos)} aviso(s)")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
