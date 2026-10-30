# Identidade do cliente (Etapa 0, só na primeira vez)

Os HTMLs saem com a identidade do cliente predominante e a Monks como assinatura (logo `.monks` pequeno na capa e no rodapé). A Monks já vem pronta em `assets/monks/` (README, tokens e logos). A do cliente é pesquisada **uma vez** e guardada em `<cliente>/design-system/<slug>/`. Os próximos países do mesmo cliente reaproveitam.

**Pule esta etapa** se `<cliente>/cliente.json` aponta para uma `marca` com `marca.json`.

## 1. Pergunte antes de pesquisar

Pergunte em texto livre (não use opções fechadas):
- Qual é o cliente (nome como deve aparecer) e o grupo/holding, se houver.
- Quais sites (o principal e os de cada país, se forem diferentes). Se a pessoa não tiver, procure o oficial e **confirme** antes de usar.
- Se existe brand book, manual de marca ou kit de imprensa que ela possa mandar (PDF, link do Figma). Material do cliente vale mais do que a inferência.
- Se o documento é interno ou vai a terceiros. Isso decide se fontes proprietárias podem ser embutidas; sem confirmação, use substitutas livres.

## 2. Pesquise em paralelo

- **Deep research** (skill `anthropic-skills:deep-research`; se não estiver disponível, WebSearch/WebFetch em subagents) sobre a marca: rebranding recente e agência, posicionamento e tom de voz, brand book público, kit de imprensa, Wikipedia/Wikimedia (logos antigos), notícias de lançamento, posts oficiais (LinkedIn, Instagram) para ver a identidade aplicada. Registre as fontes com link e data.
- **Extração do site** (Chrome DevTools num subagent de Chrome, ou `curl` quando bastar):
  - CSS custom properties de produção (`getComputedStyle(document.documentElement)` e as folhas `/_next/static/...css` ou equivalentes): cores, escala de neutros, raios, sombras, espaçamentos;
  - contagem de uso real: quais cores e fontes aparecem mais nos elementos visíveis da home;
  - fontes: `document.fonts`, arquivos `.woff2` e a tabela `name` (nome, autoria, licença);
  - logo em SVG (header, footer, favicon, imagem OG), ornamentos gráficos recorrentes;
  - prints (viewport) da home, de uma página de produto e do checkout.
- **Não** use Brandfetch nem bancos de logos de terceiros como fonte final. Logo só do site ou do material oficial.

## 3. Salve no mesmo formato da Smart Fit

`<cliente>/design-system/<slug>/` (referência real: `Smart-Fit/design-system/smartfit/`):

```
README.md        nota com frontmatter (tipo, cliente, data, fonte-principal), contexto da marca,
                 tabela "Oficial × inferido" com o grau de confiança de cada item, cores com uso observado,
                 tipografia, logo (variações e fundos), ornamentos, lacunas e fontes com link
tokens.json      tokens com valor, var CSS e nota de uso
tokens.css       as mesmas variáveis (--<prefixo>-*)
marca.json       manifesto que o motor lê (esquema abaixo)
assets/          fonts/ logos/ icones/ imagens/
screenshots/     prints usados na pesquisa
css-bruto/       CSS e extrações em JSON, para reprocessar
```

## 4. `marca.json`

Referência completa: `Smart-Fit/design-system/smartfit/marca.json`. Caminhos relativos à pasta da marca.

| Campo | O que é |
|---|---|
| `nome` | Nome da marca (aria-label do logo, título das páginas) |
| `favicon` | SVG do favicon |
| `fontes[]` | `{familia, arquivo (.woff2), peso, estilo?, unicode_range?}`, uma por arquivo |
| `fonte_display` | Família dos títulos com uma substituta: `"\"Marca Display\",\"Montserrat\""` |
| `fonte_texto` | Família do texto: `"\"Inter\""` |
| `cores.destaque` | Cor de marca usada no marca-texto dos títulos, KPIs, chip ativo e barra da capa |
| `cores.destaque_2` | Fim do degradê da barra da capa (pode repetir o destaque) |
| `cores.sobre_destaque` / `sobre_destaque_suave` | Texto sobre a cor de destaque (contraste ≥ 4,5:1) |
| `cores.fundo_escuro` | Fundo da capa do relatório e do cabeçalho das evidências |
| `logo` | `{arquivo, viewbox, partes: [{path: <índice do <path> no SVG>, var: "lg-<nome>"}], cores: {claro, escuro, impressao, cabecalho_evidencias}}`. Cada modo dá a cor de cada parte. Logo de uma cor só = uma parte |
| `ornamento` | (opcional) `{arquivo, viewbox, path}`: grafismo da marca sob o título da capa (o sorriso da Smart Fit). Sem ornamento, omita |
| `tokens` | Blocos CSS prontos: `deck_claro`, `deck_escuro`, `rel_claro`, `rel_escuro`, `rel_cabecalho`. Parta dos da Smart Fit e troque **só** as cores de marca (`--y`, `--accent*`, `--soft`, `--s2`, `--mark`, `--link-u`, `--chart-main` no escuro, `--lg-*`). Mantenha os nomes das variáveis e a paleta de criticidade |

Regras de cor:
- Criticidade (Alta, Média, Baixa) é **sempre** a paleta fixa do motor (vermelho, laranja, azul, com rótulo de texto). Se a cor de destaque do cliente for vermelha, laranja ou azul, use um neutro escuro como destaque nos componentes e deixe a cor da marca só no logo e na barra da capa, para não confundir com criticidade.
- Confira o contraste de cada par texto/fundo (WCAG AA 4,5:1) e anote no README.
- Item sem fonte oficial vai marcado `[SUGESTÃO]` no README e no `tokens.json`.

## 5. Confira

1. `python3 SKILL_DIR/scripts/motor/build.py <pais> --forcar` com um `conteudo.json` mínimo (ou o exemplo) e abra a capa, um slide de vitrine e o topo do relatório no Chrome headless.
2. Mostre os 3 prints ao usuário antes de seguir. Ajuste o `marca.json` até ele aprovar.
3. Registre a aprovação no `auditoria-estado.md` (Decisões).
