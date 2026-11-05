---
name: auditoria-mensuracao-pais
description: Roda de ponta a ponta uma auditoria de mensuração (GTM Web/Server-Side, GA4 Standard/360, Firebase) de qualquer cliente, país a país, com a metodologia aprovada na Smart Fit Brasil. Na primeira vez com um cliente, pergunta o cliente, os sites e o fluxo de compra, pesquisa a marca (deep research + extração do site) e guarda o design system dele, e guia passo a passo as conexões (gcloud, GTM, GA4, GMP, Chrome). Depois faz o inventário de 100% dos ativos, a coleta pelas APIs, o teste do funil no Chrome, a consolidação dos achados com evidência, impacto e Matriz de Criticidade, e gera o relatório técnico HTML standalone e a apresentação executiva 16:9 em PT-BR com a identidade do cliente e assinatura Monks. Use SEMPRE que pedirem para auditar, diagnosticar, levantar ou "rodar a auditoria" de mensuração de um cliente ou de um país (Smart Fit México, Colômbia, um cliente novo…), retomar uma auditoria em andamento, ou gerar/atualizar o relatório técnico ou o deck executivo, mesmo sem dizer "skill" (ex.: "bora fazer o México", "começa a auditoria do cliente X", "gera o relatório do MX", "continua de onde parou"). Não use para a execução do plano de ação (fases 1–3 com workspaces NÃO PUBLICAR), que é da relatorios-execucao-pais.
---

# Auditoria de mensuração por cliente e país

Esta skill repete, em qualquer cliente e país, o diagnóstico que a Smart Fit aprovou no Brasil em 14/10/2026, depois de recusar três vezes o material antigo. O que destravou a aprovação está na **regra central**: nenhum achado sem **evidência** rastreável e sem **impacto de negócio** quantificado, e só para ativos **ativos**, que têm dados. Cada etapa abaixo existe para produzir isso. Se um atalho deixar um achado sem evidência ou sem impacto, ele derruba a entrega inteira.

Responda e escreva sempre em PT-BR, inclusive a entrega. Se a pasta do cliente tiver `CLAUDE.md`, leia antes de começar; leia também o `<pais>/CLAUDE.md`.

## Modo de operação

- **Ponta a ponta depois da Etapa 0.** A Etapa 0 é conversada: pergunte, guie as conexões, mostre a identidade. Daí em diante vá do inventário aos HTMLs sem pedir confirmação entre etapas. Pare só quando faltar um dado que só o cliente tem e que bloqueia a etapa; mesmo assim, adiante o que não depende dele.
- **Sem acesso não para a auditoria.** Fonte sem acesso (GMP, GTM, Ads…) não interrompe nada: siga com as outras e deixe explícito o que ficou impedido, no estado, no relatório (`DEPENDENCIAS`, `A_VALIDAR`, `COBERTURA`) e no resumo final. Tabela em `references/conexoes.md` § 7.
- **Somente leitura.** Nunca publique nem edite container, workspace ou propriedade do cliente. Nada de `create`/`update`/`publish` na Tag Manager API e nenhuma escrita na Admin API.
- **Compra de teste do jeito que o cliente definiu.** Use sempre o marcador de teste de `cliente.json → teste` (na Smart Fit, nome terminando em "Data Test", também no titular do cartão) e só vá até a confirmação se `teste.ate_confirmacao` for `true`. Na confirmação, recarregue 2 vezes e registre o que cada destino recebeu: só assim se provam a duplicidade da compra e o momento do `add_payment_info`. Sem o marcador, não preencha nada. No auto mode, o classificador pode recusar o checkout ("Real-World Transactions"): não contorne. Peça ao usuário para aprovar a ação ou fazer a compra enquanto o subagent só coleta (hook de rede + dataLayer).
- **Estado retomável.** A auditoria leva horas e pode atravessar sessões. Mantenha `<pais>/auditoria-estado.md` (modelo em `references/estado.md`) com etapa, conexões, o que ficou impedido, fluxo de compra, coleta (com caminho), hipóteses, bloqueios e decisões. Atualize ao fim de cada etapa. Ao retomar, leia primeiro e continue de onde parou, sem refazer coleta que já está em `evidencias/`.
- **Subagents por fonte.** A thread principal escreve os briefings, consolida e escreve o conteúdo. Os subagents só leem e salvam evidência em `evidencias/<fonte>/<data>/`.
  - **GTM API:** um subagent por vez. A quota é ~0,25 req/s; dois em paralelo estouram.
  - **Chrome:** um subagent por vez. O Chrome do usuário é compartilhado; dois agents de Chrome em paralelo se atropelam.
  - **Data API, Admin API e pesquisa web** podem rodar em paralelo com um dos dois acima.
  - Briefings prontos em `references/subagents.md`.

## Caminhos

- `SKILL_DIR` = pasta desta skill.
- `<cliente>` = pasta do cliente: `cliente.json`, `design-system/<marca>/`, `conhecimento/` e uma pasta por país (`references/cliente-schema.md`). Na Smart Fit é a raiz do projeto `Smart-Fit/`.
- `<pais>` = `<cliente>/<pais>/` (`brasil/`, `mexico/`…). Rode os coletores **de dentro dela** (`cd <pais> && python3 scripts/...`), porque eles gravam em `scripts/../evidencias` e leem `../cliente.json`.
- Coletores canônicos em `SKILL_DIR/scripts/coletores/`; o `iniciar_pais.py` copia-os para `<pais>/scripts/`. Se corrigir um coletor, corrija o canônico e recopie.
- Monks (logo e tokens) em `SKILL_DIR/assets/monks/`: a skill já conhece; não pesquise.

## Etapa 0 · Kickoff (conversada)

### 0.1 Cliente e país
Descubra se o cliente já existe: procure `cliente.json` na pasta atual e nas pastas-mãe.
- **Cliente novo** (sem `cliente.json`): pergunte qual é o cliente (nome como deve aparecer, gênero para a concordância: "a Smart Fit", "o Itaú"), o país a auditar e **os sites que a pessoa tiver** (o principal e os de cada país). Pergunte também onde criar a pasta do cliente. Crie `<cliente>/cliente.json` (`references/cliente-schema.md`) com nome, gênero, slug, prefixo dos achados (2–3 letras, estável para sempre), marca e sites.
- **Cliente existente:** confirme o país e os sites dele; acrescente em `sites` o que for novo.

### 0.2 Identidade do cliente (só na primeira vez)
Se `cliente.json → marca` não tem `marca.json`, siga `references/identidade-cliente.md`: pergunte por brand book ou kit de marca, rode o **deep research** sobre a marca em paralelo com a extração do site (tokens de produção, fontes, logo SVG, prints), salve em `<cliente>/design-system/<slug>/` no mesmo formato da Smart Fit e escreva o `marca.json`. Mostre ao usuário a capa e um slide gerados com a identidade e ajuste até ele aprovar. A Monks já está pronta em `assets/monks/`.

### 0.3 Fluxo de compra (pergunte, não suponha)
Pergunte e registre (`references/conexoes.md` § 6): URL de entrada e etapas até a compra (ou se há vídeo do funil), o que é vendido, o documento pedido no cadastro, e **como o cliente quer o teste** (marcador reconhecido pelo site, cartão, se pode ir até a confirmação, quem cancela pedidos e leads de teste). Funil no `<pais>/CLAUDE.md`; regra de teste em `cliente.json → teste`. Com vídeo, gere as grades com ffmpeg (`-vf "fps=1/12,scale=480:-1"`, depois `tile=4x4`) e mapeie os passos antes do teste.

### 0.4 Conexões guiadas
Siga `references/conexoes.md` § 1–5, na ordem: gcloud e conta → ADC com escopos → projeto de cota e APIs → acesso aos ativos (`gtm_dump.py --list`, `ga_dump.py --list`, `gmp_users.py`) → Chrome. Em cada falha, diga ao usuário exatamente o que fazer (comando com `!`, tela ou mensagem pronta para o cliente pedir acesso), espere e teste de novo. Grave `conta_auditoria`, `projeto_cota` e `gmp_org` no `cliente.json`. Fonte que continuar sem acesso: registre o que fica impedido (§ 7) e siga.

### 0.5 País e conta principal
1. `python3 SKILL_DIR/scripts/iniciar_pais.py <pais> --cc <xx> --nome "<País>"`: esqueleto, coletores, `PEDIDO.md` (o do cliente, o de um país irmão ou o modelo da skill: confirme com o usuário qual vale) e `auditoria-estado.md`.
2. Crie ou complete o `<pais>/CLAUDE.md`: domínio, funil, contato do cliente, data do alinhamento, ativos conhecidos.
3. Filtre as contas do país nas listas de GTM e GA (nome, domínio).
4. Escolha a **conta principal**: o container web do site principal, o sGTM que ele alimenta e a propriedade GA4 que recebe o `purchase` do site. Registre no estado com a justificativa (volume, domínio, links do Ads). O combinado com o cliente é validar o formato nela e depois escalar.

## Etapa 1 · Inventário de 100% e uso real

O pedido é de 100% dos ativos, mas a **análise** é só dos ativos ativos. O inventário separa um do outro com dado, não com nome.

1. Para cada propriedade do país: `python3 scripts/ga_dump.py <prop> --users` (config, serviceLevel 360/Standard, streams, links, subproperty filters, retenção, accessBindings).
2. `python3 scripts/uso_ativos.py ga <prop> <prop> ...` e `python3 scripts/uso_ativos.py gtm <accountId>`: série mensal de eventos e sinais do container (versão live, última edição, tags ativas, `gtm.js` respondendo).
3. Classifique cada ativo em `evidencias/_uso_ativos/<data>/classificacao.json`: `{id: [status, recomendação, justificativa com número]}`. Status: Ativa · Residual · Parada · Teste recebendo produção · Duplicada. A justificativa sempre cita volume e data.
4. Acessos: `python3 scripts/ga_users.py <accountId>` → `python3 scripts/ga_users_analise.py evidencias/ga4/_acessos/<data>/<accountId>` (o ponto focal do cliente no país vai em `cliente.json → acessos_protegidos`); `python3 scripts/gtm_dump.py <GTM-ID> --users` → `gtm_users_analise.py`; com `gmp_org`, `gmp_users.py` + `gmp_mapa_acessos.py`. Sem GMP: registre que os acessos por grupo ficam invisíveis.
5. Atualize o estado.

## Etapa 2 · Diagnóstico da conta principal

Rode as frentes abaixo. O detalhe de cada uma (o que procurar, como provar, o que vira achado) está em `references/investigacao.md`. As **hipóteses** vêm do `references/catalogo-resolucoes.md` (um padrão `R-` por tipo de problema, com a detecção) e da tabela de achados do BR em `investigacao.md` § 8: teste cada uma e registre como confirmada (vira achado), descartada (vira "verificado e OK"), sem dado (vira "a validar") ou impedida (sem acesso).

1. **GTM (subagent GTM):** `python3 scripts/gtm_dump.py <GTM-ID>` para o web principal e o sGTM; depois a leitura do export (tags, triggers, variáveis, HTML customizado, terceiros, tokens, IDs de mídia, sobras) e a **prontidão para a experiência otimizada de tagging** (Tags do Google, destinos, IDs fixos, loaders por ID; `investigacao.md` § 1, padrão R-GOV-10).
2. **GA4 Data API (pode ir em paralelo):** `python3 scripts/dataapi_pacote.py <prop> --pais <cc>`. São 18 consultas fixas mais as dimensões customizadas com nome de dado pessoal, e um `resumo.json` com os números-chave. Para um país novo, acrescente o regex de documento e telefone em `PII_PAIS`. Consultas extras seguem o mesmo formato: corpo da requisição + resposta + `extracted_at`.
3. **Chrome (subagent Chrome):** funil do site principal com a regra de teste do cliente, mais a home e a página de produto para performance. Briefing em `references/subagents.md`.
4. **Validação de disparo tag a tag:** cruze tags ativas do GTM × eventos com volume na Data API × hits vistos no Chrome. Toda tag ativa recebe um status (dispara · não dispara onde deveria · sem volume · não testável · destino ≠ principal) com a prova.
5. Registre tudo numa nota datada `<pais>/achados/AAAA-MM-DD_achados-<conta>.md`: hipótese → dado → arquivo de evidência → conclusão. Essa nota é a fonte do conteúdo.

## Etapa 3 · Consolidação

Transforme a nota de achados em `<pais>/entregas/_fonte/conteudo.json`. O esquema está em `references/conteudo-schema.md`, e o exemplo real é `SKILL_DIR/assets/exemplo-conteudo-br.json`, o conteúdo do BR aprovado. Use o exemplo como régua de qualidade e profundidade, não como texto a copiar. Método completo em `references/metodo/01-formato-auditoria.md`.

- **Achado = cartão** `<prefixo>-<PILAR>-nn` (prefixo do `cliente.json`; pilares FIN, DUP, PII, PERF, GOV) com condição, observado × esperado, critério com fonte pública, causa, efeito no negócio, impacto (fórmula + resultado + premissa), evidências `E-nn`, reprodução, recomendação raiz/contorno, "pronto quando" e ação.
- **Criticidade** pela rubrica: I = maior impacto entre os 3 pilares, P = abrangência, nível base pela matriz I×P e **+1 nível** por modificador declarado (dado pessoal/credencial; dado que alimenta lance). Confiança Baixa e hipóteses impedidas por falta de acesso não entram na matriz: vão para `A_VALIDAR`.
- **Impacto** com as fórmulas de `references/metodo/02-quantificar-impacto.md`: sempre faixa e premissa, na moeda do país. Referência de mercado nunca vira previsão para o cliente. Para dado pessoal, cite a lei e o regulador do país (pesquise e registre em `<cliente>/conhecimento/` antes de citar teto de sanção) e diga com honestidade se há caso de multa por cookies/pixels.
- **Plano** `A-nnn` em Now/Next/Later com um único A, esforço P/M/G e critério de pronto escrito como teste (a mesma consulta ou o mesmo roteiro que provou o achado). Se o container não está na experiência otimizada, inclua a migração para destinos como ação F3 (Later), em lotes, com o Passo 0 de decisões do cliente (R-GOV-10).
- **Catálogo de resoluções** (`references/catalogo-resolucoes.md`): para cada achado confirmado, ache o padrão `R-<PILAR>-nn` e use-o para escrever `rec_raiz`, `rec_contorno`, `pronto` e a ação; leia as **Lições** antes de recomendar. Ao fechar a consolidação, acrescente em **Casos** uma linha por achado (`<CLIENTE> <PAÍS> <achado> → A-nnn · planejada`). Achado sem padrão ganha entrada nova no fim do pilar (regra no topo do catálogo).
- **Dependências:** cada acesso que faltou vira item de `DEPENDENCIAS` dizendo o que ele destrava, e a `COBERTURA` mostra "não verificado (sem acesso a X)".
- **Deck:** marque como `vitrine` os achados que contam a história (em geral as Altas de maior impacto em dinheiro, dado pessoal e cota), com `deck.oque/quanto/fazer` em linguagem de negócio e um gráfico quando houver série ou proporção. Os títulos são **asserções com número** ("59% dos purchase vêm do totem, sem transaction_id"), não rótulos ("Purchase do totem").
- **Segredos e dado pessoal:** token aparece só como "token em texto aberto na tag X". Nenhum e-mail, documento ou telefone real em texto; dados do teste só os fictícios.

## Etapa 4 · Entregáveis

1. `python3 SKILL_DIR/scripts/motor/validar.py <pais>`: zere os ERROS (rastreabilidade, rubrica, segredos) e leia os avisos.
2. `python3 SKILL_DIR/scripts/motor/build.py <pais>`: gera `relatorio-tecnico-<slug>-<cc>.html` (standalone, com todas as evidências embutidas e tokens mascarados) e `apresentacao-executiva-<slug>-<cc>.html`, mais as cópias `-design` com a identidade do cliente (`marca.json`) e a assinatura Monks. O que vai ao cliente é sempre a `-design`.
3. Confira visualmente com o Chrome **headless** (não o do usuário): capa, resposta em uma página, matriz, 2 vitrines, plano e um cartão do relatório:
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --user-data-dir=<scratchpad>/chrome --window-size=1920,1080 --virtual-time-budget=4000 --screenshot=<scratchpad>/s_N.png "file://<deck>-design.html#/N"`.
   Texto que estoura o slide, gráfico vazio ou `[a preencher]` voltam para o conteúdo.
4. QA final:
   - lendo só os títulos dos slides, a história fecha;
   - todo cartão tem evidência `E-nn` com data, impacto com fórmula e premissa, e ação com critério de pronto;
   - nenhum token, e-mail ou documento real; dados da compra de teste mascarados;
   - referência de mercado não aparece como previsão para o cliente;
   - confiança Baixa e impedidos fora da matriz executiva (vão como "a validar");
   - a cobertura mostra também o que está OK e o que não foi verificado por falta de acesso.
5. Quando estiver pronto para enviar: `build.py <pais> --entrega v1.0` congela a pasta `entregas/entrega-cliente-<data>_v1.0/`. O envio ao cliente é do usuário.
6. Feche o estado e escreva o resumo para o usuário: o que foi coletado, quantos achados por criticidade, os 3 maiores impactos em dinheiro, o que ficou "a validar", **as fontes sem acesso e as ações relevantes que elas impediram**, os bloqueios e os caminhos dos dois HTMLs.

## Depois da aprovação do formato

Na rodada seguinte, repita as Etapas 2 e 3 para os demais ativos **ativos** do país, acrescentando achados e evidências ao mesmo `conteudo.json` (IDs novos no fim, sem renumerar) e subindo `META.versao` e `CHANGELOG`. Próximo país do mesmo cliente: Etapa 0.3 a 0.5 (identidade e conexões já existem; confira se o país está nas mesmas contas e na mesma org GMP).
