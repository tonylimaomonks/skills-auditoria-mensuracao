"""Peças comuns do relatório técnico e do deck: formatação pt-BR, IDs, gráficos SVG e blocos de conteúdo.

Nada aqui conhece um país: tudo o que é específico vem do conteudo.json (ver references/conteudo-schema.md).
"""
import base64
import html
import json
import os
import re
import subprocess
import tempfile

PILARES_PADRAO = {"FIN": "Financeiro / Licenciamento", "INT": "Duplicidade & Integridade", "PG": "Performance & Governança"}
PIL_CURTO = {"FIN": "Financeiro", "INT": "Integridade", "PG": "Perf. & Gov."}
CRIT_ORD = {"ALTA": 0, "MÉDIA": 1, "BAIXA": 2}
CRIT_ICON = {"ALTA": "▲", "MÉDIA": "■", "BAIXA": "▼"}
CRIT_CLS = {"ALTA": "alta", "MÉDIA": "media", "BAIXA": "baixa"}
# nível base da matriz I × P, antes dos modificadores
MATRIZ = {(3, 1): "MÉDIA", (3, 2): "ALTA", (3, 3): "ALTA", (2, 1): "BAIXA", (2, 2): "MÉDIA", (2, 3): "ALTA",
          (1, 1): "BAIXA", (1, 2): "BAIXA", (1, 3): "MÉDIA"}
SOBE = {"BAIXA": "MÉDIA", "MÉDIA": "ALTA", "ALTA": "ALTA"}

PH_RE = re.compile(r"PLACEHOLDER_[A-Za-z0-9_]*")
ID_RE = re.compile(r"\b(SF-(?:FIN|DUP|INT|PII|PERF|GOV)-\d{2}|E-\d{2,3}|A-\d{3}|D-\d{2}|V-\d{2}|P-\d{2}|N-\d{2})\b")


def configurar_ids(prefixo):
    """Troca o prefixo dos achados (SF por padrão) pelo do cliente. Chamado pelo build antes de gerar."""
    global ID_RE
    from cliente import id_achado_re
    ID_RE = re.compile(r"\b(" + id_achado_re(prefixo) + r"|E-\d{2,3}|A-\d{3}|D-\d{2}|V-\d{2}|P-\d{2}|N-\d{2})\b")
    return ID_RE
CODE_RE = re.compile(r"`([^`]+)`")
SEGREDO_RE = re.compile(r"(EAA[A-Za-z0-9]{40,}|\b[A-Za-z0-9_-]{32,}\b)")
KEY_RE = re.compile(r"(access_?token|apiaccesstoken|api_?key|secret(?!proof)|password|senha|bearer)$", re.I)
MASK = "[MASCARADO]"


# ----------------------------------------------------------------- números pt-BR
def _br(s):
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def f_int(n):
    return _br(f"{int(round(n)):,}")


def f_dec(x, casas=1):
    return _br(f"{x:,.{casas}f}")


def f_pct(x, casas=1):
    return f_dec(x, casas) + "%"


def f_compacto(n):
    a, s = abs(n), ("−" if n < 0 else "")
    if a >= 1e9:
        return s + f_dec(a / 1e9) + " bi"
    if a >= 1e6:
        return s + f_dec(a / 1e6) + " mi"
    if a >= 1e3:
        return s + f_dec(a / 1e3) + " mil"
    return s + f_int(a)


def f_moeda(v, moeda="R$", casas=2):
    s = "−" if v < 0 else ""
    a = abs(v)
    if a >= 1e6:
        return f"{s}{moeda} {f_dec(a / 1e6, casas)} mi"
    if a >= 1e3:
        return f"{s}{moeda} {f_dec(a / 1e3, 1)} mil"
    return f"{s}{moeda} {f_dec(a, 2)}"


def fmt_fn(nome, moeda):
    return {"moeda": lambda v: f_moeda(v, moeda), "compacto": f_compacto, "int": f_int, "pct": f_pct}.get(nome or "compacto", f_compacto)


# ----------------------------------------------------------------- texto
def esc(s):
    return html.escape("" if s is None else str(s))


def txt(s, links=True, nw=False):
    """Escapa, marca PLACEHOLDER_*, converte `código` e liga/agrupa IDs (<prefixo>-, E-, A-, D-, V-, P-)."""
    if s is None:
        return ""
    s = str(s)
    out, last = [], 0
    for m in PH_RE.finditer(s):
        out.append(esc(s[last:m.start()]))
        out.append('<span class="ph tbd">[a preencher]</span>')
        last = m.end()
    out.append(esc(s[last:]))
    r = CODE_RE.sub(r"<code>\1</code>", "".join(out))
    if links:
        r = ID_RE.sub(r'<a href="#\1">\1</a>', r)
    elif nw:
        r = ID_RE.sub(r'<span class="nw">\1</span>', r)
    return r


def paras(s, **kw):
    return "".join(f"<p>{txt(p, **kw)}</p>" for p in str(s).split("\n\n") if p.strip())


# ----------------------------------------------------------------- arquivos
def img_b64(path, largura=1600):
    tmp = tempfile.mktemp(suffix=".jpg")
    try:
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", str(largura), path, "--out", tmp],
                       check=True, capture_output=True)
        data, mime = open(tmp, "rb").read(), "image/jpeg"
    except Exception:
        data = open(path, "rb").read()
        mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def mascarar(obj):
    """Mascara valores de parâmetros de tag cuja chave indica credencial (formato GTM key/value)."""
    if isinstance(obj, dict):
        k, v = obj.get("key"), obj.get("value")
        o = {kk: mascarar(vv) for kk, vv in obj.items()}
        if isinstance(k, str) and isinstance(v, str) and KEY_RE.search(k) and len(v) >= 12 and "{{" not in v:
            o["value"] = MASK
        return o
    if isinstance(obj, list):
        return [mascarar(x) for x in obj]
    return obj


# ----------------------------------------------------------------- gráficos (relatório: escala pequena)
def svg_barras_rel(serie, w=720, h=180, destaque=None):
    n = len(serie) or 1
    mx = max((v for _, v in serie), default=1) or 1
    bw = (w - 40) / n
    every = max(1, n // 10)
    p = [f'<svg viewBox="0 0 {w} {h + 30}" class="chart" role="img" aria-label="Série">']
    for i, (lab, v) in enumerate(serie):
        bh = (h - 20) * v / mx
        x = 30 + i * bw
        cls = "b-a" if destaque and lab in destaque else "b-b"
        p.append(f'<rect class="{cls}" x="{x:.1f}" y="{h - bh:.1f}" width="{bw * 0.78:.1f}" height="{bh:.1f}"><title>{esc(lab)}: {f_int(v)}</title></rect>')
        if i % every == 0:
            p.append(f'<text x="{x + bw * 0.39:.1f}" y="{h + 16}" text-anchor="middle" class="ax">{esc(lab)}</text>')
    p.append(f'<text x="2" y="12" class="ax">{f_compacto(mx)}</text><line x1="28" x2="{w}" y1="{h}" y2="{h}" class="axl"/></svg>')
    return "".join(p)


def svg_waterfall_rel(itens, fmt, w=760, h=260):
    mx = max(abs(i["valor"]) for i in itens) or 1
    bw = (w - 40) / len(itens)
    run = 0
    p = [f'<svg viewBox="0 0 {w} {h + 56}" class="chart" role="img" aria-label="Ponte de reconciliação">']
    for k, it in enumerate(itens):
        v = it["valor"]
        if it["tipo"] == "total":
            top, bot, run = v, 0, v
            fill = "var(--accent)" if k == 0 else "var(--ok)"
        else:
            top, bot = run, run + v
            run = bot
            fill = "var(--crit-alta)"
        y1, y2 = h - (h - 30) * top / mx, h - (h - 30) * bot / mx
        x = 20 + k * bw
        p.append(f'<rect x="{x + bw * 0.12:.1f}" y="{min(y1, y2):.1f}" width="{bw * 0.76:.1f}" height="{max(abs(y2 - y1), 1):.1f}" fill="{fill}"/>')
        p.append(f'<text x="{x + bw / 2:.1f}" y="{min(y1, y2) - 6:.1f}" text-anchor="middle" class="vl">{esc(fmt(v))}</text>')
        for j, ln in enumerate(_quebra(it["label"], 18)[:3]):
            p.append(f'<text x="{x + bw / 2:.1f}" y="{h + 16 + j * 14}" text-anchor="middle" class="ax">{esc(ln)}</text>')
    p.append(f'<line x1="10" x2="{w - 10}" y1="{h}" y2="{h}" class="axl"/></svg>')
    return "".join(p)


def _quebra(s, lim):
    linhas, cur = [], ""
    for w in str(s).split():
        if len(cur) + len(w) + 1 > lim and cur:
            linhas.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    linhas.append(cur)
    return linhas


# ----------------------------------------------------------------- gráficos (deck: tela 1920×1080)
def svg_waterfall_deck(itens, fmt, w, h, aria, compacto=False):
    ml, mr, mt, mb = (20, 20, 56, 118) if not compacto else (16, 16, 46, 104)
    pw, ph = w - ml - mr, h - mt - mb
    vmax = max(abs(i["valor"]) for i in itens if i["tipo"] == "total") * 1.04 or 1
    slot = pw / len(itens)
    bw = slot * (0.58 if not compacto else 0.62)
    y = lambda v: mt + ph - (v / vmax) * ph  # noqa: E731
    p = [f'<svg class="chart" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(aria)}">',
         f'<line class="axis" x1="{ml}" x2="{w - mr}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>']
    run, prev = 0.0, None
    fs_v, fs_l = (30, 21) if not compacto else (21, 16)
    for k, it in enumerate(itens):
        x = ml + slot * k + (slot - bw) / 2
        if it["tipo"] == "total":
            top, bot, run = it["valor"], 0, it["valor"]
            cls = "bar-total" if k == 0 else "bar-final"
        else:
            top, bot = run, run + it["valor"]
            run = bot
            cls = "bar-neg"
        y1, y2 = y(max(top, bot)), y(min(top, bot))
        hh = max(y2 - y1, 2)
        p.append(f'<rect class="{cls}" x="{x:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="3"/>')
        if prev is not None:
            px = ml + slot * (k - 1) + (slot - bw) / 2 + bw
            p.append(f'<line class="connector" x1="{px:.1f}" x2="{x:.1f}" y1="{y(prev):.1f}" y2="{y(prev):.1f}"/>')
        prev = run
        vy = (y1 + hh + fs_v + 8) if it["tipo"] == "neg" else (y1 - 12)
        p.append(f'<text class="v {"v-neg" if it["tipo"] == "neg" else ""}" x="{x + bw / 2:.1f}" y="{vy:.1f}" text-anchor="middle" font-size="{fs_v}">{esc(fmt(it["valor"]))}</text>')
        linhas = _quebra(it["label"], 18 if not compacto else 12)[:3]
        ly = mt + ph + 30
        for li, ln in enumerate(linhas):
            p.append(f'<text class="lab" x="{x + bw / 2:.1f}" y="{ly + li * (fs_l + 4):.1f}" text-anchor="middle" font-size="{fs_l}">{esc(ln)}</text>')
        if it.get("ref"):
            p.append(f'<text class="ref" x="{x + bw / 2:.1f}" y="{ly + len(linhas) * (fs_l + 4) + 2:.1f}" text-anchor="middle" font-size="{fs_l - 2}">{esc(it["ref"])}</text>')
    p.append("</svg>")
    return "".join(p)


def svg_barras_deck(serie, w, h, aria, destaque=None, marco=None, marco_txt=None, fmt=f_compacto, ultimo=False):
    ml, mr, mt, mb = 70, 16, 40, 54
    pw, ph = w - ml - mr, h - mt - mb
    vmax = max((v for _, v in serie), default=1) or 1
    passo = 10 ** (len(str(int(vmax))) - 1) / 2 or 1
    topo = ((vmax // passo) + 1) * passo
    n = len(serie) or 1
    slot = pw / n
    bw = slot * 0.72
    every = max(1, n // 5)
    y = lambda v: mt + ph - (v / topo) * ph  # noqa: E731
    p = [f'<svg class="chart" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(aria)}">']
    for g in range(5):
        gv = topo * g / 4
        p.append(f'<line class="grid" x1="{ml}" x2="{w - mr}" y1="{y(gv):.1f}" y2="{y(gv):.1f}"/>')
        p.append(f'<text class="tick" x="{ml - 10}" y="{y(gv) + 6:.1f}" text-anchor="end" font-size="17">{esc(fmt(gv))}</text>')
    labs = [lab for lab, _ in serie]
    for k, (lab, v) in enumerate(serie):
        x = ml + slot * k + (slot - bw) / 2
        cls = "bar-hi" if destaque and lab in destaque else "bar-lo"
        if ultimo and k == n - 1:
            cls = "bar-final"
        p.append(f'<rect class="{cls}" x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{max(y(0) - y(v), 1):.1f}" rx="2"><title>{esc(lab)}: {f_int(v)}</title></rect>')
        if n <= 8 or (k % every == 0 and k < n - 2) or k == n - 1:  # poucas categorias: todos os rótulos
            p.append(f'<text class="tick" x="{x + bw / 2:.1f}" y="{h - mb + 26:.1f}" text-anchor="middle" font-size="{17 if n <= 8 else 17}">{esc(lab)}</text>')
    if marco and marco in labs:
        mx = ml + slot * labs.index(marco)
        p.append(f'<line class="marco" x1="{mx:.1f}" x2="{mx:.1f}" y1="{mt - 14}" y2="{y(0):.1f}"/>')
        if marco_txt:
            p.append(f'<text class="marco-t" x="{mx + 10:.1f}" y="{mt - 18:.1f}" font-size="19">{esc(marco_txt)}</text>')
    p.append("</svg>")
    return "".join(p)


def svg_barra100(segs, w, h, aria):
    total = sum(s[1] for s in segs) or 1
    cls = ["seg-hi", "seg-mid", "seg-lo", "seg-lo"]
    p = [f'<svg class="chart" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(aria)}">']
    x, bh = 0.0, 120
    for i, s in enumerate(segs):
        rot, val = s[0], s[1]
        sw = w * val / total
        p.append(f'<rect class="{cls[min(i, 3)]}" x="{x:.1f}" y="0" width="{max(sw - 4, 1):.1f}" height="{bh}" rx="4"/>')
        if sw > 120:
            p.append(f'<text class="seg-pct" x="{x + 22:.1f}" y="{bh / 2 + 16:.1f}" font-size="44">{f_pct(100 * val / total)}</text>')
            p.append(f'<text class="lab-strong" x="{x + 4:.1f}" y="{bh + 46:.1f}" font-size="26">{esc(rot)}</text>')
            p.append(f'<text class="lab" x="{x + 4:.1f}" y="{bh + 80:.1f}" font-size="22">{esc(f_compacto(val))}</text>')
        x += sw
    p.append("</svg>")
    return "".join(p)


# ----------------------------------------------------------------- blocos de conteúdo
def tabela(cab, linhas, cls="", legenda=None, html_celulas=False):
    cel = (lambda c: str(c)) if html_celulas else (lambda c: txt(c))
    h = "".join(f'<th scope="col">{txt(x, links=False)}</th>' for x in cab)
    b = "".join("<tr>" + "".join(f"<td>{cel(c)}</td>" for c in r) + "</tr>" for r in linhas)
    cap = f"<caption>{txt(legenda)}</caption>" if legenda else ""
    return f'<div class="tw"><table class="{cls}">{cap}<thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def bloco(b, root, moeda="R$", deck=False):
    """Renderiza um bloco {tipo: ...} do conteudo.json. root = pasta do país (caminhos de arquivo relativos a ela)."""
    tp = b.get("tipo")
    leg = b.get("legenda")
    fig = (lambda svg: f'<figure>{svg}{f"<figcaption>{txt(leg)}</figcaption>" if leg else ""}</figure>')
    if tp == "texto":
        return paras(b["texto"], links=not deck, nw=deck)
    if tp == "lista":
        return "<ul>" + "".join(f"<li>{txt(x, links=not deck, nw=deck)}</li>" for x in b["itens"]) + "</ul>"
    if tp == "tabela":
        if deck:
            h = "".join(f"<th>{txt(x, links=False)}</th>" for x in b["cab"])
            r = "".join("<tr>" + "".join(f"<td>{txt(c, links=False, nw=True)}</td>" for c in row) + "</tr>" for row in b["linhas"])
            return f'<table class="tbl sm-t{" xs-t" if len(b["linhas"]) > 6 else ""}"><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table>' + (f'<p class="legend">{txt(leg, links=False)}</p>' if leg else "")
        return tabela(b["cab"], b["linhas"], cls="kv" if b.get("kv") else b.get("cls", ""), legenda=leg)
    if tp == "kpis":
        if deck:
            return '<div class="kpis4">' + "".join(f'<div class="kpi big"><b>{txt(k["v"], links=False)}</b><span>{txt(k["l"], links=False)}</span><em>{txt(k.get("s", ""), links=False)}</em></div>' for k in b["itens"]) + "</div>"
        return '<div class="kpis">' + "".join(f'<div class="kpi"><div class="v">{txt(k["v"], links=False)}</div><div class="l">{txt(k["l"])}</div><div class="s">{txt(k.get("s", ""))}</div></div>' for k in b["itens"]) + "</div>"
    if tp == "barras":
        serie = [(str(a), float(v)) for a, v in b["serie"]]
        dest = set(map(str, b.get("destaque", [])))
        if deck:
            return svg_barras_deck(serie, b.get("w", 860), b.get("h", 400), leg or "Série", destaque=dest,
                                   marco=b.get("marco"), marco_txt=b.get("marco_txt"), fmt=fmt_fn(b.get("fmt"), moeda), ultimo=b.get("ultimo", False))
        return fig(svg_barras_rel(serie, destaque=dest))
    if tp == "barra100":
        svg = svg_barra100(b["segs"], b.get("w", 1000), b.get("h", 210), leg or "Barra 100%")
        nota = "".join(f"<li><b>{esc(s[0])}:</b> {txt(s[2], links=not deck)}</li>" for s in b["segs"] if len(s) > 2 and s[2])
        return svg + (f'<ul class="segnote">{nota}</ul>' if nota else "")
    if tp == "waterfall":
        f = fmt_fn(b.get("fmt", "moeda"), moeda)
        if deck:
            return svg_waterfall_deck(b["itens"], f, b.get("w", 1060), b.get("h", 640), leg or "Waterfall", compacto=b.get("compacto", False))
        return fig(svg_waterfall_rel(b["itens"], f))
    if tp == "imagem":
        src = img_b64(os.path.join(root, b["arquivo"]), 1800 if deck else 1600)
        alt = esc(leg or os.path.basename(b["arquivo"]))
        if deck:
            return f'<figure class="shot"><img alt="{alt}" src="{src}">{f"<figcaption>{txt(leg, links=False)}</figcaption>" if leg else ""}</figure>'
        return f'<figure class="shot"><img loading="lazy" alt="{alt}" src="{src}">{f"<figcaption>{txt(leg)}</figcaption>" if leg else ""}</figure>'
    if tp in ("json", "query"):
        d = json.load(open(os.path.join(root, b["arquivo"])))
        if tp == "query":
            d = d.get("request", d)
        s = json.dumps(mascarar(d), ensure_ascii=False, indent=2)
        lim = b.get("max", 6000)
        if len(s) > lim:
            s = s[:lim] + f"\n… ({f_int(len(s) - lim)} caracteres omitidos; arquivo completo no índice de evidências)"
        rot = "Requisição" if tp == "query" else "Trecho"
        return f'<details class="raw"><summary>{rot}: <code>{esc(b["arquivo"])}</code></summary><pre>{esc(s)}</pre></details>' + (f"<p class=\"src\">{txt(leg)}</p>" if leg else "")
    if tp == "html":  # escape hatch: HTML pronto (usar pouco)
        return b["html"]
    raise ValueError(f"bloco desconhecido: {tp}")


def blocos(lista, root, moeda="R$", deck=False):
    return "".join(bloco(b, root, moeda, deck) for b in (lista or []))
