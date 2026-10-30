# Esquema do `conteudo.json`

Arquivo: `<pais>/entregas/_fonte/conteudo.json`. O motor (`scripts/motor/build.py`) gera o relatório e o deck só a partir dele. Exemplo completo e aprovado: `assets/exemplo-conteudo-br.json`. Texto aceita `` `código` ``; IDs (`SF-…`, `E-nn`, `A-nnn`, `D-nn`, `V-nn`, `P-nn`) viram link no relatório automaticamente. `PLACEHOLDER_X` aparece como "[a preencher]" e o validador avisa.

## Sumário
- META · PILARES · REUNIAO · COMBINADO · RTM
- SUMARIO · COBERTURA · ESCOPO · INVENTARIO
- ACHADOS (cartão completo + deck) · VERIFICADO_OK · A_VALIDAR
- ACOES · DOD · DEPENDENCIAS · PERGUNTAS · DECISOES · PROVA
- MONEY · SLIDES_EXTRA · NOTAS · EVIDENCIAS · GLOSSARIO · CHANGELOG · RETESTE
- Blocos (tabela, texto, lista, kpis, barras, barra100, waterfall, imagem, json, query, html)

## META
```json
{"pais": "México", "cc": "mx", "cliente": "Smart Fit", "moeda": "MX$", "lei_dados": "<lei do país>",
 "titulo": "Auditoria de mensuração Smart Fit México: conta principal", "titulo_deck": "(opcional, capa do deck)",
 "rodada": "Rodada 1", "versao": "v1.0", "data_doc": "DD/MM/AAAA", "reuniao": "DD/MM/AAAA (opcional)",
 "periodo": "DD/MM/AAAA a DD/MM/AAAA (30 dias)", "periodo_curto": "DD/MM–DD/MM/AAAA", "extraido": "DD/MM/AAAA",
 "escopo": "lista completa dos ativos analisados", "escopo_curto": "GTM web + sGTM + GA4 (id) — vai na capa do deck",
 "autores": "Monks · Data & Martech", "confidencialidade": "Confidencial: Smart Fit e Monks. Contém evidências técnicas; tokens e dados pessoais redigidos.",
 "fases": {"Now": "Fase 1 · datas", "Next": "Fase 2 · datas", "Later": "Fase 3 · datas"},
 "decisoes_ate": "DD/MM/AAAA (opcional)", "prazo_texto": "(opcional)", "combinado": "texto da seção 2", "plano_intro": "texto da seção 8",
 "nota_parcial": "(opcional, slide RTM)", "nota_pendente": "(opcional)", "titulo_combinado/titulo_rtm/titulo_matriz/titulo_plano": "(opcionais, sobrescrevem o título-asserção automático)"}
```
`PILARES` é opcional (padrão FIN/INT/PG do pedido).

## Abertura
- `REUNIAO`: frases do cliente no alinhamento (aspas). `COMBINADO`: `[{titulo, texto, on}]`, os passos do slide 2.
- `RTM`: `[{id: "P-01", pedido, onde, status: Atendido|Parcial|Pendente, nota}]`, um por item do `PEDIDO.md` (o BR teve 12).
- `SUMARIO`: `{resposta_curta, titulo_deck, kpis: [{v, l, d?, s, crit?}] (até 4), destaque?: {titulo, acoes: [A-…], nota}, top: [SF-…], paragrafos: [texto], nota_escopo, fonte}`. `titulo_deck` é a frase que o executivo leva se só vir um slide.
- `COBERTURA`: `{titulo_deck, itens: [{v, l}]}`, o "o que lemos" (nº de tags, streams, eventos analisados, passos do funil).
- `ESCOPO`: `{fontes, limitacoes, fora}`.
- `INVENTARIO`: `{secoes: [{titulo, blocos: [...], evid: [E-…]}]}`. Típico: conta GTM (tabela de containers), container web (kv), sGTM (kv), GA4 (kv), uso dos ativos (tabela), acessos (tabela), validação tag a tag (tabela).

## ACHADOS
```json
{"id": "SF-DUP-01", "pilar": "INT", "scores": {"FIN": 1, "INT": 3, "PG": 2}, "I": 3, "P": 3,
 "mods": ["+1 dado pessoal ..."], "crit": "ALTA", "conf": "Alta (API + Chrome)",
 "titulo": "asserção com número", "curto": "rótulo de até ~45 caracteres para a matriz",
 "ativo": "onde está (propriedade, stream, host, tag)", "evid": ["E-05", "E-06"],
 "condicao": "o que os dados mostram, com números e período",
 "obs_esp": [["observado", "esperado"]], "criterio": "regra/boa prática", "fontes": [["nome", "url"]],
 "causa": "causa técnica", "efeito": "efeito no negócio (atribuição, receita, lance, risco legal)",
 "impacto": {"formula": "...", "valor": "resultado com faixa", "premissa": "o que precisa ser verdade"},
 "reproduzir": ["passo 1 (cite E-nn)", "..."], "rec_raiz": "...", "rec_contorno": "— ou contorno imediato",
 "pronto": "teste objetivo com o mesmo método da evidência", "acao": "A-006",
 "status": "Aberto", "revisao": "(opcional)", "risco_aceito": "(opcional, se rebaixou)",
 "tecnico": [bloco, ...],
 "vitrine": true, "ordem_vitrine": 1,
 "deck": {"oque": "...", "quanto": "...", "fazer": "...", "nota_quanto": "(opcional)", "titulo": "(opcional)", "kicker": "(opcional; o motor prefixa \"Achado N · \" pela ordem_vitrine)",
          "notas": "notas do apresentador", "grafico_titulo": "...", "grafico": bloco, "periodo": "(opcional)"}}
```
Regras que o validador confere: `I` = maior score; `crit` entre o nível base de MATRIZ[(I, P)] e o base + nº de `mods`; toda `evid` existe em EVIDENCIAS; `acao` existe; `impacto` completo.

## Demais listas
- `VERIFICADO_OK`: `[{item, evid, detalhe}]`, o que foi checado e está certo (dá credibilidade).
- `A_VALIDAR`: `[{id: "V-01", item, porque, como}]`, confiança baixa e fora da matriz.
- `ACOES`: `[{id: "A-001", achados: [...], oque, R, A, C, esforco: P|M|G, horizonte: Now|Next|Later, dep, pronto, metodo, fase}]`.
- `DOD`: lista de textos. `DEPENDENCIAS`: `[{id: "D-01", item, porque, destrava, status?}]`.
- `PERGUNTAS`: `[{n, q, fecha}]`. `DECISOES`: `[{d, porque, senao}]`. `PROVA`: até 5 IDs de ação para o slide "como vamos provar".
- `MONEY` (opcional, slide da receita): `{titulo, kicker?, notas, fonte, ids, principal: {titulo, itens: waterfall, fmt: "moeda"}, lateral?: {titulo, itens, fmt: "compacto", nota}}`. Itens de waterfall: `{label, valor, tipo: total|neg, ref?}` (negativos com valor < 0). O `resumo.json` do `dataapi_pacote.py` dá os números.
- `SLIDES_EXTRA`: `[{titulo, kicker, blocos, notas, fonte, ids, apendice?}]`, entram depois das vitrines (ex.: inventário de uso, acessos).
- `NOTAS`: notas do apresentador por slide fixo (`capa`, `combinado`, `rtm`, `bluf`, `decisoes`, `cobertura`, `matriz`, `plano`, `prova`, `fecho`).
- `EVIDENCIAS`: `[{id: "E-01", titulo, tipo, arquivo, periodo, extraido, query?, restrito?}]`. `arquivo` é relativo à pasta do país; vários arquivos com `" · "` (os seguintes herdam a pasta do anterior) e glob (`*.json`). Todos são embutidos no relatório.
- `GLOSSARIO`: `[[termo, definição]]`. `CHANGELOG`: `[[versão, data, mudança]]`. `RETESTE`: `[{achado, status, data, resultado}]` (rodadas seguintes).

## Blocos
Usados em `INVENTARIO.secoes[].blocos`, `ACHADOS[].tecnico`, `deck.grafico` e `SLIDES_EXTRA[].blocos`.
- `{"tipo": "tabela", "cab": [...], "linhas": [[...]], "legenda": "...", "kv": true?}`
- `{"tipo": "texto", "texto": "parágrafos separados por linha em branco"}` · `{"tipo": "lista", "itens": [...]}`
- `{"tipo": "kpis", "itens": [{"v", "l", "s"}]}`
- `{"tipo": "barras", "serie": [["13/09", 7100], ...], "destaque": ["rótulos em vermelho"], "marco": "03/10", "marco_txt": "...", "fmt": "compacto|moeda|int", "ultimo": true?}`
- `{"tipo": "barra100", "segs": [["rótulo", valor, "nota"], ...]}`
- `{"tipo": "waterfall", "itens": [...], "fmt": "moeda|compacto"}`
- `{"tipo": "imagem", "arquivo": "evidencias/chrome/<data>/x.png", "legenda": "..."}`: print com dado pessoal precisa de tarja antes.
- `{"tipo": "json", "arquivo": "...", "max": 6000}` (trecho, com tokens mascarados) · `{"tipo": "query", "arquivo": "evidencias/ga4/.../Q07_....json"}` (mostra o corpo da requisição)
- `{"tipo": "html", "html": "..."}`: último recurso.
