# Quantificar o impacto de negócio dos achados de mensuração (deep research)

> Cópia para a skill (29/10/2026) do original em `Smart-Fit/conhecimento/`. Nasceu na auditoria Smart Fit BR: exemplos, lei (LGPD/ANPD) e moeda são do BR. Para outro país ou cliente, pesquise a lei local e registre em `<cliente>/conhecimento/` antes de citar sanção.

> Criado em 13/10/2026 (deep research web). Faz parte de `00-indice-e-gaps.md`. O formato e a anatomia dos cartões ficam em `01-formato-auditoria-tecnica-e-executiva.md`. Esta nota é só sobre **como transformar cada achado em R$, %, risco ou cota**, com fórmula e fonte.
> **Regra de uso:** os números da Smart Fit que aparecem nos exemplos (75% de purchase falso, 23% de duplicidade no app, R$ 808 mil/30d, 43 mi de `click`/7d, 38 tags Ads) vieram das rodadas de achados. **Revalidar no `evidencias/` antes de levar ao cliente.** Os exemplos numéricos aqui são **ilustrativos** e mostram a mecânica da conta.
> **Legenda de confiança da fonte:** **Alta** = documentação oficial (Google, Meta, WebKit), lei ou norma (Planalto, DOU). **Média** = parceiro oficial/revendedor, estudo publicado com método (Deloitte, web.dev case study, HTTP Archive). **Baixa** = blog de fornecedor, número sem método, figura repetida sem fonte primária.

---

## TL;DR: as 8 conclusões reutilizáveis

1. **Inflação de conversão é um viés multiplicativo**: ROAS e CPA do painel ficam errados pelo fator `(1 + i)`, sendo `i` = valor ou contagem espúria ÷ valor ou contagem real. Com tROAS, o algoritmo "acerta" o alvo no painel e entrega um ROAS real de `alvo ÷ (1 + i)`. Fonte de mecanismo: Google (tROAS prevê valor por leilão), Alta.
2. **O GA4 só deduplica `transaction_id` na web**, e **não no app** (Alta). `purchase` **sem** `transaction_id` não é deduplicado. Com `transaction_id=""`, ele deduplica **tudo** junto. A duplicidade no app (Firebase) chega inflada a qualquer destino que leia o GA4.
3. **Google Ads deduplica só dentro da mesma conversion action** (Alta). A Meta deduplica pixel × CAPI só com o par `event_id` + `event_name` dentro de 48 h, e **não deduplica** dois eventos da mesma fonte (Alta).
4. **O custo do GA4 360 é por evento faturável, em faixas regressivas**. A base inclui 25 mi de eventos/mês (Alta). A única tabela pública com preços (revendedor Merkle UK, G-Cloud 14, 2024) cobra £12,15/mi na faixa 25 mi–500 mi e £2,88/mi na faixa 500 mi–2,5 bi (Média). Evento de subpropriedade conta como +0,5 (parceiros, Média; confirmar no contrato).
5. **sGTM no Cloud Run custa cerca de US$ 45–50 por instância/mês** (1 vCPU, 0,5 GB, CPU sempre alocada). O Google recomenda mínimo de 2 instâncias (guia de setup) ou 3 (overview) (Alta). No modelo instance-based **não existe tarifa por request**: requisição redundante custa capacidade (instâncias) e egress.
6. **LGPD**: multa de até 2% do faturamento Brasil, limitada a **R$ 50 mi por infração** (art. 52, II, Alta). Com faturamento acima de R$ 2,5 bi, o teto de R$ 50 mi é o que vale. A ANPD diz textualmente que "continuar navegando" **não é consentimento** (Guia de cookies, out/2022, p. 18-19, Alta). Até 2024 só uma empresa privada tinha sido multada (Telekall, R$ 14,4 mil). O risco é real, mas o histórico de enforcement é baixo, e isso precisa ser dito.
7. **Performance**: Deloitte mostra +8,4% de conversão no varejo para cada 0,1 s de ganho mobile (Média). A Vodafone, num A/B, teve −31% de LCP e +8% de vendas (Média-Alta). A QuintoAndar (Brasil) teve INP −80% e +36% de conversões, **removendo pixels de terceiros** junto com outras otimizações (Média). O web.dev afirma que existe correlação entre tamanho do container e INP pior, e informa a mediana de container ≈ 50 KB (Alta).
8. **Token em texto aberto** é credencial vazada (CWE-798/CWE-312). Para a Meta, quem tem o token consegue enviar eventos ao dataset ("event poisoning"). **Não encontrei incidente público documentado** de abuso de token CAPI. O impacto precisa ser apresentado como cenário de risco e não como fato.

---

## 1. Conversões infladas, duplicadas ou falsas → Smart Bidding (Google) e otimização da Meta

### 1.1 Princípio

Os lances automáticos aprendem com o que a mensuração diz que aconteceu. O Target ROAS do Google "prevê o valor de uma conversão potencial a cada busca" e "dá lance alto se espera conversão de alto valor, baixo se não espera" ([About Target ROAS bidding](https://support.google.com/google-ads/answer/6268637)). O tCPA e o Maximizar conversões otimizam pela **contagem**. Se a contagem ou o valor reportado incluem conversões que não existiram, o algoritmo (a) acha que cada clique vale mais do que vale e passa a dar lances mais altos e gastar mais para "bater" o alvo, e (b) quando a inflação **não é uniforme** (só no app, só num tipo de página, só numa campanha), desloca orçamento para os segmentos inflados, o que gera **má alocação**. O próprio Google lista "tag de conversão mal posicionada que gera contagem imprecisa" entre os casos que pedem **data exclusion**, e avisa que, depois de corrigido, "a performance pode oscilar por 1–2 ciclos de conversão" e que é recomendável reajustar as metas de CPA/ROAS ([Use data exclusions for conversion data outages](https://support.google.com/google-ads/answer/10276486)). Na Meta vale a mesma lógica para eventos de otimização: a fase de aprendizado precisa de ~50 eventos de otimização em 7 dias por conjunto de anúncios (Meta Business Help, citado por terceiros, Média). Eventos falsos ajudam a "sair do aprendizado" com sinal ruim.

**Regras de deduplicação (o que está protegido e o que não está):**

| Plataforma | Como deduplica | O que **não** cobre | Fonte |
|---|---|---|---|
| GA4 | `transaction_id` igual, **mesmo usuário** | **App streams** ("only works for data collected through web streams, not app streams"). `purchase` sem ID. Com `transaction_id=""`, deduplica *todos* juntos (subcontagem) | [GA4 Measure ecommerce](https://support.google.com/analytics/answer/12313109) (Alta) |
| Google Ads | `transaction_id` igual **na mesma conversion action** ("the duplicate conversion won't be counted") | Conversões view-through, **duas conversion actions diferentes** para a mesma compra (ex.: tag Ads + import GA4 contando como primária), ID reutilizado (subcontagem) | [Use a transaction ID to minimize duplicate conversions](https://support.google.com/google-ads/answer/6386790) (Alta) |
| Meta (Pixel × CAPI) | `eventID` (pixel) = `event_id` (servidor) **e** `event` = `event_name`, até **48 h** | Dois eventos da **mesma fonte** ("If you send us two consecutive browser events with the same information, we do not discard either") | [Handling Duplicate Pixel and CAPI Events](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events) (Alta) |

**Correção retroativa disponível no Google Ads:** *conversion adjustments*. Uma **retração** zera valor e contagem e afeta CPA e ROAS. Uma **reformulação** muda só o valor e afeta ROAS. As duas usam o order ID ([About conversion adjustments](https://support.google.com/google-ads/answer/7686447), Alta). Sem `transaction_id`, **não dá para retrair** a duplicata, e isso é parte do impacto.

### 1.2 Fórmulas / heurísticas

Definições: `V_real` = receita real (backend/ERP), `V_esp` = valor espúrio (duplicado ou falso), `N_real` e `N_esp` = contagens.

- **Fator de inflação de valor:** `i_v = V_esp / V_real`. O ROAS do painel é `ROAS_painel = ROAS_real × (1 + i_v)`.
- **ROAS real sob tROAS:** se a campanha bate o alvo no painel, `ROAS_real ≈ tROAS ÷ (1 + i_v)`. Exemplo: com tROAS de 500% e i_v = 30%, o ROAS real é ≈ 385%.
- **CPA real sob tCPA / Max conversions:** `i_n = N_esp / N_real`, `CPA_real = CPA_painel × (1 + i_n)`.
  - Exemplo com o achado dos 75% de `purchase` falso na web (só vale **se** esse evento for conversão primária no Ads ou na Meta): `N_esp/N_total = 0,75` ⇒ `i_n = 0,75/0,25 = 3` ⇒ `CPA_real = 4 × CPA_painel`. O ticket médio real é `4 × ticket médio do painel`, porque os falsos têm R$ 0 e diluem a média.
- **Gasto sob suspeita (para o slide):** `Gasto_exposto = Σ gasto das campanhas cujo objetivo/lance usa a conversão afetada` (puxar da API do Ads/Meta). Não afirmar "R$ X desperdiçado". Afirmar "R$ X de investimento otimizado contra um sinal com Y% de ruído".
- **Má alocação (inflação não uniforme):** `Δshare_i = share_painel_i − share_real_i`, sendo `share = V_canal / ΣV`. Se o app tem 23% de transações duplicadas e a web não tem, o app aparece com `(1 + i_app)` vezes mais retorno relativo do que tem de fato. A ordem de grandeza da distorção na decisão de mix é `i_app − i_web`.
- **Para duplicidade no app (exemplo):** se o GA4/Firebase mostra R$ 808 mil de receita duplicada em 30 dias, então `i_v(app) = 808k / (Receita_app_painel − 808k)`. **Preencher com o valor do painel; não arredondar para "X%" sem a base.**
- **Retrabalho / reaprendizado:** depois da correção, Google indica **1–2 ciclos de conversão** de oscilação. O ciclo = tempo de atraso entre clique e conversão (relatório *Days to conversion*). Isso entra no slide como "custo de transição" e não como prejuízo.

### 1.3 Templates PT-BR (prontos)

- "Hoje **{i_n}%** das compras que o Google Ads/Meta usa para otimizar **não existem** (`purchase` com R$ 0 e sem `transaction_id`). Com isso, o algoritmo enxerga um custo por matrícula **{1+i_n}× menor** do que o real e aplica esse viés a **R$ {gasto_exposto}/mês** de mídia."
- "No app, **{dup}%** das transações são contadas duas vezes, o que soma **R$ {V_esp} de receita inexistente em 30 dias**. Uma campanha com meta de ROAS {alvo}% que 'bate a meta' no painel entrega, na prática, cerca de **{alvo/(1+i)}%**."
- "Como esses eventos não têm `transaction_id`, **não dá para corrigir o histórico** (o Google Ads exige o order ID para retrair conversões). A correção só vale daqui para a frente e exige *data exclusion* do período contaminado."

### 1.4 Confiança

Mecânica de dedup e tROAS: **Alta** (docs oficiais). "50 eventos/7 dias" da Meta: **Média** (Meta Business Help citado por terceiros; conferir no Help Center). Qualquer "% de perda de eficiência" genérico de blog: **Baixa, não usar**. O valor do impacto vem **dos dados da Smart Fit** e não de benchmark.

**Ganhos de referência quando há dados de melhor qualidade** (servem para o slide "o que se ganha ao corrigir", sempre como *referência de mercado*):
- Enhanced Conversions: mediana de +5% de taxa de conversão em Search e +17% em YouTube, nos "early studies" do Google. **Confiança Média-Baixa**: a figura é repetida por Adobe/Datahash, não achei na página atual do Google, e a Accuracast cita 12% para YouTube ([Adobe Experience League](https://experienceleague.adobe.com/en/docs/platform-learn/data-collection/event-forwarding/set-up-google-ads-enhanced-conversions)). A página oficial cita o caso ASOS (+8,6% Search / +31% YouTube) ([Google Ads Help 11192862](https://support.google.com/google-ads/answer/11192862), Alta como case).

---

## 2. GA4 360: licenciamento por volume de eventos e "evento lixo custa cota"

### 2.1 Princípio

No GA4 360, a cobrança é por **evento faturável**. Existe uma **taxa-base fixa que inclui os primeiros 25 mi de eventos/mês** e, acima disso, uma **taxa variável por evento em faixas de volume** ("as monthly volume increases, the cost per event decreases"). **Todo evento é faturável**, exceto `user_engagement`, spam e eventos de sistema ocultos. A prévia de faturamento fica em Admin → Uso ("View usage and sample pricing"), com tarifas padrão "não contratuais, que variam por mercado" ([Manage billing and monitor usage](https://support.google.com/marketingplatform/answer/9013858), Alta). Logo, um evento sem uso analítico (ex.: `click` genérico com 43 mi de hits/7d) **é custo marginal direto** e, além disso, consome processamento, ocupa espaço em exploração/BigQuery e polui relatórios. Eventos copiados para **subpropriedades/roll-ups** são cobrados como **meio evento adicional** ("100 events pushed into a subproperty = 150 billable"), segundo [Cardinal Path](https://cardinalpath.com/blog/ua-360-vs-ga4-360-pricing-model) e [Adswerve](https://adswerve.com/blog/everything-you-need-to-know-about-ga4-360-subproperties) ("one-half the cost of the events in the source property, per your GA4 360 contract terms"). Eventos filtrados **para fora** da subpropriedade não geram essa meia cobrança. A página oficial de subpropriedades **não fala de faturamento**, então a confiança é **Média** e é preciso confirmar no contrato.

### 2.2 Referências de preço (públicas)

| Item | Valor | Fonte | Confiança |
|---|---|---|---|
| Base | inclui 25 mi eventos/mês | [Google](https://support.google.com/marketingplatform/answer/9013858) | Alta |
| Preço de lista sugerido | "a partir de US$ 50.000/ano" (25 mi/mês) | [Cardinal Path](https://cardinalpath.com/blog/ua-360-vs-ga4-360-pricing-model) | Média |
| **Tabela variável pública (Merkle UK, G-Cloud 14, mai/2024)** | Base £3.000/mês (£36 mil/ano) até 25 mi. **£12,15/mi** de 25 mi a 500 mi. **£2,88/mi** de 500 mi a 2,5 bi. **£0,77/mi** de 2,5 bi a 10 bi. £0,58/mi de 10 bi a 25 bi. £0,35/mi acima de 25 bi. Exemplo do próprio doc: 2,6 bi/mês = £14.608/mês | [Pricing document G-Cloud 14 (Merkle)](https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/documents/719318/843534734432015-pricing-document-2024-05-07-1337.odt) | Média (revendedor, Reino Unido, 2024: é ordem de grandeza e não tarifa da Smart Fit) |
| Faixa anedótica | US$ 50–150 mil/ano | [Lilach Bullock](https://www.lilachbullock.com/how-much-does-google-analytics-cost-to-use/) | Baixa |

**Não achei** tarifa pública do Google para a faixa ~25 bi/mês. A taxa real da Smart Fit vem do contrato com o revendedor ou da prévia em Admin → Uso. **Pedir ao cliente.**

**Limites 360 que viram argumento de governança** ([GA4 limits](https://support.google.com/analytics/answer/11202874), Alta): 100 parâmetros/evento (Standard 25). 125 dimensões e 125 métricas personalizadas de escopo de evento (Standard 50/50). 100 user properties (25). 25 dimensões de item (10). 50 key events (30). 400 públicos (100). Retenção de até 50 meses (14). 2.000 nomes distintos de evento por usuário de app (500). Na web não há limite de nomes de evento. Até **400 subpropriedades por propriedade de origem** e roll-up com até 200 fontes ([About roll-up properties](https://support.google.com/analytics/answer/11526039)). Argumento: "custom dimension ocupada com lixo é slot de 360 que você paga e não usa".

### 2.3 Fórmulas

- **Eventos lixo/mês:** `E_mes = hits_7d ÷ 7 × 30,4`. Para o `click` (exemplo): 43 mi ÷ 7 × 30,4 ≈ **186,7 mi/mês**.
- **Faturáveis com subpropriedades:** `E_fat = E_mes × (1 + 0,5 × n_sub_que_recebem_o_evento)`. Com 1 subpropriedade Web que herda o evento: ≈ **280 mi/mês**.
- **Custo marginal:** `Custo = E_fat ÷ 10⁶ × preço_marginal_da_faixa`. A faixa é definida pelo volume **total** faturável do contrato/mês, e o evento lixo é cobrado na faixa **mais alta atingida** (marginal).
  - Ilustrativo com a tabela Merkle: se o total está entre 500 mi e 2,5 bi/mês (a propriedade 175020184 tem ~2,65 bi/90d ≈ 0,9 bi/mês, revalidar), o custo é 280 × £2,88 ≈ **£ 807/mês ≈ £ 9,7 mil/ano**. Se a faixa for 25 mi–500 mi, o custo é 280 × £12,15 ≈ **£ 3,4 mil/mês ≈ £ 40,8 mil/ano**. **Mostrar como faixa e substituir pela tarifa do contrato.**
- **Participação no volume:** `% = E_mes ÷ volume_total_mes` (ex.: 186,7 mi ÷ ~895 mi ≈ **21%**). Esse é o número de impacto mais robusto, porque não depende de preço: "1 em cada 5 eventos pagos não serve para nada".
- **Efeito degrau:** se remover o lixo derruba o volume para uma faixa contratual inferior (contratos de valor fixo por faixa, como a tabela "Fixed Rate" da Merkle), a economia é `preço_faixa_atual − preço_faixa_nova` e não marginal.

### 2.4 Templates PT-BR

- "O evento `click` gera **~187 mi de eventos/mês (≈21% de todo o volume da propriedade 360)** e não alimenta nenhum relatório, público ou conversão. No GA4 360 cada evento é faturável. Pela tabela pública de referência de um revendedor (G-Cloud 2024), esse volume custa entre **£ 0,8 mil e £ 3,4 mil por mês**, e a tarifa exata depende do contrato da Smart Fit."
- "Cada evento enviado para a propriedade principal **e** replicado nas subpropriedades é cobrado de novo como meio evento. Filtrar o lixo **na origem** economiza nas duas pontas."

### 2.5 Confiança

Modelo de cobrança: **Alta**. Regra de 0,5 por subpropriedade: **Média** (Cardinal Path/Adswerve, "per your contract"). Preços: **Média** (revendedor UK) e servem como **ordem de grandeza**. Nunca apresentar como "a Smart Fit paga X".

---

## 3. sGTM no Cloud Run: custo e o que se perde sem domínio first-party

### 3.1 Princípio (custo)

Cada servidor de tagging (1 vCPU, 0,5 GB, CPU sempre alocada) custa "aproximadamente US$ 45/mês". O Google recomenda "um mínimo de 2 instâncias para reduzir o risco de perda de dados" e estima que "autoscaling de 2 a 10 servidores atende 35–350 requests por segundo" ([Cloud Run setup guide](https://developers.google.com/tag-platform/tag-manager/server-side/cloud-run-setup-guide), Alta). O overview fala em "mínimo de 3 instâncias por container para redundância" e US$ 30–50 por servidor/mês ([Server-side tagging overview](https://developers.google.com/tag-platform/tag-manager/server-side/overview), Alta). A página de planejamento dá a regra "custo mínimo = instâncias mínimas × custo por servidor (≈ US$ 50)", e o teto é `max_instances × US$ 50`, mais **egress** (todo dado que sai do servidor: requests para vendors e respostas ao browser) e **logging** acima do free tier ([Planning infrastructure requirements and costs](https://developers.google.com/tag-platform/learn/sst-fundamentals/7-planning-infrastructure), Alta).

**Preço de lista Cloud Run, Tier 1, instance-based** (CPU sempre alocada): **US$ 0,000018/vCPU-s** e **US$ 0,000002/GiB-s**, **sem cobrança por request** ("Requests: N/A"). No modelo request-based: US$ 0,000024/vCPU-s ativo, US$ 0,0000025/GiB-s e **US$ 0,40 por milhão de requests** ([Cloud Run pricing](https://cloud.google.com/run/pricing), Alta, extraído em 13/10/2026). Conta: 30,4 d × 86.400 s × 0,000018 = US$ 47,3 de CPU, mais 0,5 GiB × … × 0,000002 = US$ 2,6 de memória, o que dá **≈ US$ 50/instância/mês**, batendo com a doc. ⚠️ `southamerica-east1` (São Paulo) pode estar em **Tier 2**, com preço maior. **Confirmar a região do serviço no projeto do cliente.**

### 3.2 Fórmulas (custo)

- `Custo_base_mês = min_instances × ~US$ 50` (+ egress + logs). Com 3 instâncias: **≈ US$ 150/mês** de piso.
- **Custo por milhão de requests (derivado, instance-based):** cada instância atende ~17,5–35 rps (35–350 rps ÷ 2–10). Isso dá ~46–92 mi requests/mês por instância e **≈ US$ 0,54–1,09 por milhão de requests** em capacidade. É uma estimativa derivada e precisa ser rotulada assim.
- **Requisições redundantes (ex.: o mesmo evento chegando 2× ao sGTM, ou o client GA4 + uma tag duplicada mandando para o mesmo vendor):** `Custo_red = req_redundantes_mês ÷ 10⁶ × custo_por_milhão + egress_red`. Também multiplica chamadas a APIs de terceiros (Meta CAPI, TikTok Events API), o que gera duplicidade **na mídia**, e esse custo é maior que a infra (ver §1).
- **Mensagem honesta:** em geral o custo de infra do sGTM é **pequeno** (centenas de dólares/mês). O impacto real de chamadas redundantes está em **dados duplicados nas plataformas**, e não na fatura do Cloud Run. Não inflar esse pilar.

### 3.3 Princípio (domínio first-party, ITP e bloqueadores)

- **Safari/ITP:** cookies persistentes criados via `document.cookie` foram limitados a **7 dias** (ITP 2.1) ([WebKit ITP 2.1](https://webkit.org/blog/8613/intelligent-tracking-prevention-2-1/), Alta). Cookies definidos por respostas HTTP de subdomínio **CNAME-cloaked para terceiro** também são limitados a **7 dias** ([WebKit, CNAME Cloaking and Bounce Tracking Defense](https://webkit.org/?p=11338), Alta). Todo armazenamento gravável por script (LocalStorage, IndexedDB etc.) é apagado após **7 dias de uso do Safari sem interação** com o site ([WebKit, Full Third-Party Cookie Blocking and More](https://webkit.org/?p=10218), Alta). Há ainda um teto de **24 h** quando se chega por link decorado de domínio classificado como rastreador (ITP 2.2, via Simo Ahava, Média) e um teto de 7 dias para cookies de resposta vinda de **IP de terceiro** (Safari 16.4, só fontes secundárias como Stape: Baixa-Média). Efeito prático: o usuário de Safari que volta depois de mais de 7 dias **vira usuário novo**, a atribuição do clique pago se perde e a jornada se quebra.
- **Link Tracking Protection (iOS 17+)**: remove `gclid`/`fbclid` etc. em links abertos no Mail, Mensagens e Navegação Privada (UTMs são preservadas). As fontes são secundárias, porque a Apple não publica a lista (Baixa-Média).
- **Domínio first-party / tag gateway:** o Google reporta **+11% de "sinais"** (carregamentos do script da tag, e não conversões) para quem configura o Google tag gateway ([Google Ads Help 16214371](https://support.google.com/google-ads/answer/16214371), Alta, para "sinais"). O "+14% de conversões" que circula é de Fastly/terceiros, conflita com a página oficial e **não deve ser usado**. A Adswerve reporta +9–18% de conversões medidas na base dela (Baixa-Média).
- **Bloqueadores:** a GWI mede 31,5% de usuários globais que usam ad blocker "às vezes" (Q1/2024). Para o Brasil, o que encontrei foram números antigos ou sem método (10%, 21% urbano em 2016) ([Backlinko/GWI](https://backlinko.com/ad-blockers-users), Baixa para o Brasil). **Não citar % de perda de dados do GA por bloqueador**, porque não existe fonte robusta.
- **Market share no Brasil (StatCounter, set/2026, todas as plataformas):** Chrome 77,1%, Edge 7,7%, **Safari 6,6%** ([StatCounter](https://gs.statcounter.com/browser-market-share/all/brazil), Média). **Melhor do que isso: usar a dimensão `browser` do próprio GA4 da Smart Fit** (o público de academia premium/app pode ter peso maior de iOS).

### 3.4 Fórmulas (perda de sinal)

- `Usuários_afetados_ITP = sessões_Safari_iOS ÷ sessões_totais` (GA4) × `% de retornos com intervalo > 7 dias` (GA4: coorte, ou dias desde a última sessão).
- `Conversões_em_risco_de_atribuição = conversões_Safari × % com clique pago > 7 dias antes da conversão` (Ads: *Time lag*/*Days to conversion*).
- Para o ganho de first-party, usar **faixa** e não ponto: "+11% de sinais (Google, oficial)". Chamar de "conversões recuperáveis" só depois de medir antes e depois.

### 3.5 Templates PT-BR

- "O servidor de tagging custa ~US$ 50/instância/mês (Google). Com o mínimo recomendado de 2–3 instâncias, o piso é **US$ 100–150/mês**. A infra não é o problema. O problema é que **{x}% das chamadas que passam por ele são redundantes** e chegam duplicadas na Meta e no TikTok."
- "Sem domínio próprio para o sGTM, os cookies de medição no Safari duram **no máximo 7 dias** (regra oficial do WebKit). **{y}% das sessões** da Smart Fit vêm de Safari, e quem volta depois de uma semana é contado como usuário novo e perde a origem da mídia."

### 3.6 Confiança

Custo/instância e recomendação de instâncias: **Alta**. Preço Cloud Run: **Alta** (preço de lista, região a confirmar). ITP 7 dias: **Alta** (WebKit). Ganho de tag gateway: **Alta para "sinais" e Baixa para "conversões"**. Ad blocker no Brasil: **Baixa**.

---

## 4. LGPD: sanções, dosimetria, consentimento de cookies e PII no browser

### 4.1 Princípio

**Teto legal (art. 52, LGPD):** advertência, **multa simples "de até 2% do faturamento da pessoa jurídica de direito privado, grupo ou conglomerado no Brasil no seu último exercício, excluídos os tributos, limitada, no total, a R$ 50.000.000,00 por infração"**, multa diária, publicização, bloqueio e eliminação dos dados, e (incluídas pela Lei 13.853/2019) suspensão e proibição de tratamento ([Lei 13.709/2018, Planalto](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm), Alta). O **ônus da prova do consentimento é do controlador** (art. 8º, §2º), e o art. 46 exige medidas de segurança "aptas a proteger os dados pessoais de acessos não autorizados". Também existe responsabilidade civil por dano (art. 42), além de Procon/ações coletivas. Não quantificar essa parte.

**Dosimetria (Resolução CD/ANPD nº 4/2023)** ([DOU](https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-4-de-24-de-fevereiro-de-2023-466146077), Alta):
- **Classificação (art. 8º):** *leve* (residual). *Média*, quando pode "afetar significativamente interesses e direitos fundamentais", impedir ou limitar direitos ou causar dano material/moral. *Grave*, quando é média **e** envolve pelo menos um destes: **(a) tratamento em larga escala**, (b) vantagem econômica, (c) risco à vida, (d) dados sensíveis/crianças/idosos, **(e) tratamento sem hipótese legal**, (f) efeito discriminatório, (g) prática irregular sistemática. Ou ainda quando há obstrução à fiscalização.
- **Valor-base (art. 11):** classificação × faturamento do ramo afetado (sem tributos) × grau do dano (Apêndice I). Alíquotas do Apêndice I segundo fonte secundária: **leve 0,08–0,15%, média 0,13–0,50%, grave 0,45–1,50% do faturamento** ([Confidata](https://confidata.com.br/blog/regulamento-dosimetria-anpd-sancoes), Média. O Apêndice é tabela/imagem no DOU, conferir).
- **Agravantes (art. 12):** reincidência específica +10% cada (até 40%), genérica +5% (até 20%), medida de orientação descumprida +20% cada (até 80%), medida corretiva descumprida +30% cada (até 90%).
- **Atenuantes (art. 13):** cessar a infração **antes** de procedimento da ANPD dá **−75%** (−50% e −30% em fases posteriores). Política de governança dá −20%. Medidas de mitigação antes do procedimento dão −20%. Cooperação/boa-fé dá −5%. **Argumento de venda da auditoria:** corrigir agora é a maior atenuante prevista.
- **Piso e teto (art. 15):** nunca menor que o mínimo do Apêndice II **ou o dobro da vantagem econômica** estimável. Limitado a 2% do faturamento ou R$ 50 mi.

**Cookies (Guia orientativo ANPD, out/2022)** ([PDF ANPD](https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/guia-orientativo-cookies-e-protecao-de-dados-pessoais.pdf), Alta). Citações literais:
- p. 18–19: o consentimento "deve ser inequívoco… não se admitindo a sua inferência ou a obtenção de forma tácita ou a partir de uma omissão do titular. Por isso… **não é recomendável** a utilização de banners de cookies com opções de autorização pré-selecionadas ou a adoção de mecanismos de consentimento tácito, como **a pressuposição de que, ao continuar a navegação em uma página, o titular forneceria consentimento**".
- p. 25: "o legítimo interesse **dificilmente será a hipótese legal mais apropriada**… para fins de publicidade… em especial, se a coleta é efetuada por meio de cookies de terceiros". Para cookies de publicidade, o consentimento "pode ser considerado uma hipótese legal mais apropriada".
- p. 26–27 (exemplo 4): medição de audiência por legítimo interesse **só** com dados agregados, **sem compartilhamento com terceiros** e sem cruzamento. Isso **não** descreve GA4 + Google Ads + Meta + TikTok.
- p. 30–33: boas práticas são botão "rejeitar todos" no 1º nível e "desativar cookies baseados no consentimento por padrão". A evitar: "um único botão no banner de primeiro nível… ('concordo', 'aceito', 'ciente')" e "cookies não necessários ativados por padrão".

**Consent Mode:** o *EU user consent policy* do Google cobre EEE/Reino Unido/Suíça. **Não achei exigência do Google para o Brasil** (Alta para a ausência na política, Baixa para "o Brasil é opt-in" de blog). O argumento é de LGPD: sem sinais de consentimento (`ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`), as tags disparam independentemente da escolha. O banner implícito passa a ser só decorativo. Quando o Consent Mode é implementado corretamente, a modelagem do Google "recupera, em média, mais de 70% das jornadas clique→conversão perdidas por escolhas de consentimento" (resultado inicial, varia por anunciante) ([Google blog](https://blog.google/products/marketingplatform/360/conversion-modeling-through-consent-mode-google-ads/), Média-Alta). Ou seja, dá para ficar em conformidade sem perder a maior parte do sinal.

**PII em localStorage/sessionStorage e envio a terceiros:**
- OWASP: não armazenar dado sensível em Web Storage. Qualquer script na página (inclusive as ~N tags de terceiros do GTM) lê esse armazenamento, e um único XSS exfiltra ([OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html), [OWASP WSTG Browser Storage](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/12-Testing_Browser_Storage), Alta).
- Google Analytics proíbe enviar PII (e-mail, telefone etc.). A consequência contratual prevista é encerramento da conta/destruição de dados ([GA best practices to avoid sending PII](https://support.google.com/analytics/answer/6366371), Alta). A *data redaction* do GA4 (e-mail e query params) é "best effort" e **só para web**.

**Enforcement real (calibrar o discurso):** a primeira multa foi da Telekall (microempresa, jul/2023): R$ 7,2 mil + R$ 7,2 mil + advertência ([Mobile Time](https://www.mobiletime.com.br/noticias/06/07/2023/anpd-aplica-sua-primeira-sancao-com-multa-a-telekall/), Média). As outras sanções até 2024 foram a órgãos públicos (INSS, Ministério da Saúde, SES-SC, IAMSPE, SEEDF, SAS-PE), em geral advertências e publicização ([Confidata, mapa de sanções](https://confidata.com.br/blog/mapa-sancoes-anpd-todos-casos-2026), Média). Em dez/2024 houve fiscalização de 20 grandes empresas por falta de encarregado/canal, sem multa noticiada. **Não achei sanção da ANPD por cookies/pixels até out/2026.** "Cookies e rastreamento online" está na Agenda Regulatória 2025-2026 (Resolução CD/ANPD nº 31/2025, via blog, Média-Baixa). Referência de custo de incidente: o custo médio de violação de dados no Brasil é **R$ 7,19 mi** (IBM Cost of a Data Breach 2025) ([PR Newswire/IBM](https://www.prnewswire.com/br/comunicados-para-a-imprensa/relatorio-da-ibm-custo-medio-de-uma-violacao-de-dados-no-brasil-atinge-r-7-19-milhoes-302517777.html), Média).

### 4.2 Fórmulas

- **Teto por infração:** `Multa_max = min(2% × Faturamento_BR_sem_tributos, R$ 50 mi)`. Com faturamento ≥ R$ 2,5 bi, o teto efetivo é **R$ 50 mi por infração**. Conferir a receita da Smart Fit Brasil no RI da companhia e **não citar número de memória**.
- **Faixa de valor-base (ilustrativa):** `Base = alíquota_classe × Faturamento_ramo` (Apêndice I, confirmar), depois `× (1 + Σagravantes − Σatenuantes)`, limitado ao teto.
- **Exposição qualitativa (para a matriz):** `Exposição = n_infrações_distintas × probabilidade × teto`. Infrações candidatas distintas: (1) tratamento de cookies de publicidade sem hipótese legal válida (consentimento tácito), (2) segurança inadequada (PII em Web Storage acessível a terceiros, art. 46), (3) compartilhamento de PII com terceiros sem base/transparência. Mostrar como **cenário** e nunca como multa esperada.

### 4.3 Templates PT-BR

- "O banner atual trata 'continuar navegando' como aceite. O guia da ANPD (out/2022, p. 19) diz textualmente que esse mecanismo **não é compatível com a LGPD**, e o ônus de provar o consentimento é da Smart Fit (art. 8º, §2º). Hoje as tags de mídia disparam **antes e independentemente** de qualquer escolha, porque não há sinais de Consent Mode."
- "E-mail e telefone do cliente ficam gravados **em texto aberto no navegador** (localStorage/sessionStorage), legíveis por qualquer um dos {N} scripts de terceiros carregados na página. Pela dosimetria da ANPD, tratamento em larga escala é agravante de classificação ('grave'), e o teto é de **R$ 50 mi por infração**. Corrigir **antes** de qualquer procedimento da ANPD reduz uma eventual multa em **75%** (art. 13, Res. 4/2023)."
- Calibragem obrigatória no deck: "Até hoje a ANPD não multou ninguém por cookies. O risco é regulatório, reputacional e de **reclamação de titular**, e o custo de corrigir é baixo comparado ao teto."

### 4.4 Confiança

Lei, resolução e guia: **Alta**. Alíquotas do Apêndice I: **Média** (fonte secundária). Histórico de sanções: **Média** (compilação de blog conferida com notícias). Consent Mode no Brasil: **ausência de exigência = Alta**, e os "70%" são **Média-Alta** (Google, "early results").

---

## 5. Performance: tag bloat → Core Web Vitals → conversão

### 5.1 Princípio

O web.dev (Google) diz que o tag manager prejudica os CWV indiretamente, por disputa de banda (LCP), conteúdo injetado (CLS) e disputa da main thread (INP), e afirma: **"we have seen a correlation between the size of tag managers and poorer INP scores"**. A biblioteca do GTM tem ~33 KB comprimida, **o container mediano tem ~50 KB** e o limite é 300 KB. "Um container grande costuma ser sinal de container mal mantido". Tags sem uso devem ser **pausadas ou removidas**, e não bloqueadas por exceção. "Vários click/timer triggers podem aumentar dramaticamente o trabalho do tag manager". Tags não essenciais devem disparar depois do carregamento ([Best practices for tags and tag managers](https://web.dev/articles/tag-best-practices), Alta). Obs.: tags **pausadas continuam no container** e pesam no download. O ideal é removê-las.

**Evidência de efeito em negócio (usar como referência de mercado e não como previsão):**

| Estudo | Resultado | Método | Confiança |
|---|---|---|---|
| Deloitte / Google, *Milliseconds Make Millions* (2020) | **−0,1 s** em 4 métricas de velocidade mobile ⇒ **+8,4% de conversões e +9,2% de AOV no varejo** (+10,1% em viagens). Maior sensibilidade nas etapas **pré-checkout** | 37 marcas europeias/EUA, correlacional | Média ([web.dev](https://web.dev/case-studies/milliseconds-make-millions), [PDF Deloitte](https://www2.deloitte.com/content/dam/Deloitte/ie/Documents/Consulting/Milliseconds_Make_Millions_report.pdf)) |
| Vodafone (Itália) | **LCP −31%** (8,3 s → 5,7 s) ⇒ **+8% de vendas**, +15% lead/visita, +11% carrinho/visita | **A/B 50/50** em tráfego pago | Média-Alta ([web.dev](https://web.dev/case-studies/vodafone)) |
| QuintoAndar (**Brasil**) | **INP −80%** (1.006 → 216 ms mobile) ⇒ **+36% de conversões** (volume, YoY). Inclui "**removing third-party pixels from the client**" | Antes/depois, várias mudanças juntas, sem controle | Média ([web.dev](https://web.dev/case-studies/quintoandar-inp)) |
| HTTP Archive Web Almanac | Top 1.000 sites: mediana de 66 terceiros (2024). 129/106 requests de terceiros (desktop/mobile, 2025). JS mediano 558 KB mobile (2024). Top-10 terceiros: tempo de bloqueio mediano médio de 1,4 s (2022) | Crawl em massa | Alta para benchmark ([2024](https://almanac.httparchive.org/en/2024/third-parties), [2025](https://almanac.httparchive.org/en/2025/third-parties), [2022](https://almanac.httparchive.org/en/2022/third-parties)) |

### 5.2 Fórmulas / heurísticas (cadeia de evidência)

1. **Medir** (Chrome DevTools/Lighthouse no funil real): `KB_tags` (transfer size de gtm.js, gtag/js, fbevents, ttq etc.), `n_requests_terceiros`, `TBT_terceiros` (Lighthouse *third-party-summary* dá *main-thread blocking time* por entidade) e INP/LCP no CrUX/RUM.
2. **Atribuir:** `Δms_estimado = TBT_terceiros_removível` (tags removíveis/consolidáveis, ex.: 38 tags Google Ads por página → 1 Google tag com destinos). O TBT é proxy de INP **no laboratório**, e a QuintoAndar usou exatamente esse proxy.
3. **Converter (cenário e não previsão):** `ΔConv% ≈ 8,4% × (Δs_mobile ÷ 0,1 s)` (elasticidade Deloitte para varejo), **com teto de bom senso**. Apresentar só se Δ ≥ 0,1 s em métricas de campo e como "referência Deloitte". Receita: `ΔReceita = ΔConv% × matrículas_web_mês × ticket_médio_real`.
4. **Benchmark:** `tamanho_container ÷ 50 KB` (mediana web.dev) e `n_terceiros ÷ 27` (mediana top 1 mi, Almanac 2024).

### 5.3 Templates PT-BR

- "Cada página carrega **{n} tags do Google Ads** que fazem a mesma coisa. O container tem **{X} KB** (a mediana da web é ~50 KB, segundo o Google), e os scripts de terceiros bloqueiam a main thread por **{T} ms** no checkout. O Google documenta correlação entre container grande e pior responsividade (INP)."
- "Referência de mercado: na Deloitte, **0,1 s mais rápido no mobile = +8,4% de conversão no varejo**. Na brasileira QuintoAndar, tirar pixels de terceiros do navegador fez parte de uma melhoria de INP de 80%, acompanhada de +36% de conversões. **Não prometemos esse número.** Propomos medir antes e depois com a mesma métrica."

### 5.4 Confiança

Correlação tamanho × INP e mediana de container: **Alta** (web.dev). Elasticidades: **Média**, porque são estudos de terceiros e não causais para a Smart Fit. O "53% abandonam acima de 3 s" (Google/SOASTA 2016-17) é **antigo, não usar**.

---

## 6. Segurança: tokens de API (Meta CAPI / TikTok Events API) em texto aberto no sGTM

### 6.1 Princípio

O token de acesso da Conversions API é o que autentica cada chamada ("Pass the access token as a parameter in each API call"). Ele é gerado no Events Manager ou por um **system user**, e clicar em "Manage" cria automaticamente um "Conversions API system user" ([Meta CAPI Get Started](https://developers.facebook.com/docs/marketing-api/conversions-api/get-started), Alta). Tokens de system user **não expiram** sozinhos, então valem até alguém revogar (fontes de fornecedores, Média). Quem tem o token consegue **enviar eventos para o dataset/pixel** da Smart Fit. Isso permite injetar compras falsas ou valores absurdos (*event poisoning*), contaminar a otimização da Meta (§1) e a mensuração, e consumir limites de API. Para o TikTok Events API, o token também fica atrelado ao pixel e é de longa duração (fontes de fornecedores, Média-Baixa). Tecnicamente é **CWE-798 (Use of Hard-coded Credentials)** e **CWE-312 (Cleartext Storage of Sensitive Information)** ([CWE-798](https://cwe.mitre.org/data/definitions/798.html), [CWE-312](https://cwe.mitre.org/data/definitions/312.html), Alta). O vetor de exposição é **qualquer pessoa com acesso de leitura ao container sGTM** ou a um export JSON dele. No nosso caso o export está em disco, o que reforça que o token deve ser tratado como comprometido e **rotacionado**. Também é exposição pelo art. 46 da LGPD (medidas de segurança), já que os eventos CAPI costumam levar e-mail/telefone com hash.

**Limite de honestidade:** **não encontrei incidente público documentado** de abuso de token CAPI/TikTok para envenenar eventos. Apresentar como **risco plausível de alta consequência e baixa complexidade**, sem afirmar que acontece no mercado.

### 6.2 Fórmulas / heurísticas

- **Superfície de exposição:** `Exposição = n_usuários_com_acesso_ao_container_sGTM (accessBindings/usuários GTM) + n_cópias_de_export conhecidas + idade_do_token`. Puxar com `scripts/gtm_dump.py --users`.
- **Impacto se explorado:** igual ao §1, com `i` arbitrário (o atacante escolhe volume e valor). Exposição financeira = `Gasto_Meta_mês + Gasto_TikTok_mês` otimizados contra um dataset que terceiros podem escrever.
- **Custo de correção:** rotação do token (minutos), migração para variável/secret fora do container (horas). Relação custo/benefício trivial.

### 6.3 Templates PT-BR

- "O token que autoriza o envio de conversões para a Meta (e o do TikTok) está **em texto aberto na tag {nome} do servidor de tagging**, visível para todos os **{n}** usuários com acesso ao container. Com ele, qualquer pessoa pode **injetar compras falsas** no pixel da Smart Fit e distorcer a otimização de **R$ {gasto}/mês** em mídia. Recomendação: rotacionar hoje e guardar fora do container."
- (Nunca colocar o valor do token na entrega. Ver CLAUDE.md.)

### 6.4 Confiança

Mecânica do token e CWE: **Alta**. Não-expiração de token de system user: **Média**. Existência de abuso real no mercado: **sem evidência, não afirmar**.

---

## 7. Tag quebrada enviando checkout ao BigQuery (complemento)

Sem fonte externa de impacto necessária, porque o impacto é interno. Fórmula: `Gap = dias_sem_dado_válido × eventos_checkout/dia` e "**{n} dias de funil de checkout irrecuperáveis no BigQuery**", que é o histórico que alimenta modelos, LTV e conciliação com o ERP. Se a tag manda payload com PII para tabela sem controle de acesso, vale também o §4 (art. 46). Custo de BigQuery: streaming/Storage Write API é cobrado por GB ingerido, irrelevante perto do custo de decisão. **Não quantificar em R$ sem dado.**

---

## Tabela-resumo: Achado tipo → métrica de impacto → fórmula → fonte

| Achado tipo | Métrica de impacto | Fórmula | Fonte (confiança) |
|---|---|---|---|
| `purchase` falso (R$ 0, sem `transaction_id`) usado como conversão | CPA real vs. painel; ticket médio distorcido | `i_n = N_falso/N_real`; `CPA_real = CPA_painel × (1+i_n)` (75% falso ⇒ 4×) | [Google tROAS](https://support.google.com/google-ads/answer/6268637), [Data exclusions](https://support.google.com/google-ads/answer/10276486) (Alta) |
| `purchase` duplicado (app/Firebase, reload) | Receita inflada (R$); ROAS real sob tROAS | `i_v = V_dup/V_real`; `ROAS_real = tROAS/(1+i_v)` | [GA4 dedup só web](https://support.google.com/analytics/answer/12313109) (Alta) |
| `purchase` sem `transaction_id` | % receita não deduplicável e não retratável | `% = V_sem_id / V_total` | [Ads transaction ID](https://support.google.com/google-ads/answer/6386790), [Conversion adjustments](https://support.google.com/google-ads/answer/7686447) (Alta) |
| Pixel + CAPI sem `event_id` | Eventos duplicados na Meta | `dup = eventos_pixel ∩ eventos_CAPI sem par event_id/event_name` | [Meta dedup 48h](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events) (Alta) |
| Inflação concentrada num canal | Má alocação de verba | `Δshare = share_painel − share_real`; distorção ≈ `i_canalA − i_canalB` | Derivado de tROAS (Alta, mecanismo) |
| Evento lixo (`click` 43 mi/7d) no 360 | % do volume faturável; £/R$ por mês | `E_fat = hits_7d/7×30,4×(1+0,5×n_sub)`; `custo = E_fat/10⁶ × preço_marginal` | [Google billing](https://support.google.com/marketingplatform/answer/9013858) (Alta), [Merkle G-Cloud](https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/documents/719318/843534734432015-pricing-document-2024-05-07-1337.odt) (Média), [Adswerve 0,5](https://adswerve.com/blog/everything-you-need-to-know-about-ga4-360-subproperties) (Média) |
| Custom dims/params ocupados com lixo | Slots 360 desperdiçados | `slots_usados_sem_uso / 125` | [GA4 limits](https://support.google.com/analytics/answer/11202874) (Alta) |
| Chamadas redundantes ao sGTM | US$ infra + duplicidade nas mídias | `req_red/10⁶ × US$ 0,54–1,09` + egress | [Cloud Run setup](https://developers.google.com/tag-platform/tag-manager/server-side/cloud-run-setup-guide), [Cloud Run pricing](https://cloud.google.com/run/pricing) (Alta; US$/mi derivado) |
| sGTM sem domínio first-party | % sessões com cookie ≤ 7 d; atribuição perdida | `sessões_Safari × % retorno > 7d`; ganho ref. +11% sinais | [WebKit ITP 2.1](https://webkit.org/blog/8613/intelligent-tracking-prevention-2-1/), [WebKit CNAME](https://webkit.org/?p=11338), [Tag gateway](https://support.google.com/google-ads/answer/16214371) (Alta) |
| Banner implícito / sem Consent Mode | Exposição LGPD (teto R$) + sinal recuperável | `min(2%×Fat_BR, R$ 50 mi)` por infração; modelagem recupera >70% (ref.) | [LGPD art. 52](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm), [Guia cookies ANPD p.19](https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/guia-orientativo-cookies-e-protecao-de-dados-pessoais.pdf), [Res. 4/2023](https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-4-de-24-de-fevereiro-de-2023-466146077), [Google CoMo](https://blog.google/products/marketingplatform/360/conversion-modeling-through-consent-mode-google-ads/) (Alta / Média-Alta) |
| PII em localStorage/sessionStorage | Nº de scripts terceiros com acesso; exposição art. 46 | `n_scripts_terceiros_na_página` × dados expostos; teto LGPD | [OWASP HTML5](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html), LGPD art. 46 (Alta); [IBM CoDB 2025 R$ 7,19 mi](https://www.prnewswire.com/br/comunicados-para-a-imprensa/relatorio-da-ibm-custo-medio-de-uma-violacao-de-dados-no-brasil-atinge-r-7-19-milhoes-302517777.html) (Média) |
| PII enviada ao GA4/mídias | Risco contratual (exclusão de dados/conta) + LGPD | contagem de hits com PII / total (Data API) | [GA PII policy](https://support.google.com/analytics/answer/6366371) (Alta) |
| Tag bloat (38 tags Ads/página, tags pausadas) | KB, nº requests, TBT terceiros → ΔConv% cenário | `ΔConv ≈ 8,4% × Δs/0,1` (ref.); benchmark `KB/50` | [web.dev tag best practices](https://web.dev/articles/tag-best-practices) (Alta), [Deloitte](https://web.dev/case-studies/milliseconds-make-millions), [Vodafone](https://web.dev/case-studies/vodafone), [QuintoAndar](https://web.dev/case-studies/quintoandar-inp) (Média) |
| Token Meta/TikTok em texto aberto | Superfície de exposição; gasto otimizado sobre dataset gravável por terceiros | `n_acessos + cópias + idade`; exposição = gasto Meta+TikTok/mês | [Meta CAPI](https://developers.facebook.com/docs/marketing-api/conversions-api/get-started), [CWE-798](https://cwe.mitre.org/data/definitions/798.html) (Alta); abuso real: sem evidência |
| Tag BigQuery quebrada | Dias de dado irrecuperável | `dias × eventos_checkout/dia` | Interno (dado próprio) |

---

## Pendências para fechar os números (pedir ao cliente / extrair)

1. Tarifa contratual do GA4 360 (revendedor) ou print da prévia em Admin → Uso. Confirmar a regra de 0,5 por subpropriedade no contrato.
2. Quais eventos GA4/Firebase são importados como conversão primária no Google Ads, e qual evento otimiza as campanhas Meta/TikTok. Sem isso, o §1 vira "risco" e não "impacto".
3. Gasto mensal por plataforma/campanha (API Ads/Meta) para o `Gasto_exposto`.
4. Região do serviço Cloud Run do sGTM (Tier 1 vs. 2) e min/max instances atuais.
5. Faturamento Brasil (RI) para o teto LGPD e % de sessões Safari/iOS (GA4).
6. Receita real de backend em 30 d para a base do `i_v` (app e web).
