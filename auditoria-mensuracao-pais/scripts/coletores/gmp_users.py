"""Relação de usuários da organização GMP (Google Marketing Platform Admin API v1alpha). Só leitura.

Exporta, para cada organização visível: admins (adminAccessBindings), grupos de usuários (userGroups)
e membros de cada grupo e contas GA vinculadas (analyticsAccountLinks), em evidencias/gmp/<data>/<org_id>/.

Uso:  python3 scripts/gmp_users.py [org_id]
Escopo do ADC: https://www.googleapis.com/auth/marketingplatformadmin.analytics.read
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, paged, save  # noqa: E402

BASE = "https://marketingplatformadmin.googleapis.com/v1alpha"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "evidencias/gmp", datetime.date.today().isoformat())


def main():
    orgs = paged(f"{BASE}/organizations?pageSize=100", "organizations")
    save(os.path.join(OUT, "organizations.json"), orgs)
    for o in orgs:
        print(o["name"], "|", o.get("displayName"))
    if len(sys.argv) > 1:
        orgs = [o for o in orgs if o["name"].split("/")[1] == sys.argv[1]]
    for o in orgs:
        oid = o["name"].split("/")[1]
        d = os.path.join(OUT, oid)
        try:
            admins = paged(f"{BASE}/{o['name']}/adminAccessBindings?pageSize=1000", "adminAccessBindings")
        except RuntimeError as e:
            print(f"{oid}: sem permissão para admins ({str(e)[:3]})")
            admins = None
        save(os.path.join(d, "adminAccessBindings.json"), admins)
        try:  # contas GA vinculadas à org: pré-requisito do gmp_mapa_acessos.py
            links = paged(f"{BASE}/{o['name']}/analyticsAccountLinks?pageSize=1000", "analyticsAccountLinks")
        except RuntimeError as e:
            print(f"{oid}: sem permissão para analyticsAccountLinks ({str(e)[:3]})")
            links = None
        save(os.path.join(d, "analyticsAccountLinks.json"), links)
        try:
            groups = paged(f"{BASE}/{o['name']}/userGroups?pageSize=1000", "userGroups")
        except RuntimeError as e:
            print(f"{oid}: sem permissão para grupos ({str(e)[:3]})")
            continue
        for g in groups:
            g["members"] = paged(f"{BASE}/{g['name']}/members?pageSize=1000", "userGroupMembers")
            print(f"  grupo {g.get('displayName', g['name'])}: {len(g['members'])} membros")
        save(os.path.join(d, "userGroups_members.json"), groups)
        print(f"{oid}: {len(admins or [])} admin bindings, {len(groups)} grupos")


if __name__ == "__main__":
    main()
