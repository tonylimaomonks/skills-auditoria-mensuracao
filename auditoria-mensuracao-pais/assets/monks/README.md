---
tipo: design-system
marca: Monks (antiga Media.Monks / MediaMonks), grupo S4 Capital
data: 2026-10-13
uso: assinatura secundária (co-branding) na apresentação executiva Smart Fit
tags: [smart-fit, design-system, monks, co-branding]
---

# Monks: design system e identidade visual

Esta nota serve de referência para usar a Monks como **assinatura secundária** nos entregáveis da auditoria Smart Fit, onde a identidade da Smart Fit é a predominante. Os tokens prontos estão em `tokens.css` (variáveis `--mk-*`) e em `tokens.json`.

**Como ler as marcações de origem:**
- **[oficial-site]**: extraído do código de monks.com (CSS, HTML, manifest e bundles JS) em 13/10/2026.
- **[oficial-bb]**: lido nos slides do brand book 2024 publicados pelo designer responsável pelo rebrand (Chris Allen, "Lead Brand & Design Strategist").
- **[inferido]**: dedução ou sugestão nossa. Não é regra oficial.

---

## 1. Contexto da marca

- **Linha do tempo.** MediaMonks (2001) → **Media.Monks** (2021, fusão MediaMonks + MightyHive sob a S4 Capital; o logo da época tinha o hexágono da MightyHive) → **Monks** (anunciado em 18/07/2024, quando o nome deixou de ter "Media"). Fontes: Wikipedia e Campaign ME.
  - Correção ao briefing: o rebrand atual **não é de 2022**. Ele foi feito em 2023–2024 e anunciado em julho de 2024.
- **Autoria.** O rebrand foi conduzido internamente. Chris Allen se apresenta como líder "across its full scope, from identity and architecture to the motion language". Nenhuma agência externa aparece nas fontes. O tipo customizado foi feito **em colaboração com a Monotype** [oficial-bb].
- **Lógica do logo: "The Dot".** O ponto vem da pontuação de "Media.Monks". Ele foi preservado e virou o núcleo do sistema. A marca passou a ser escrita **`.monks`**, com o ponto à esquerda. Na tipografia, o "o" sob medida tem contraforma circular e simboliza "the collective intelligence of all our Monks" [oficial-bb].
- **Arquitetura de marca.** "ONE BRAND, ONE P&L, ONE LOGO" [oficial-bb]. São duas práticas (Marketing e Technology) sob uma marca única, com sub-marcas no padrão `Nome.Monks` (ex.: Monks.Flow, Formula.Monks).
- **Brand spectrum** [oficial-bb]:
  - "Clean and serious" (core brand)
  - "Bold and sophisticated" (a expressão "Now", com a esfera iridescente)
  - "Loud and expressive" (cultura e comunidades)

  O brand book avisa: "All treatments and logos need to follow the guidelines and get brand approval".

## 2. Logo e variações

Os SVGs ficam em `assets/logos/`. Os arquivos `*.original-currentColor.svg` são o código-fonte exato do site, extraído do bundle JS `static/chunks/9164.*.js` (o mapa de ícones `cf-a2-icon`) [oficial-site]. As variantes de cor foram geradas por nós trocando apenas o `fill`.

| Arquivo | O que é | viewBox | Status |
|---|---|---|---|
| `dot-monks-logo.*.svg` | **Logo atual `.monks`**, usado no header e no chat do site | 0 0 99 21 | **Usar este** |
| `media-monks-m.*.svg` | Monograma **`.m`**, usado no mobile (`data-mobile-logo`) e no favicon | 0 0 23 10 | Ícone/avatar |
| `favicon.svg` | `.m` lilás `#DFBBFE` sobre círculo `#2C2D38` | 308×308 | Ícone oficial |
| `favicon-mask.svg`, `apple-touch-icon.png` | Ícones do site | n/a | Referência |
| `wikimedia-Monks_logo.svg` | `.monks` em `#371534` (Wikimedia Commons, marcado como PD-textlogo) | 0 0 109 26.8 | Referência de cor |
| `the-monks.*.svg` | Wordmark `the.monks` (ícone legado no bundle) | 0 0 111 14 | Não usar no deck |
| `media-monks.*.svg`, `media-monks-stacked.*.svg` | Logos **antigos** `media.monks` (com hexágono e empilhado) | n/a | **Obsoleto**, não usar |
| `b-corp-logo.*.svg` | Selo B Corp que aparece no site | n/a | Só se for relevante |

Variantes de cor do logo atual:
- `preto` (#2D2D2D, que é o "preto" real da marca)
- `branco` (#FFFFFF)
- `off-white` (#EAE8E4)
- `lilas` (#DFBBFE, a combinação do favicon e do portfólio: "pale lilac on charcoal")
- `pink-tinted` (#371534)

Os renders PNG para conferência estão em `screenshots/render-logo-*.png`.

**Regras de uso encontradas:**
- O asset "dot" expressivo (esfera iridescente): só a esfera única está aprovada. "The two orbs for Marketing and Technology services should not be used at any time" [oficial-bb]. Não precisamos dela num deck de auditoria.
- A fonte do logo é reservada ao logo (ver a seção 4).
- **Não foram encontradas** regras públicas de área de proteção, tamanho mínimo nem co-branding com clientes. Ver as lacunas.

## 3. Cores

### 3.1 Núcleo (o que o site realmente usa)

| Token | Hex | Uso | Onde foi visto |
|---|---|---|---|
| `--mk-charcoal` | `#2D2D2D` | Texto principal e "preto" da marca | 60 ocorrências no `main.css`, `theme-color` e `data-theme-foreground` [oficial-site]. No brand book é "Tan Tinted" |
| `--mk-tan-pastel` | `#EAE8E4` | Fundo padrão (off-white quente) | `:root --themed-background`, 38 ocorrências [oficial-site]. "Tan Pastel" [oficial-bb] |
| `--mk-ink` | `#191715` | Fundo escuro (menu, footer) | `n2-footer`, `navigation-overlay` [oficial-site] |
| `--mk-warm-grey` | `#68655F` | Texto secundário | `m26-text-card`, labels [oficial-site] |
| `--mk-steel-pastel` | `#DEDFE5` | Texto sobre `#191715` | `n3-multi-language` [oficial-site]. No slide do brand book está sem hex |
| `--mk-steel-tinted` | `#2C2D38` | Fundo do favicon/PWA | `manifest.json background_color`, `mask-icon` [oficial-site] |
| `--mk-purple-pastel` | `#DFBBFE` | Cor de destaque da marca (lilás) | `manifest.json theme_color`, favicon, formulário de contato [oficial-site] |
| `--mk-pink-vibrant` | `#FF2CE4` | Magenta do letreiro `.monks` | og:image (`screenshots/og-home-hero.jpg`) e brand book [oficial-bb] |
| `#B81C21` / `#2861C5` | | Erro de formulário e anel de foco | Só UI, não usar no deck |

### 3.2 Paleta completa do brand book 2024 [oficial-bb]

Fonte: slide "Full color palette" (`assets/imagens/chrisallen-monks-color-palette.webp`). São 33 cores em três faixas: pastel (fundos), vibrant (acentos) e tinted (texto escuro do mesmo matiz). O slide diz que CMYK, Pantone e as combinações recomendadas ou a evitar estão num "accessibility deep dive", que não é público.

| Matiz | Pastel | Vibrant | Tinted |
|---|---|---|---|
| Yellow | `#FFF0A9` | `#FFCB16` | `#270F0F` |
| Orange | `#FFDDAB` | `#FB961F` | `#360E0B` |
| Red | `#FFCACA` | `#FF245B` | `#440035` |
| Pink | `#FFB2E8` | `#FF2CE4` | `#371534`* |
| Purple | `#DFBBFE` | `#7D26C9` | `#3C0C60` |
| Blue | `#CBF6FF`* | `#4F24EE` | `#001D38` |
| Teal | `#BCFFEF` | `#4DBAC1` | `#0D3842` |
| Green | `#DCFF93` | `#00DC7C` | `#002838` |
| Tan | `#EAE8E4` | `#6C6962` | `#2D2D2D` |
| Steel | `#DEDFE5`* | `#656982` | `#2C2D38` |
| Neutros | White `#FFFFFF` | Light Grey `#E4E4E5` | Black `#000000` |

\* **Divergências no slide, resolvidas pelo site [inferido]:**
- Blue Pastel aparece rotulado "#BCFFEF" (repetindo o Teal). Usamos `#CBF6FF`, que aparece no HTML de /careers e bate com o tom do círculo.
- Pink Tinted aparece rotulado "#3C0C60" (repetindo o Purple). Usamos `#371534`, par de `#FFB2E8` no site e cor do logo no Wikimedia.
- Steel Pastel está sem hex no slide. Usamos `#DEDFE5`, que vem do site.

### 3.3 Pares fundo/texto usados no site [oficial-site]

Cada página recebe um par pastel + tinted do mesmo matiz, pelos atributos `data-foreground-color` e `data-background-color`:

| Par | Onde foi visto |
|---|---|
| `#EAE8E4` / `#2D2D2D` | Padrão em todas as páginas |
| `#FFF0A9` / `#270F0F` | /solutions/data, 11 blocos |
| `#FFB2E8` / `#371534` | /what-we-do, 12 blocos |
| `#FFB2E8` / `#001D38` | Overlays |
| `#DFBBFE` / `#3C0C60` | Formulário de contato |
| `#FFCACA` / `#440035` | Case Boomtown |
| `#BCFFEF` / `#0D3842` | /careers |
| `#001D38` com logo `#BCFFEF` | Chat |

## 4. Tipografia

| Papel | Família no site | Pesos | Classe CSS | Status / licença |
|---|---|---|---|---|
| Display / logo | **Helvetica Now Extended** (no brand book: "Helvetica Now for Monks Ext XBd", apelidada de "Monkvetica") | 800 | `.font-extended` | **Proprietária**, feita sob medida com a Monotype. "Reserved for our Monks logo and selected applications… All uses require brand approval". **Não aprovada** para sub-logos, sites externos, posts, eventos e conteúdo [oficial-bb] |
| Texto | **Helvetica Now** | 400, 500 | `.font-sans-serif`, `.font-sans-serif-medium` | Monotype (comercial). O card de componentes do brand book cita "Helvetica Neue" como tipografia de uso geral |
| Serifada / expressão | **Morian Trial** | 400 e 400 itálico | `.font-serif` | Versão *trial* de uma fonte comercial, usada em "Architects of Now" na expressão de marca |
| Manuscrita | **Caveat** | 400 | `.font-handwritten` | **Google Fonts (SIL OFL), livre** |

Escala fluida do site [oficial-site]:
- display-l: 40→80px
- display-m: 25→60px
- display-s: 22→35px
- body-l: 20→24px
- body-m: 18px
- label: 14→16px

**Arquivos baixados** (`assets/fonts/`) servem só de referência, porque são woff2/woff servidos por monks.com. **Não embuta** Helvetica Now nem Morian em HTML nosso: a licença de webfont da Monks não se estende a outros domínios, e a fonte do logo é restrita.

**Fallbacks sugeridos (Google Fonts) [inferido]:**
- Display extended 800 → **Archivo** (eixo `wdth` 125, `wght` 800) ou **Archivo Black**. Na prática, para a assinatura, use o **SVG do logo** e não texto.
- Texto → **Inter** (400/500) ou a pilha de sistema `"Helvetica Neue", Helvetica, Arial`. Aliás, a própria Smart Fit provavelmente tem tipografia própria, que deve prevalecer.
- Serifada → **Instrument Serif** ou **Newsreader** (só se houver um slide de encerramento "Monks").
- Manuscrita → **Caveat** (é a mesma fonte do site).

## 5. Forma, layout e tom visual

- **Raios** [oficial-site]:
  - `50%` (51 ocorrências: botões de ícone circulares; o círculo é a forma-assinatura)
  - `4px`
  - pílulas `10rem` (botão "Open" + seta circular no brand book)
  - cards `2–3rem`
- **Grid** [oficial-site]: 4 colunas no mobile e 8 no desktop. Breakpoints de 800, 1200, 1440 e 1920px.
- **Ícones** [oficial-site]: traço fino com `vector-effect: non-scaling-stroke`, em viewBox 70×70 dentro de um círculo. Há setas, play, close etc. em `assets/icones/`. Também há "scribbles" (setas e círculos desenhados à mão: `hand-drawn-arrow*`, `scribble-circle`, `outline-1..3`).
- **Shape language** [oficial-bb]: círculo, cápsula, quadrado arredondado e retângulo, em blocos sólidos.
- **Tom visual** [oficial-bb + inferido]: é minimalista ("Minimalism wasn't an aesthetic choice. It was the only approach that could scale"):
  - Fundo off-white quente e texto charcoal (nunca preto puro).
  - Muito espaço em branco e tipografia grande.
  - Um acento pastel por seção.
  - A esfera iridescente só nas peças "Now".
  - Tom de voz: confiante e curto, com títulos terminando em ponto ("The dot.", "Approved asset.", "Full color palette.").

## 6. Como usar a Monks como assinatura secundária num deck Smart Fit

Não achamos regra oficial de co-branding com cliente. As orientações abaixo são **[inferido]**, montadas a partir do que é oficial: a fonte do logo é restrita, o brand book pede aprovação para tratamentos novos e o ponto é o núcleo da marca.

1. **Logo:** usar só o SVG `dot-monks-logo` (`.monks`), sem alterar proporção nem redesenhar com fonte. Nunca usar `media.monks`, o hexágono ou `the.monks`.
2. **Cor do logo, conforme o fundo do slide Smart Fit:**
   - Fundo claro: `dot-monks-logo.preto.svg` (#2D2D2D).
   - Fundo escuro ou amarelo Smart Fit: `branco` (#FFF) ou `off-white`.
   - Não colorir com o amarelo da Smart Fit nem com outras cores fora da paleta Monks.
3. **Hierarquia:**
   - **Capa:** logo Smart Fit dominante. `.monks` pequeno (altura ~40–50% da do logo Smart Fit), no canto inferior, com legenda opcional "Auditoria de mensuração conduzida por".
   - **Rodapé dos slides:** `.monks` monocromático a ~14–16px de altura, com opacidade cheia, alinhado ao número da página.
   - **Separador:** um filete vertical de 1px entre os logos (padrão comum de endosso), com respiro mínimo igual à altura do `.monks` [inferido].
4. **Área de proteção [inferido]:** pelo menos o diâmetro do ponto multiplicado por 2 em volta do logo. Não sobrepor a fotos sem contraste.
5. **Tipografia do deck:** a da Smart Fit. Não usar Helvetica Now nem fontes Monks no corpo.
6. **Slide de encerramento opcional "Monks":**
   - Fundo `#2D2D2D` com `.monks` em `#EAE8E4`, ou fundo `#2C2D38` com `.monks` lilás `#DFBBFE` (a mesma combinação do favicon).
   - Uma frase curta terminada em ponto e o contato.
   - É o único lugar onde a paleta Monks aparece com força.
7. **Aprovação:** como o brand book exige "brand approval" para tratamentos, vale validar a capa com o time de brand/marketing da Monks antes de enviar ao cliente.

## 7. Inventário de arquivos

- `tokens.css` / `tokens.json`: tokens `--mk-*` com origem anotada.
- `assets/logos/`:
  - `.monks` (preto, branco, off-white, lilás, pink-tinted e original com currentColor)
  - `.m`
  - favicon, favicon-mask, apple-touch-icon
  - `wikimedia-Monks_logo.svg`
  - legados: media.monks, empilhado, the.monks
  - selo B Corp
- `assets/fonts/` (só referência, proprietárias exceto Caveat):
  - `HelveticaNowExtended-800`, `HelveticaNow-400`, `HelveticaNow-500` (woff2)
  - `MorianTrial-400` e `-400italic` (woff)
  - `Caveat-400` (woff2)
- `assets/icones/`: 25 ícones de UI do site (setas, play/pause, close, plus, search, social, scribbles), todos SVG com currentColor.
- `assets/imagens/`: 10 slides do brand book 2024 (webp) + hero JPG, do portfólio de Chris Allen:
  - color-palette, typography, the-dot, dot-detail, dot-approved
  - brand-architecture, core-components, brand-spectrum, brand-book-2024, applications
- `screenshots/`:
  - og:images do site: home/what-we-do (letreiro `.monks`), careers, case Boomtown, solutions/data
  - renders PNG dos logos (gerados com Quick Look)
- `css-bruto/`:
  - `main.css` (494 KB, tema Drupal "monks") e `drupal.css`
  - `manifest.json`
  - HTML de home, careers, what-we-do, solutions/data e case Boomtown
  - `page-about-404.html` (a URL /about retorna 404)

## 8. Lacunas

- Não há brand guidelines ou press kit públicos. As URLs `monks.com/press`, `/brand`, `/newsroom` e `/brand-assets` retornam 404, e o s4capital.com/media não tem downloads de logo.
- O Brandfetch (`brandfetch.com/monks.com`) retornou 403 e não foi consultado.
- Não achamos post no Brand New (UnderConsideration), no Behance nem no Dribbble sobre o rebrand da Monks.
- Faltam regras oficiais de área de proteção, tamanho mínimo, co-branding com cliente e "do/don't" do logo. O portfólio menciona que essas regras existem, mas só mostra o slide da esfera.
- Faltam os valores CMYK/Pantone (estão no "accessibility deep dive", que não é público).
- Os três hex divergentes do slide foram resolvidos por inferência (ver 3.2).
- **Próximo passo sugerido:** pedir ao time de Brand/Marketing da Monks (via canal interno) o brand book 2024 completo, o kit de logos oficial e a regra de co-branding com clientes.

## 9. Fontes

- monks.com:
  - https://www.monks.com/
  - https://www.monks.com/careers
  - https://www.monks.com/what-we-do
  - https://www.monks.com/solutions/data
  - https://www.monks.com/case-studies/boomtown-amplify-ai-powered-platform
- CSS: https://www.monks.com/themes/custom/monks/static/css/main.css
- Manifest: https://www.monks.com/themes/custom/monks/static/json/manifest.json
- Fontes do site: `https://www.monks.com/themes/custom/monks/static/fonts/{4a5b76d5,882730d9,5c2e1d99,7202a0e3}.woff2`, `{9bd974dc,6958b196}.woff`
- Bundle de ícones e logos: https://www.monks.com/themes/custom/monks/static/chunks/9164.e44aba530f0bfe0a76e9.js (lido como texto, não executado)
- Favicon: https://www.monks.com/themes/custom/monks/static/images/svg/favicon.svg
- Brand book 2024 (portfólio do designer): https://mrchrisallen.me/work/monks
- Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Monks_logo.svg
- Wikipedia: https://en.wikipedia.org/wiki/Monks_(media_company)
- Campaign ME, rebrand 2024: https://campaignme.com/sir-martin-sorells-media-monks-rebrands-to-monks/
- Campaign ME, Media.Monks 2021 (hexágono MightyHive): https://mot-backup.campaignme.com/s4-unites-mediamonks-and-mightyhive-under-new-brand-media-monks/
- S4 Capital: https://www.s4capital.com/media (sem kit de marca)
- Helvetica Now (Monotype): https://www.monotype.com/fonts/helvetica-now
