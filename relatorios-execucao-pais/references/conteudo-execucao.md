# Formato do conteúdo da execução

Três arquivos por país, todos em `<pais>/entregas/_fonte/`. Caminhos de arquivo dentro deles são **relativos à pasta do país** (`evidencias/chrome/2026-10-27/...`, `entregas/_fonte/prints_execucao/A-002.jpg`).

| Arquivo | O que guarda | Quem escreve |
|---|---|---|
| `execucao.json` | META, ações, pedidos, reteste, a sequência de slides e os ajustes do relatório de evidências | você, à mão (Edit) |
| `evidencias_execucao_<F>.json` | catálogo de evidências por ação, um arquivo por fase | `rodada.py` (não editar à mão, exceto para marcar `obsoleta`) |
| `ev_registro.json` | EV já enviados ao cliente → arquivo | `build.py --entrega` / `--registrar` |
| `rodadas/<AAAA-MM-DD>.json` | itens de cada rodada, entrada do `rodada.py` | você |

Exemplo completo e real: `brasil/entregas/_fonte/execucao.json` (v1.7, 23 slides, enviado em 27/10/2026).

## Sumário
1. META · 2. STATUS e FASES · 3. ACOES · 4. PEDIDOS e RETESTE · 5. DECK.slides · 6. EVIDENCIAS · 7. Catálogo e rodadas · 8. Contagens nos títulos

## 1. META

| Campo | Exemplo BR | Onde aparece |
|---|---|---|
| `cc`, `pais`, `pais_curto` | `"BR"`, `"Brasil"`, `"BR"` | nomes dos arquivos (`-br`), aba do navegador |
| `titulo` | "Auditoria de mensuração Smart Fit BR: execução do plano de ação" | slide 1 (título acessível), rodapé das evidências |
| `capa_titulo` | "Auditoria Smart Fit BR: o que já mudou e o que muda para o negócio" | h1 da capa (a última palavra ganha o marca-texto) |
| `capa_sub` | opcional; padrão "Acompanhamento das fases 1 a 3 · a partir do {diagnostico}" | capa |
| `autores`, `versao`, `atualizado` | "Monks", "v1.7", "27/10/2026" | capa, rodapé de todo slide, cabeçalho das evidências |
| `escopo` / `escopo_curto` | ativos completos / versão curta para a capa -design | capa (a -design troca pelo curto), cabeçalho das evidências |
| `confidencialidade` | "Confidencial · uso interno Smart Fit e Monks" | capa, evidências |
| `diagnostico` | "diagnóstico aprovado em 14/10/2026 (relatório técnico v1.3)" | capa, "Base" nas evidências |
| `rel_tecnico`, `rel_tecnico_curto` | "relatório técnico v1.5", "relatório v1.5" | referências "Relatório técnico v1.5 · SF-xxx · E-xx" |
| `periodo_coleta` | "15 a 27/10" | KPI das evidências; **atualize a cada rodada** |
| `coleta` | opcional; padrão "Monks · Tag Assistant, Tag Manager API, GA4 Admin/Data API, interfaces das plataformas" | evidências |

## 2. STATUS e FASES

`STATUS` é opcional (o padrão abaixo é o do BR). Cada status tem classe css e rótulo **com texto**, nunca só cor:

| chave | rótulo | quando |
|---|---|---|
| `concluida` | ✓ Concluída | feito e provado (na live, se mexeu em produção) |
| `publicar` | ◐ Validada · falta publicar | workspace "NÃO PUBLICAR" validado em Preview; a Smart Fit publica |
| `andamento` | ◐ Em andamento | a Monks está trabalhando |
| `decisao` | ◇ Decisão Smart Fit | depende de escolha do cliente (marcar planilha, aderir a recomendação) |
| `espera` | ‖ Em espera | recomendação entregue ou bloqueio externo (logs, billing, dev do site) |
| `revisao` | ↺ Achado revisado | o dado novo mudou a criticidade do achado |
| `nao` | ○ Não iniciada | |

`FASES`: `[{"id": "F1", "nome": "Fase 1", "tema": "Segurança, LGPD e acessos", "janela": "15 a 20/10"}, ...]`. Os temas do método: F1 segurança, dado pessoal e acessos · F2 integridade, custo 360 e ativos · F3 performance, limpeza e governança. Troque "LGPD" pela lei do país.

## 3. ACOES

Uma por ação do plano aprovado, na ordem do plano dentro de cada fase. O ID `A-nnn` vem do relatório técnico e nunca muda.

| Campo | Regra |
|---|---|
| `id`, `fase`, `achado` (`SF-PII-04`), `crit` (`ALTA`/`MÉDIA`/`BAIXA`) | do plano aprovado |
| `titulo` | curto, o que muda ("E-mail, telefone e nome fora do GA4") |
| `antes` | o que acontecia, **com o número do diagnóstico** ("14,4 mil eventos com e-mail em 30 dias") |
| `feito` | o que a Monks fez e como provou (workspace, Preview, API). Com `print` na vitrine, até ~330 caracteres, senão o print sai do slide |
| `negocio` | o que muda para o negócio, sem jargão: risco que fecha, receita que passa a ser confiável, custo que some |
| `status`, `proximo` | `proximo` sempre com o dono ("Smart Fit publica o workspace 777", "Nenhum: …") |
| `data` | data da última evidência ("26/10"); vazio se não houve |
| `rel` | achado e evidência do relatório técnico: `"SF-PII-04 · E-09"` |
| `onde` | o que o cliente abre fora dos relatórios: `"Workspace 777 do GTM-TCXTCQ5"`, planilha |
| `print`, `legenda` | jpg **recortado** em `entregas/_fonte/prints_execucao/<A-nnn>.jpg`, mostrado na vitrine; a legenda diz o que se vê |
| `evid` | pastas internas de evidência (não aparecem ao cliente; servem de rastro e de fallback) |

Texto: PT-BR, `PLACEHOLDER_xxx` vira o marcador "após a publicação" no deck. Crases viram `<code>`.

## 4. PEDIDOS e RETESTE

`PEDIDOS` (slide "O que depende de vocês", em ordem de prioridade): `{"o": "Publicar o workspace 777 do GTM-TCXTCQ5", "nome": "Versão sugerida: \"Monks | Fase 3 (A-028, A-015)\"", "fecha": "A-028, A-015"}`. Pedido que começa com "Publicar" conta em `{publicacoes}`.

`RETESTE` (slide "Como vamos provar" e o bloco "Critério de pronto" no card da ação): `{"id": "A-028", "criterio": "Tag Manager API: 0 tags da lista na live; funil sem regressão", "resultado": "PLACEHOLDER_reteste_a028"}`. O critério é **o mesmo teste que provou o achado**. Depois do reteste, `resultado` vira o número observado com data e fonte ("26/10, Tag Manager API: 0 tags com [TESTE] na v599").

## 5. DECK.slides

Lista ordenada; **um item = um slide**. Campos comuns: `titulo` (asserção com número; aceita contagens, §8), `kicker`, `notas` (notas do apresentador, faladas), `fonte`, `ids`, `apendice` (true = vai para o apêndice; o apêndice fica todo no fim). Se `fonte`/`ids` faltarem, o tipo preenche.

| tipo | campos próprios | o que gera |
|---|---|---|
| `capa` | — (usa META) | capa escura |
| `fases` | `destaque` (id da fase em destaque) | 3 cartões com barra por status, calculados das ações |
| `bluf` | `kpis: [{v, l, sub, ids, tom: ok/pub/rev}]` (4), `destaque: {titulo, itens: [{mono, txt, em}], nota}` | "Resposta em uma página" |
| `quadro` | `fase`, `colunas`: `"padrao"` (crit + próximo passo) ou `"hoje"` (hoje + para o negócio), `xl` (fonte menor, fase com 10+ ações) | tabela da fase |
| `vitrine` | `acoes: [A-nnn]` (1 ou 2), `numeros: [{v, l, ok}]` opcional | o que acontecia → o que fizemos → o que muda, status, referência EV com link; com 1 ação e `print`, mostra o print |
| `pedidos` | — (usa PEDIDOS) | tabela numerada |
| `tres_blocos` | `blocos: [{h, p}] × 3`, `pe: {status, txt}` opcional | slide livre em três caixas (aviso, cenário de risco) |
| `reteste` | `dod` opcional | tabela do RETESTE + definição de pronto |
| `indice` | `fases: ["F1", "F2"]` | índice de evidências (EV com link, print no slide N, onde ver, achado) |
| `prints` | `acoes` (2) | dois prints lado a lado (apêndice) |

## 6. EVIDENCIAS (ajustes do relatório de evidências)

```json
"EVIDENCIAS": {
  "rodadas": {"26/10": "· depois da publicação (v598…): reteste na live, Tag Manager API e Data API"},
  "fora": {"entregas/_fonte/prints_execucao/A-002.jpg": "recorte do deck, repete o print 06"},
  "mascara": {"evidencias/chrome/.../01_lead.png": [[290, 307, 834, 353]]},
  "como_ler": [["ID estável", "texto…"], ...],
  "avisos": [{"id": "s-fora", "toc": "Fora do escopo · A-004", "titulo": "…", "sub": "…", "texto": "**negrito** e `código`", "itens": ["…"]}]
}
```
- `rodadas`: rótulo de cada rodada (aparece no bloco "Rodada DD/MM" dos cards). O `rodada.py` grava quando o JSON da rodada traz `rotulo`.
- `fora`: arquivo do catálogo que **não** entra (repetido, ou com dado sensível sem recorte). Use isto em vez de apagar o item: apagar renumera.
- `mascara`: tarjas em px (x0, y0, x1, y1) aplicadas antes de embutir; o original não vai no HTML. Gerar tarja nova exige Pillow (venv do scratchpad). Abra a imagem para medir.
- `como_ler`: substitui os 6 itens padrão; inclua "Rodadas" e "Ainda falta" quando fizer sentido.
- `avisos`: seções no fim (ação que saiu do escopo etc.).

## 7. Catálogo e rodadas

Item do catálogo (o `rodada.py` completa os campos vazios):

```json
{"tipo": "print" | "dado" | "registro", "arquivo": "evidencias/…", "titulo": "Preview: view_item sem regressão",
 "legenda": "o que se vê, sem interpretação", "prova": "o que isso prova para o critério da ação",
 "fonte": "Tag Assistant (Preview, conta Monks)", "data": "27/10/2026",
 "trecho": "linhas que provam (para dados)", "resumo_numerico": "875 de 875 com ID",
 "sensivel": "", "obsoleta": false, "rodada": null | "26/10"}
```
- `print` só vira miniatura se o arquivo for png/jpg e existir; senão vai para "Dados e registros".
- **Numeração EV** por ação: a original (`rodada: null`) primeiro, depois cada rodada na ordem; dentro de cada uma, prints antes de dados. Por isso item novo de ação já enviada **sempre** entra como rodada. O `build.py` recusa mudar o arquivo de um EV que está no `ev_registro.json`.
- `obsoleta: true` tira o item do relatório, mas também renumera; só serve para item ainda não enviado.

Arquivo da rodada (`rodadas/2026-10-29.json`), entrada do `rodada.py`:

```json
{"rodada": "29/10", "rotulo": "· depois da publicação do workspace 777: reteste na live e Tag Manager API",
 "acoes": {
   "A-028": {"fase": "F3", "itens": [ {item}, ... ]},
   "A-032": {"fase": "F3", "nova": true, "resumo": "frase-resumo do card", "metodo": "como coletamos", "itens": [ ... ]}
 }}
```
`nova: true` só para ação sem nenhum EV enviado (entra como bloco original). `resumo` e `metodo` podem ser atualizados em qualquer rodada.

## 8. Contagens nos títulos

`{chave}` vira o número; `{chave|singular|plural}` escolhe a forma. Chaves: `acoes`, `pedidos`, `publicacoes`, e por fase (`F1`, `F2`…): `F1_total`, `F1_<status>` (`F1_concluida`, `F1_espera`, `F1_publicar`…), `F1_prontas` (concluída + publicar), `F1_andaram` (tudo menos não iniciada e em espera).

Ex.: `"Fase 2: {F2_andaram} das {F2_total} ações andaram e {F2_publicar} {F2_publicar|está pronta|estão prontas} para publicar"`.
O número se atualiza sozinho; **a frase não**. Se o status mudar a história (ex.: zero publicações pendentes), reescreva o título.
