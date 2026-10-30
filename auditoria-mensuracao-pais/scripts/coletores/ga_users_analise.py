"""Consolida accessBindings + Data Access Report de uma conta GA em uma tabela por usuário.

Uso: python3 scripts/ga_users_analise.py evidencias/ga4/_acessos/<data>/<accountId>
Saída: <dir>/usuarios_consolidado.json
"""
import collections
import datetime as dt
import json
import os
import sys

d = sys.argv[1]
L = lambda f: json.load(open(os.path.join(d, f)))  # noqa: E731
HOJE = dt.datetime.now(dt.timezone.utc)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapi import CLIENTE, CONTA_AUDITORIA, INTERNOS  # noqa: E402
RANK = ["no-cost-data", "no-revenue-data", "viewer", "analyst", "marketer", "editor", "admin"]
# Regras fixas (BR, 13/10/2026): nunca sugerir remover a ponta do cliente; Admin da auditoria é temporário.
# Pontos focais do cliente em cliente.json → acessos_protegidos (acrescentar o de cada país).
PROTEGIDOS = CLIENTE.get("acessos_protegidos", {})
AUDITORIA = {CONTA_AUDITORIA: "Admin da auditoria Monks: temporário, remover ao encerrar"} if CONTA_AUDITORIA else {}

props = {p["name"].split("/")[1]: p for p in L("properties.json")}
users = collections.defaultdict(lambda: {"conta": [], "props": {}, "apps": collections.Counter(),
                                         "ult": None, "ult_ui": None, "ult_api": None, "qtd": 0,
                                         "props_usadas": set()})
for b in L("accessBindings_account.json"):
    users[b["user"].lower()]["conta"] = [r.split("/")[1] for r in b["roles"]]
for pname, binds in L("accessBindings_properties.json").items():
    for b in binds or []:
        users[b["user"].lower()]["props"][pname.split("/")[1]] = [r.split("/")[1] for r in b["roles"]]
com_acesso = set(users)

prop_uso = collections.defaultdict(lambda: {"ult": None, "usuarios": set(), "qtd": 0})
# Conta sem nenhuma propriedade 360 não tem Data Access Report (a API devolve 400): ninguém é mensurável por uso,
# e a recomendação passa a se apoiar em papel, domínio e na última alteração de config (Change History).
_rep = L("accessReport_account.json") if os.path.exists(os.path.join(d, "accessReport_account.json")) else None
SEM_LOG = not _rep
for r in (_rep or {}).get("rows", []):
    email, pnome, pid, app, ts = [v["value"] for v in r["dimensionValues"]]
    t = dt.datetime.fromtimestamp(int(ts) / 1e6, dt.timezone.utc)
    n = int(r["metricValues"][0]["value"])
    u = users[email.lower()]
    u["qtd"] += n
    u["props_usadas"].add(pid)
    app = "Interface GA" if app == "(not applicable)" else app
    u["apps"][app] += n
    for k in ["ult"] + (["ult_ui"] if app == "Interface GA" else ["ult_api"]):
        if u[k] is None or t > u[k]:
            u[k] = t
    pu = prop_uso[pid]
    pu["qtd"] += n
    pu["usuarios"].add(email.lower())
    if pu["ult"] is None or t > pu["ult"]:
        pu["ult"] = t


def dias(t):
    return None if t is None else max(0, (HOJE - t).days)


out = []
for email, u in users.items():
    dom = email.split("@")[-1]
    papeis = set(u["conta"]) | {r for rs in u["props"].values() for r in rs}
    topo = max((r for r in papeis if r in RANK), key=RANK.index, default=None)
    dd = dias(u["ult"])
    # Data Access Report só existe para propriedades 360: quem só tem grant em Standard não é mensurável
    so_standard = SEM_LOG or (not u["conta"] and u["props"] and all(
        props.get(k, {}).get("serviceLevel") != "GOOGLE_ANALYTICS_360" for k in u["props"]))
    if email not in com_acesso:
        faixa = "Sem acesso concedido"
    elif so_standard and dd is None:
        faixa = "Não mensurável (só Standard)"
    elif dd is None:
        faixa = "Nunca usou (24m)"
    elif dd <= 90:
        faixa = "Ativo (≤90d)"
    elif dd <= 365:
        faixa = "Pouco uso (91-365d)"
    else:
        faixa = "Inativo (>365d)"
    tipo = ("Interno" if dom in INTERNOS else "Conta de serviço" if "gserviceaccount" in dom
            else "Pessoal (gmail)" if dom == "gmail.com" else "Google" if dom == "google.com" else "Externo")
    so_conector = u["ult"] is not None and u["ult_ui"] is None
    motivos = []
    if email not in com_acesso:
        rec = "—"
    elif faixa.startswith("Não mensurável"):
        rec = "Validar com o cliente"
        motivos.append("conta sem 360: sem log de uso pela API" if SEM_LOG else "acesso só a propriedade Standard, sem log de uso pela API")
    elif faixa in ("Nunca usou (24m)", "Inativo (>365d)"):
        rec = "Remover"
        motivos.append("sem acesso em 24 meses" if dd is None else f"último acesso há {dd} dias")
    elif faixa == "Pouco uso (91-365d)":
        rec = "Revisar"
        motivos.append(f"último acesso há {dd} dias")
    else:
        rec = "Manter"
    if tipo == "Pessoal (gmail)" and rec != "—":
        rec = "Remover" if rec != "Manter" else "Revisar"
        motivos.append("conta pessoal fora do domínio corporativo")
    if topo in ("admin", "editor") and tipo != "Interno" and rec != "—":
        motivos.append(f"externo com papel {topo}")
        rec = "Revisar" if rec == "Manter" else rec
    if so_conector and rec != "Remover":
        motivos.append("uso só via conector (" + ", ".join(a for a in u["apps"]) + "): remover quebra relatórios")
    if email in PROTEGIDOS:
        rec, motivos = "Validar com o cliente", [PROTEGIDOS[email]]
    elif email in AUDITORIA:
        rec, motivos = "Manter (temporário)", [AUDITORIA[email]]
    out.append({
        "email": email, "dominio": dom, "tipo": tipo,
        "papel_conta": u["conta"], "papeis_props": {props.get(k, {}).get("displayName", k): v for k, v in u["props"].items()},
        "papel_max": topo, "ultimo_acesso": u["ult"] and u["ult"].date().isoformat(), "dias": dd,
        "ultimo_ui": u["ult_ui"] and u["ult_ui"].date().isoformat(),
        "ultimo_api": u["ult_api"] and u["ult_api"].date().isoformat(),
        "acessos": u["qtd"], "apps": dict(u["apps"].most_common()),
        "props_usadas": sorted(props.get(p, {}).get("displayName", p) for p in u["props_usadas"]),
        "faixa": faixa, "recomendacao": rec, "motivos": motivos,
    })
out.sort(key=lambda x: (RANK.index(x["papel_max"]) * -1 if x["papel_max"] else 1, x["email"]))

props_out = []
for pid, p in props.items():
    pu = prop_uso.get(pid)
    props_out.append({
        "id": pid, "nome": p["displayName"], "criada": p.get("createTime", "")[:10],
        "tipo": "Subpropriedade" if p.get("parent", "").startswith("properties/") else "Propriedade",
        "nivel": p.get("serviceLevel", "").replace("GOOGLE_ANALYTICS_", ""),
        "grants_diretos": len((L("accessBindings_properties.json").get(p["name"]) or [])),
        "ultimo_acesso": pu and pu["ult"].date().isoformat(), "dias": pu and dias(pu["ult"]),
        "usuarios_distintos": pu and len(pu["usuarios"]), "acessos": pu and pu["qtd"],
    })
# Change History (~2 anos): criador de propriedades e última alteração de config por usuário
criadores, ult_alt = {}, {}
if os.path.exists(os.path.join(d, "changeHistory.json")):
    for e in L("changeHistory.json") or []:
        a, t = e.get("userActorEmail"), e["changeTime"][:10]
        if a and t > ult_alt.get(a, ""):
            ult_alt[a] = t
        for ch in e.get("changes", []):
            res = ch.get("resourceAfterChange") or {}
            if ch["action"] == "CREATED" and "property" in res:
                criadores[res["property"]["name"].split("/")[1]] = {"por": a, "em": t}
for x in out:
    x["ultima_alteracao_config"] = ult_alt.get(x["email"])
for x in props_out:
    x["criador"] = criadores.get(x["id"])
acc = L("account.json")
json.dump({"conta": {"id": acc["name"], "nome": acc["displayName"], "criada": acc["createTime"][:10]},
           "janela_log": None if SEM_LOG else f"{(HOJE - dt.timedelta(days=720)).date()} a {HOJE.date()}", "usuarios": out, "propriedades": props_out},
          open(os.path.join(d, "usuarios_consolidado.json"), "w"), ensure_ascii=False, indent=1)
c = collections.Counter((x["faixa"], x["recomendacao"]) for x in out)
for k, v in sorted(c.items()):
    print(k, v)
print(collections.Counter(x["papel_max"] for x in out if x["faixa"] != "Sem acesso concedido"))
