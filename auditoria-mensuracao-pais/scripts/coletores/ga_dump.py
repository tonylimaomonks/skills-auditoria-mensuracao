"""Exporta (somente leitura) configuração de propriedades GA4 via Admin API.

Uso:
  python3 scripts/ga_dump.py --list           # accountSummaries (todas as contas/propriedades acessíveis)
  python3 scripts/ga_dump.py 175020184        # config completa da propriedade
  python3 scripts/ga_dump.py 175020184 --users  # inclui accessBindings (exige analytics.manage.users.readonly)

Saída: evidencias/ga4/<propertyId>/<data>/*.json
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, paged, save  # noqa: E402

V1B = "https://analyticsadmin.googleapis.com/v1beta"
V1A = "https://analyticsadmin.googleapis.com/v1alpha"
ROOT = os.path.join(os.path.dirname(__file__), "..", "evidencias", "ga4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("property_id", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--users", action="store_true")
    a = ap.parse_args()

    if a.list or not a.property_id:
        summ = paged(f"{V1B}/accountSummaries?pageSize=200", "accountSummaries")
        for acc in summ:
            for p in acc.get("propertySummaries", []):
                print(" | ".join([acc.get("displayName", ""), p["property"], p.get("displayName", ""),
                                  p.get("propertyType", ""), p.get("parent", "")]))
        save(os.path.join(ROOT, "_account_summaries.json"), summ)
        return

    p = f"properties/{a.property_id}"
    out = os.path.join(ROOT, a.property_id, datetime.date.today().isoformat())
    save(os.path.join(out, "property.json"), call(f"{V1A}/{p}"))  # alpha traz serviceLevel (360 x Standard)

    endpoints = [
        (V1B, "dataStreams", "dataStreams"),
        (V1B, "customDimensions", "customDimensions"),
        (V1B, "customMetrics", "customMetrics"),
        (V1B, "keyEvents", "keyEvents"),
        (V1B, "firebaseLinks", "firebaseLinks"),
        (V1B, "googleAdsLinks", "googleAdsLinks"),
        (V1A, "bigQueryLinks", "bigqueryLinks"),
        (V1A, "subpropertyEventFilters", "subpropertyEventFilters"),
        (V1A, "rollupPropertySourceLinks", "rollupPropertySourceLinks"),
        (V1A, "searchAds360Links", "searchAds360Links"),
        (V1A, "displayVideo360AdvertiserLinks", "displayVideo360AdvertiserLinks"),
        (V1A, "calculatedMetrics", "calculatedMetrics"),
        (V1A, "channelGroups", "channelGroups"),
        (V1A, "audiences", "audiences"),
    ]
    for base, ep, key in endpoints:
        try:
            save(os.path.join(out, f"{ep}.json"), paged(f"{base}/{p}/{ep}", key))
        except RuntimeError as e:
            print(f"{ep}: {str(e).splitlines()[0]}")

    for single in ["dataRetentionSettings", "googleSignalsSettings", "attributionSettings",
                   "dataSharingSettings", "reportingIdentitySettings"]:
        try:
            save(os.path.join(out, f"{single}.json"), call(f"{V1A}/{p}/{single}"))
        except RuntimeError as e:
            print(f"{single}: {str(e).splitlines()[0]}")

    streams = paged(f"{V1B}/{p}/dataStreams", "dataStreams")
    for s in streams:
        sid = s["name"].split("/")[-1]
        for sub in ["enhancedMeasurementSettings", "measurementProtocolSecrets", "dataRedactionSettings"]:
            url = f"{V1A}/{s['name']}/{sub}"
            try:
                res = paged(url, "measurementProtocolSecrets") if sub == "measurementProtocolSecrets" else call(url)
                if sub == "measurementProtocolSecrets":
                    res = [{k: v for k, v in r.items() if k != "secretValue"} for r in res]
                save(os.path.join(out, "streams", sid, f"{sub}.json"), res)
            except RuntimeError as e:
                print(f"{sid}/{sub}: {str(e).splitlines()[0]}")

    if a.users:
        save(os.path.join(out, "accessBindings.json"), paged(f"{V1A}/{p}/accessBindings", "accessBindings"))
        acc = call(f"{V1A}/{p}")["account"]
        save(os.path.join(out, "accessBindings_account.json"), paged(f"{V1A}/{acc}/accessBindings", "accessBindings"))


if __name__ == "__main__":
    main()
