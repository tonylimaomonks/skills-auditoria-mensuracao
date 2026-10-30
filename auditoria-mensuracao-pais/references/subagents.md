# Briefings dos subagents

Regras para todos: só leitura; salvar tudo em `<pais>/evidencias/<fonte>/<data>/` com um `README.md` que diz o que cada arquivo prova; não editar `conteudo.json` nem notas de achados; devolver um resumo curto com números e caminhos. Nunca extrair valor de dado pessoal: só contagem e o nome do campo.

Concorrência: no máximo **um** subagent de GTM API e **um** de Chrome ao mesmo tempo. Data/Admin API podem rodar ao lado de um deles.

## GTM (leitura do export)
```
Contexto: auditoria de mensuração <Cliente> <País>, conta principal. Pasta do país: <abs>/<pais>. Rode os comandos de dentro dela.
Tarefa:
1. python3 scripts/gtm_dump.py <GTM-WEB> e python3 scripts/gtm_dump.py <GTM-SGTM> (a quota é baixa; o script já espera 4 s entre chamadas).
2. Leia os live_version.json e produza em evidencias/gtm/<GTM-WEB>/<data>/:
   - inventario_tags.json: uma linha por tag {tagId, nome, tipo, pausada, pasta, triggers (nomes), destino (measurementId/AW-/pixel), parâmetros com nome de dado pessoal, usa variável de dado pessoal sem hash, html_dominios}
   - higiene.json: tags pausadas, triggers sem tag ativa, variáveis sem referência, tags sem pasta, nomes [TESTE]/UPD
   - terceiros.json: domínios carregados por tags HTML/templates, com a tag
   - tokens.json: tags com parâmetro de credencial em texto aberto (só tagId, nome e nome do parâmetro; NUNCA o valor)
   - sgtm.json: clients, tags e destinos do server, versão live, logType, server_container_url usado pelas tags web
3. README.md com as contagens.
Siga references/investigacao.md §1–2 (<SKILL_DIR>/references/investigacao.md). Não publique nem edite nada.
```

## Data API extra
```
Contexto: <País>, propriedade <prop>. Pasta do país: <abs>/<pais>.
O pacote padrão já rodou (evidencias/ga4/<prop>/<data>/dataapi/Q*.json e resumo.json). Para fechar as hipóteses abaixo, rode consultas runReport extras usando scripts/gapi.py (call, save) e salve cada uma como X<nn>_<assunto>.json com {descricao, request, response, extracted_at} na mesma pasta:
<lista de hipóteses com o que medir>
Só contagens; nenhum valor de dado pessoal.
```

## Chrome (funil completo com a compra de teste do cliente)

Preencha `<MARCADOR>`, `<REGRA DE TESTE>` e as etapas com `cliente.json → teste` e o funil do `<pais>/CLAUDE.md` (Etapa 0.3). Se `teste.ate_confirmacao` for `false`, troque "Vá até a confirmação" por "Pare antes de confirmar o pagamento" e tire o bloco da confirmação.
```
Contexto: auditoria <Cliente> <País>, site <URL de entrada>. Use o MCP chrome-devtools (Chrome do usuário via autoConnect). Abra ABAS NOVAS; não toque nas abas pessoais. Ninguém mais está usando o Chrome agora.
Dados fictícios: nome completo terminando OBRIGATORIAMENTE em "<MARCADOR>" (ex.: "Lucas Monks <MARCADOR>"), inclusive como titular do cartão; e-mail qa.monks.<ddmmhhmm>@teste1000.com; telefone fictício do país; documento gerado (CPF no BR; CURP/RFC de teste no MX). Nenhuma referência a Claude nos campos.
Compra de teste: <REGRA DE TESTE>. Vá até a confirmação. Sem o marcador, não preencha nada.
Para cada etapa (<etapas do funil do país, ex. Smart Fit: home → busca de unidade → unidade/plano → upsell → lead → dados pessoais → endereço → pagamento → confirmação>):
- print do viewport (não fullPage) em evidencias/chrome/<data>/<nn>_<etapa>.png
- list_network_requests filtrado por collect? (GA4), domínio do sGTM, facebook, tiktok, googleadservices, doubleclick e outros pixels; salvar hits_<nn>_<etapa>.json com url, método, status e parâmetros decodificados (en, tid, ep.*, up.*, dl, pr*)
- evaluate_script: window.dataLayer (datalayer_<nn>.json); chaves de localStorage/sessionStorage com e-mail/telefone/nome/documento (só NOME da chave e o tipo de dado, nunca o valor)
- console: erros (console_<nn>.json)
Na confirmação: purchase com transaction_id, value, currency e items; depois RECARREGUE a confirmação 2× e conte, por destino (GA4, Ads, Meta, TikTok, sGTM, demais pixels), quantos purchase saem (hits_<nn>_reload1.json, _reload2.json). Registre o número do pedido (é de teste).
Verificar: evento esperado de cada etapa e parâmetros (items, value, currency); em que momento sai o add_payment_info; disparo duplicado (mesmo en para o mesmo tid na mesma página); dado pessoal em URL/dl/ep/pixel/monitoramento; parâmetro id/base64 na URL (decodificar e dizer o que contém, sem copiar dado real). Redija (<REDIGIDO>) os valores do teste nos arquivos salvos.
Depois:
- Home em contexto isolado: banner de consentimento (print), o que dispara antes de aceitar (hits), gcs/gcd.
- Performance mobile (trace Slow 4G/CPU 4× + lighthouse_audit) na home e na página de produto: LCP, INP/TBT, CLS, nº de requests, gtm.js (transferido e descomprimido), third parties por main thread.
README.md com a tabela etapa × evento × destino × problema, a contagem do reload por destino e a lista de hipóteses confirmadas/descartadas.
```

## Validação tag a tag
```
Entrada: evidencias/gtm/<GTM-WEB>/<data>/inventario_tags.json, dataapi/Q01,Q03,Q10 e os hits do Chrome.
Para cada tag ativa, classifique: dispara | não dispara onde deveria | sem volume 30d | não testável | destino ≠ principal, com a prova (reqid do Chrome ou evento+volume da Data API). Salve validacao_tags.json e um README com as contagens por status.
```
