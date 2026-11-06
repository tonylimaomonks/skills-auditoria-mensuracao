// Monta o .pptx a partir do que extrair.js gravou: fundo PNG por slide + texto nativo editável por cima,
// nas fontes substitutas do Google Fonts (abre igual no Google Slides e no PowerPoint).
// Uso: node montar.js <pasta-extracao> <saida.pptx>
const pptxgen = require('pptxgenjs');
const fs = require('fs'), path = require('path');
const [dir, outFile] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(path.join(dir, 'deck.json')));
const deck = D.slides, F_ = D.fontes;

const PX = 1 / 144;          // 1920 px = 13,333 in
const PT = 0.5;              // 1 px = 0,5 pt
const MONO = F_.mono || 'Roboto Mono';
const face = (r) => r.mono ? MONO : (F_.mapa[r.fam] || r.fam);
const nat = (f) => (F_.nat[f] && F_.nat[f].nat) || 1.25;
const fontOf = (r) => { const f = face(r); return { face: f, nat: nat(f) }; };

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = D.titulo || 'Apresentação';
pres.author = 'Monks';
pres.theme = { headFontFace: F_.display || 'Arial', bodyFontFace: F_.texto || 'Arial' };

let apxStarted = false;
pres.addSection({ title: 'Apresentação' });
deck.forEach((s, i) => {
  const n = String(i + 1).padStart(2, '0');
  if (s.apx && !apxStarted) { pres.addSection({ title: 'Apêndice' }); apxStarted = true; }
  const slide = pres.addSlide({ sectionTitle: apxStarted ? 'Apêndice' : 'Apresentação' });
  slide.background = { path: path.join(dir, `bg-${n}.png`) };

  for (const b of s.blocks) {
    const runs = b.runs.filter(r => r.br || r.t);
    const main = runs.filter(r => r.t).sort((a, c) => c.t.length - a.t.length)[0];
    const F = fontOf(main);
    const size = main.size;
    const mult = Math.max(0.7, Math.min(2.5, b.lh / (size * F.nat)));
    const [bx, by, bw, bh] = b.box;
    const [tx, ty, tw, th] = b.text;
    const oneLine = th < b.lh * 1.5;
    // x/largura: caixa de conteúdo do bloco; texto de uma linha ganha folga para não quebrar
    const left = !(b.align === 'center' || b.align === 'right' || b.align === 'end');
    let x = left ? tx : Math.min(bx, tx);
    let w = Math.max(bx + bw, tx + tw) - x;
    if (oneLine) {
      const slack = Math.max(tw * 0.18, 24);
      if (b.align === 'center') { x -= slack / 2; w += slack; }
      else if (b.align === 'right' || b.align === 'end') { x -= slack; w += slack; }
      else w += slack;
    } else if (/^H[1-3]$/.test(b.tag)) w = tw * 1.03 + 8;   // títulos usam text-wrap:balance
    else w += Math.max(4, w * 0.01);
    // y: topo da primeira linha (o retângulo do texto inclui só a área da fonte, sem a entrelinha)
    const y = ty - (b.lh - size * F.nat) / 2;
    const h = Math.max(th + (b.lh - size * F.nat), b.lh);

    const textRuns = runs.map((r, k) => {
      if (r.br) return { text: '', options: { breakLine: true } };
      const f = fontOf(r);
      const o = {
        fontFace: f.face, fontSize: +(r.size * PT).toFixed(1), color: r.color,
        bold: r.weight >= 600, italic: r.italic,
      };
      if (r.ls) o.charSpacing = +(r.ls * PT).toFixed(2);
      if (r.hl) o.highlight = 'FFC409';
      return { text: r.t, options: o };
    });
    // breakLine é aplicado no run anterior ao <br>
    const merged = [];
    for (const r of textRuns) {
      if (r.text === '' && r.options.breakLine) { if (merged.length) merged[merged.length - 1].options.breakLine = true; }
      else merged.push(r);
    }
    if (!merged.length) continue;
    const opts = {
      x: x * PX, y: y * PX, w: w * PX, h: h * PX, margin: 0, isTextBox: true,
      valign: 'top', align: b.align === 'center' ? 'center' : (b.align === 'right' || b.align === 'end') ? 'right' : 'left',
      lineSpacingMultiple: +mult.toFixed(2), fit: 'none', wrap: true,
      objectName: `${b.tag.toLowerCase()}${b.cls ? '.' + String(b.cls).split(' ')[0] : ''}`,
    };
    if (b.bullet) {
      const ind = size * 1.1;
      opts.x = (x - ind) * PX; opts.w = (w + ind) * PX;
      opts.bullet = b.bullet === 'decimal' ? { type: 'number', indent: ind * PT } : { indent: ind * PT };
    }
    slide.addText(merged, opts);
  }
  if (s.notes) slide.addNotes(s.notes);
});

pres.writeFile({ fileName: outFile }).then(f => console.log('ok', f));
