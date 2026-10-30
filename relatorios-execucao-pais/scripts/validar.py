"""Validação do conteúdo da execução antes do build: ERRO bloqueia, AVISO só informa.

Uso:  python3 validar.py <pasta-do-pais>
"""
import json
import re
import sys

from comum import CRITS, PH_RE, carregar, contagens, fonte, preencher

META_OBRIG = ("cc", "titulo", "capa_titulo", "versao", "atualizado", "escopo", "escopo_curto", "confidencialidade", "diagnostico")
ACAO_OBRIG = ("id", "fase", "achado", "crit", "titulo", "antes", "feito", "negocio", "status", "proximo")
TIPOS_SLIDE = {"capa", "fases", "bluf", "quadro", "vitrine", "pedidos", "tres_blocos", "reteste", "indice", "prints"}
TOKEN_META = re.compile(r"EAA[A-Za-z0-9]{40,}|access_token=[A-Za-z0-9._-]{12,}|Bearer\s+[A-Za-z0-9._-]{20,}", re.I)
LONGO = re.compile(r"\b(?=[A-Za-z0-9_]*\d)(?=[A-Za-z0-9_]*[A-Z])(?=[A-Za-z0-9_]*[a-z])[A-Za-z0-9_]{32,}\b")  # mistura de maiúscula, minúscula e dígito
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
EMAIL_OK = re.compile(r"datatest|data\.test|monks\.com|example\.|teste|test@", re.I)
FEITO_MAX_COM_PRINT = 330  # acima disso o print sai do slide da vitrine (visto no BR em 19/10)


def textos(obj, caminho=""):
    """Todos os textos do conteúdo/catálogo, com o caminho, menos nomes de arquivo."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("arquivo", "print", "evid"):
                continue
            yield from textos(v, f"{caminho}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from textos(v, f"{caminho}[{i}]")
    elif isinstance(obj, str):
        yield caminho, obj


def registro(root):
    p = fonte(root) / "ev_registro.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def validar(root, C, CAT):
    E, A = [], []
    M = C["META"]
    for k in META_OBRIG:
        if not M.get(k):
            E.append(f"META.{k} vazio")
    fases = {f["id"] for f in C["FASES"]}
    ids = [a.get("id") for a in C["ACOES"]]
    for d in {i for i in ids if ids.count(i) > 1}:
        E.append(f"ação duplicada: {d}")
    ACO = {a["id"]: a for a in C["ACOES"]}
    for a in C["ACOES"]:
        for k in ACAO_OBRIG:
            if a.get(k) in (None, "") and k != "feito":
                E.append(f"{a.get('id')}: campo {k} vazio")
        if a["fase"] not in fases:
            E.append(f"{a['id']}: fase {a['fase']} não existe em FASES")
        if a["status"] not in C["STATUS"]:
            E.append(f"{a['id']}: status {a['status']} inválido ({', '.join(C['STATUS'])})")
        if a["crit"] not in CRITS:
            E.append(f"{a['id']}: crit {a['crit']} inválida")
        if a.get("print"):
            if not (root / a["print"]).exists():
                E.append(f"{a['id']}: print ausente {a['print']}")
            if not a.get("legenda"):
                E.append(f"{a['id']}: print sem legenda")
    for r in C["RETESTE"]:
        if r["id"] not in ACO:
            E.append(f"RETESTE {r['id']}: ação inexistente")
    ret_ids = {r["id"] for r in C["RETESTE"]}
    fecha = " ".join(p.get("fecha", "") for p in C["PEDIDOS"])
    for a in C["ACOES"]:
        if a["status"] == "publicar" and a["id"] not in fecha:
            A.append(f"{a['id']} está 'publicar' e não aparece em nenhum PEDIDO")
        if a["status"] == "concluida" and a["id"] not in CAT and not a.get("evid"):
            A.append(f"{a['id']} concluída sem evidência no catálogo")
        if a["status"] == "publicar" and a["id"] not in ret_ids:
            A.append(f"{a['id']} espera publicação e não tem linha no RETESTE (critério de pronto)")

    # slides
    cnt = contagens(C)
    vit_print = set()
    for n, s in enumerate(C["DECK"]["slides"], 1):
        tp = s.get("tipo")
        if tp not in TIPOS_SLIDE:
            E.append(f"slide {n}: tipo {tp} desconhecido")
            continue
        for i in s.get("acoes", []):
            if i not in ACO:
                E.append(f"slide {n}: ação {i} não existe")
        if tp == "quadro" and s.get("fase") not in fases:
            E.append(f"slide {n}: quadro com fase inválida")
        if tp not in ("capa",) and not s.get("titulo"):
            E.append(f"slide {n} ({tp}): sem título")
        for k in ("titulo", "notas"):
            try:
                preencher(s.get(k), cnt)
            except KeyError as e:
                E.append(f"slide {n}: {e}")
        if tp == "vitrine" and len(s.get("acoes", [])) == 1:
            vit_print.add(s["acoes"][0])
    for i in vit_print:
        a = ACO.get(i)
        if a and a.get("print") and len(a.get("feito", "")) > FEITO_MAX_COM_PRINT:
            A.append(f"{i}: 'feito' com {len(a['feito'])} caracteres e print na vitrine; confira no headless se o print cabe")
    apx = [bool(s.get("apendice")) for s in C["DECK"]["slides"]]
    if True in apx and False in apx[apx.index(True):]:
        E.append("slide de corpo depois do apêndice: o apêndice precisa ficar no fim")

    # catálogo
    rods = C["EVIDENCIAS"].get("rodadas", {})
    for aid, c in CAT.items():
        if aid not in ACO:
            E.append(f"catálogo: ação {aid} não está em ACOES")
        for it in c.get("itens", []):
            if not (root / it["arquivo"]).exists():
                E.append(f"catálogo {aid}: arquivo ausente {it['arquivo']}")
            for k in ("tipo", "titulo", "legenda", "prova", "fonte", "data"):
                if not it.get(k):
                    A.append(f"catálogo {aid}: item '{it.get('titulo', it['arquivo'])}' sem {k}")
            if it.get("rodada") and it["rodada"] not in rods:
                A.append(f"catálogo {aid}: rodada {it['rodada']} sem rótulo em EVIDENCIAS.rodadas")

    # segredos e dado pessoal
    for cam, s in list(textos(C)) + list(textos(CAT)):
        if TOKEN_META.search(s):
            E.append(f"possível token em texto aberto em {cam}")
        elif LONGO.search(s):
            A.append(f"sequência longa (token? hash?) em {cam}: {LONGO.search(s).group(0)[:16]}…")
        for m in EMAIL.finditer(s):
            if not EMAIL_OK.search(m.group(0)):
                A.append(f"e-mail em {cam}: confira se é fictício ({m.group(0)[:3]}…)")

    ph = sorted({m.group(0) for _, s in textos(C) for m in PH_RE.finditer(s)})
    if ph:
        A.append(f"{len(ph)} marcador(es) 'após a publicação' ainda abertos: {', '.join(ph)}")
    return E, A


def conferir_registro(root, ev_mapa):
    """EV já enviado ao cliente (ev_registro.json, gravado no --entrega) não pode mudar de arquivo nem sumir."""
    E = []
    for ev, arq in registro(root).items():
        if ev not in ev_mapa:
            E.append(f"{ev} foi enviado ({arq}) e sumiu do relatório: item removido ou marcado como obsoleta/fora?")
        elif ev_mapa[ev] != arq:
            E.append(f"{ev} mudou de arquivo: enviado {arq} → agora {ev_mapa[ev]} (renumeração: itens novos entram como rodada no fim)")
    return E


if __name__ == "__main__":
    root, C, CAT = carregar(sys.argv[1])
    E, A = validar(root, C, CAT)
    for x in A:
        print("AVISO", x)
    for x in E:
        print("ERRO ", x)
    print(f"{len(E)} erro(s), {len(A)} aviso(s)")
    sys.exit(1 if E else 0)
