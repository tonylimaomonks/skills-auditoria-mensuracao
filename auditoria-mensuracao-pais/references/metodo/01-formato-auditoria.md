# Formato da auditoria: relatório técnico + deck executivo (deep research)

> Cópia para a skill (29/10/2026) do original em `Smart-Fit/conhecimento/`. Nasceu na auditoria Smart Fit BR: exemplos, lei (LGPD/ANPD) e moeda são do BR. Para outro país ou cliente, pesquise a lei local e registre em `<cliente>/conhecimento/` antes de citar sanção.

> Criado em 13/10/2026 (deep research web). Faz parte de `00-indice-e-gaps.md`, lacuna 1.
> **Fora de escopo**, porque já está coberto em `../Flutter/DAT-92/.../comunicacao-negocio-deep-research.md`: Minto/SCQA/BLUF, títulos-asserção, confiança calibrada, Knaflic e anti-padrões de dashboard.
> A quantificação em R$ (fórmulas) fica em `02-quantificar-impacto-achados-mensuracao.md`. Aqui o assunto é **forma**: anatomia, rubrica, plano, sequência e HTML.

---

## TL;DR (o que muda em relação às entregas recusadas)

1. **Cada achado vira um "cartão"** no formato de pentest/auditoria interna, com ID estável, condição, critério, causa, efeito, evidência reproduzível, recomendação, owner e critério de reteste. O "Aprimorar 36%" some, e o que aparece no lugar é "SF-DUP-03: `purchase` dispara 2× no reload de `/checkout/resume` (tag 412 + trigger 87)".
2. **A criticidade é calculada por uma rubrica publicada**: Impacto (o maior entre os 3 pilares) × Probabilidade/Abrangência, com fatores 1 a 3 e override justificado por escrito. O cliente consegue refazer a conta.
3. **O plano de ação é um backlog verificável**. Cada linha tem um "critério de pronto" escrito como teste (query/request que precisa passar), com o mesmo método usado para provar o achado. É o conceito de *retest* de pentest.
4. **O deck é de steerco**: decisões pedidas no começo, "findings on a page", money slide, roadmap e decisões. Os critérios de aceite do cliente aparecem **espelhados literalmente**, com uma matriz "Pedido → onde está atendido".
5. **A rastreabilidade é a prova de seriedade**. O mesmo ID aparece no slide, no cartão do relatório e no arquivo bruto em `evidencias/`, sempre com carimbo de data de extração.

---

## 1. Como auditorias de tracking, segurança e auditoria interna estruturam achados

### 1.1 O que as referências fazem

| Fonte | Estrutura do achado | O que aproveitar |
|---|---|---|
| **Pentest (Bright Defense, Wiz, PTES)** | ID único, título, severidade, score com racional, ativo afetado e local exato, acesso necessário, **passos de reprodução**, evidência, **observado × esperado**, impacto técnico e **impacto de negócio**, remediação, referências, **owner, data-alvo, status de reteste** | Anatomia completa. Separar **severidade técnica** de **prioridade de negócio** e justificar quando divergirem. Status de reteste: *resolvido / parcialmente / ainda presente / risco aceito* |
| **PTES Reporting** | Dois blocos: *Executive Summary* (metas, postura, **roadmap estratégico**) e *Technical Report* (escopo, caminho, impacto, remediação) | Relatório técnico ≠ deck, e o deck termina em roadmap |
| **Auditoria interna IIA (5 C's / 5 atributos)** | **Condição** (o que é), **Critério** (o que deveria ser e "quem diz?"), **Causa** (raiz, sem repetir a condição), **Efeito/Consequência** (impacto de negócio), **Ação corretiva** (que ataca a *causa*) | O campo **Critério** é o que faltou nas entregas antigas: amarra o achado a uma regra citável (doc do Google, LGPD, limite 360, best practice) |
| **Analytics Debugger (GA4/GTM)** | Scorecard por categoria, contagem por severidade (Critical/Warning/Info), achado = título + severidade + efeito ("purchase sem transaction_id → receita duplicada"), screenshots, passo a passo e roadmap. "Não é um documento de 100 páginas na prateleira" | Exemplos de títulos que já trazem efeito. Para a Smart Fit, um scorecard em **% sozinho é proibido**, porque repete o erro "36%" |
| **ObservePoint** | Auditoria por *rules* (expectativa × resultado na página): presença de tag, duplicidade, valores de variáveis, dataLayer, tags fora do GTM, tempo de carga. Recorrente e pré-produção | Formular o critério de cada achado como **regra testável** ("em `/checkout/resume`, `purchase` = 1 request, `transaction_id` ≠ vazio"). Essa regra vira o critério de pronto |
| **Trackingplan / Avo** | Monitoramento contínuo mais deep dive trimestral. Detecta propriedade obrigatória que some, muda de tipo ou recebe placeholder | Recomendação de governança: transformar as regras da auditoria em monitor contínuo (fase "Later") |
| **Checklists GA4 (Piotr Litwa, Inflow, Measuremind)** | Áreas: property settings, streams, eventos, key events, custom definitions, audiências, atribuição, Consent Mode v2, retenção, paridade com o BigQuery. No GTM: higiene, tags, triggers, dataLayer, consent, versionamento, performance, nomenclatura | **Grade de cobertura**: mostrar quais áreas foram checadas, inclusive as "OK", para provar 100% de cobertura |

### 1.2 Anatomia recomendada do "cartão de achado" (Smart Fit)

Ela funde pentest, IIA 5C e o modelo do relatório Loja do Mecânico (dado → causa → solução → efeito):

```
┌ SF-DUP-03 · purchase duplicado no reload da página de confirmação ──────────┐
│ [ALTA] Pilar: Duplicidade & Integridade (+ Financeiro)  Status: Aberto       │
│ Ativo: GTM-TCXTCQ5 v<n> · tag #412 "GA4 - purchase" · trigger #87 · G-BJP…   │
│ Confiança: Alta (reproduzido 3/3)   Extraído: 2026-10-14 10:32 BRT           │
├──────────────────────────────────────────────────────────────────────────────┤
│ CONDIÇÃO   (o que vimos, com número)                                         │
│ CRITÉRIO   (o que deveria ser + fonte citável)                               │
│ CAUSA      (raiz técnica: config de tag/trigger/dataLayer)                   │
│ EFEITO     (negócio: R$, conversões, cota 360, decisão de mídia, LGPD)       │
│ EVIDÊNCIA  [E-031 request] [E-032 query API + resultado] [E-033 print]       │
│ REPRODUZIR 1.… 2.… 3.… (qualquer pessoa do cliente refaz)                    │
│ RECOMENDAÇÃO  opção A (correção de raiz) · opção B (contorno/compensação)    │
│ PRONTO QUANDO  teste verificável idêntico ao da evidência → resultado alvo   │
│ Owner (A): … · Esforço: P · Prazo: Now · Depende de: SF-GOV-01               │
│ ▸ Detalhes técnicos (payload completo, JSON da tag) [colapsável]             │
└──────────────────────────────────────────────────────────────────────────────┘
```

Regras do cartão:
- **O título é uma asserção com efeito** e nunca um rótulo: "purchase duplicado infla receita no GA4 e no Ads", e não "Duplicidade de eventos".
- **Observado × esperado** fica lado a lado, numa tabela de 2 colunas ou num diff.
- **Critério com fonte**: link da doc do Google (ex.: deduplicação por `transaction_id`, que só vale para web stream e para o mesmo usuário, e onde `transaction_id=""` deduplica *tudo*), da LGPD, do limite 360 etc.
- **A recomendação ataca a causa** (regra IIA). Sempre que houver, dar duas opções: correção de raiz e contorno (Wiz).
- **Override de severidade explícito**: "Técnica = Média; prioridade = Alta porque afeta o lance do Smart Bidding" (Bright Defense).
- O **ID é estável** entre versões. Achado fechado não reaproveita ID.

Prefixos de ID sugeridos por pilar e tema: `SF-FIN-xx` (licença/cota/sGTM), `SF-DUP-xx` (duplicidade/integridade), `SF-PII-xx` (privacidade/LGPD; vai em Integridade ou Governança conforme a rubrica), `SF-PERF-xx`, `SF-GOV-xx` (acessos, nomenclatura, versões, tokens). Evidências: `E-nnn`. Ações: `A-nnn`, ligadas a 1..n achados.

---

## 2. Criticidade: métodos e rubrica transparente

### 2.1 Métodos de referência

- **OWASP Risk Rating**: Probabilidade (agente + vulnerabilidade) e Impacto (técnico + **negócio: dano financeiro, reputação, não conformidade, privacidade**), fatores de 0 a 9 e médias. 0–<3 Baixo, 3–<6 Médio, 6–9 Alto. A matriz 3×3 resulta em Note/Low/Medium/High/Critical. A OWASP manda **customizar os fatores e pesos** e **preferir o impacto de negócio ao técnico** quando houver informação confiável.
- **CVSS v4.0**: grupos Base / Threat / Environmental / **Supplemental**. O Supplemental não altera o score, mas informa, por exemplo, *Recovery*, *Value Density* e *Response Effort*. A ideia que vale adaptar é separar a **severidade intrínseca** do **contexto do ambiente** e anexar metadados que não mudam a nota (como esforço).
- **Severidade × prioridade (Rootly, GitLab Data)**: severidade é o impacto, prioridade é a urgência. O GitLab classifica incidentes de dados por **disrupção de negócio, criticidade do dado e dependências downstream** e, na dúvida, sobe para o nível maior. A FireHydrant alerta que, sem definições claras, "tudo vira SEV1".
- **Dimensões de qualidade de dados (DAMA/UK Gov)**: acurácia, completude, consistência, atualidade, **unicidade** e validade. Servem como vocabulário para o pilar Integridade (duplicidade = unicidade; `transaction_id` ausente = completude; `value` errado = acurácia).
- **Impacto × Esforço 2×2**: Quick Wins / Major Projects / Fill-ins / Thankless. Atribuir nota em silêncio para evitar ancoragem. É para **priorizar ações**, não para classificar achados.
- **RICE (Intercom)**: (Reach × Impact × Confidence) ÷ Effort, com Confidence discreta (100/80/50%). Útil para ordenar o backlog "Next/Later". Reach = % de transações/sessões afetadas.
- **Críticas a heatmaps (Cox, "What's wrong with risk matrices")**: matrizes comparam mal pares de riscos e podem dar nota maior a riscos menores. A mitigação é usar a matriz **com explicação dos julgamentos embutidos** e acompanhar com **R$ quando der**. Por isso a rubrica abaixo publica os fatores e cada cartão mostra a conta.

### 2.2 Rubrica proposta (3 pilares do PEDIDO)

**Passo 1. Impacto (I) por pilar, 1 a 3.** O impacto do achado é o **maior** dos três pilares (não a média), e o pilar dominante vira o "pilar" do cartão.

| Nível | Financeiro / Licenciamento | Duplicidade & Integridade | Performance & Governança |
|---|---|---|---|
| **3 Alto** | Gasto evitável relevante em cota GA 360 ou infra sGTM (ex.: eventos não usados > X% do volume faturável; chamadas SS redundantes em todo o tráfego) **ou** sinal errado alimentando lance de mídia (conversão inflada/perdida no Ads/Meta) | Receita/conversões no GA4 ou nas mídias com distorção ≥ 5% **ou** evento de funil (purchase/begin_checkout) ausente ou duplicado **ou** PII (e-mail, CPF, telefone, nome) enviada a terceiros | Token/segredo em texto aberto; acesso de admin indevido (ex-colaborador/agência); impacto em CWV acima do limite "bom" em página de checkout; publicação sem controle |
| **2 Médio** | Custo evitável moderado ou localizado (1 stream/subpropriedade) | Distorção de 1–5% ou em parâmetro secundário (`items` incompleto, `currency` ausente); dimensão de atribuição corrompida | Tags órfãs/pausadas em volume que pesa no container (> 70% do limite de ~200 KB); nomenclatura que impede manutenção; CWV "precisa melhorar" |
| **1 Baixo** | Sem custo mensurável | < 1% ou só em relatório não decisório | Higiene: variável não usada, pasta, descrição |

**Passo 2. Probabilidade/Abrangência (P), 1 a 3.**
- 3 = ocorre em toda execução ou em todo o tráfego do fluxo afetado (determinístico, reproduzido 3/3), ou já está ocorrendo nos dados da API.
- 2 = ocorre sob condição comum (reload, voltar do navegador, app × web, um navegador).
- 1 = raro ou depende de condição improvável.

**Passo 3. Matriz (inspirada na OWASP, 3×3 → 3 níveis do cliente).**

| I \ P | 1 | 2 | 3 |
|---|---|---|---|
| **3** | Média | **Alta** | **Alta** |
| **2** | Baixa | Média | **Alta** |
| **1** | Baixa | Baixa | Média |

**Passo 4. Modificadores explícitos (só para cima, sempre justificados no cartão).**
- **+1 nível** se houver **risco legal/LGPD** (PII a terceiros) ou **exposição de credencial**, independentemente de P. É o "piso Alta".
- **+1 nível** se o dado alimenta **automação de lance** (key event importado no Google Ads/Meta CAPI).
- Nunca rebaixar sem registrar "risco aceito por <nome>, <data>".

**Passo 5. Confiança (metadado e não nota)**: Alta = reproduzido + dado da API; Média = só um dos dois; Baixa = inferido da configuração. Achado de confiança Baixa entra como "a validar" e não vai para a matriz executiva.

**Saída de cada cartão**: `I=3 (Integridade) · P=2 (reload) · Mod: +Ads → ALTA · Conf: Alta`. A seção "Metodologia" do relatório publica a tabela acima uma vez só.

> Por que não CVSS puro ou score 0–10: o cliente pediu Alta/Média/Baixa por pilar. Um decimal parece precisão falsa (o mesmo problema do "36%"). A rubrica de 3 níveis com fatores visíveis é auditável e cabe num slide.

---

## 3. Plano de ação

### 3.1 Princípios

- **Horizontes em vez de datas (Now / Next / Later, Janna Bastow/ProdPad)**: datas fixas viram promessa quebrada. Os horizontes expressam confiança. Para cliente corporativo, mapear para **30/60/90 dias**: Now ≈ 0–30, Next ≈ 30–60, Later ≈ 60–90+.
- **RACI com um único A por ação** ("golden rule"). R pode ser plural, mas pequeno, e o C deve ser enxuto porque cada consultado atrasa. Owners prováveis: Smart Fit Mídia/Martech (A), dev do site/checkout (R), Monks (R para configuração GTM/GA4 se autorizado; hoje é **só leitura**), Jurídico/DPO (C para PII).
- **Definition of Done × Acceptance Criteria (Atlassian)**: o DoD é global (vale para toda ação) e o critério de aceite é específico por ação. Ambos precisam passar.
- **Reteste de pentest**: o achado só fecha quando o reteste confirma que a **causa raiz** foi corrigida, e não apenas que o sintoma sumiu. O reteste registra data, método, evidência e resultado.
- **Status consistentes**: Aberto → Em correção → Aguardando reteste → Resolvido / Parcial / Ainda presente / Risco aceito.

### 3.2 DoD global (vale para todas as ações)

1. Mudança publicada em versão nomeada do GTM (nome e descrição com o ID da ação, ex.: `A-007 / SF-DUP-03`).
2. Testada em Preview/DebugView **e** em produção com o mesmo roteiro de reprodução do achado.
3. Evidência de reteste salva em `evidencias/reteste/<ID>/<data>/`.
4. Nenhuma regressão nas regras-sentinela do funil (contagem por etapa, `purchase` = 1 por transação, ausência de PII em `page_location`).

### 3.3 Template da linha do plano

| Ação | Achados | Pilar / Crit. | O que fazer (raiz) | R | A | Esforço | Horizonte | Depende de | **Critério de pronto (teste verificável)** | Método de validação |
|---|---|---|---|---|---|---|---|---|---|---|
| A-007 | SF-DUP-03 | Integridade / Alta | Trigger de `purchase` passa a disparar uma vez por `transaction_id` (cookie/sessionStorage ou dedupe no sGTM) | Dev site | Martech SF | P | Now | — | Reload de `/checkout/resume` 3× → **1** request `collect?en=purchase`; Data API, 7 dias após o deploy: `countDistinct(transactionId) = count(purchase)` (± 0,5%) | Chrome DevTools (filtro `collect?`) + query `E-032` reexecutada |
| A-012 | SF-PII-01 | Integridade / Alta (+LGPD) | Remover `id` base64 de `page_location` (redaction de query param no stream + limpeza no GTM) | Martech SF | DPO SF | P | Now | Aprovação jurídica | 0 ocorrências de `id=` em `pageLocation` (Data API, 7 dias); request de `/checkout/person` sem o parâmetro | Data API + request |

- **Esforço em T-shirt**: P (< 1 dia de config), M (1–5 dias ou depende de dev), G (> 1 sprint, migração/arquitetura). Mostrar a premissa ("considera 1 dev front com acesso ao GTM").
- **Priorização dentro do horizonte**: primeiro a criticidade, depois Impacto × Esforço (Quick Wins primeiro) e, para desempatar o backlog Next/Later, o RICE.
- **Dependências** viram coluna e também um mini-diagrama no deck, se houver cadeia (ex.: limpar acessos → rotacionar tokens → mover tokens para variável secreta).

---

## 4. Deck executivo de auditoria (steerco)

### 4.1 Princípios

- O deck existe para **gerar decisão**: dizer quais decisões são necessárias, as implicações e o próximo passo (SlideModel). Limitar a **2–4 decisões**.
- O detalhe vai para o **apêndice** e para o relatório técnico. O corpo fica em cerca de 12 slides.
- A ordem recorrente em audit committee packs é: sumário → tabela de achados (ID, área, rating, impacto em R$) → heatmap → causas raiz → status/plano → decisões.
- O **executive summary vem primeiro, mas é escrito por último** (eSecurityPlanet/PTES). Ele é não técnico e não leva payload.

### 4.2 Recuperar confiança depois de 3 recusas

- **Ouvir antes de corrigir**: abrir com o que o cliente disse, nas palavras dele ("granularidade", "evidências", "só contas ativas com dados", "ligar técnico ao negócio"). Usar como fonte a `REUNIÃO-ALINHAMENTO-09-10.md`.
- **Prova em vez de promessa**: depois de uma quebra de confiança, promessa vale menos e entrega demonstrada vale mais. Mostrar **1 achado completo** cedo (slide 4 ou 5), em vez de prometer o método.
- **Escopo combinado por escrito**: no slide 2, "O que combinamos em 09/10": só a conta principal → validar o formato → escalar. Fechar com uma decisão explícita: "o formato está aprovado para escalar?".
- **Matriz de rastreabilidade Pedido → Entrega (RTM)**: colunas mínimas `ID do pedido | Texto literal do PEDIDO.md | Onde está atendido (slide/seção/ID) | Método de verificação | Status (Atendido/Parcial/Fase 2)`. Mantê-la enxuta: 4 a 6 colunas mantidas valem mais que 10 abandonadas. Ela vai no deck (slide 3, resumida) e no relatório (completa).
- **Cobertura e método visíveis**: "1 container web + 1 sGTM + 1 propriedade 360 + 4 subpropriedades; N tags lidas via API em DD/MM; funil de 9 passos percorrido 3×". Mostrar inclusive o que está **OK**, para provar cobertura total e não só uma lista de problemas.
- **Diferenciação explícita da versão anterior** (sem expor o time): "Antes: % de itens a aprimorar. Agora: cada achado com evidência reproduzível, R$ e critério de pronto".

### 4.3 Slides-chave

- **Findings on a page**: grade com as linhas = achados (ID + título curto) e as colunas = 3 pilares, com a célula do pilar dominante colorida pelo nível **e com texto** (ALTA/MÉDIA/BAIXA, nunca só cor). Alternativa: matriz 3×3 I×P com os IDs plotados. Cada ID é um link para o cartão no relatório.
- **Money slide**: um único número ou uma ponte (waterfall) "receita/conversões reportadas → reais" ou "eventos faturáveis 360 → necessários", com a faixa de confiança. A fórmula fica em `02-quantificar…`.
- **Roadmap**: 3 colunas Now/Next/Later (30/60/90), cartões com ID da ação, owner e critério de pronto resumido.
- **Decisões/pedidos**: 2–4 itens no formato "Decidir X até DD/MM, porque Y; se não, Z".

---

## 5. Evidência no HTML

### 5.1 Princípios

- **Evidência mínima suficiente**: incluir só o necessário para provar e corrigir (Bright Defense). O resto fica no arquivo bruto, referenciado por ID.
- **Redação de segredos e PII**: mascarar tokens, cookies, `Authorization`, e-mail, CPF, telefone, nome e o valor do `id` base64. Ferramentas automáticas de sanitização de HAR (Google HAR Analyzer, Cloudflare HAR sanitizer, `har-capture`) **erram em corpo de request**, então é preciso conferir por busca textual ("Bearer", "token", "@", padrão de CPF) antes de publicar (Okta/Auth0). Regra do projeto: tokens Meta/TikTok aparecem só como "token em texto aberto na tag X".
  - Padrão visual: `access_token=EAAG••••••••[redigido, 212 chars]`, `cpf=***.***.***-**`, `em=t***@t***.com`. Mostrar o **formato** e o **comprimento** prova que o valor existe sem expô-lo.
- **Duas versões quando necessário**: o relatório completo com acesso restrito (Martech + Jurídico) e o deck sem payload bruto, só com o fato (como o *attestation letter* do pentest).
- **Carimbo de frescor** em todo número: `Fonte: GA4 Data API · property 175020184 · 2026-07-15→2026-10-13 · extraído 2026-10-14 10:32 BRT · E-032`. No deck vai no rodapé do slide; no relatório, no cabeçalho de cada evidência.
- **A query aparece junto com o resultado**: mostrar a chamada (`runReport` com dimensões, métricas e filtro em JSON resumido) e a tabela de resultado. Assim o cliente consegue reexecutar.

### 5.2 Blocos de evidência (componentes)

| Tipo | Componente HTML | Conteúdo |
|---|---|---|
| Request de rede | `<figure class="ev ev-request">` com `<pre>` e destaque (`<mark>`) dos parâmetros relevantes | URL decodificada em linhas `chave = valor`, com os parâmetros-chave destacados (`en`, `tid`, `ep.transaction_id`, `epn.value`, `dl`) e o resto colapsado |
| Payload / dataLayer | `<pre><code>` JSON com destaque | Diff observado × esperado (`<del>`/`<ins>`) |
| Config GTM | Tabela da tag/trigger: ID, nome, tipo, triggers, exceções, versão live | Link para o JSON bruto `evidencias/gtm/GTM-TCXTCQ5/<data>/tags.json#412` |
| Query de API | `<details>` com o request JSON, mais a tabela do resultado sempre visível | Período, filtro e carimbo |
| Print | `<figure>` com `<img loading="lazy">` (base64 embutido para manter o arquivo único) e `<figcaption>` com ID, URL, data e o que observar; áreas redigidas com tarja preta e etiqueta "redigido" | Recortar só a área relevante |

### 5.3 Rastreabilidade deck ↔ relatório ↔ evidência

- Uma convenção para tudo: `SF-<PILAR>-<nn>` (achado), `E-<nnn>` (evidência), `A-<nnn>` (ação), `P-<nn>` (item do PEDIDO).
- Arquivo `evidencias/INDEX.csv` (ou JSON) com as colunas `E-id, achado, tipo, caminho do arquivo, fonte, período, extraído_em, sha256`. O hash prova que o arquivo não mudou depois da extração.
- No HTML, toda menção a um ID é âncora (`#SF-DUP-03`). No deck, o rodapé do slide lista os IDs citados ("Evidência: SF-DUP-03 · E-031/032").

---

## 6. Implementação HTML

### 6.1 Relatório técnico longo

- **Arquivo único e autocontido**: CSS/JS inline, imagens em base64 e sem CDN, para abrir offline e permitir envio por e-mail. Gráficos em SVG inline ou Chart.js embutido.
- **TOC sticky**: `<nav aria-label="Sumário">` com `position: sticky; top: 0; align-self: flex-start` (o elemento sticky tem de ser mais curto que o container) e scrollspy com **IntersectionObserver** (sem listener de scroll), marcando o link ativo com `aria-current="true"`.
- **Filtros por criticidade e pilar**: chips `<button aria-pressed>` que aplicam `hidden` aos cartões. Uma região `aria-live="polite"` anuncia "12 achados exibidos", com debounce de cerca de 300 ms. O estado do filtro fica refletido na URL (`?crit=alta&pilar=fin`) para que um link compartilhado preserve a visão.
- **Colapsáveis**: `<details><summary>` nativo para "Detalhes técnicos", payloads e JSON. Se houver botão customizado, seguir o padrão *Disclosure* da APG (role button, Enter/Space, `aria-expanded`, `aria-controls` opcional). Botões "Expandir tudo / Recolher tudo" ajudam a revisão.
- **Tabelas**: usar `<table>` nativa (a APG recomenda nativo; grid só se for interativo), com `<caption>` e `<th scope>`. Ordenação simples via `aria-sort`, se houver.
- **Cor**: a criticidade nunca é só cor (WCAG 1.4.1). Badge com texto e ícone: "▲ ALTA", "■ MÉDIA", "▼ BAIXA". Contraste ≥ 4.5:1 para texto e ≥ 3:1 para elementos gráficos (1.4.11). Foco visível. `prefers-reduced-motion` para desligar animações.
- **Print CSS**: `@media print { nav, .filters { display:none } details { display:block } details > *:not(summary) { display:block } .card { break-inside: avoid } a[href^="#"]::after { content: " (" attr(href) ")" } }`. Antes de imprimir, abrir todos os `<details>` via `beforeprint`. Cabeçalho e rodapé com versão e data.
- **Metadados no topo**: versão do relatório (v1.0, data), escopo, período dos dados, autores e **classificação de confidencialidade** (contém evidências sensíveis).

### 6.2 Deck 16:9

O motor do DAT-75 já é reaproveitável (ver `00-indice-e-gaps.md`). Checklist:
- **Canvas fixo de 1920×1080** dentro de um viewport, com `transform-origin: 0 0` e `scale = min(innerWidth/1920, innerHeight/1080)` mais translate para letterbox, recalculado no `resize`.
- **Alternar slides por classe** (visibility/opacity/pointer-events) em vez de `display:none`, porque o `display:flex` dos filhos sobrescreve.
- **Teclado**: ←/→, Espaço, PageUp/PageDown, Home/End. **Hash** `#/7` para linkar um slide. Contador "7 / 14" e barra de progresso.
- **Notas do apresentador**: `<aside class="notes">` oculto. A tecla `S` abre `window.open` com as notas, o próximo slide e o timer, sincronizados via `BroadcastChannel` (padrão do speaker view do reveal.js).
- **Print/PDF**: `@page { size: 1920px 1080px; margin: 0 }`, `.slide { break-after: page; break-inside: avoid; transform: none }`, `-webkit-print-color-adjust: exact; print-color-adjust: exact`, todos os slides visíveis no print e 1 slide por página. Testar no Chrome (o reveal.js só garante Chrome/Chromium): margens "Nenhuma" e "Gráficos de segundo plano" ligado. O diálogo de impressão pode sobrescrever o `@page`, então documentar essas configurações no rodapé do slide de capa ou num README.
- **Opção de notas impressas** em página separada após cada slide (como o `showNotes: "separate-page"` do reveal.js), útil para o cliente que vai repassar o deck.
- **Acessibilidade**: cada slide como `<section role="group" aria-roledescription="slide" aria-label="7 de 14: <título>">`, título real em `<h2>`, `alt` em gráficos e texto da conclusão no próprio título (asserção).
- **Arquivo único** sem fonte de terceiros (stack de fontes do sistema ou fonte embutida em base64).

---

## 7. Esqueleto recomendado do RELATÓRIO TÉCNICO (`entregas/relatorio-tecnico-smartfit-br.html`)

0. **Capa / metadados**: versão, data, período dos dados, escopo (conta principal BR), autores, confidencialidade.
1. **Sumário executivo (1 tela)**: 3–5 achados mais críticos com R$/efeito, contagem por criticidade × pilar e as 3 ações Now.
2. **O que foi pedido e onde está atendido (RTM)**: tabela P-01..P-nn com o texto literal do `PEDIDO.md` e da reunião de 09/10 → seção/ID → status.
3. **Escopo, cobertura e método**: ativos (GTM-TCXTCQ5, sGTM GTM-5J2HW2RB, GA4 175020184 + subpropriedades), fontes (Tag Manager API v2, Admin/Data API, Chrome DevTools no funil de 9 passos), datas de extração, limitações (somente leitura, quota, analyticsadmin pendente), o que ficou fora (fase 2).
4. **Metodologia de criticidade**: a rubrica da seção 2.2 publicada (I × P, modificadores, confiança).
5. **Inventário (com dados)**: containers, contagem de tags/triggers/variáveis por tipo e status (ativa/pausada/órfã), templates e clients do sGTM, propriedades/streams/subpropriedades, retenção, links (Ads/BQ/Firebase), key events, custom definitions vs. limite 360, acessos. A grade de cobertura mostra os itens OK.
6. **Matriz de Criticidade**: heatmap achados × pilares mais a matriz I×P com IDs clicáveis.
7. **Achados detalhados**, um cartão por achado e agrupados por pilar:
   - 7.1 Financeiro/Licenciamento (cota 360, eventos faturáveis desnecessários, subpropriedades, chamadas SS redundantes, custo de logs/infra do sGTM).
   - 7.2 Duplicidade & Integridade (funil view_item → purchase, `transaction_id`/`value`/`items`, duplicidade de purchase, PII em URL/payload, consistência GA4 × mídias).
   - 7.3 Performance & Governança (peso do gtm.js/container vs. ~200 KB, CWV no checkout, scripts de terceiros e `ERR_NAME_NOT_RESOLVED`, tokens em texto aberto, acessos, nomenclatura, versionamento).
8. **Plano de ação**: backlog A-001..A-nnn (template 3.3), DoD global, RACI e roadmap Now/Next/Later (30/60/90).
9. **Reteste**: tabela de status por achado (preenchida nas rodadas seguintes).
10. **Apêndices**: índice de evidências (E-id → arquivo, período, hash), queries da API na íntegra, glossário (para leitor de negócio) e changelog do relatório.

## 8. Esqueleto recomendado do DECK EXECUTIVO (`entregas/apresentacao-executiva-smartfit-br.html`, cerca de 13 slides + apêndice)

| # | Função | Título-asserção (placeholder) |
|---|---|---|
| 1 | Capa | "Auditoria de mensuração Smart Fit BR: conta principal (dados de DD/MM a DD/MM)" |
| 2 | O que combinamos | "Combinamos começar pela conta principal, com evidência de cada achado e o impacto no negócio" (as palavras do cliente em 09/10) |
| 3 | Pedido → entrega | "Os N critérios do pedido estão atendidos nesta rodada; X ficam para a fase 2 por decisão de escopo" (RTM resumida) |
| 4 | BLUF / resposta | "Hoje a mensuração [infla/perde] ~R$ X em receita reportada e consome ~Y% da cota 360 sem uso; 3 correções resolvem Z%" |
| 5 | Decisões pedidas (prévia) | "Precisamos de 3 decisões até DD/MM para começar as correções 'Now'" |
| 6 | Cobertura e método | "Lemos 100% de 1 container web + 1 server + 1 propriedade 360 e percorremos o funil de compra 3×" (inclui o que está OK) |
| 7 | Findings on a page | "N achados: A em Alta, concentrados em Integridade do checkout" (heatmap × pilares) |
| 8 | Money slide | "Receita reportada × real: o `purchase` duplicado e incompleto distorce o número que guia o lance de mídia em X%" (waterfall) |
| 9 | Achado-vitrine 1 (Integridade) | "[Achado] → custa/distorce [R$/%] → corrigimos com [ação] em [prazo]" (prova o formato, com 1 evidência visual) |
| 10 | Achado-vitrine 2 (Financeiro) | "X% dos eventos faturáveis do 360 não são usados em nenhum relatório ou audiência" |
| 11 | Achado-vitrine 3 (Governança/LGPD) | "Dados pessoais do checkout chegam a [GA4/mídias] pela URL: exposição LGPD com correção em 1 dia" |
| 12 | Roadmap | "Em 30 dias eliminamos os achados Alta; em 90, a mensuração passa a ter monitor contínuo" (Now/Next/Later) |
| 13 | Como vamos provar | "Cada correção só fecha quando o mesmo teste que provou o problema passar" (critérios de pronto e reteste) |
| 14 | Decisões e próximos passos | "Decidir: (1) aprovar o formato para escalar às demais contas, (2) owners das ações Now, (3) acesso de edição/janela de deploy" |
| A1–An | Apêndice | Um slide por achado restante (ID, 3 perguntas: o que acontece / quanto custa / o que fazer), rubrica, glossário, índice de evidências |

Regras do deck: cada slide de achado responde às 3 perguntas do `CLAUDE.md`; o rodapé leva fonte, período, data de extração e IDs; nenhum payload bruto; criticidade com texto e não só cor; total de cerca de 14 slides no corpo.

---

## Fontes

**Formato de achado / relatórios de auditoria**
- Bright Defense, What is a Penetration Testing Report: https://www.brightdefense.com/resources/what-is-a-penetration-testing-report/
- Wiz, Penetration testing report: https://www.wiz.io/api/md/academy/vulnerability-management/penetration-testing-report
- PTES, Reporting: https://pentest-standard.readthedocs.io/en/latest/reporting.html
- eSecurityPlanet, How to write a pentest report: https://www.esecurityplanet.com/fr/networks/pentest-report/
- IIA, The Five Attributes Approach: https://internalauditor.theiia.org/en/articles/2023/february/the-five-attributes-approach/
- IIA, Your work isn't done yet (5 C's): https://internalauditor.theiia.org/en/voices/20192/your-work-isnt-done-yet/
- IIA, On the frontlines: rebuilding trust: https://internalauditor.theiia.org/en/voices/2024/september/on-the-frontlines-rebuilding-trust
- Analytics Debugger, Audits: https://www.analytics-debugger.com/en/services/audits
- ObservePoint, Web Analytics Audit / GTM Audit: https://www.observepoint.com/?p=428 · https://www.observepoint.com/?p=432
- Trackingplan, Server-side tracking audit checklist: https://www.trackingplan.com/blog/server-side-tracking-audit-checklist-metrics-tools-and-process · Conversion tracking audit: https://trackingplan.com/blog/conversion-tracking-audit-tool
- Avo, Tracking Plan Audit: https://www.avo.app/docs/audit/index
- Piotr Litwa, GA4 audit checklist: https://piotrlitwa.com/articles/en/ga4-audit-checklist.html · GTM audit: https://piotrlitwa.com/articles/md/en/gtm-audit.md
- Inflow, GA4 Audit Checklist (PDF): https://www.goinflow.com/wp-content/uploads/2025/01/Inflows-Google-Analytics-4-Audit-Checklist.pdf
- Measure Minds, How to run a GTM audit: https://measuremindsgroup.com/how-to-run-a-gtm-audit
- Seer Interactive, GTM container audit: https://www.seerinteractive.com/blog/gtm-container-audit-guide/
- Simo Ahava, governance / server-side: https://simoahava.com/tags/governance · https://www.simoahava.com/analytics/agency-transparency-control-unsolved-problems-server-side-tagging/

**Criticidade / priorização**
- OWASP Risk Rating Methodology: https://community.owasp.org/OWASP_Risk_Rating_Methodology
- CVSS v4.0 (FIRST): https://www.first.org/cvss/specification-document · resumo: https://www.hivepro.com/blogs/cvss-4-0-explained
- GitLab Data Team Incident Management: https://handbook.gitlab.com/handbook/enterprise-data/data-governance/incident-management
- FireHydrant, Incident severity and priority: https://firehydrant.io/blog/incident-severity-and-priority-101
- Rootly, Severity vs priority: https://docs.rootly.com/glossary/severity-vs-priority
- DAMA / UK Gov data quality dimensions: https://www.gov.uk/government/news/meet-the-data-quality-dimensions · https://atlan.com/data-quality-dimensions/
- Impact-Effort Matrix: https://untools.co/impact-effort-matrix/ · https://www.learnleansigma.com/guides/impact-effort-matrix/
- RICE (Intercom/ProductPlan): https://www.productplan.com/glossary/rice-scoring-model
- Cox, críticas a matrizes de risco (resumo): https://www.juliantalbot.com/post/yet-another-article-about-risk-matrices

**Plano de ação**
- ProdPad, Now-Next-Later roadmap: https://www.prodpad.com/glossary/now-next-later-roadmap/
- RACI (one accountable): https://www.moxo.com/blog/raci-matrix · https://www.range.co/blog/raci-responsibility-matrix
- Atlassian, Definition of Done: https://www.atlassian.com/blog/development/8-steps-to-a-definition-of-done-in-jira
- RTM: https://inflectra.com/Ideas/Topic/Requirements-Traceability-Matrix-Template.aspx · https://www.6sigma.us/six-sigma-in-focus/requirements-traceability-matrix-rtm/

**Deck / steerco / confiança**
- SlideModel, Steering committee presentations: https://slidemodel.com/steering-committee-presentations/
- Prezent, Steering committee presentation guide: https://www.prezent.ai/blog/steering-committee-presentation-guide
- Umbrex, Managing client expectations: https://umbrex.com/resources/the-consulting-career-guide/managing-client-expectations/
- Rebuilding trust: https://www.monde-economique.ch/?p=35399

**Critérios técnicos citáveis nos cartões**
- GA4, deduplicação por transaction_id: https://support.google.com/analytics/answer/12313109
- GA4, Data redaction (e-mail e query params, só web): https://support.google.com/analytics/answer/13544947
- GA4 360, limites (custom dims 125, key events 50, retenção 50 meses): https://support.google.com/analytics/answer/11202874 · https://support.google.com/analytics/answer/14240153
- GA4, subpropriedades (evento custa 1/2 do evento da origem; filtrados não cobram): https://support.google.com/analytics/answer/11526072
- GA 360, billing e uso (base de 25M eventos/mês, tiers; excluir `user_engagement` via Data API): https://support.google.com/marketingplatform/answer/9013858
- sGTM, infraestrutura e custos (≈ US$ 45–50/instância/mês, mín. 2, logs caros): https://developers.google.com/tag-platform/learn/sst-fundamentals/7-planning-infrastructure · https://developers.google.com/tag-platform/tag-manager/server-side/cloud-run-setup-guide
- Limite de container GTM (~200 KB, aviso em 70%): https://www.analyticsmania.com/post/google-tag-manager-limits/ · https://www.zionandzion.com/google-tag-manager-container-size-limit/
- Limiares CWV (LCP 2,5 s, INP 200 ms, CLS 0,1 no p75): https://web.dev/articles/defining-core-web-vitals-thresholds
- PII em GA (guias): https://docs.publishing.service.gov.uk/analytics/pii.html · https://www.goinflow.com/blog/remove-pii-from-google-analytics/

**Evidência / redação**
- Auth0, Sanitizing HAR: https://support.auth0.com/center/s/article/How-to-Remove-Secrets-from-a-har-File
- Swoop, redacted HAR via Google HAR Analyzer: https://support.swoopanalytics.com/hc/en-us/articles/4423563555085-generating-redacted-network-traces-har-files
- har-capture (PyPI): https://pypi.org/project/har-capture/0.11.0/

**HTML / slides / acessibilidade**
- reveal.js, PDF export (print-pdf, showNotes, Chrome only): https://revealjs.com/pdf-export
- Padrão de stage 1920×1080 com scale: https://www.ui-skills.com/skills/zarazhangrui/frontend-slides
- Print CSS (break-after, @page, print-color-adjust): https://azukiazusa.dev/en/blog/css-print-style · https://htmlcsstoimage.com/blog/optimize-html-for-pdf-printing
- WAI-ARIA APG, Disclosure: https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ · Table: https://w3.org/WAI/ARIA/apg/patterns/table
- MDN, aria-roledescription (slide): https://developer.mozilla.org/docs/Web/Accessibility/ARIA/Attributes/aria-roledescription
- TOC sticky + IntersectionObserver: https://garden.bradwoods.io/notes/javascript/web-api/intersection-observer/table-of-contents · https://developer.chrome.com/docs/css-ui/sticky-headers
- Cor não pode ser o único meio (WCAG 1.4.1 / 1.4.11): https://ubs.com/fx/en/web-publishing-guidelines/accessibility/checks-custom-made-html/using-color

> **Ressalvas de fonte**: vários itens (Analytics Debugger, Trackingplan, templates de steerco, a guidance de live region da TimelyCare) são de fornecedores ou de templates e entram como convenção prática, não como norma. O limite de 200 KB do GTM não é publicado oficialmente pelo Google. Não foi encontrado material específico de Analytics Mania, Optimize Smart ou MeasureSchool sobre o *formato* de relatório de auditoria. Preços do 360 e do Cloud Run devem ser confirmados no contrato e no Pricing Calculator.
