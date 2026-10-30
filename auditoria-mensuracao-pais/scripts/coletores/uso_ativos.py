"""Coleta sinais de uso (somente leitura) para decidir quais propriedades GA e containers GTM estão vivos.

Uso:
  python3 scripts/uso_ativos.py ga 175020184 337385445 ...
  python3 scripts/uso_ativos.py gtm 6003531403

GA  → Data API: eventos por mês desde 2015, últimos 30 dias por stream; Admin API: streams e vínculos.
GTM → versão live (data de publicação = fingerprint), workspaces (última edição), nº de versões, tags ativas,
      IDs de destino GA4/Ads nas tags e se o gtm.js público responde.
Saída: evidencias/_uso_ativos/<data>/{ga,gtm}/<id>.json
"""
import datetime
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, paged, save  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "evidencias", "_uso_ativos", datetime.date.today().isoformat())
DATA = "https://analyticsdata.googleapis.com/v1beta"
ADM = "https://analyticsadmin.googleapis.com/v1beta"
ADMA = "https://analyticsadmin.googleapis.com/v1alpha"
GTM = "https://tagmanager.googleapis.com/tagmanager/v2"


def tryc(fn, *a, **k):
    try:
        return fn(*a, **k)
    except RuntimeError as e:
        return {"erro": str(e).splitlines()[0]}


def ga(pid):
    p = f"properties/{pid}"
    out = {"id": pid, "property": tryc(call, f"{ADMA}/{p}")}
    out["mensal"] = tryc(call, f"{DATA}/{p}:runReport", "POST", {
        "dimensions": [{"name": "yearMonth"}], "metrics": [{"name": "eventCount"}, {"name": "activeUsers"}],
        "dateRanges": [{"startDate": "2015-08-14", "endDate": "today"}], "limit": 1000})
    out["ult30_stream"] = tryc(call, f"{DATA}/{p}:runReport", "POST", {
        "dimensions": [{"name": "streamName"}, {"name": "streamId"}],
        "metrics": [{"name": "eventCount"}, {"name": "activeUsers"}, {"name": "keyEvents"}],
        "dateRanges": [{"startDate": "30daysAgo", "endDate": "yesterday"}]})
    out["ultimo_dia"] = tryc(call, f"{DATA}/{p}:runReport", "POST", {
        "dimensions": [{"name": "date"}], "metrics": [{"name": "eventCount"}],
        "dateRanges": [{"startDate": "2015-08-14", "endDate": "today"}],
        "orderBys": [{"dimension": {"dimensionName": "date"}, "desc": True}], "limit": 1})
    for ep, key, base in [("dataStreams", "dataStreams", ADM), ("googleAdsLinks", "googleAdsLinks", ADM),
                          ("firebaseLinks", "firebaseLinks", ADM), ("bigQueryLinks", "bigqueryLinks", ADMA)]:
        out[ep] = tryc(paged, f"{base}/{p}/{ep}", key)
    save(os.path.join(ROOT, "ga", f"{pid}.json"), out)


def slow(fn, *a):
    r = tryc(fn, *a)
    time.sleep(4)
    return r


def gtm(acc_id):
    for c in slow(paged, f"{GTM}/accounts/{acc_id}/containers", "container"):
        out = {"container": c}
        out["live"] = slow(call, f"{GTM}/{c['path']}/versions:live")
        out["workspaces"] = slow(paged, f"{GTM}/{c['path']}/workspaces", "workspace")
        out["version_headers"] = slow(paged, f"{GTM}/{c['path']}/version_headers", "containerVersionHeader")
        js = "server" not in c.get("usageContext", [])
        if js:
            try:
                with urllib.request.urlopen(f"https://www.googletagmanager.com/gtm.js?id={c['publicId']}", timeout=20) as r:
                    out["gtm_js"] = {"status": r.status, "bytes": len(r.read())}
            except Exception as e:  # 404 = sem versão publicada
                out["gtm_js"] = {"status": getattr(e, "code", str(e))}
        save(os.path.join(ROOT, "gtm", f"{c['publicId']}.json"), out)


if __name__ == "__main__":
    kind, ids = sys.argv[1], sys.argv[2:]
    for i in ids:
        ga(i) if kind == "ga" else gtm(i)
