// Escolhe a fonte do Google Fonts mais próxima de uma fonte de marca que o Google Slides não tem: mede a
// largura de um título em caixa alta na fonte da marca (carregada pelo deck) e em cada candidata.
// Uso: node medir_fontes.js <deck.html> "<família da marca>" [peso=700] [candidatas separadas por vírgula]
// Saída: candidatas ordenadas pela distância de largura (1,000 = igual). Prefira ≤ 1,00 (não estoura a caixa).
const puppeteer = require('puppeteer-core'); const path = require('path');
const [deckHtml, marca, peso = '700', lista] = process.argv.slice(2);
const C = (lista ? lista.split(',') : ['Montserrat', 'Poppins', 'Inter', 'Archivo', 'Plus Jakarta Sans', 'Outfit',
  'Lexend', 'Red Hat Display', 'Figtree', 'Sora', 'Manrope', 'Urbanist', 'Kanit', 'Barlow', 'Rubik', 'Work Sans',
  'Lato', 'Roboto', 'Open Sans', 'Raleway', 'Nunito Sans', 'Archivo Narrow', 'Barlow Semi Condensed',
  'Roboto Condensed', 'Encode Sans', 'DM Sans', 'Oswald', 'Anton', 'Bebas Neue']).map(s => s.trim());
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new' });
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(deckHtml), { waitUntil: 'networkidle0' });
  const r = await p.evaluate(async (marca, peso, C) => {
    const l = document.createElement('link'); l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?' + C.map(f => 'family=' + f.replace(/ /g, '+') + ':wght@' + peso).join('&') + '&display=block';
    document.head.appendChild(l); await new Promise(r => { l.onload = r; l.onerror = r; });
    const T = 'DE 15 A 20/10, 9 AÇÕES ATACAM CREDENCIAL, DADO PESSOAL, CONVERSÕES E ACESSOS; O PLANO FECHA EM 26/10';
    const w = async (f) => {
      await document.fonts.load(`${peso} 50px "${f}"`);
      const s = document.createElement('span');
      s.style.cssText = `font-family:"${f}",monospace;font-weight:${peso};font-size:50px;white-space:nowrap;position:absolute`;
      s.textContent = T; document.body.appendChild(s); const x = s.getBoundingClientRect().width; s.remove(); return x;
    };
    const base = await w(marca);
    const out = [];
    for (const f of C) out.push([f, +((await w(f)) / base).toFixed(3)]);
    return out;
  }, marca, peso, C);
  r.sort((a, c) => Math.abs(1 - a[1]) - Math.abs(1 - c[1]));
  r.forEach(([f, x]) => console.log(x.toFixed(3), f));
  await b.close();
})();
