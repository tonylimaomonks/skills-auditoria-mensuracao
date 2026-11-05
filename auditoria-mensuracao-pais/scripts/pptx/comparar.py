"""QA do port: folhas lado a lado (esquerda HTML original, direita pptx simulado), 3 slides por folha, e o ranking
dos slides com maior diferença de pixels (comece a conferência por eles).
Uso: python comparar.py <pasta-extracao> <pasta-sim> <pasta-saida>
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ext, sim, out = map(Path, sys.argv[1:4])
refs = sorted(ext.glob("ref-*.png"))
dif = []
for r in refs:
    s = sim / r.name.replace("ref-", "sim-")
    a, b = Image.open(r).convert("L"), Image.open(s).convert("L")
    dif.append((ImageStat.Stat(ImageChops.difference(a, b)).mean[0], r.stem[4:]))
for k in range(0, len(refs), 3):
    W = Image.new("RGB", (1920, 540 * 3), "white")
    for j, r in enumerate(refs[k:k + 3]):
        W.paste(Image.open(r).resize((960, 540)), (0, 540 * j))
        W.paste(Image.open(sim / r.name.replace("ref-", "sim-")).resize((960, 540)), (960, 540 * j))
    W.save(out / f"par-{k // 3 + 1:02d}.png")
linhas = [f"slide {n}: {m:.1f}" for m, n in sorted(dif, reverse=True)]
(out / "diferenca.txt").write_text("\n".join(linhas) + "\n")
print("maiores diferenças:", ", ".join(linhas[:6]))
