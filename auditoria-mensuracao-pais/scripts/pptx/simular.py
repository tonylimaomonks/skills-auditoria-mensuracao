"""QA do port: redesenha o .pptx em HTML (fundo + caixas de texto nas fontes do Google Fonts, com o
espaçamento proporcional que o Google Slides usa), um arquivo sim-NN.html por slide.
Uso: python simular.py <deck.pptx> <deck.json da extração> <pasta-saida>   (OUTLINE=1 mostra as caixas)
"""
import sys, os, base64, html, json
from pptx import Presentation

src, dj, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
p = Presentation(src)
S = 1920 / p.slide_width  # emu -> px
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
NAT = {k: v["nat"] for k, v in json.load(open(dj))["fontes"]["nat"].items()}
_fam = "&".join("family=" + f.replace(" ", "+") + ":wght@400;700" for f in NAT)
FONTS = f'<link href="https://fonts.googleapis.com/css2?{_fam}&display=block" rel="stylesheet">'

for i, sl in enumerate(p.slides, 1):
    bg = sl.background._cSld.bg
    blip = bg.find('.//' + A + 'blip')
    rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    img = sl.part.related_part(rid).blob
    parts = [f'<html><head><meta charset=utf-8>{FONTS}<style>body{{margin:0}}#s{{position:relative;width:1920px;height:1080px;background:url(data:image/png;base64,{base64.b64encode(img).decode()})}}.b{{position:absolute;overflow:visible;outline:1px dashed rgba(255,0,255,{os.environ.get("OUTLINE","0")})}}p{{margin:0}}</style></head><body><div id=s>']
    for sh in sl.shapes:
        if not sh.has_text_frame: continue
        x, y, w, h = (v * S for v in (sh.left, sh.top, sh.width, sh.height))
        ps = []
        for para in sh.text_frame.paragraphs:
            pPr = para._p.find(A + 'pPr')
            mult = 1.0
            ln = para._p.find('.//' + A + 'lnSpc/' + A + 'spcPct')
            if ln is not None: mult = int(ln.get('val')) / 100000
            algn = pPr.get('algn') if pPr is not None else None
            al = {'ctr': 'center', 'r': 'right'}.get(algn, 'left')
            bullet = pPr is not None and (pPr.find(A + 'buChar') is not None or pPr.find(A + 'buAutoNum') is not None)
            spans = []; fsz = 12; face = ''
            for r in para.runs:
                rp = r._r.find(A + 'rPr')
                f = r.font
                face = f.name or ''; fsz = f.size.pt if f.size else 12
                col = str(f.color.rgb) if f.color and f.color.type else '000000'
                st = f'font-family:"{face}";font-size:{fsz/0.5}px;color:#{col};font-weight:{700 if f.bold else 400};'
                if rp is not None and rp.get('spc'): st += f'letter-spacing:{int(rp.get("spc"))/100/0.5}px;'
                hl = rp.find(A + 'highlight') if rp is not None else None
                if hl is not None: st += 'background:#FFC409;'
                spans.append(f'<span style=\'{st}\'>{html.escape(r.text)}</span>')
            lh = mult * NAT.get(face, 1.3) * fsz / 0.5
            pre = '• ' if bullet else ''
            ps.append(f'<p style="text-align:{al};line-height:{lh:.1f}px;white-space:pre-wrap">{pre}{"".join(spans)}</p>')
        parts.append(f'<div class=b style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px">{"".join(ps)}</div>')
    parts.append('</div></body></html>')
    open(os.path.join(out, f'sim-{i:02d}.html'), 'w').write(''.join(parts))
print('ok', len(p.slides))
