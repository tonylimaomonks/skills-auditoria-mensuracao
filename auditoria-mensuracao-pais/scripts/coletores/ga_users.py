"""Mapeia acessos GA4 (somente leitura): accessBindings, Data Access Report e Change History.

Uso: python3 scripts/ga_users.py 9925058 [314140441 ...]
Saída: evidencias/ga4/_acessos/<data>/<accountId>/*.json
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, paged, save  # noqa: E402

V1A = "https://analyticsadmin.googleapis.com/v1alpha"
V1B = "https://analyticsadmin.googleapis.com/v1beta"
ROOT = os.path.join(os.path.dirname(__file__), "..", "evidencias", "ga4", "_acessos",
                    datetime.date.today().isoformat())


def try_(label, fn):
    try:
        return fn()
    except RuntimeError as e:
        print(f"{label}: {str(e)[:300]}")
        return None


def access_report(entity, start="2020-01-01"):
    body = {
        "dimensions": [{"dimensionName": "userEmail"}, {"dimensionName": "accessedPropertyName"},
                       {"dimensionName": "accessedPropertyId"}, {"dimensionName": "accessorAppName"},
                       {"dimensionName": "mostRecentAccessEpochTimeMicros"}],
        "metrics": [{"metricName": "accessCount"}],
        "dateRanges": [{"startDate": start, "endDate": "today"}],
        "limit": 100000,
    }
    return call(f"{V1B}/{entity}:runAccessReport", "POST", body)


def change_history(account):
    out, page = [], None
    while True:
        body = {"pageSize": 200}
        if page:
            body["pageToken"] = page
        r = call(f"{V1A}/{account}:searchChangeHistoryEvents", "POST", body)
        out += r.get("changeHistoryEvents", [])
        page = r.get("nextPageToken")
        if not page or len(out) > 20000:
            return out


def main():
    for acc_id in sys.argv[1:]:
        acc = f"accounts/{acc_id}"
        d = os.path.join(ROOT, acc_id)
        save(os.path.join(d, "account.json"), try_("account", lambda: call(f"{V1B}/{acc}")))
        props = try_("properties", lambda: paged(
            f"{V1B}/properties?filter=parent:{acc}&showDeleted=false&pageSize=200", "properties")) or []
        subs = []
        for p in props:
            subs += try_("subprops", lambda: paged(
                f"{V1B}/properties?filter=parent:{p['name']}&pageSize=200", "properties")) or []
        props += subs
        save(os.path.join(d, "properties.json"), props)
        save(os.path.join(d, "accessBindings_account.json"),
             try_("ab acc", lambda: paged(f"{V1A}/{acc}/accessBindings?pageSize=500", "accessBindings")))
        pb = {}
        for p in props:
            pb[p["name"]] = try_(p["name"], lambda: paged(
                f"{V1A}/{p['name']}/accessBindings?pageSize=500", "accessBindings"))
        save(os.path.join(d, "accessBindings_properties.json"), pb)
        save(os.path.join(d, "accessReport_account.json"), try_("access report", lambda: access_report(acc)))
        save(os.path.join(d, "changeHistory.json"), try_("change history", lambda: change_history(acc)))


if __name__ == "__main__":
    main()
