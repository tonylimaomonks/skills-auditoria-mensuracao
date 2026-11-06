// Renderiza cada slide do deck HTML do motor em 1920x1080 (tema claro), extrai os blocos de texto com
// posição e estilo e salva o fundo sem texto em PNG (bg-NN.png) e o slide inteiro (ref-NN.png, para o QA).
// Uso: node extrair.js <deck.html> <pasta-saida> <fontes.json>
// fontes.json = {"mapa": {"<família web>": "<fonte do Google Fonts>"}, "mono": "Roboto Mono"}; a altura
// natural da linha de cada fonte substituta é medida aqui e vai para deck.json (montar.js usa).
const puppeteer = require('puppeteer-core');
const fs = require('fs'), path = require('path');
const [src, out, fontesArq] = process.argv.slice(2);
const FONTES = JSON.parse(fs.readFileSync(fontesArq));
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new', args: ['--hide-scrollbars', '--force-color-profile=srgb'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
  await page.goto('file://' + path.resolve(src), { waitUntil: 'networkidle0' });
  await page.evaluate(() => { document.documentElement.setAttribute('data-theme','light'); document.querySelectorAll('svg').forEach(v=>{v.style.color=getComputedStyle(v).color}); return document.fonts.ready; });
  await page.addStyleTag({ content: `
    #deck{transform:none!important}
    .slide{transition:none!important}
    #bar,#cnt,.nav,.progress{display:none!important}
    aside.notes{display:none!important}` });
  const n = await page.evaluate(() => document.querySelectorAll('.slide').length);
  const deck = [];
  for (let i = 0; i < n; i++) {
    const data = await page.evaluate((i) => {
      const slides = [...document.querySelectorAll('.slide')];
      slides.forEach((s, k) => { s.classList.toggle('active', k === i); });
      const s = slides[i];
      document.querySelectorAll('.pptx-hide').forEach(e => e.classList.remove('pptx-hide'));
      const INLINE = new Set(['inline', 'inline-block', 'inline-flex', 'contents']);
      const rgb2hex = (c) => {
        const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
        const p = m[1].split(',').map(x => parseFloat(x));
        if (p.length === 4 && p[3] === 0) return null;
        return p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
      };
      const visible = (el) => {
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return false;
        if (el.closest('svg') || el.closest('aside.notes') || el.closest('.sr')) return false;
        if (cs.display === 'contents') return true;
        const r = el.getBoundingClientRect(); return r.width > 1 && r.height > 1;
      };
      const isBlock = (el) => !INLINE.has(getComputedStyle(el).display);
      // blocos de texto: elemento não inline com texto direto ou em filhos inline
      const blocks = [];
      const walk = (el) => {
        if (!visible(el)) return;
        if (el.tagName === 'svg' || el.tagName === 'STYLE' || el.tagName === 'SCRIPT') return;
        let hasText = false;
        const scan = (node) => {
          for (const c of node.childNodes) {
            if (c.nodeType === 3 && c.textContent.trim()) hasText = true;
            else if (c.nodeType === 1 && c.tagName !== 'svg' && !isBlock(c) && visible(c)) scan(c);
          }
        };
        if (isBlock(el)) scan(el);
        if (hasText) blocks.push(el);
        for (const c of el.children) walk(c);
      };
      walk(s);
      const out = [];
      for (const b of blocks) {
        const cs = getComputedStyle(b);
        const r = b.getBoundingClientRect();
        const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth);
        const pr = parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth);
        const pt = parseFloat(cs.paddingTop) + parseFloat(cs.borderTopWidth);
        const pb = parseFloat(cs.paddingBottom) + parseFloat(cs.borderBottomWidth);
        // área real ocupada pelo texto (para blocos flex/centralizados)
        const range = document.createRange();
        const runs = [];
        let tx0 = 1e9, ty0 = 1e9, tx1 = -1e9, ty1 = -1e9;
        const collect = (node) => {
          for (const c of node.childNodes) {
            if (c.nodeType === 3) {
              let t = c.textContent.replace(/\s+/g, ' ');
              if (!t.trim() && !t) continue;
              const p = c.parentElement, ps = getComputedStyle(p);
              range.selectNodeContents(c);
              for (const rr of range.getClientRects()) {
                if (rr.width < 0.5) continue;
                tx0 = Math.min(tx0, rr.left); ty0 = Math.min(ty0, rr.top);
                tx1 = Math.max(tx1, rr.right); ty1 = Math.max(ty1, rr.bottom);
              }
              if (ps.textTransform === 'uppercase') t = t.toUpperCase();
              const hlEl = p.closest('.hl'); const hl = hlEl && getComputedStyle(hlEl).backgroundImage !== 'none';
              runs.push({
                t, font: ps.fontFamily, size: parseFloat(ps.fontSize), weight: parseInt(ps.fontWeight),
                italic: ps.fontStyle === 'italic', color: rgb2hex(ps.color) || '000000',
                ls: parseFloat(ps.letterSpacing) || 0, hl: !!hl,
                mono: /mono|Menlo|monospace/i.test(ps.fontFamily.split(',')[0]),
                fam: ps.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, ''),
              });
            } else if (c.nodeType === 1) {
              if (c.tagName === 'BR') { runs.push({ br: true }); continue; }
              if (c.tagName === 'svg' || isBlock(c) || !visible(c)) continue;
              const ccs = getComputedStyle(c);
              let padL = 0, padR = 0;
              if (ccs.display === 'inline-block' || ccs.display === 'inline-flex') {
                padL = parseFloat(ccs.paddingLeft) + parseFloat(ccs.marginLeft) + parseFloat(ccs.borderLeftWidth);
                padR = parseFloat(ccs.paddingRight) + parseFloat(ccs.marginRight) + parseFloat(ccs.borderRightWidth);
              }
              const sp = (px) => {
                if (px < 2) return;
                const ctx = (window.__cv ||= document.createElement('canvas').getContext('2d'));
                ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
                const k = Math.round(px / ctx.measureText('\u00A0').width);
                if (k > 0) runs.push({ t: '\u00A0'.repeat(k), font: cs.fontFamily, size: parseFloat(cs.fontSize), weight: 400, italic: false, color: '000000', ls: 0, hl: false, mono: false, pad: true, fam: cs.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '') });
              };
              sp(padL); collect(c); sp(padR);
            }
          }
        };
        collect(b);
        if (!runs.some(x => x.t && x.t.trim())) continue;
        let clipped = false;
        for (let a = b; a && a !== s.parentElement; a = a.parentElement) {
          const as = getComputedStyle(a);
          if (as.overflow !== 'visible' || as.overflowY !== 'visible') {
            const ar = a.getBoundingClientRect();
            if (ty0 >= ar.bottom - 2 || tx0 >= ar.right - 2) { clipped = true; break; }
          }
        }
        const srect = s.getBoundingClientRect();
        if (ty0 >= srect.bottom - 2) clipped = true;
        if (clipped) continue;
        // apara espaços nas pontas
        const first = runs.find(x => x.t !== undefined); if (first) first.t = first.t.replace(/^\s+/, '');
        const last = [...runs].reverse().find(x => x.t !== undefined); if (last) last.t = last.t.replace(/\s+$/, '');
        const cx0 = r.left + pl, cx1 = r.right - pr, cy0 = r.top + pt, cy1 = r.bottom - pb;
        const lh = cs.lineHeight === 'normal' ? parseFloat(cs.fontSize) * 1.2 : parseFloat(cs.lineHeight);
        out.push({
          tag: b.tagName, cls: b.className && b.className.baseVal === undefined ? b.className : '',
          box: [cx0, cy0, cx1 - cx0, cy1 - cy0], text: [tx0, ty0, tx1 - tx0, ty1 - ty0],
          align: cs.textAlign, lh, ws: cs.whiteSpace, runs,
          bullet: b.tagName === 'LI' && cs.listStyleType !== 'none' ? cs.listStyleType : null,
        });
      }
      const notes = s.querySelector('aside.notes');
      return {
        id: s.id, label: s.getAttribute('aria-label'), apx: s.classList.contains('apx'),
        notes: notes ? [...notes.querySelectorAll('p')].map(p => p.innerText.trim()).join('\n\n') : '',
        blocks: out,
      };
    }, i);
    // fundo: esconde o texto HTML (o SVG mantém o texto dele) e tira o marca-texto do título
    await page.evaluate(() => {
      let rules = '', k = 0;
      document.querySelectorAll('.slide.active *').forEach(el => {
        for (const ps of ['::before', '::after']) {
          const c = getComputedStyle(el, ps);
          if (c.content && c.content !== 'none' && c.content !== 'normal' && c.content !== '""') {
            if (!el.dataset.pc) el.dataset.pc = 'p' + (k++);
            rules += `[data-pc="${el.dataset.pc}"]${ps}{color:${c.color}!important;-webkit-text-fill-color:${c.color}!important}`;
          }
        }
      });
      const st = document.createElement('style'); st.id = 'hide-text';
      st.textContent = `.slide.active *:not(svg):not(svg *){color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important}
        .slide.active h2 .hl{background:none!important}
        .slide.active li::marker{color:transparent!important}` + rules;
      document.head.appendChild(st);
    });
    await page.screenshot({ path: path.join(out, `bg-${String(i + 1).padStart(2, '0')}.png`) });
    await page.evaluate(() => document.getElementById('hide-text').remove());
    await page.screenshot({ path: path.join(out, `ref-${String(i + 1).padStart(2, '0')}.png`) });
    deck.push(data);
    process.stdout.write(`${i + 1} `);
  }
  // altura natural (line-height: normal) das fontes substitutas, carregadas do Google Fonts
  const subs = [...new Set([...Object.values(FONTES.mapa || {}), FONTES.mono || 'Roboto Mono'])];
  const nat = await page.evaluate(async (subs) => {
    const l = document.createElement('link'); l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?' + subs.map(f => 'family=' + f.replace(/ /g, '+') + ':wght@400;700').join('&') + '&display=block';
    document.head.appendChild(l);
    await new Promise(r => { l.onload = r; l.onerror = r; setTimeout(r, 8000); });
    const r = {};
    for (const f of subs) {
      let ok = false;
      try { ok = (await document.fonts.load(`700 100px "${f}"`)).length > 0; } catch (e) {}
      const sp = document.createElement('span');
      sp.style.cssText = `font-family:"${f}";font-size:100px;line-height:normal;position:absolute;white-space:nowrap`;
      sp.textContent = 'ÁgÇ'; document.body.appendChild(sp);
      r[f] = { nat: +(sp.getBoundingClientRect().height / 100).toFixed(3), carregou: ok };
      sp.remove();
    }
    return r;
  }, subs);
  const titulo = (deck[0] && deck[0].label || '').replace(/^\d+ de \d+: /, '');
  fs.writeFileSync(path.join(out, 'deck.json'), JSON.stringify({ titulo, fontes: { ...FONTES, nat }, slides: deck }, null, 1));
  for (const [f, v] of Object.entries(nat)) if (!v.carregou) console.error(`\nAVISO: "${f}" não carregou do Google Fonts (nome errado ou sem rede); altura de linha estimada`);
  await browser.close();
  console.log('\nok', n);
})();
