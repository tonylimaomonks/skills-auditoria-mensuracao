"""Port do deck HTML do motor para .pptx, pensado para abrir no Google Slides (e no PowerPoint).

Cada slide vira: o visual do HTML (fundos, cards, gráficos SVG, logos, pílulas) como imagem de fundo e todo o
texto como caixa de texto nativa e editável por cima, na mesma posição, cor e tamanho, mais as notas do
apresentador. As fontes da marca que o Google Slides não tem são trocadas pela do Google Fonts indicada em
marca.json → pptx_fontes (escolha com medir_fontes.js). Gráficos ficam como imagem (não editáveis).

Uso:
  python3 port_pptx.py <deck-design.html> --marca <pasta da marca> [--saida deck.pptx] [--qa <pasta>]
  --qa grava o simulador (sim-NN.png), as folhas lado a lado HTML × pptx (par-NN.png) e o ranking de diferença.

Dependências: node + Chrome (/Applications/Google Chrome.app); pptxgenjs e puppeteer-core são instalados em
node_modules/ desta pasta na primeira execução. O QA cria .venv/ aqui com python-pptx e pillow. Precisa de rede
(Google Fonts) para medir as fontes substitutas.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MONO = "Roboto Mono"


def _familia(stack):
    return stack.split(",")[0].strip().strip('"').strip("'")


def fontes(marca_dir):
    """Mapa família web → fonte do Google Fonts, a partir do marca.json. Devolve (fontes, avisos)."""
    M = json.loads((Path(marca_dir) / "marca.json").read_text(encoding="utf-8"))
    pf = dict(M.get("pptx_fontes") or {})
    mono = pf.pop("mono", MONO)
    disp, txt = _familia(M["fonte_display"]), _familia(M["fonte_texto"])
    avisos = []
    for f in {disp, txt}:
        if f not in pf:
            pf[f] = f
            avisos.append(f'marca.json sem pptx_fontes["{f}"]: usando "{f}" no pptx (só funciona no Google Slides '
                          f'se for do Google Fonts; escolha a substituta com medir_fontes.js)')
    return {"mapa": pf, "mono": mono, "display": pf[disp], "texto": pf[txt]}, avisos


def _deps():
    if not (AQUI / "node_modules/pptxgenjs").exists() or not (AQUI / "node_modules/puppeteer-core").exists():
        print("instalando pptxgenjs e puppeteer-core em", AQUI / "node_modules")
        subprocess.run(["npm", "install", "--silent", "--no-audit", "--no-fund", "--prefix", str(AQUI)], check=True)


def _venv():
    py = AQUI / ".venv/bin/python"
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(AQUI / ".venv")], check=True)
        subprocess.run([str(py), "-m", "pip", "-q", "install", "python-pptx", "pillow"], check=True)
    return str(py)


def gerar(deck_html, saida, marca_dir, qa=None):
    """Gera o .pptx. Devolve {'slides': n, 'avisos': [...], 'qa': pasta ou None}."""
    _deps()
    F, avisos = fontes(marca_dir)
    tmp = Path(qa) if qa else Path(tempfile.mkdtemp(prefix="pptx-"))
    ext = tmp / "extracao"
    ext.mkdir(parents=True, exist_ok=True)
    (ext / "fontes.json").write_text(json.dumps(F, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run(["node", str(AQUI / "extrair.js"), str(Path(deck_html).resolve()), str(ext), str(ext / "fontes.json")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("extrair.js falhou:\n" + r.stderr[-2000:])
    avisos += [l.strip() for l in r.stderr.splitlines() if l.strip().startswith("AVISO")]
    D = json.loads((ext / "deck.json").read_text(encoding="utf-8"))
    n = len(D["slides"])
    saida = Path(saida).resolve()
    r = subprocess.run(["node", str(AQUI / "montar.js"), str(ext), str(saida)], capture_output=True, text=True)
    if r.returncode:
        sys.exit("montar.js falhou:\n" + r.stderr[-2000:])
    with zipfile.ZipFile(saida) as z:
        ns = len([x for x in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)])
    if ns != n:
        sys.exit(f"pptx com {ns} slides, deck HTML com {n}")
    if qa:
        py = _venv()
        sim = tmp / "sim"
        subprocess.run([py, str(AQUI / "simular.py"), str(saida), str(ext / "deck.json"), str(sim)], check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run(["node", str(AQUI / "fotografar.js")] + sorted(str(p) for p in sim.glob("sim-*.html")),
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run([py, str(AQUI / "comparar.py"), str(ext), str(sim), str(tmp)], check=True)
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"slides": n, "avisos": avisos, "qa": str(tmp) if qa else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--marca", required=True, help="pasta da marca (com marca.json)")
    ap.add_argument("--saida")
    ap.add_argument("--qa", help="pasta para o simulador e as folhas de comparação")
    a = ap.parse_args()
    saida = a.saida or re.sub(r"(-design)?\.html$", ".pptx", a.deck)
    res = gerar(a.deck, saida, a.marca, a.qa)
    for x in res["avisos"]:
        print("AVISO", x)
    print(f"pptx: {saida} · {res['slides']} slides · {os.path.getsize(saida) / 1e6:.1f} MB")
    if res["qa"]:
        print(f"QA: {res['qa']}/par-*.png (esquerda HTML, direita pptx) e {res['qa']}/diferenca.txt")


if __name__ == "__main__":
    main()
