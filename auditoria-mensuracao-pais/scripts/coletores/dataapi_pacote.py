"""Pacote padrão de consultas da GA4 Data API para a auditoria de mensuração (somente leitura).

São as consultas que sustentaram os achados do Brasil, agora genéricas por país: volume e cota 360,
duplicidade e ausência de transaction_id, receita não verificável, hosts de teste na propriedade de
produção, dado pessoal em pageLocation e em dimensões customizadas, eventName com cara de injeção,
moeda e itens da compra.

Uso (de dentro da pasta do país):
  python3 scripts/dataapi_pacote.py <propertyId> --pais mx [--fim AAAA-MM-DD] [--dias 30] [--so Q07,Q13]

Saída: evidencias/ga4/<propertyId>/<data>/dataapi/Qnn_<nome>.json  ({descricao, request, response, extracted_at})
       evidencias/ga4/<propertyId>/<data>/dataapi/resumo.json        (números-chave para o conteudo.json)
Cada arquivo guarda o corpo exato da requisição: o mesmo corpo vira o "pronto quando" do plano de ação.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gapi import call, save  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Documento pessoal e telefone por país (regex RE2 em pageLocation). Acrescentar o país novo aqui.
PII_PAIS = {
    "br": {"documento": r".*(cpf|document|documento)=[0-9.%-]{11,}.*",
           "telefone": r".*(tel|phone|telefone|celular|whatsapp)=[0-9+%() .-]{10,}.*"},
    # MX: CURP ou RFC como valor INTEIRO de um parâmetro/segmento, em maiúsculas (consulta case-sensitive).
    # A versão solta (qualquer trecho de 4 letras + 6 dígitos…) casou com 250 mil page_view de /gimnasios em 29/10/2026: falso positivo.
    "mx": {"documento": r".*[=/]([A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9A-Z][0-9]|[A-Z&]{3,4}[0-9]{6}[A-Z0-9]{3})([&#/]|$).*",  # CURP | RFC
           "telefone": r".*(tel|phone|telefono|celular|whatsapp)=[0-9+%() .-]{10,}.*"},
}
EMAIL_RE = r".*(%40|@)[a-zA-Z0-9-]+\..*"
INJECAO_RE = r".*(['\"<>;`]|select |union |sleep\(|@@|\$\{|%27|%22|%3[cC]|\.\./).*"
PII_PARAM = re.compile(r"(e-?mail|phone|telefon|celular|cpf|curp|rfc|document|nome|name|first_?name|last_?name|"
                       r"endereco|address|direccion|street|cep|zip|codigo_?postal|birth|nascimento|nacimiento)", re.I)


def f_eq(campo, valor):
    return {"filter": {"fieldName": campo, "stringFilter": {"value": valor}}}


def f_re(campo, rx, caso=False):
    return {"filter": {"fieldName": campo, "stringFilter": {"matchType": "FULL_REGEXP", "value": rx, "caseSensitive": caso}}}


def f_in(campo, valores):
    return {"filter": {"fieldName": campo, "inListFilter": {"values": valores}}}


def e_(*exprs):
    return {"andGroup": {"expressions": list(exprs)}}


def q(dims, mets, filtro=None, limit=10000, **extra):
    b = {"dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets], "limit": limit}
    if filtro:
        b["dimensionFilter"] = filtro
    b.update(extra)
    return b


FUNIL = ["page_view", "view_item_list", "select_item", "view_item", "add_to_cart", "begin_checkout",
         "add_shipping_info", "add_payment_info", "generate_lead", "sign_up", "purchase", "refund"]


def pacote(pais):
    pii = PII_PAIS[pais]
    P = f_eq("eventName", "purchase")
    return [
        ("Q01", "eventos_30d", "Volume por evento: base da cota 360 e dos eventos sem uso", 30, q(["eventName"], ["eventCount", "totalUsers"], limit=2000)),
        ("Q02", "eventos_por_stream_30d", "Volume por stream (web, iOS, Android): quais streams têm dados", 30, q(["streamId", "streamName"], ["eventCount", "activeUsers"])),
        ("Q03", "eventos_stream_evento_30d", "Evento × stream: paridade web × app e evento genérico de alto volume", 30, q(["streamName", "eventName"], ["eventCount"], limit=5000)),
        ("Q04", "keyevents_30d", "Key events e volume: lixo marcado como conversão", 30, q(["eventName"], ["keyEvents", "eventCount"])),
        ("Q05", "hosts_30d", "Hosts que escrevem na propriedade: staging, teste e domínios de terceiros", 30, q(["hostName", "streamName"], ["eventCount", "totalUsers"], limit=500)),
        ("Q06", "purchase_por_host_30d", "Compras e receita por host e plataforma", 30, q(["hostName", "platform"], ["eventCount", "purchaseRevenue", "totalUsers", "transactions"], P)),
        ("Q07", "purchase_por_transacao_30d", "Compras por transaction_id: duplicidade e receita inflada (paginado)", 30, q(["transactionId", "platform"], ["eventCount", "purchaseRevenue"], P, limit=250000)),
        ("Q08", "purchase_sem_txid_por_host_30d", "Compras sem transaction_id por host e página", 30, q(["hostName", "pagePath"], ["eventCount", "purchaseRevenue", "totalUsers"], e_(P, f_eq("transactionId", "(not set)")), limit=500)),
        ("Q09", "purchase_diario_por_host_30d", "Série diária de compras por host: quebras e mudanças de patamar", 30, q(["date", "hostName"], ["eventCount", "purchaseRevenue"], P, limit=5000)),
        ("Q10", "funil_por_host_30d", "Eventos do funil por host: etapas ausentes ou duplicadas", 30, q(["eventName", "hostName"], ["eventCount", "totalUsers"], f_in("eventName", FUNIL), limit=2000)),
        ("Q11", "moeda_purchase_30d", "Moeda das compras (currency esperado do país)", 30, q(["currencyCode", "platform"], ["eventCount", "purchaseRevenue"], P)),
        ("Q12", "itens_comprados_30d", "Itens da compra: plano + adicionais em items", 30, q(["itemName", "itemCategory"], ["itemsPurchased", "itemRevenue"], limit=500)),
        ("Q13", "pii_email_pagelocation_30d", "E-mail em pageLocation (só contagem; nenhum valor extraído)", 30, q(["hostName", "eventName"], ["eventCount", "totalUsers"], f_re("pageLocation", EMAIL_RE))),
        ("Q14", "pii_documento_pagelocation_30d", f"Documento pessoal ({pais.upper()}) em pageLocation (só contagem)", 30, q(["hostName", "pagePath"], ["eventCount"], f_re("pageLocation", pii["documento"], caso=True))),
        ("Q15", "pii_telefone_pagelocation_30d", "Telefone em parâmetro de URL (só contagem)", 30, q(["hostName", "eventName"], ["eventCount"], f_re("pageLocation", pii["telefone"]))),
        ("Q16", "browser_web_30d", "Navegador/SO na web: peso do Safari (ITP) para o sGTM fora do domínio", 30, q(["browser", "operatingSystem"], ["sessions"], f_eq("platform", "web"), limit=25)),
        ("Q17", "injecao_eventname_90d", "eventName com cara de injeção (sondagem SQL/XSS chegando como evento)", 90, q(["eventName", "hostName", "date"], ["eventCount"], f_re("eventName", INJECAO_RE), limit=500)),
        ("Q18", "eventos_mensal_12m", "Série mensal de eventos (12 meses): tendência de cota", 365, q(["yearMonth"], ["eventCount"], limit=24, orderBys=[{"dimension": {"dimensionName": "yearMonth"}}])),
    ]


def run_report(prop, corpo, paginar=False):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport"
    r = call(url, "POST", corpo)
    if paginar:
        total = r.get("rowCount", 0)
        while len(r.get("rows", [])) < total:
            nxt = call(url, "POST", {**corpo, "offset": len(r["rows"])})
            if not nxt.get("rows"):
                break
            r["rows"] += nxt["rows"]
    return r


def linhas(r):
    return [([d["value"] for d in x.get("dimensionValues", [])], [float(m["value"]) for m in x.get("metricValues", [])]) for x in r.get("rows", [])]


def resumo(res):
    out = {}
    if "Q01" in res:
        ev = {d[0]: m[0] for d, m in linhas(res["Q01"])}
        out["eventos_total"] = sum(ev.values())
        out["faturaveis"] = out["eventos_total"] - ev.get("user_engagement", 0)
        out["top_eventos"] = sorted(ev.items(), key=lambda x: -x[1])[:15]
        out["top_eventos_pct_faturaveis"] = [(k, round(100 * v / out["faturaveis"], 2)) for k, v in out["top_eventos"] if out["faturaveis"]]
    if "Q07" in res:
        tx = linhas(res["Q07"])
        com_id = [(d, m) for d, m in tx if d[0] not in ("(not set)", "")]
        sem_id = [(d, m) for d, m in tx if d[0] in ("(not set)", "")]
        dup = [(d, m) for d, m in com_id if m[0] > 1]
        ev_extra = sum(m[0] - 1 for _, m in dup)
        rec_extra = sum(m[1] * (m[0] - 1) / m[0] for _, m in dup)
        out["purchase"] = {
            "eventos": sum(m[0] for _, m in tx), "receita": round(sum(m[1] for _, m in tx), 2),
            "transacoes_unicas_com_id": len(com_id), "transacoes_duplicadas": len(dup),
            "eventos_extra_duplicados": ev_extra, "receita_extra_duplicada_estimada": round(rec_extra, 2),
            "sem_id_eventos": sum(m[0] for _, m in sem_id), "sem_id_receita": round(sum(m[1] for _, m in sem_id), 2),
            "duplicadas_por_plataforma": {},
        }
        for d, m in dup:
            k = d[1]
            out["purchase"]["duplicadas_por_plataforma"][k] = out["purchase"]["duplicadas_por_plataforma"].get(k, 0) + 1
        p = out["purchase"]
        p["pct_eventos_que_sao_transacao_unica"] = round(100 * p["transacoes_unicas_com_id"] / p["eventos"], 2) if p["eventos"] else None
        p["receita_verificavel_estimada"] = round(p["receita"] - p["sem_id_receita"] - rec_extra, 2)
        p["pct_receita_verificavel"] = round(100 * p["receita_verificavel_estimada"] / p["receita"], 2) if p["receita"] else None
    for k, nome in (("Q13", "pii_email_eventos"), ("Q14", "pii_documento_eventos"), ("Q15", "pii_telefone_eventos"), ("Q17", "injecao_eventos")):
        if k in res:
            out[nome] = sum(m[0] for _, m in linhas(res[k]))
    for k, r in res.items():
        if k.startswith("Q19_"):
            out.setdefault("pii_customdim", {})[r["_dim"]] = sum(m[0] for _, m in linhas(r))
    if "Q05" in res:
        out["hosts"] = [(d[0], d[1], m[0]) for d, m in linhas(res["Q05"])][:40]
    if "Q11" in res:
        out["moedas"] = [(d[0], d[1], m[0]) for d, m in linhas(res["Q11"])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("property_id")
    ap.add_argument("--pais", required=True, choices=sorted(PII_PAIS))
    ap.add_argument("--fim", help="último dia do período (padrão: ontem)")
    ap.add_argument("--dias", type=int, default=30)
    ap.add_argument("--so", help="só estas consultas, ex.: Q07,Q13")
    a = ap.parse_args()
    fim = dt.date.fromisoformat(a.fim) if a.fim else dt.date.today() - dt.timedelta(days=1)
    hoje = dt.date.today().isoformat()
    out = os.path.join(ROOT, "evidencias", "ga4", a.property_id, hoje, "dataapi")
    so = set(a.so.split(",")) if a.so else None
    res = {}
    for qid, nome, desc, dias, corpo in pacote(a.pais):
        if so and qid not in so:
            continue
        dias = a.dias if dias == 30 else dias
        corpo = {"dateRanges": [{"startDate": (fim - dt.timedelta(days=dias - 1)).isoformat(), "endDate": fim.isoformat()}], **corpo}
        try:
            r = run_report(a.property_id, corpo, paginar=(qid == "Q07"))
        except Exception as ex:  # dimensão inexistente na propriedade, quota etc.: registra e segue
            print(f"{qid} {nome}: ERRO {ex}")
            save(os.path.join(out, f"{qid}_{nome}.json"), {"descricao": desc, "request": corpo, "erro": str(ex), "extracted_at": dt.datetime.now().isoformat(timespec="seconds")})
            continue
        res[qid] = r
        save(os.path.join(out, f"{qid}_{nome}.json"), {"descricao": desc, "request": corpo, "response": r, "extracted_at": dt.datetime.now().isoformat(timespec="seconds")})
        print(f"{qid} {nome}: {r.get('rowCount', 0)} linhas")
    # Q19: dimensões customizadas com nome de dado pessoal (e-mail: contém "@"; demais: preenchida)
    if not so or "Q19" in so:
        meta = call(f"https://analyticsdata.googleapis.com/v1beta/properties/{a.property_id}/metadata")
        alvo = [d["apiName"] for d in meta.get("dimensions", []) if d["apiName"].startswith("customEvent:") and PII_PARAM.search(d["apiName"])]
        for n, dim in enumerate(alvo, 1):
            corpo = {"dateRanges": [{"startDate": (fim - dt.timedelta(days=a.dias - 1)).isoformat(), "endDate": fim.isoformat()}],
                     **q(["eventName", "platform"], ["eventCount"],
                         {"filter": {"fieldName": dim, "stringFilter": {"matchType": "CONTAINS", "value": "@"}}} if re.search("mail", dim, re.I)
                         else {"notExpression": {"orGroup": {"expressions": [f_eq(dim, "(not set)"), f_eq(dim, "")]}}})}
            r = run_report(a.property_id, corpo)
            r["_dim"] = dim
            res[f"Q19_{n:02d}"] = r
            save(os.path.join(out, f"Q19_{n:02d}_pii_customdim_{dim.split(':')[1]}.json"),
                 {"descricao": f"Eventos com {dim} preenchido (só contagem; conferir se o valor é hash ou texto aberto pela amostra no Chrome)", "request": corpo, "response": r,
                  "extracted_at": dt.datetime.now().isoformat(timespec="seconds")})
            print(f"Q19 {dim}: {r.get('rowCount', 0)} linhas")
    rs = resumo(res)
    rs["periodo"] = [(fim - dt.timedelta(days=a.dias - 1)).isoformat(), fim.isoformat()]
    save(os.path.join(out, "resumo.json"), rs)
    print(json.dumps({k: v for k, v in rs.items() if k not in ("top_eventos", "hosts")}, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
