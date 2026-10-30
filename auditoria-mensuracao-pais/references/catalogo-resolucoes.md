# Catálogo de resoluções (problema → como resolver)

> Vale para todos os clientes da skill `auditoria-mensuracao-pais`. Criado em 29/10/2026 a partir do diagnóstico e da execução da Smart Fit Brasil (31 achados SF-xxx, 31 ações A-nnn, achados novos N-01 a N-11). **Documento vivo**: cresce a cada país e a cada ação nova.

Cada entrada é um **tipo de problema** e não um achado. Achados diferentes que se resolvem da mesma forma (ex.: `transaction_id` ausente no totem e no Espaço do Cliente) ficam na mesma entrada. Nenhuma ação vem pronta: o catálogo diz como detectar, o que costuma causar, quem resolve, o que a Monks pode fazer, como provar que está pronto e o que já deu errado. A ação de cada país continua sendo escrita para o caso concreto.

## Como usar

- **Na auditoria (Etapa 3):** para cada achado confirmado, procure o padrão no índice. Use a entrada para escrever `rec_raiz`, `rec_contorno`, `pronto` e a ação `A-nnn`, e leia as **Lições** antes de recomendar.
- **Na execução (Etapa 5):** antes de mexer no workspace, leia o padrão e os padrões transversais (§ P). Depois do reteste, atualize a entrada.
- **No Chrome e nas APIs:** a linha "Detecção" diz qual consulta ou roteiro prova o problema e depois serve de reteste.

## Como alimentar (regra)

1. **Ação nova num país:** se cabe num padrão existente, acrescente uma linha em **Casos** (`<CLIENTE> <PAÍS> <achado> → <ação> · <status> (<data>): <resultado em uma frase>`; os casos "BR" sem cliente são da Smart Fit). Se não cabe, crie a entrada **no fim do pilar** com o próximo número livre (`R-<PILAR>-nn`). IDs são estáveis: nunca renumere nem reaproveite.
2. **A execução ensinou algo** (falso positivo, armadilha da API, contorno que funcionou, decisão do cliente que mudou o caminho): vire uma linha em **Lições**, com o caso de origem entre parênteses.
3. **Ação descartada ou adiada pelo cliente** também entra em Casos, com o motivo. Isso ajuda a prever a reação em outro país.
4. Mudou o catálogo? Registre no **Changelog** no fim do arquivo.

Modelo de entrada:

```
### R-<PILAR>-nn · <problema em uma linha>
- **Sintoma / detecção:** o que aparece e qual consulta, export ou roteiro prova
- **Causas comuns:**
- **Resolução raiz:** quem corrige e o quê
- **O que a Monks faz:** contorno no GTM (workspace NÃO PUBLICAR), lista para o cliente, recomendação
- **Pronto quando:** teste (o mesmo método da detecção)
- **Típico:** fase · esforço · R (responsável) / A (aprovador)
- **Lições:**
- **Casos:**
```

## Índice

| ID | Problema | Casos |
|---|---|---|
| R-DUP-01 | `purchase` sem `transaction_id` ou sem valor | BR SF-DUP-01, SF-DUP-03 |
| R-DUP-02 | `purchase` repetido para o mesmo `transaction_id` | BR SF-DUP-02 |
| R-DUP-03 | Payload de e-commerce errado (carrinho inteiro, `value` de outro preço, promo errada) | BR SF-DUP-04, N-09 |
| R-DUP-04 | Conversão de mídia contada mais de uma vez ou na conta errada | BR SF-DUP-06, N-02, N-03 |
| R-DUP-05 | Trigger quebrado por mudança no site | BR SF-DUP-07 |
| R-DUP-06 | Outro container, staging ou `debug_mode` escrevendo na propriedade de produção | BR SF-DUP-08 |
| R-FIN-01 | Evento genérico consumindo a cota 360 | BR SF-FIN-01 |
| R-FIN-02 | Subpropriedade com filtro errado (copia tudo ou foi "pausada" com filtro fictício) | BR SF-FIN-03, SF-DUP-05 |
| R-FIN-03 | sGTM: versão sem nome, logging e custo não medidos | BR SF-FIN-02 |
| R-PII-01 | Dado pessoal em parâmetro de tag (GA4 ou mídia) | BR SF-PII-04, SF-PII-05, N-07 |
| R-PII-02 | Dado pessoal gravado no navegador (localStorage/sessionStorage) | BR SF-PII-01, SF-PII-02 |
| R-PII-03 | Dado pessoal indo para ferramenta de terceiro ou exposto pelo código do site | BR SF-PII-05, N-08 |
| R-PII-04 | Consentimento: banner implícito, mídia antes do aceite, sem Consent Mode | BR SF-PII-03 |
| R-PII-05 | Credencial (token CAPI/Events API) em texto aberto no sGTM | BR SF-GOV-10 (A-001) |
| R-PERF-01 | Peso de tags piora INP/LCP | BR SF-PERF-01 |
| R-PERF-02 | sGTM fora do domínio próprio ou fora da região | BR SF-PERF-02, SF-FIN-04 |
| R-GOV-01 | Higiene do container: pausadas, triggers/variáveis sem uso, tags sem efeito | BR SF-GOV-04, SF-GOV-11 |
| R-GOV-02 | Tags "[TESTE]"/"UPD" em produção ou propriedade de teste recebendo produção | BR SF-GOV-12, SF-GOV-02 |
| R-GOV-03 | Key events sem significado de negócio | BR SF-GOV-03 |
| R-GOV-04 | Acessos sem uso, Admins externos, acesso via grupo GMP | BR SF-GOV-07, SF-GOV-08 |
| R-GOV-05 | Painéis e conectores com credencial pessoal | BR SF-GOV-09 |
| R-GOV-06 | Ativos mortos ou sem dono (propriedades, containers, Cloud Run) | BR SF-GOV-10, SF-GOV-06 |
| R-GOV-07 | Domínio com a marca levando a terceiro | BR SF-GOV-05 |
| R-GOV-08 | eventNames estranhos (sondagem de injeção, SDK desconhecido) | BR SF-GOV-13, N-10 |
| R-GOV-09 | Sem processo de publicação nem monitoramento | BR SF-GOV-04 (A-016) |
| P-01 a P-10 | Padrões transversais de execução | todos |

---

## DUP · Duplicidade e integridade

### R-DUP-01 · `purchase` sem `transaction_id` ou sem valor
- **Sintoma / detecção:** Data API Q08/Q09: `purchase` com `transactionId=(not set)` ou `purchaseRevenue=0`, aberto por `hostName` e `pagePath`. A receita sem ID não deduplica nem concilia com o backend.
- **Causas comuns:** (a) a página de sucesso dispara `purchase` sem os parâmetros de e-commerce e sem trava de disparo único; (b) o push do dataLayer põe `transaction_id` **na raiz do evento**, fora de `ecommerce`, e a variável do GTM só lê `ecommerce.transaction_id`.
- **Resolução raiz:** dev do fluxo envia `transaction_id` (ID do pedido), `value` e `currency` **dentro de `ecommerce`**, uma vez por pedido.
- **O que a Monks faz:** no caso (b), a variável do ID passa a ler `ecommerce.transaction_id` e, se vier vazio, o campo da raiz. A variável mantém o mesmo nome, então nenhuma tag muda (P-02). No caso (a) não há contorno no GTM: sobra o pedido ao dev e, enquanto isso, não usar aquele `purchase` como conversão de lance.
- **Pronto quando:** Data API, 7 dias depois da publicação: `transactionId=(not set)` = 0 no host/página e `eventCount(purchase)` ≈ `countDistinct(transactionId)` (±0,5%).
- **Típico:** F2 · P (contorno) / M (dev) · R = dev do fluxo / A = Head de Martech.
- **Lições:**
  - Antes de mexer, ache o push no bundle JS de produção (`_app-*.js`) e compare com um fluxo que funciona. No BR, a recompra mandava o ID dentro de `ecommerce` e o upgrade/adicional não, o que provou a causa (SF-DUP-03).
  - O contorno no GTM não dispensa o pedido ao dev: registre os dois no deck.
- **Casos:**
  - BR SF-DUP-03 → A-010 · concluída (v599, 22/10): 875 de 875 purchases do Espaço do Cliente com ID; receita sem ID de 73,4% para 0%.
  - BR SF-DUP-01 → A-006 · fora do plano: o cliente desconsiderou o totem em 14/10.

### R-DUP-02 · `purchase` repetido para o mesmo `transaction_id`
- **Sintoma / detecção:** Data API Q07 (transações com `eventCount > 1`) aberta por plataforma e **`appVersion`**. Na web: no Chrome, recarregar a confirmação 2× e contar os `purchase` por destino.
- **Causas comuns:** o app ou a página dispara a cada exibição ou retorno da tela de confirmação, sem guardar os IDs já enviados.
- **Resolução raiz:** guardar localmente os `transaction_id` enviados ou disparar a partir da confirmação do backend. Na web, trava de disparo único por pedido.
- **O que a Monks faz:** recomendação, e enquanto isso receita deduplicada por `transaction_id` em relatórios e BigQuery. Na web dá para fazer trava no GTM (cookie ou storage com o último ID enviado).
- **Pronto quando:** < 1% de transações repetidas **nas versões corrigidas**, em 7 dias.
- **Típico:** F2 · M · R = time de app / A = PO do app.
- **Lições:**
  - No app, meça **por versão**: o total demora semanas a cair porque versões antigas continuam em uso (decisão de 26/10 no BR). O total vai como informação, não como critério.
- **Casos:**
  - BR SF-DUP-02 → A-009 · concluída: 25% até a 4.9.19, 0,19% na 4.9.20+ (19 a 25/10).

### R-DUP-03 · Payload de e-commerce errado
- **Sintoma / detecção:** no Chrome, `window.dataLayer` a cada clique no carrinho, nos adicionais e na troca de plano, comparando a soma dos `add_to_cart` com o carrinho final. Na Data API, `purchaseRevenue` × `itemRevenue` por página. Veja também a promoção e o `item_list_*` de cada push.
- **Causas comuns:** o push manda o carrinho inteiro a cada mudança em vez de só o item; push repetido no mesmo clique; `ecommerce` não é limpo entre pushes (a tag seguinte herda os itens); `value` lido do campo errado (no BR, o preço do plano no `value` do adicional); variável de promoção lendo a vitrine e não o plano escolhido.
- **Resolução raiz:** dev publica só o item que entrou ou saiu, `ecommerce: null` antes de cada push, `value` = soma de `items[].price × quantity`, `view_cart` no load.
- **O que a Monks faz:** variável JS que reconstrói o carrinho, manda às tags só a diferença e ignora push repetido. Para `value` errado, calcular pelos itens. Na mídia, deixar a conversão de `add_to_cart` como secundária até corrigir.
- **Pronto quando:** roteiro fixo de N cliques no Chrome em que a soma dos `add_to_cart` é igual ao carrinho final; Data API com `purchaseRevenue` ≈ `itemRevenue` (7 dias).
- **Típico:** F2 · M · R = dev do site + Martech / A = Head de Martech.
- **Lições:**
  - O contorno no GTM não resiste a reload: recarregar a página reconta o carrinho. Declare esse limite no deck (A-011).
  - Na segunda medição (23/10) o problema estava pior do que no diagnóstico (13/10), porque o site mudou: refaça o roteiro antes de construir o contorno.
- **Casos:**
  - BR SF-DUP-04 → A-011 · workspace 776 aguardando publicação: /carts R$ 1.103,50 → R$ 444,40 no Preview.
  - BR N-09 (adicional com o preço do plano no `value`): na lista viva, a reportar no fim das fases.

### R-DUP-04 · Conversão de mídia contada mais de uma vez ou na conta errada
- **Sintoma / detecção:** no Chrome, requests a `googleadservices`/`facebook`/`tiktok` na compra, contados por conta e por label. No Google Ads, as metas da MCC (primária × secundária). No Events Manager do TikTok/Meta, vários eventos de compra no mesmo pixel e a faixa "Server & browser".
- **Causas comuns:** duas ações **primárias** na mesma meta (o Ads só deduplica pelo order ID dentro da mesma ação); trigger sem condição mandando a compra para a conta de outro negócio; vários eventos de compra (`Purchase`, `PlaceAnOrder`, `compra_*`) no mesmo pixel; pixel e Events API sem `event_id` comum.
- **Resolução raiz:** uma ação primária por meta; o evento de compra que otimiza é um só; o mesmo `event_id` no browser e no servidor.
- **O que a Monks faz:** confirmar no Ads/Events Manager antes de propor mudança no GTM. Trigger com a condição que falta, em workspace.
- **Pronto quando:** Ads com uma ação primária por meta; compra de teste gerando 1 conversão por conta pretendida; Events Manager com deduplicação browser × servidor.
- **Típico:** F1 · P · R = Mídia + Martech / A = Head de Mídia.
- **Lições:**
  - Tags por plano mutuamente exclusivas não são duplicidade. Confira as condições antes de contar (SF-DUP-06).
  - Outra conta recebendo a compra pode ser intencional (Franquias no BR): pergunte antes de "corrigir".
  - Sem acesso ao Ads/Events Manager, o achado fica "a validar".
- **Casos:**
  - BR SF-DUP-06 → A-025 · concluída (16/10): a duplicidade nos lances foi descartada (2408 e ações por plano são secundárias); a tag 2417 de Franquias ficou em stand-by para conversar.
  - BR N-02, N-03 (TikTok): na lista viva, faltam o Ads Manager e o Event breakdown.

### R-DUP-05 · Trigger quebrado por mudança no site
- **Sintoma / detecção:** validação tag a tag (P-08): tag ativa no GTM × evento na Data API × hit no Chrome. No TikTok/Meta, "último recebimento há N dias".
- **Causas comuns:** o trigger compara texto exato (seletor CSS, nome de evento, path) e o deploy do site mudou; não existe contrato de dataLayer.
- **Resolução raiz:** contrato de dataLayer (eventos e parâmetros) validado em QA a cada deploy (dev).
- **O que a Monks faz:** seletor sem diferenciar caixa ou por `data-id`, trigger no evento de sucesso (ex.: `lead_form_success`) e não no clique, path com "começa com". Tags sem efeito saem pausadas no mesmo workspace. A Monks entrega também o rascunho do contrato.
- **Pronto quando:** Data API com evento > 0 em 7 dias; conversão > 0 na mídia; no Chrome, o hit com o parâmetro certo.
- **Típico:** F2 · M · R = Martech + dev / A = Head de Martech.
- **Lições:**
  - Antes de declarar quebrado, capture o beacon **na live e no Preview**: 2682 e 2785 eram falso positivo (A-027).
  - Corrigir o trigger de um lead pode duplicá-lo se outra rota já emite o mesmo evento. Na Data API, veja `linkUrl` e a origem antes (N-05).
  - LP com pouco tráfego: "0 conversões" em 4 dias não prova quebra. Informe as visitas/dia junto.
- **Casos:**
  - BR SF-DUP-07 → A-027 · concluída (v599, 22/10): search de 4 para 65,6 mil; parceiros de 0 para 156.

### R-DUP-06 · Outro container, staging ou `debug_mode` na propriedade de produção
- **Sintoma / detecção:** Data API Q05 (hosts que não são de produção). No Chrome, nas LPs: quantos `tid` iguais por página e se há `debug_mode`/`_dbg` nos hits.
- **Causas comuns:** o mesmo Measurement ID em vários containers e ambientes, sem dono; `debug_mode` esquecido numa tag; sem filtro de tráfego de desenvolvimento.
- **Resolução raiz:** um container por página; sem `debug_mode` em produção; staging em outra propriedade ou com o filtro "Developer traffic" e os hosts marcados como internos.
- **O que a Monks faz:** tira o `debug_mode` em workspace e entrega a lista de hosts de staging/dev. Filtro no GA é com o cliente (P-06).
- **Pronto quando:** Chrome sem `debug_mode` nos hits das LPs; Data API com 0 eventos de hosts de staging em 7 dias.
- **Típico:** F2 · M · R = Martech + dev / A = Head de Martech.
- **Lições:**
  - Meça antes de afirmar duplicidade de `page_view`. No BR não duplicava; o problema era o `debug_mode`, que **tira os eventos dos relatórios** (metade dos page_view e todos os leads das LPs).
- **Casos:**
  - BR SF-DUP-08 → A-029 · workspace 63 (GTM-PS879FDQ) aguardando publicação; lista de 60 hosts entregue.

## FIN · Financeiro e licenciamento

### R-FIN-01 · Evento genérico consumindo a cota 360
- **Sintoma / detecção:** Data API Q01/Q03: fatia de cada `eventName` nos eventos faturáveis. Catálogo dos parâmetros do evento (cardinalidade, redundância, `debug` em produção).
- **Causas comuns:** o SDK registra todo toque como `click` genérico, sem agregação, e nenhuma subpropriedade filtra.
- **Resolução raiz:** o time do app remove o evento ou o troca por eventos nomeados de interações relevantes.
- **O que a Monks faz:** catálogo dos parâmetros (xlsx) e recomendação. O contorno é o filtro de evento na subpropriedade, que o cliente aplica.
- **Pronto quando:** Data API: o evento ≤ 5% dos faturáveis em 7 dias; Admin → Uso mostra a queda.
- **Típico:** F2 · M · R = Martech + app / A = Head de Martech.
- **Lições:**
  - **Pergunte o uso antes de propor o filtro.** No BR o cliente usa o `click` para uma métrica, e a ação parou esperando o OK (A-012). O catálogo de parâmetros vira o anexo da decisão.
- **Casos:**
  - BR SF-FIN-01 → A-012 · em andamento: catálogo entregue (19 a 25/10); falta o Martech confirmar a métrica dependente.

### R-FIN-02 · Subpropriedade com filtro errado
- **Sintoma / detecção:** Admin API `subpropertyEventFilters` e a série mensal do `uso_ativos`. Volume da subpropriedade ≈ volume da principal → copia tudo (cobrança dupla). Volume 0 com o canal ativo → "pausada" com filtro que nunca casa, e o canal cai só na principal.
- **Causas comuns:** filtro criado sem conferir o volume; desligamento feito trocando o valor do filtro, sem destino novo nem aviso aos usuários.
- **Resolução raiz:** decidir o destino do canal (restaurar o filtro ou mandar para a propriedade própria); arquivar a subpropriedade sem uso; conferir a fatura 360 do período. Para subpropriedade nova, conferir volume esperado × recebido em 48 h.
- **O que a Monks faz:** a lista de desativação e o checklist de criação. A mudança no GA é do cliente (P-06).
- **Pronto quando:** Admin API sem filtro fictício; Data API com o canal no destino escolhido; fatura conferida e registrada.
- **Típico:** F2 · P · R = Martech + Compras / A = Head de Martech.
- **Lições:**
  - O cliente pode preferir não ter subpropriedade (Smart System no BR ficou só na principal). Ofereça essa opção.
- **Casos:**
  - BR SF-FIN-03 → A-017 · fora do plano (14/10); a 492149744 entrou na lista de desativação pela A-018 (26/10).
  - BR SF-DUP-05 → A-006 · fora do plano (totem desconsiderado em 14/10).

### R-FIN-03 · sGTM: versão sem nome, logging e custo não medidos
- **Sintoma / detecção:** export do sGTM (nome da versão live, `logType` das tags); billing do Cloud Run.
- **Causas comuns:** publicação sem convenção de nome; logging no padrão do serviço.
- **Resolução raiz:** medir o Cloud Logging no billing e, se for relevante, criar filtro de exclusão dos logs de requisição; nomear versões com o ID da ação.
- **O que a Monks faz:** lê o código do template antes de recomendar mudar `logType`; pede o billing.
- **Pronto quando:** billing conferido; filtro aplicado se fizer sentido; próxima versão nomeada.
- **Típico:** F2 · P · R = Infra / A = Head de Martech.
- **Lições:**
  - `logType=debug` dos templates só grava log em Preview: não gera custo em produção e não exige mudança (A-013).
  - Logs do Cloud Run: pedir **uma vez, no fim das 3 fases** (D-09).
- **Casos:**
  - BR SF-FIN-02 → A-013 · concluída (16/10): sem mudança no GTM; billing em espera.

## PII · Dado pessoal e credenciais

### R-PII-01 · Dado pessoal em parâmetro de tag
- **Sintoma / detecção:** Data API Q19: "@" e padrão de documento/telefone do país em `customEvent:*` e `pageLocation`. Export do GTM: parâmetros com variável de PII sem hash (`inventario_tags.json`). Chrome: payload do hit depois do lead e da compra, com os dados fictícios digitados.
- **Causas comuns:** variáveis de e-mail, telefone e nome mandadas como parâmetro comum; captura genérica de texto de botão (o botão mostra o e-mail do cliente logado); dimensão customizada registrada para PII.
- **Resolução raiz:** tirar os parâmetros da tag; arquivar as dimensões; ligar a redaction de e-mail e de query params no stream; pedir data deletion do histórico. Os três últimos ficam com o cliente.
- **O que a Monks faz:** remove os parâmetros em workspace. Na captura genérica, filtra na variável os valores com "@" ou com dígitos de documento. Lista para o cliente: dimensões a arquivar, redaction e deletion request.
- **Pronto quando:** Data API com 0 ocorrências em 7 dias; hit no Chrome sem o campo; tag sem o parâmetro na versão live.
- **Típico:** F1 · P · R = Martech / A = Head de Martech · +1 nível de criticidade.
- **Lições:**
  - A data redaction do stream não cobre parâmetro customizado arbitrário.
  - Tag que alimenta o sGTM para CAPI/Events API precisa do e-mail/telefone: não remova. Confirme a rota no sGTM e se há hash (2684/2698 no BR ficaram como estavam).
  - Depois de corrigir uma tag, rode a Q19 em **todos** os parâmetros: no BR apareceu outra rota pelo `cta_button` (N-07).
  - Telefone: procure com o DDI do país; documento: CPF (BR), CURP/RFC (MX).
- **Casos:**
  - BR SF-PII-04 → A-002 · concluída (v598, 20/10): 0 de 19 hits pós-lead com PII na live.
  - BR SF-PII-05 (tag 2578) → A-026 · parte GTM concluída (v598).
  - BR N-07 (`cta_button`): na lista viva.

### R-PII-02 · Dado pessoal gravado no navegador
- **Sintoma / detecção:** Chrome → Application (localStorage, sessionStorage, cookies) depois do lead e da compra; console com `ReferenceError`.
- **Causas comuns:** tag HTML que grava antes de enviar e quebra no envio (o `try/catch` engole o erro); SDK de terceiro usando o e-mail como identificador.
- **Resolução raiz:** pausar a tag quebrada (se o fluxo for necessário, reescrever pelo servidor); SDK com identificador não pessoal ou hash.
- **O que a Monks faz:** pausa em workspace; script de limpeza da chave como contorno.
- **Pronto quando:** Chrome com o funil completo: sem a chave no storage e sem `ReferenceError`.
- **Típico:** F1 · P · R = dev do site / A = Head de Martech · +1 nível.
- **Lições:**
  - SDK instalado fora do GTM pode estar fora do escopo do cliente: confirme o dono antes de planejar (Indigitall descartada no BR).
- **Casos:**
  - BR SF-PII-01 → A-003 · concluída (v598): chave `null`, 0 envios; o código saiu do `gtm.js`.
  - BR SF-PII-02 → A-004 · fora do escopo (23/10).

### R-PII-03 · Dado pessoal para terceiro ou exposto pelo código do site
- **Sintoma / detecção:** Chrome: corpo dos POSTs do funil filtrado pelos valores fictícios digitados (APM, monitoramento, chat); console (`console.log` de dado); query string das APIs do próprio site.
- **Causas comuns:** dataLayer com e-mail/telefone em claro (ex.: `add_person_info`) que o agente da ferramenta captura como atributo; log de debug esquecido; documento passado na URL.
- **Resolução raiz:** dev tira a PII do push ou manda só hash SHA-256; documento no corpo (POST), não na URL; sem `console.log` de dado.
- **O que a Monks faz:** a evidência (endpoint, campo, contagem) e o pedido ao dev (P-09). Contorno imediato sem deploy: regra de ofuscação na própria ferramenta.
- **Pronto quando:** mesmo roteiro do Chrome: 0 POSTs com os campos; console limpo; URL sem documento.
- **Típico:** F1 · P · R = dev do site / A = Head de Martech · +1 nível.
- **Casos:**
  - BR SF-PII-05 (New Relic) → A-026 · com o dev (ofuscação e `add_person_info`).
  - BR N-08 (data de nascimento no console, CPF na URL): na lista viva.

### R-PII-04 · Consentimento
- **Sintoma / detecção:** Chrome em janela anônima: contar requests de mídia antes de qualquer escolha e depois de "rejeitar"; parâmetros `gcs`/`gcd` nos hits.
- **Causas comuns:** banner implícito ("ao continuar navegando"), sem CMP com bloqueio prévio, sem Consent Mode v2.
- **Resolução raiz:** decisão jurídica do modelo; CMP com "rejeitar" no 1º nível; Consent Mode v2 (4 sinais) bloqueando mídia até o aceite.
- **O que a Monks faz:** diagnóstico e recomendação. A escolha é do jurídico.
- **Pronto quando:** com "rejeitar", 0 requests de mídia antes do aceite e `gcs`/`gcd` refletindo a escolha.
- **Típico:** F1 (iniciar/decidir) · M · R = dev + Martech / A = DPO/Jurídico.
- **Lições:**
  - Costuma parar em decisão do cliente: entregue a recomendação e siga (P-07).
  - Cite a lei e o regulador do país (BR: LGPD/ANPD; MX: `04-lei-dados-pessoais-mexico.md`) como teto, nunca como previsão.
- **Casos:**
  - BR SF-PII-03 → A-005 · em espera (decisão do jurídico).

### R-PII-05 · Credencial em texto aberto no sGTM
- **Sintoma / detecção:** export do sGTM: `tokens.json` (só a tag e o nome do parâmetro, **nunca o valor**).
- **Causas comuns:** access token da Meta CAPI/TikTok Events API colado direto no campo da tag.
- **Resolução raiz:** gerar token novo no Events Manager, revogar o antigo, guardar em variável de acesso restrito; fazer junto com a remoção de acessos e antes de excluir sGTM antigo.
- **O que a Monks faz:** explica o risco e recomenda. A rotação é do cliente.
- **Pronto quando:** tokens antigos revogados; eventos chegando com o token novo em 24 h.
- **Típico:** F1 · P · R = Martech / A = Head de Martech · +1 nível.
- **Casos:**
  - BR SF-GOV-10 → A-001 · em espera (rotação depois da próxima rodada de remoção de acessos).

## PERF · Performance

### R-PERF-01 · Peso de tags piora INP/LCP
- **Sintoma / detecção:** Lighthouse mobile e trace do Chrome (Third parties, tempo na thread principal); quantos destinos Google Ads carregam por página; CrUX p75.
- **Causas comuns:** acúmulo de destinos de mídia, pares pausada/ativa, Clarity e pixels no load de todas as páginas.
- **Resolução raiz:** consolidar destinos, remover pausadas e órfãs (R-GOV-01), adiar Clarity e pixels para depois da interação, rever a necessidade de cada pixel por página.
- **O que a Monks faz:** planilha com todas as tags, triggers e variáveis, cada uma com classe e motivo, separando "remover já" de "precisa decisão"; aba de IDs Ads por conta. Depois da decisão do cliente, remove em workspace e mede o INP de novo.
- **Pronto quando:** trace mobile com INP ≤ 200 ms e terceiros < 500 ms na thread principal; CrUX confirma em 28 dias.
- **Típico:** F3 · G · R = Martech + dev / A = Head de Martech.
- **Lições:**
  - Fica parado na decisão do cliente sobre o que manter. Mande a planilha cedo.
- **Casos:**
  - BR SF-PERF-01 → A-014 · aguardando decisão: 75 tags para o cliente marcar.

### R-PERF-02 · sGTM fora do domínio próprio ou fora da região
- **Sintoma / detecção:** export (`server_container_url` das tags web, URL declarada no container server); Chrome (destino dos hits e `Set-Cookie` first-party); região do Cloud Run.
- **Causas comuns:** sGTM publicado no `*.run.app` padrão; região dos EUA por padrão.
- **Resolução raiz:** subdomínio próprio servindo o sGTM; Cloud Run na região do país (Infra).
- **O que a Monks faz:** confere se o container server já declara um subdomínio e se ele responde 200. Se sim, troca só a variável do endereço em workspace (P-02).
- **Pronto quando:** hits do sGTM para `*.<domínio do cliente>` e cookies FPID/FPLC/_fbp aceitos no domínio.
- **Típico:** F3 · P (troca de variável) / G (infra) · R = Infra + Martech / A = Head de Martech.
- **Lições:**
  - Com o Google tag gateway, o service worker bloqueia envio cross-origin ao `run.app` em parte das sessões. Antes de declarar perda, confira no Events Manager (TikTok/Meta) se o volume chega pelo servidor (SF-FIN-04 foi rebaixado para Baixa assim).
- **Casos:**
  - BR SF-PERF-02 → A-015 · workspace 777 aguardando publicação (sfbrasil já respondia); região com Infra.
  - BR SF-FIN-04 → A-024 · concluída (TikTok ~100% do GA4); logs do Cloud Run no fim.

## GOV · Governança

### R-GOV-01 · Higiene do container
- **Sintoma / detecção:** export: `higiene.json` (pausadas, triggers sem tag ativa, variáveis sem referência, tags sem pasta) e validação tag a tag (tags ativas sem efeito: página removida, SDK que não carrega, trigger quebrado).
- **Causas comuns:** campanhas, LPs e fornecedores saem e as tags ficam; não há rotina de revisão nem dono por tag.
- **Resolução raiz:** limpeza única, convenção de nome com dono e validade, ritual trimestral (R-GOV-09).
- **O que a Monks faz:** remove em workspace NÃO PUBLICAR guardando o JSON de cada item (P-03), com Preview do funil inteiro comparando as tags por etapa antes e depois.
- **Pronto quando:** Tag Manager API: 0 itens da lista na live; funil sem regressão; console sem `ReferenceError` de tag.
- **Típico:** F3 · M · R = Martech + Monks / A = Head de Martech.
- **Lições:**
  - **Setup/teardown tag é referenciada pelo nome.** Renomear ou remover a tag de setup sem atualizar a dependente quebra o envio, e a API recusa com 400 "unknown setup tag" (N-06). Mapeie as dependências antes.
  - Renomeie as [TESTE] antes de limpar (R-GOV-02), senão a limpeza derruba o envio principal.
  - O que depende de decisão do cliente vai para uma lista separada (R-PERF-01) e não trava o resto.
- **Casos:**
  - BR SF-GOV-11 → A-028 · workspace 777 aguardando publicação: 69 tags, 30 triggers e 13 variáveis.

### R-GOV-02 · Tags "[TESTE]"/"UPD" em produção ou propriedade de teste recebendo produção
- **Sintoma / detecção:** export (nomes com [TESTE], UPD, OLD e se disparam); Chrome (`tid` de propriedade de teste no funil).
- **Causas comuns:** o teste virou produção sem renomear, e a versão antiga foi pausada no lugar.
- **Resolução raiz:** renomear com a convenção, pôr nas pastas certas e registrar no changelog; as originais pausadas viram [OLD]; teste com data de fim.
- **O que a Monks faz:** só nome, pasta e nota em workspace (disparo conferido em Preview).
- **Pronto quando:** Tag Manager API: 0 tags ativas com [TESTE]; Chrome: 0 hits para a propriedade de teste.
- **Típico:** F2 · P · R = Martech / A = Head de Martech.
- **Casos:**
  - BR SF-GOV-12 → A-030 · concluída (v599): 0 [TESTE] na live; as 3 UPD seguem até a A-008.
  - BR SF-GOV-02 → A-008 · fora do plano (14/10).

### R-GOV-03 · Key events sem significado de negócio
- **Sintoma / detecção:** Admin API `keyEvents` + Data API Q04 (fatia de cada key event).
- **Causas comuns:** eventos marcados ao longo dos anos sem revisão.
- **Resolução raiz:** revisar com Mídia (manter só ações de valor) e conferir as conversões importadas em cada conta Ads.
- **O que a Monks faz:** a lista proposta. A mudança no GA é do cliente.
- **Pronto quando:** `keyEvents` = lista aprovada; 0 `screen_view`/`page_view` como key event.
- **Típico:** F2 · P · R = Martech + Mídia / A = Head de Mídia.
- **Casos:**
  - BR SF-GOV-03 → A-007 · adiada pelo cliente (14/10).

### R-GOV-04 · Acessos sem uso, Admins externos, acesso via grupo GMP
- **Sintoma / detecção:** `ga_users.py`/`ga_users_analise.py`, `gtm_dump.py --users`, `gmp_users.py`/`gmp_mapa_acessos.py`, Data Access Report × accessBindings (quem lê sem permissão na conta = grupo da org GMP).
- **Causas comuns:** acessos dados por projeto ou agência e nunca revistos; grupos da organização GMP fora do inventário.
- **Resolução raiz:** o cliente valida a lista, a remoção é feita em lote, Admins externos ficam com prazo, e a revisão passa a ser trimestral (GA, GTM e grupos GMP).
- **O que a Monks faz:** planilha com uma linha por usuário (onde está o acesso e onde remover), cruzada com a lista de agências ativas do cliente.
- **Pronto quando:** 0 usuários diretos sem uso há mais de 365 dias; Admins externos só com prazo; toda identidade com uso em 90 dias tem permissão na conta ou está num grupo inventariado.
- **Típico:** F1 · P · R = Martech + Monks / A = Head de Martech.
- **Lições:**
  - Peça leitura da organização GMP no kickoff: sem ela o acesso por grupo fica invisível.
  - Antes de remover, confira se a pessoa alimenta algum conector (R-GOV-05).
  - A remoção de uma agência que saiu atravessa países: no BR foram 172 permissões em 10 países.
- **Casos:**
  - BR SF-GOV-07 → A-020 · concluída: 60 identidades da WPP removidas, verificação pós-remoção sem acesso.
  - BR SF-GOV-08 → A-021 · concluída: grupos da org GMP mapeados.

### R-GOV-05 · Painéis e conectores com credencial pessoal
- **Sintoma / detecção:** Data Access Report por app e por usuário (fatia de leituras por credencial).
- **Causas comuns:** o Looker Studio e o Supermetrics usam por padrão a credencial do autor.
- **Resolução raiz:** inventariar os painéis críticos e migrar as fontes para conta de serviço; manter uma lista de apps de terceiros aprovados.
- **Pronto quando:** ≥ 80% das leituras via conector por conta de serviço; nenhuma credencial pessoal com mais de 10%.
- **Típico:** F2 · M · R = BI + Martech / A = Head de Martech.
- **Casos:**
  - BR SF-GOV-09 → A-022 · sem andamento registrado.

### R-GOV-06 · Ativos mortos ou sem dono
- **Sintoma / detecção:** `uso_ativos.py` (volume na Data API + `gtm.js` respondendo); Change History e último sinal dos Admins; Cloud Run de sGTM "[DESATIVADO]" ainda respondendo.
- **Causas comuns:** ativos criados por projeto sem processo de encerramento; propriedade "[TESTE]" promovida a produção sem dono formal.
- **Resolução raiz:** lista de desativação validada; exportar o JSON dos containers, tirar os usuários, mover propriedades para a lixeira, excluir o Cloud Run (depois de rotacionar os tokens, R-PII-05); ativo que fica ganha nome definitivo e 2 Admins internos ativos.
- **O que a Monks faz:** **entrega a lista; quem desativa é o cliente** (decisão de 26/10 no BR).
- **Pronto quando:** containers da lista sem versão live nem usuários; propriedades na lixeira; URL do Cloud Run sem resposta.
- **Típico:** F2 · M · R = Martech + Infra / A = Head de Martech.
- **Casos:**
  - BR SF-GOV-10 → A-023 · lista entregue (24 ativos), cliente desativa.
  - BR SF-GOV-06 → A-018 · decisão do cliente: Smart System só na propriedade principal.

### R-GOV-07 · Domínio com a marca levando a terceiro
- **Sintoma / detecção:** `curl -sIL` nos domínios dos containers; whois.
- **Causas comuns:** produto descontinuado sem plano de saída; domínio expirado e registrado por outro.
- **Resolução raiz:** confirmar o titular. Se for do cliente, corrigir o redirecionamento e revisar o acesso ao DNS. Se não for, retirar links e QR codes e avaliar medida de marca. Nos dois casos, pausar ou arquivar o container.
- **O que a Monks faz:** a evidência; pausa as tags em workspace.
- **Pronto quando:** `curl` termina em domínio do cliente (ou não resolve) e o container está sem tag ativa.
- **Típico:** F1 · P · R = TI/Infra / A = Head de TI.
- **Casos:**
  - BR SF-GOV-05 → A-019 · concluída: 5 de 5 tags pausadas; o domínio não é mais da Smart Fit.

### R-GOV-08 · eventNames estranhos
- **Sintoma / detecção:** Data API Q17 (eventNames novos por dia, padrões de injeção SQL/XSS) aberta por plataforma e versão.
- **Causas comuns:** scanner de segurança batendo no endpoint de coleta; SDK de terceiro ou build de teste no app.
- **Resolução raiz:** não há correção no GA4. Alerta de eventName novo, WAF/CDN no site e no gateway (Segurança), consultas parametrizadas em quem lê o BigQuery (BI), pergunta ao time de app sobre o SDK.
- **O que a Monks faz:** a regra no monitor-sentinela (R-GOV-09), validada contra o dia do incidente, e o cenário de risco documentado.
- **Pronto quando:** o alerta dispara no dia do incidente histórico; Segurança registra a varredura.
- **Típico:** F3 · P · R = Martech + Segurança / A = Head de TI.
- **Lições:**
  - O GA4 não executa o payload, mas o export para o BigQuery e os painéis podem (injeção de segunda ordem). O mesmo canal aceita compras e leads falsos.
- **Casos:**
  - BR SF-GOV-13 → A-031 · concluída: só ocorreu em 12/10; alerta no monitor.
  - BR N-10 (SDK de jogo no Android 4.9.25): na lista viva.

### R-GOV-09 · Sem processo de publicação nem monitoramento
- **Sintoma / detecção:** versões sem nome ou sem ID de demanda, testes em produção, sobras (R-GOV-01, R-GOV-02).
- **Resolução raiz:** checklist de publicação (nome da versão com a demanda, Preview no funil, reteste em produção) + monitor diário somente leitura com regras-sentinela (tags [TESTE], PII em tag GA4, eventName novo ou de injeção, e-mail na URL, host novo, `purchase` sem ID).
- **O que a Monks faz:** escreve o checklist e o monitor e roda uma vez. O cliente agenda (Cloud Run job ou GitHub Action) com uma conta de serviço de leitura.
- **Pronto quando:** o monitor roda agendado e as regras de GTM passam; as pendências conhecidas aparecem como alerta.
- **Típico:** F3 · M · R = Martech + Monks / A = Head de Martech.
- **Lições:**
  - Inclua no checklist um marcador de teste (nome "Data Test") que as tags de mídia bloqueiem: o Preview dispara conversões reais (P-04).
- **Casos:**
  - BR SF-GOV-04 → A-016 · concluída: 10 passos e 11 regras (`brasil/achados/2026-10-27_a016-checklist-publicacao-e-monitor.md`).

---

## P · Padrões transversais de execução

- **P-01 · Workspace e publicação.** A Monks prepara em workspace com "NÃO PUBLICAR" no nome, valida em Preview (UI do GTM + Tag Assistant) e **o cliente publica**. A versão leva o ID da ação (ex.: "A-002 / SF-PII-04").
- **P-02 · Contorno sem mexer nas tags.** Quando muitas tags leem a mesma variável, mude a variável e mantenha o nome: fallback de campo (A-010, 25 tags), reconstrução do carrinho (A-011, 14 tags), endereço do servidor (A-015).
- **P-03 · Guardar antes de remover.** Exporte o JSON de cada tag, trigger e variável removida ou alterada em `evidencias/gtm/<id>/<data>/`.
- **P-04 · Preview não isola a mídia.** Lead e compra feitos no Preview geram conversões reais. Use sempre "Data Test", anote o número do pedido e peça ao cliente para desconsiderar (N-11).
- **P-05 · Reteste = o mesmo método que provou.** Data API com janela de 7 dias depois da publicação; app por `appVersion`; Chrome com o mesmo roteiro. Orquestrado com subagents por fonte (Chrome e GTM API nunca em paralelo).
- **P-06 · GA é só leitura.** Filtros, redaction, deletion request, key events, subpropriedades e desativações viram lista para o cliente aplicar.
- **P-07 · Decisão do cliente não trava a fase.** Entregue diagnóstico, recomendação e planilha, e marque como "decisão" ou "espera". Ação desconsiderada fica "fora do plano", com aviso no deck.
- **P-08 · Contraprova antes de afirmar.** Quebra ou duplicidade só com duas fontes (live + Preview, GA4 + Events Manager, GTM + Data API + Chrome).
- **P-09 · Código do site ou do app.** A Monks não corrige: entrega a evidência (arquivo do bundle, push, endpoint, campo, contagem) e o pedido ao dev. Se houver contorno no GTM, aplica e declara o limite.
- **P-10 · Achado novo na execução.** Vai para a lista viva `N-xx` em `achados/` e só é reportado no fim das 3 fases. Se o padrão for novo, já ganha a entrada `R-` aqui.

## Em aberto (padrão sem caso resolvido)

- **Qualidade de match na mídia** (EMQ baixo, `content_id` ausente no TikTok): BR N-01, N-04. Falta saber quais parâmetros de matching cada evento manda e se vêm do sGTM ou do pixel. Respeitar a decisão de consentimento (R-PII-04). Vira `R-DUP-` ou `R-FIN-` quando houver resolução.

## Changelog

- 29/10/2026 · v1: criado a partir do BR (diagnóstico v1.0–v1.5, execução até a v1.7, N-01 a N-11).
