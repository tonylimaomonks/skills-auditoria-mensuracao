"""Exporta (somente leitura) containers GTM via Tag Manager API v2.

Uso:
  python3 scripts/gtm_dump.py --list                 # lista contas e containers acessíveis
  python3 scripts/gtm_dump.py GTM-TCXTCQ5            # exporta versão publicada (live) + workspaces
  python3 scripts/gtm_dump.py GTM-TCXTCQ5 --users    # inclui permissões (exige escopo tagmanager.manage.users)

Saída: evidencias/gtm/<publicId>/<data>/*.json
Quota padrão da API é baixa (~0,25 req/s), por isso o sleep entre chamadas.
"""
import argparse
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, paged, save  # noqa: E402

BASE = "https://tagmanager.googleapis.com/tagmanager/v2"
ROOT = os.path.join(os.path.dirname(__file__), "..", "evidencias", "gtm")


def slow(fn, *a):
    r = fn(*a)
    time.sleep(4)
    return r


def containers():
    for acc in slow(paged, f"{BASE}/accounts", "account"):
        for c in slow(paged, f"{BASE}/{acc['path']}/containers", "container"):
            yield acc, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("public_id", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--users", action="store_true")
    a = ap.parse_args()

    if a.list or not a.public_id:
        rows = [(acc["name"], c["publicId"], c["name"], ",".join(c.get("usageContext", [])), c["path"])
                for acc, c in containers()]
        for r in rows:
            print(" | ".join(r))
        save(os.path.join(ROOT, "_inventario_containers.json"),
             [dict(zip(["account", "publicId", "name", "usageContext", "path"], r)) for r in rows])
        return

    match = next(((acc, c) for acc, c in containers() if c["publicId"] == a.public_id), None)
    if not match:
        sys.exit(f"{a.public_id} não encontrado nas contas acessíveis")
    acc, c = match
    out = os.path.join(ROOT, a.public_id, datetime.date.today().isoformat())
    save(os.path.join(out, "container.json"), c)

    try:
        save(os.path.join(out, "live_version.json"), slow(call, f"{BASE}/{c['path']}/versions:live"))
    except RuntimeError as e:
        print("sem versão live:", e)
    save(os.path.join(out, "version_headers.json"),
         slow(paged, f"{BASE}/{c['path']}/version_headers", "containerVersionHeader"))

    for ws in slow(paged, f"{BASE}/{c['path']}/workspaces", "workspace"):
        wdir = os.path.join(out, f"workspace_{ws['workspaceId']}")
        save(os.path.join(wdir, "workspace.json"), ws)
        for kind in ["tags:tag", "triggers:trigger", "variables:variable",
                     "built_in_variables:builtInVariable", "templates:template", "clients:client",
                     "transformations:transformation", "folders:folder"]:
            ep, key = kind.split(":")
            try:
                save(os.path.join(wdir, f"{ep}.json"), slow(paged, f"{BASE}/{ws['path']}/{ep}", key))
            except RuntimeError as e:
                print(f"{ep}: {str(e).splitlines()[0]}")

    if a.users:
        save(os.path.join(out, "user_permissions.json"),
             slow(paged, f"{BASE}/{acc['path']}/user_permissions", "userPermission"))


if __name__ == "__main__":
    main()
