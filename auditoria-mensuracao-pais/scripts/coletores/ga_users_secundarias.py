"""Consolida usuários de contas GA só-Standard (sem Data Access Report) usando sinais indiretos:
uso da mesma pessoa na conta principal 360 + última alteração de config no Change History da própria conta.

Uso: python3 scripts/ga_users_secundarias.py evidencias/ga4/_acessos/<data> <contaPrincipal> <conta> [<conta> ...]
Saída: evidencias/ga4/_acessos/<data>/secundarias_consolidado.json
"""
import json
import os
import sys

base, principal, contas = sys.argv[1], sys.argv[2], sys.argv[3:]
L = lambda a, f: json.load(open(os.path.join(base, a, f)))  # noqa: E731
main = {u["email"]: u for u in L(principal, "usuarios_consolidado.json")["usuarios"]}
uso = {}
classif = os.path.join(base, "..", "..", "..", "_uso_ativos", os.path.basename(base), "classificacao.json")
if os.path.exists(classif):
    uso = {r["id"]: r for r in json.load(open(classif))["ga"]}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapi import CLIENTE, CONTA_AUDITORIA, INTERNOS  # noqa: E402

out = []
for a in contas:
    acc = L(a, "account.json")
    props = {p["name"]: p for p in L(a, "properties.json")}
    ch = L(a, "changeHistory.json") or []
    ult_alt, criadores = {}, {}
    for e in ch:
        who, t = e.get("userActorEmail"), e["changeTime"][:10]
        if who and t > ult_alt.get(who, ""):
            ult_alt[who] = t
        for c in e.get("changes", []):
            r = c.get("resourceAfterChange") or {}
            if c["action"] == "CREATED" and ("property" in r or "account" in r):
                k = list(r)[0]
                criadores[r[k]["name"]] = {"por": who, "em": t, "nome_original": r[k].get("displayName")}
    users = {}
    for b in L(a, "accessBindings_account.json") or []:
        users.setdefault(b["user"].lower(), {"conta": [], "props": {}})["conta"] = [r.split("/")[1] for r in b["roles"]]
    for p, bs in (L(a, "accessBindings_properties.json") or {}).items():
        for b in bs or []:
            users.setdefault(b["user"].lower(), {"conta": [], "props": {}})["props"][props[p]["displayName"]] = [r.split("/")[1] for r in b["roles"]]
    props_mortas = all(uso.get(p.split("/")[1], {}).get("recomendacao", "").startswith("Desativar") for p in props)
    linhas = []
    for email, u in users.items():
        dom = email.split("@")[-1]
        m = main.get(email)
        sinal = m and m["ultimo_acesso"]
        alt = ult_alt.get(email)
        recente = max(filter(None, [sinal, alt]), default=None)
        tipo = "Interno" if dom in INTERNOS else "Externo"
        papeis = set(u["conta"]) | {r for rs in u["props"].values() for r in rs}
        motivos = []
        if email == CONTA_AUDITORIA:
            rec, motivos = "Manter (temporário)", ["Admin da auditoria Monks: remover ao encerrar"]
        elif props_mortas:
            rec = "Remover (com a conta)"
            motivos.append("todas as propriedades da conta são candidatas a desativar")
        elif recente is None or recente < "2025-10-13":
            rec = "Remover"
            motivos.append("nenhum sinal de atividade no GA há mais de 1 ano" if recente else "nenhum sinal de atividade no GA")
        elif recente < "2026-07-15":
            rec = "Revisar"
            motivos.append("último sinal há mais de 90 dias")
        else:
            rec = "Manter"
        if tipo == "Externo" and "admin" in papeis and email != CONTA_AUDITORIA:
            motivos.append("externo com Admin")
            rec = "Revisar" if rec == "Manter" else rec
        linhas.append({
            "email": email, "tipo": tipo, "papel_conta": u["conta"], "papeis_props": u["props"],
            "uso_principal": sinal, "faixa_principal": m["faixa"] if m else "Sem vínculo com a conta principal",
            "ultima_alteracao": alt, "ultimo_sinal": recente, "recomendacao": rec, "motivos": motivos,
        })
    out.append({
        "id": a, "nome": acc["displayName"].strip(), "criada": acc["createTime"][:10],
        "criador_conta": criadores.get(acc["name"]),
        "historico_desde": min((e["changeTime"][:10] for e in ch), default=None),
        "propriedades": [{"id": p.split("/")[1], "nome": v["displayName"], "criada": v["createTime"][:10],
                          "criador": criadores.get(p), "uso": uso.get(p.split("/")[1], {}).get("status"),
                          "eventos_30d": uso.get(p.split("/")[1], {}).get("eventos_30d"),
                          "recomendacao_prop": uso.get(p.split("/")[1], {}).get("recomendacao")} for p, v in props.items()],
        "usuarios": sorted(linhas, key=lambda x: (x["recomendacao"], x["email"])),
    })
json.dump(out, open(os.path.join(base, "secundarias_consolidado.json"), "w"), ensure_ascii=False, indent=1)
for c in out:
    print("##", c["nome"], c["criada"], "criador:", c["criador_conta"], "hist desde", c["historico_desde"])
    for p in c["propriedades"]:
        print("   P", p)
    for u in c["usuarios"]:
        print("   ", u["email"], u["papel_conta"] or u["papeis_props"], u["ultimo_sinal"], u["recomendacao"], u["motivos"])
