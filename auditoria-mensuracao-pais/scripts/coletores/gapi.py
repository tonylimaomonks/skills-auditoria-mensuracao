"""Helper mínimo (stdlib) para chamar APIs Google com o token do gcloud ADC."""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

_token = None


def cliente():
    """cliente.json do cliente (os coletores ficam em <cliente>/<pais>/scripts/). Vazio se ainda não existir."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cliente.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


CLIENTE = cliente()
# projeto GCP de cota de todas as chamadas (cliente.json → projeto_cota); QUOTA_PROJECT no ambiente sobrescreve
QUOTA_PROJECT = CLIENTE.get("projeto_cota") or "apis-511715"
CONTA_AUDITORIA = CLIENTE.get("conta_auditoria", "")
INTERNOS = set(CLIENTE.get("dominios_internos", []))


def token():
    global _token
    if _token is None:
        _token = subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"], text=True
        ).strip()
    return _token


def call(url, method="GET", body=None, retries=3):
    headers = {"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}
    headers["x-goog-user-project"] = os.environ.get("QUOTA_PROJECT", QUOTA_PROJECT)
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            if e.code == 429 and attempt < retries - 1:
                time.sleep(30)
                continue
            raise RuntimeError(f"{e.code} {url}\n{msg}") from None


def paged(url, key):
    out, page = [], None
    while True:
        sep = "&" if "?" in url else "?"
        resp = call(url + (f"{sep}pageToken={page}" if page else ""))
        out += resp.get(key, [])
        page = resp.get("nextPageToken")
        if not page:
            return out


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print("salvo:", path)
