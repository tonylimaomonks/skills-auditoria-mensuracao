---
name: relatorios-execucao-pais
description: Cria e atualiza os dois entregáveis vivos da execução do plano de ação de uma auditoria de mensuração (Fases 1–3), de qualquer cliente e país (Smart Fit Brasil, México, um cliente novo…), o deck de execução (apresentacao-execucao-<slug>-<cc>) e o relatório de evidências (relatorio-evidencias-execucao-<slug>-<cc>, com IDs EV-Axxx-nn estáveis), com a identidade do cliente. Registra rodadas novas de evidência, atualiza status, reteste, pedidos e vitrines, gera os HTMLs com o design aprovado, confere no Chrome headless e congela a pasta entrega-cliente-*. Use SEMPRE que disserem que uma ação foi concluída, publicada ou retestada, que o cliente publicou um workspace, que há prints ou dados novos para entrar nas evidências, ou pedir para "atualizar o deck de execução", "subir a versão", "gerar a v1.8", "colocar o reteste nas evidências", "montar a pasta de entrega" ou começar a execução de um país depois do diagnóstico aprovado, mesmo sem dizer "skill" ou "relatório". Não use para o diagnóstico (relatório técnico e deck executivo da auditoria, que são da auditoria-mensuracao-pais), nem para escrever no Jira.
---

# Relatórios da execução (deck + evidências)

Depois que o cliente aprova o diagnóstico de um país, a Monks executa o plano em 3 fases. Dois entregáveis acompanham essa execução e são atualizados a cada ação:

- **Deck de execução**: slides 16:9 para a liderança do cliente (na Smart Fit, Nathalia e Karent). Conta o que acontecia, o que fizemos e o que muda para o negócio, fase a fase, e fecha com o que depende do cliente. Lendo só os títulos, a história precisa fechar.
- **Relatório de evidências**: a prova de cada ação, com prints em galeria e dados de API. Cada evidência tem um ID `EV-Axxx-nn`, que o deck cita com link.

O cliente recusou três vezes material sem evidência. A credibilidade da execução vem de três coisas que esta skill protege: **toda afirmação do deck tem um EV que a prova**, **um EV enviado nunca muda de número** (o cliente cita esses códigos em e-mail e no Jira) e **nenhuma ação fecha por declaração**, só quando o mesmo teste do achado passa na live.

Leia antes o `CLAUDE.md` da pasta do cliente (se houver) e o `<pais>/CLAUDE.md`. Nome, prefixo dos achados, slug dos arquivos, regra de teste e marca vêm do `<cliente>/cliente.json` (esquema na skill `auditoria-mensuracao-pais`, `references/cliente-schema.md`). Escreva sempre em PT-BR.

## Arquivos

`SKILL_DIR` = `~/.claude/skills/relatorios-execucao-pais`. Rode tudo **de dentro da pasta do país** (`cd brasil`).

| O quê | Onde |
|---|---|
| Conteúdo (META, ações, pedidos, reteste, slides) | `<pais>/entregas/_fonte/execucao.json` |
| Catálogo de evidências por fase | `<pais>/entregas/_fonte/evidencias_execucao_F1.json`, `_F2`, `_F3` |
| Rodadas (entrada do `rodada.py`) | `<pais>/entregas/_fonte/rodadas/AAAA-MM-DD.json` |
| EV já enviados | `<pais>/entregas/_fonte/ev_registro.json` |
| Prints recortados para as vitrines | `<pais>/entregas/_fonte/prints_execucao/A-nnn.jpg` |
| Saída | `<pais>/entregas/apresentacao-execucao-<slug>-<cc>[-design].html`, `relatorio-evidencias-execucao-<slug>-<cc>.html` |
| Pasta enviada | `<pais>/entregas/entrega-cliente-AAAA-MM-DD_vX.Y/` |

O formato de cada campo, os 10 tipos de slide e o item do catálogo estão em `references/conteudo-execucao.md`. Leia a seção que for usar. O exemplo real e completo é o `brasil/entregas/_fonte/execucao.json` (v1.7).

O motor usa o CSS/JS do deck e o `design.py` da skill `auditoria-mensuracao-pais`, uma fonte única para o design dos dois decks. Se o design mudar lá, muda aqui também.

## Fluxo de atualização (o caso comum)

Gatilhos típicos: "a Smart Fit publicou o ws 777", "retestei a A-011", "tenho prints novos da A-015", "sobe a v1.8".

### 1. Situe-se
Leia o `execucao.json` (META.versao, status das ações citadas, RETESTE, PEDIDOS) e a última pasta `entrega-cliente-*`, para saber o que o cliente já viu. Rode `python3 SKILL_DIR/scripts/validar.py .` para ver o estado de partida.

### 2. Garanta a evidência antes do texto
Afirmação nova no deck precisa de arquivo em `evidencias/<fonte>/<data>/`. Se o usuário só contou o que aconteceu e não há arquivo, a evidência precisa ser coletada:
- **Reteste em produção ou validação de Preview = subagents separados por fonte**: um de GTM API, um de Data API e um de Chrome. Chrome e GTM API **nunca em paralelo** (Chrome compartilhado; quota da GTM API de ~0,25 req/s). Os subagents só leem e salvam evidência em `evidencias/<fonte>/<data>/`; não editam o conteúdo nem publicam nada. A thread principal escreve os briefings e consolida.
- O critério do reteste é o de `RETESTE[].criterio`: é o mesmo teste que provou o achado. Data API com janela de 7 dias depois da publicação.
- Funil com dados fictícios, com o marcador de teste do cliente (`cliente.json → teste`; na Smart Fit, nome terminando em "Data Test").
- **Abra cada print** antes de catalogar (Read na imagem). Em 26/10 um README de prints estava errado (prints duplicados e um mostrando outra coisa). Legenda descreve o que se vê, não o que deveria aparecer.
- Achado novo encontrado durante a execução **não** entra nestes relatórios: vai para a lista viva `N-xx` em `<pais>/achados/` e só é reportado no fim das 3 fases.

### 3. Registre a rodada
Escreva `entregas/_fonte/rodadas/AAAA-MM-DD.json` (formato em `references/conteudo-execucao.md` §7) e rode:
```
python3 SKILL_DIR/scripts/rodada.py . entregas/_fonte/rodadas/AAAA-MM-DD.json
```
É idempotente: corrigir o JSON e rodar de novo troca os itens da rodada. Para cada item:
- `legenda`: só o fato visível. `prova`: o que isso prova para o critério da ação. Fato e leitura separados, porque é isso que deixa o cliente conferir sozinho.
- `trecho`: as linhas que provam (consulta + resultado, diff, trecho do gtm.js), curtas, com números. `resumo_numerico`: o número-chave ("875 de 875 com ID").
- `fonte` e `data` sempre.
- Identificador real no print (Client ID, e-mail, CPF/CURP, cookie, conta Google): tarja em `EVIDENCIAS.mascara` (medir abrindo a imagem; Pillow no venv do scratchpad). Arquivo repetido ou sensível sem recorte: `EVIDENCIAS.fora`. **Nunca apague item enviado**: apagar renumera.
- Token ou segredo: só "token em texto aberto na tag X", nunca o valor, nem em `trecho`.

### 4. Atualize o conteúdo (`execucao.json`)
- **Ação**: `status`, `feito` (o que fizemos e como provamos), `negocio` (o que muda, sem jargão), `proximo` (sempre com dono: "Smart Fit publica…", "Nenhum: …"), `data`. Status com publicação pendente = `publicar`; a Monks nunca publica.
- **RETESTE**: troque o `PLACEHOLDER_reteste_*` pelo resultado observado, com data e fonte ("26/10 na live: 0 dos 19 hits pós-lead com PII").
- **PEDIDOS**: tire o que o cliente já fez e reordene por prioridade.
- **Vitrine** (ação que vale um slide): recorte o print que conta a história em `prints_execucao/A-nnn.jpg` e preencha `print` e `legenda`. Com print, mantenha `feito` em até ~330 caracteres.
- **Títulos**: asserção com número ("Receita do Espaço do Cliente deduplicável: a parte sem transaction_id foi de 73% para 0%"), não rótulo ("A-010 · Espaço do Cliente"). As contagens (`{F2_publicar}`) se atualizam sozinhas, mas a frase não. Releia os títulos de `fases`, `bluf`, `quadro` e `pedidos` e reescreva os que a mudança deixou falsos. Atualize também as `notas`, que o Tony fala na apresentação.
- **META**: suba `versao` (v1.7 → v1.8), `atualizado` e `periodo_coleta`. Atualize o `como_ler` se ele citar datas de rodada.

### 5. Gere e confira
```
python3 SKILL_DIR/scripts/build.py .
```
A ordem é fixa: valida, gera as evidências (que definem as faixas EV), gera o deck (que cita as faixas) e aplica o design. ERRO bloqueia o build: ação ou arquivo inexistente, token, slide de corpo depois do apêndice, **EV enviado que mudou de arquivo ou sumiu**. Se o erro for de renumeração, o item novo não entrou como rodada. Corrija o catálogo; não apague o registro. Leia os AVISOS: PLACEHOLDER aberto, `feito` longo com print, ação `publicar` sem pedido, e-mail no texto.

Depois, confira no **Chrome headless** (nunca o Chrome do usuário), um PNG por slide alterado e mais a capa, o bluf, os quadros e os pedidos:
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --user-data-dir=<scratchpad>/chrome --window-size=1920,1080 --virtual-time-budget=4000 \
  --screenshot=<scratchpad>/s_N.png "file://<pais>/entregas/apresentacao-execucao-<slug>-<cc>-design.html#/N"
```
Abra os PNGs. Volta para o conteúdo: texto que estoura o slide, print empurrado para fora, tabela cortada (use `xl: true` no quadro), marcador "após a publicação" onde já existe resultado. No relatório de evidências, abra `#A-nnn` das ações mexidas e confira a rodada nova no fim do card.

QA antes de entregar:
- lendo só os títulos dos slides, a história fecha e bate com os status;
- todo slide de vitrine cita um EV;
- nenhum token, e-mail ou documento real;
- os números do deck são os mesmos do `trecho` da evidência.

### 6. Congele a entrega (quando o usuário pedir)
```
python3 SKILL_DIR/scripts/build.py . --entrega v1.8 --incluir entregas/<anexo>.xlsx ...
```
O comando cria a pasta `entregas/entrega-cliente-<hoje>_v1.8/` com o deck `-design` (copiado com o nome simples), o relatório de evidências e os anexos, e grava os EV no `ev_registro.json`. A partir daí esses números ficam travados. A pasta tem que sair completa: o cliente recebe tudo de uma vez. Por isso, inclua os anexos que o deck cita (catálogos e listas xlsx, o relatório técnico vigente se ele estiver na pasta anterior). Para saber quais são, compare com a pasta da versão anterior.

O envio ao cliente e o Jira (MARTECH, DAAF) ficam com o usuário ou com outra skill.

### 7. Feche
Responda ao usuário com:
- a versão;
- as ações que mudaram de status (antes → depois);
- os EV novos por ação;
- os slides alterados e os títulos novos;
- os avisos que ficaram (PLACEHOLDER etc.);
- os caminhos dos dois HTMLs e da pasta de entrega.

Registre na memória do projeto o que foi decisão (ex.: ação que saiu do escopo, criticidade revisada).

Atualize o **catálogo de resoluções** (`../auditoria-mensuracao-pais/references/catalogo-resolucoes.md`) para cada ação que mudou de status: a linha do caso em **Casos** (status, data, resultado em uma frase), uma linha em **Lições** se a execução ensinou algo (falso positivo, armadilha da API, contorno que funcionou, decisão do cliente que mudou o caminho) e uma entrada nova se surgiu um tipo de problema sem padrão (inclusive N-xx). Antes de preparar uma ação nova num workspace, leia o padrão dela e os padrões transversais (§ P).

## Começar a execução de um país

Depois que o diagnóstico do país foi aprovado (relatório técnico da `auditoria-mensuracao-pais`):

1. `python3 SKILL_DIR/scripts/iniciar_execucao.py .`: cria o `execucao.json` a partir do `conteudo.json` da auditoria. As ações vêm do plano (Now/Next/Later → F1/F2/F3), todas "não iniciadas", com o critério de pronto no RETESTE e um deck mínimo (capa, onde estamos, um quadro por fase, pedidos, reteste, índice).
2. Revise os campos marcados `[preencher]` (data da aprovação, janelas das fases, `periodo_coleta`). Ajuste os títulos curtos das ações e a lei do país no tema da F1.
3. Conforme as ações andam, entram as vitrines, o `bluf` ("Resposta em uma página", 4 KPIs) e os avisos. A ordem do BR funciona bem: capa → onde estamos → bluf → quadro F1 → vitrines F1 → pedidos → vitrines e quadros F2/F3 → reteste → apêndice (índices, prints, avisos).

## Brasil

O BR foi migrado para este motor em 29/10/2026. O build reproduz a v1.7: o relatório de evidências sai byte a byte igual, e o deck só ganhou `<span class="nw">` para que IDs como "A-004" não quebrem linha. O `ev_registro.json` do BR já tem os 138 EV da v1.7. Os builders antigos (`build_deck_execucao.py`, `build_relatorio_evidencias.py`, `conteudo_execucao.py`, `scripts/evidencias_execucao_<ddmm>.py`) ficaram só como histórico e não refletem mais o conteúdo. Edite o `execucao.json`.
