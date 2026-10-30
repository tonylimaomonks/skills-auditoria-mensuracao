# Investigação da conta principal: o que procurar, como provar

Cada frente lista o que olhar e a prova que fecha o ponto. "Prova" = arquivo em `evidencias/` que outra pessoa consegue reabrir e refazer. Os IDs `SF-…` entre parênteses são os achados do Brasil que nasceram daquela checagem; use-os como hipóteses (tabela no fim).

## Sumário
1. GTM web (export da Tag Manager API)
2. sGTM
3. GA4 Admin API
4. GA4 Data API (pacote padrão + consultas extras)
5. Chrome: funil, dado pessoal, consentimento, performance
6. Validação de disparo tag a tag
7. Inventário de uso e acessos
8. Catálogo de hipóteses (achados do BR)

## 1. GTM web
Fonte: `evidencias/gtm/<GTM-ID>/<data>/live_version.json` e `workspace_*/`.
- Contagens: tags (ativas/pausadas), triggers, variáveis, templates, pastas; tags por tipo (`gaawe`, `googtag`, `awct`, `html`, templates de terceiros). Viram a tabela de inventário (seção 5 do relatório).
- **Higiene (GOV-04, GOV-11):** tags pausadas; triggers sem nenhuma tag ativa; variáveis sem referência (procurar `{{Nome}}` em todo o JSON); tags sem pasta; nomes com `[TESTE]`, `teste`, `UPD`, `old`.
- **Terceiros e HTML customizado:** liste cada tag `html` com o domínio que carrega (`src=`/`fetch(`/`XMLHttpRequest`). Script de terceiro sem dono conhecido vira pergunta; script que lê formulário vira suspeita de dado pessoal.
- **Dado pessoal em parâmetro de tag (PII-04, PII-05):** parâmetros de evento GA4 ou de mídia com chave `email`, `phone`, `cpf`/`curp`/`rfc`, `nome`, `name`, `address`, ou valor `{{...email...}}` sem hash. `user_data` com hash para CAPI é o esperado e entra no "verificado OK".
- **IDs de mídia:** quantos IDs de Google Ads (`awct`, `gclidw`, `AW-`), pixels Meta/TikTok, e se o mesmo ID dispara em mais de uma tag no mesmo evento (DUP-04, DUP-06).
- **Conversões:** tags no trigger de compra/lead; se há duas tags enviando o mesmo evento para o mesmo destino (duplicidade).
- **Tokens (GOV-10):** parâmetros `accessToken`, `apiKey`, `secret` em texto aberto. No conteúdo, só "token em texto aberto na tag X".
- **Server container URL:** se as tags GA4 apontam para `*.run.app` (PERF-02) ou para subdomínio próprio.

## 2. sGTM
Fonte: export do container server.
- Clients configurados; tags e para onde encaminham (GA4, Meta CAPI, TikTok Events API); se o encaminhamento GA4 duplica o envio client-side.
- Nome e data da versão live (versão "teste" em produção, FIN-02); `logType=debug`.
- Domínio e região (`*.run.app` us-central1 × subdomínio first-party na região do país): impacto em ITP/Safari (PERF-02) e latência.
- Tokens em texto aberto (GOV-10).
- Custo: sem billing do cliente, o custo é faixa de referência; peça o billing como dependência.

## 3. GA4 Admin API
Fonte: `evidencias/ga4/<prop>/<data>/`.
- `property.json`: serviceLevel (360/Standard), fuso, moeda, criação.
- `dataStreams.json`: streams e quais têm dados (cruzar com Q02); stream de app sem Firebase link.
- `keyEvents.json` × Q04: key event que não é conversão de negócio (GOV-03).
- `googleAdsLinks.json`/`bigQueryLinks.json`/`firebaseLinks.json`: o que alimenta mídia e o que exporta.
- `subpropertyEventFilters.json` (360): subpropriedade que copia a principal inteira (FIN-03) ou filtro "pausado" com valor fictício (DUP-05).
- Retenção, redaction de e-mail/query params (se o redaction estiver desligado e houver e-mail em URL, o achado sobe).

## 4. GA4 Data API
`python3 scripts/dataapi_pacote.py <prop> --pais <cc>` gera Q01–Q19 e o `resumo.json`:
- **Cota 360 (FIN-01):** Q01/Q03, evento genérico com fatia grande dos faturáveis (ex.: `click`, `screen_view`) e sem uso em público, key event ou relatório.
- **Compra (DUP-01/02/03):** Q07 dá transações únicas, duplicadas (por plataforma) e sem ID; Q06/Q08/Q09 localizam o host e a página. `resumo.json → purchase` traz receita verificável e o waterfall pronto (reportada → duplicata → sem ID → verificável).
- **Hosts (DUP-08, GOV-02):** Q05, staging/dev/teste/domínio de terceiro escrevendo na propriedade de produção.
- **Funil (DUP-04, DUP-07):** Q10, etapas ausentes por host e `select_item`/`add_to_cart` acima do esperado.
- **Moeda e itens:** Q11 (moeda do país?) e Q12 (plano + adicionais em `items`?).
- **Dado pessoal (PII-04):** Q13/Q14/Q15/Q19, **só contagem**; nunca extrair valores. Se Q19 achar dimensão com e-mail, confirme no Chrome se vai em texto aberto ou hash.
- **Injeção (GOV-13):** Q17.
- **Safari/ITP:** Q16 dá o peso do impacto do sGTM fora do domínio.
- Consultas extras: mesmo formato (corpo + resposta + `extracted_at`), nome `X01_<assunto>.json` na mesma pasta.

## 5. Chrome
Briefing em `subagents.md`. Saída: `evidencias/chrome/<data>/` com prints, `hits_*.json` (requests filtrados), `datalayer_*.json`, `storage_*.json`, `console_*.json`.
- Eventos de etapa e parâmetros (`transaction_id` só existe na compra; até o pagamento, conferir `items`, `value`, `currency` em `view_item`/`add_to_cart`/`begin_checkout`/`add_payment_info`).
- Duplicidade por etapa e por destino (quantos `collect?` com o mesmo `en=` por página; `page_view` dobrado; mesmo pixel 2×).
- Dado pessoal: URL (`page_location` com e-mail/documento/`id` base64 decodificado), payload GA4 (`ep.*`, `up.*`), sGTM, pixels, `localStorage`/`sessionStorage` (PII-01, PII-02), ferramentas de monitoramento (New Relic, Hotjar, Clarity) com corpo de POST (PII-05).
- Consentimento (PII-03): banner na primeira visita em janela anônima; tags de mídia disparando antes da escolha; parâmetros `gcs`/`gcd` do Consent Mode.
- Performance (PERF-01): Lighthouse mobile na home e na página de produto/unidade; nº de requests, peso total, `gtm.js` (KB), quantos containers/`gtag` por página, CrUX se houver.
- Console: erros de script de terceiro (`ERR_NAME_NOT_RESOLVED`, 404).

## 6. Validação de disparo tag a tag
Para cada tag ativa do web principal: status + prova.
- **dispara:** visto no Chrome (reqid) ou com volume no evento correspondente na Data API.
- **não dispara onde deveria:** trigger/seletor que não existe mais no site (DUP-07).
- **sem volume 30 d:** evento GA4 da tag sem eventos.
- **não testável:** depende de login, app ou fluxo fora do escopo.
- **destino ≠ principal:** manda para outra propriedade/conta (GOV-02, DUP-06).
Saída: `evidencias/gtm/<GTM-ID>/<data>/validacao_tags.json` (uma linha por tag). Vira tabela no relatório (bloco `tabela`) e alimenta GOV-11/DUP-07.

## 7. Inventário de uso e acessos
- Uso: `classificacao.json` (Etapa 1). Ativos parados/residuais viram a lista de desativação (GOV-10); propriedade de teste recebendo produção vira GOV-02.
- Acessos: usuários sem uso há > 6 meses, Admins externos (agência), e-mails pessoais (@gmail), ex-colaboradores; leituras sem permissão na conta (via grupo GMP, GOV-08); painéis com credencial pessoal (GOV-09). Nunca sugerir remover o ponto focal do cliente.

## 8. Catálogo de hipóteses (achados do BR, 13/10/2026)

Ponto de partida concreto. O catálogo vivo, com detecção, resolução e lições por tipo de problema e casos de todos os clientes, é o `catalogo-resolucoes.md`; registre no estado o padrão `R-` de cada hipótese.

| BR | Crit. BR | Hipótese a testar no país novo | Como provar |
|---|---|---|---|
| SF-DUP-01 | Alta | Compras sem `transaction_id` e sem valor vindas de um host secundário (totem, app web) | Q08 + Q09 |
| SF-DUP-02 | Alta | `purchase` repetido no app para o mesmo `transaction_id` | Q07 → duplicadas por plataforma |
| SF-DUP-03 | Alta | Área logada/upgrade com `purchase` sem `transaction_id` | Q08 por host/página |
| SF-DUP-04 | Média | Adicional no checkout duplica `add_to_cart`; parâmetros inconsistentes (idioma, promo, items) | Chrome no upsell |
| SF-DUP-05 | Alta | Subpropriedade de um canal pausada com filtro fictício, canal caindo só na principal | Admin: subpropertyEventFilters + Q05 |
| SF-DUP-06 | Média | Conversão de um negócio (ex.: franquias) recebendo a compra de aluno | Chrome: googleadservices por conta/label |
| SF-DUP-07 | Média | Triggers quebrados por mudança no site (busca, lead, parceiros sem medição) | Validação tag a tag |
| SF-DUP-08 | Média | Outro container/LP e staging escrevendo na propriedade 360 | Q05 + Chrome em LPs |
| SF-FIN-01 | Alta | Evento genérico do app consumindo fatia grande da cota 360 | Q01/Q03 |
| SF-FIN-02 | Baixa | sGTM com versão de teste em produção, logging não medido | Export do sGTM |
| SF-FIN-03 | Média | Subpropriedade que copia a 360 inteira (cobrança dupla) | Admin + série mensal (uso_ativos) |
| SF-FIN-04 | Baixa | Checkout não chega ao sGTM em parte das sessões | Chrome (rede) + Events Manager se houver acesso |
| SF-PII-01 | Alta | Tag quebrada que grava nome/e-mail/telefone no localStorage | Chrome: console + Application |
| SF-PII-02 | Alta | SDK de terceiro guardando e-mail no sessionStorage | Chrome: Application |
| SF-PII-03 | Alta | Banner implícito ("ao continuar navegando") e mídia antes do consentimento | Chrome anônimo |
| SF-PII-04 | Alta | E-mail em texto aberto em parâmetro do GA4 | Q19 + export GTM |
| SF-PII-05 | Alta | Dado pessoal em claro para monitoramento (New Relic etc.) | Chrome: corpo dos POSTs |
| SF-PERF-01 | Alta | Peso de tags piora INP/LCP no celular | Lighthouse mobile + Third parties |
| SF-PERF-02 | Média | sGTM em `*.run.app` fora do domínio (ITP) | Export + Q16 |
| SF-GOV-02 | Média | Propriedade de teste recebendo a jornada de produção | Chrome (tid) + uso_ativos |
| SF-GOV-03 | Alta | Key events que não são conversão de negócio | Q04 + keyEvents.json |
| SF-GOV-04 | Média | Higiene: pausadas, triggers sem uso, tag de teste no purchase | Export GTM |
| SF-GOV-05 | Média | Domínio com a marca levando a site de terceiro | `curl -sIL` nos domínios dos containers |
| SF-GOV-06 | Média | Propriedades criadas sem dono que ficou | Change History |
| SF-GOV-07 | Alta | Acessos sem uso e Admins externos | ga_users_analise |
| SF-GOV-08 | Alta | Leitura via grupo GMP fora do controle da conta | Data Access Report × accessBindings |
| SF-GOV-09 | Média | Painéis dependentes de credencial pessoal | Data Access Report por app |
| SF-GOV-10 | Média | Ativos mortos e sGTM antigo no ar, tokens a rotacionar | uso_ativos + export |
| SF-GOV-11 | Média | 1 em 4 tags ativas sem efeito | Validação tag a tag |
| SF-GOV-12 | Média | Tags "[TESTE]" são o envio principal de produção | Export + Chrome |
| SF-GOV-13 | Baixa | Sondagem de injeção chegando como evento | Q17 |
