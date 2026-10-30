"""Consolida permissões GTM (user_permissions) e cruza com o uso do GA.

Uso: python3 scripts/gtm_users_analise.py evidencias/gtm/_acessos/<data>/<accountId> evidencias/ga4/_acessos/<data>/<gaAccountId>
Saída: <gtm dir>/usuarios_consolidado.json
"""
import json
import os
import sys

gd, gad = sys.argv[1], sys.argv[2]
perms = json.load(open(os.path.join(gd, "user_permissions.json")))
acc = json.load(open(os.path.join(gd, "account.json")))
inv = json.load(open(os.path.join(os.path.dirname(__file__), "..", "evidencias", "gtm", "_inventario_containers.json")))
conts = {c["path"].split("/")[-1]: c for c in inv if c["path"].startswith(acc["path"] + "/")}
ga = {u["email"]: u for u in json.load(open(os.path.join(gad, "usuarios_consolidado.json")))["usuarios"]}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gapi import CLIENTE, CONTA_AUDITORIA, INTERNOS  # noqa: E402
NIVEL = ["read", "edit", "approve", "publish"]

out = []
for p in perms:
    email = p["emailAddress"].lower()
    dom = email.split("@")[-1]
    cs = {c["containerId"]: c["permission"] for c in p.get("containerAccess", []) if c.get("permission") != "noAccess"}
    admin = p.get("accountAccess", {}).get("permission") == "admin"
    pub = [conts[c]["publicId"] for c, v in cs.items() if v == "publish" and c in conts]
    g = ga.get(email)
    gfaixa = ("Usa GA via grupo" if g and g["faixa"] == "Sem acesso concedido"
              else g["faixa"] if g else "Sem acesso ao GA")
    tipo = "Interno" if dom in INTERNOS else "Pessoal (gmail)" if dom == "gmail.com" else "Externo"
    motivos = []
    if g and g["faixa"] in ("Inativo (>365d)", "Nunca usou (24m)"):
        rec = "Revisar"
        motivos.append(f"também sem uso do GA ({g['faixa']})")
    elif not g:
        rec = "Revisar"
        motivos.append("sem acesso direto ao GA, uso do GTM não mensurável")
    else:
        rec = "Manter"
    if tipo != "Interno" and (admin or pub):
        motivos.append("externo com " + ("Admin da conta" if admin else f"Publicar em {len(pub)} containers"))
        rec = "Revisar"
    if tipo == "Pessoal (gmail)":
        motivos.append("conta pessoal")
        rec = "Revisar"
    if email == CONTA_AUDITORIA:
        rec, motivos = "Manter (temporário)", ["Admin da auditoria Monks: remover ao encerrar"]
    out.append({
        "email": email, "dominio": dom, "tipo": tipo, "admin_conta": admin,
        "containers": {conts[c]["publicId"] + " · " + conts[c]["name"].strip(): v for c, v in cs.items() if c in conts},
        "n_containers": len(cs), "n_publish": len(pub),
        "maior": max(cs.values(), key=NIVEL.index) if cs else None,
        "ga_faixa": gfaixa, "ga_ultimo": g and g["ultimo_acesso"], "recomendacao": rec, "motivos": motivos,
    })
out.sort(key=lambda x: (not x["admin_conta"], -x["n_publish"], x["email"]))
json.dump({"conta": {"id": acc["accountId"], "nome": acc["name"]},
           "containers": [{"id": k, "publicId": v["publicId"], "nome": v["name"].strip(), "contexto": v["usageContext"],
                           "usuarios": sum(1 for u in perms for c in u.get("containerAccess", [])
                                           if c["containerId"] == k and c.get("permission") != "noAccess"),
                           "publicam": sum(1 for u in perms for c in u.get("containerAccess", [])
                                           if c["containerId"] == k and c.get("permission") == "publish")}
                          for k, v in conts.items()],
           "usuarios": out}, open(os.path.join(gd, "usuarios_consolidado.json"), "w"), ensure_ascii=False, indent=1)
import collections  # noqa: E402
print(len(out), collections.Counter(x["tipo"] for x in out), "admins", sum(x["admin_conta"] for x in out))
print(collections.Counter(x["recomendacao"] for x in out), collections.Counter(x["ga_faixa"] for x in out))
for x in out:
    if x["admin_conta"] or x["tipo"] != "Interno":
        print(x["email"], x["admin_conta"], x["maior"], x["n_containers"], x["n_publish"], x["ga_faixa"], x["motivos"])
