"""Mapa de acessos da organização GMP do cliente (cliente.json → gmp_org). Só leitura.

Para cada conta GA vinculada à organização (analyticsAccountLinks): accessBindings da conta e de cada
propriedade (GA Admin API v1alpha). Para cada conta GTM visível: user_permissions (Tag Manager API v2).
Saída em evidencias/gmp/<data>/<org_id>/ (ga_bindings.json, gtm_permissions.json).

Pré-requisito: scripts/gmp_users.py já rodado na mesma data (gera analyticsAccountLinks.json).
Uso:  python3 scripts/gmp_mapa_acessos.py
"""
import datetime
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from gapi import CLIENTE, paged, save  # noqa: E402

ORG = CLIENTE.get("gmp_org")
if not ORG:
    sys.exit("cliente.json sem gmp_org: sem acesso à organização GMP. Registre o bloqueio no estado (acessos via grupo ficam invisíveis) e siga")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "evidencias/gmp", datetime.date.today().isoformat(), ORG)
GA = "https://analyticsadmin.googleapis.com/v1alpha"
GTM = "https://tagmanager.googleapis.com/tagmanager/v2"


def tenta(fn, *a):
    try:
        return fn(*a), None
    except RuntimeError as e:
        return [], str(e).split("\n")[0][:80]


def ga():
    links = json.load(open(os.path.join(OUT, "analyticsAccountLinks.json")))
    out = []
    for l in links:
        acc = l["analyticsAccount"].split("/", 1)[1]
        conta = {"account": acc, "nome": l["displayName"].strip(), "erros": []}
        conta["bindings"], err = tenta(paged, f"{GA}/{acc}/accessBindings?pageSize=200", "accessBindings")
        if err:
            conta["erros"].append(err)
        props, err = tenta(paged, f"{GA}/properties?filter=ancestor:{acc}&pageSize=200&showDeleted=false", "properties")
        if err:
            conta["erros"].append(err)
        conta["propriedades"] = []
        for p in props:
            b, err = tenta(paged, f"{GA}/{p['name']}/accessBindings?pageSize=200", "accessBindings")
            conta["propriedades"].append({"property": p["name"], "nome": p["displayName"], "tipo": p.get("propertyType"),
                                          "serviceLevel": p.get("serviceLevel"), "bindings": b, "erro": err})
        print(f"GA {acc} {conta['nome']}: {len(conta['bindings'])} na conta, {len(props)} propriedades" + (f" · {conta['erros']}" if conta["erros"] else ""))
        out.append(conta)
    save(os.path.join(OUT, "ga_bindings.json"), out)


def gtm():
    out = []
    time.sleep(4)
    for acc in paged(f"{GTM}/accounts", "account"):
        time.sleep(4)
        conts, _ = tenta(paged, f"{GTM}/{acc['path']}/containers", "container")
        time.sleep(4)
        perms, err = tenta(paged, f"{GTM}/{acc['path']}/user_permissions", "userPermission")
        out.append({"account": acc["path"], "nome": acc["name"], "containers": {c["containerId"]: [c["publicId"], c["name"]] for c in conts},
                    "permissions": perms, "erro": err})
        print(f"GTM {acc['path']} {acc['name']}: {len(perms)} usuários" + (f" · {err}" if err else ""))
    save(os.path.join(OUT, "gtm_permissions.json"), out)


if __name__ == "__main__":
    ga()
    gtm()
