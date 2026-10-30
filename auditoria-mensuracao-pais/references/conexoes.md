# Conexões: guiar o usuário passo a passo

Na Etapa 0, confira cada conexão **na ordem abaixo**. Para cada uma: teste, e se falhar, diga ao usuário exatamente o que fazer (o comando, a tela ou a mensagem para o cliente), espere a confirmação e teste de novo. Comandos interativos (login) o usuário roda com `! <comando>` no prompt. Registre cada resultado na tabela "Conexões" do `auditoria-estado.md`.

**Nenhuma conexão faltando para a auditoria.** Sem uma fonte, siga com as outras e deixe claro o que ela impede (§ 7).

## 1. gcloud e conta

Teste: `gcloud --version` e `gcloud auth list`.
- gcloud não instalado → `brew install --cask google-cloud-sdk` (macOS) ou o instalador de cloud.google.com/sdk.
- Pergunte qual conta Google da Monks vai ser usada (vai para `cliente.json → conta_auditoria`). Pode haver outra conta ativa no gcloud: use `--account=<conta>` nos comandos `gcloud services`.

## 2. Credencial (ADC) com os escopos

Teste: `gcloud auth application-default print-access-token` (precisa devolver um token).
Se falhar, ou se as APIs responderem "insufficient authentication scopes", peça:

```
! gcloud auth application-default login --account=<conta> --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.manage.users,https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/analytics.manage.users.readonly,https://www.googleapis.com/auth/marketingplatformadmin.analytics.read
```

- `tagmanager.edit.containers` só serve à execução (workspaces "NÃO PUBLICAR"). Na auditoria tudo é leitura.
- Se o Google bloquear `analytics.readonly` no client ID padrão do gcloud: criar um OAuth client (Desktop) no projeto de cota e refazer o login com `--client-id-file=<json>`.
- `workspaces.quick_preview` não funciona com o ADC: Preview só pela UI do GTM.

## 3. Projeto de cota

Pergunte qual projeto GCP usar (`cliente.json → projeto_cota`; o da conta do Tony é `apis-511715`). Habilite as APIs nele:

```
gcloud services enable tagmanager.googleapis.com analyticsadmin.googleapis.com analyticsdata.googleapis.com marketingplatformadmin.googleapis.com --project=<projeto> --account=<conta>
```

Erro `SERVICE_DISABLED` ou `USER_PROJECT_DENIED` → API não habilitada ou a conta sem `serviceusage.services.use` no projeto. Não use projetos de terceiros (no BR, nunca `data-mediamonks`).

## 4. Acesso aos ativos do cliente

Rode de dentro da pasta do país:
- `python3 scripts/gtm_dump.py --list` → contas e containers visíveis.
- `python3 scripts/ga_dump.py --list` → contas e propriedades visíveis.
- `python3 scripts/gmp_users.py` → organização GMP (só se houver `gmp_org`).

Filtre pelo país (nome da conta, domínio). O que faltar vira pedido ao cliente. Mensagem pronta (ajuste nomes):

> Para a auditoria de <país>, precisamos de acesso de **leitura** para `<conta_auditoria>`:
> 1. Google Tag Manager: contas <…> (permissão "Leitura" na conta e nos containers web e server-side);
> 2. Google Analytics: contas <…> (papel "Leitor" na conta; se o 360 tiver subpropriedades, também nelas);
> 3. Organização Google Marketing Platform: papel de leitura (para ver usuários e grupos que dão acesso pela organização);
> 4. (Opcional, para validar conversões) Google Ads (leitura na MCC), Meta Events Manager e TikTok Events Manager.
> Não publicamos nem alteramos nada.

O ID da organização GMP aparece em marketingplatform.google.com (Administração → organização) ou na resposta do `gmp_users.py`; grave em `cliente.json → gmp_org`.

## 5. Chrome

O teste do funil usa o MCP `chrome-devtools` com `--autoConnect` no Chrome do usuário.
- Teste: listar as páginas abertas pelo MCP.
- Se falhar: peça para abrir `chrome://inspect/#remote-debugging` e ativar a depuração remota, e confirmar que o MCP `chrome-devtools` está configurado (`claude mcp list`).
- Abra sempre abas novas; não mexa nas abas pessoais. Um subagent de Chrome por vez.

## 6. Fluxo de compra (pergunte, não suponha)

Antes do teste, pergunte ao usuário e registre no `<pais>/CLAUDE.md` (funil) e no `cliente.json → teste`:
- URL de entrada e caminho até a compra (ou se há vídeo/gravação do funil na pasta: se houver, gere as grades com ffmpeg e mapeie antes).
- O que é vendido e o que muda por país (planos, adicionais, documento pedido no cadastro).
- **Como o cliente quer o teste**: existe marcador de teste reconhecido pelo site (na Smart Fit, nome terminando em "Data Test")? Qual cartão usar? Pode ir até a confirmação do pedido? Quem cancela/desconsidera os pedidos e leads de teste?
- Se não houver modo de teste: vá só até a etapa anterior ao pagamento e registre como limite (§ 7).

No auto mode do Claude Code, o classificador pode recusar o preenchimento do checkout ("Real-World Transactions"). Não contorne: peça ao usuário para aprovar a ação ou fazer a compra enquanto o subagent só coleta (hook de rede + dataLayer).

## 7. Sem acesso: seguir e deixar claro o que fica impedido

Para cada fonte sem acesso, registre na tabela "Sem acesso" do estado o que fica impedido, leve para o conteúdo como `DEPENDENCIAS` (o que destrava) e marque as hipóteses afetadas como "impedida", **fora da matriz** e em `A_VALIDAR`. Na `COBERTURA`, o que não foi verificado aparece como "não verificado (sem acesso a X)", nunca como OK.

| Sem | O que fica impedido (padrões do catálogo) | Alternativa parcial |
|---|---|---|
| GTM (API) | Inventário e higiene do container (R-GOV-01, R-GOV-02), tokens em texto aberto no sGTM (R-PII-05), parâmetros de PII nas tags (R-PII-01, parte do export), domínio e região do sGTM (R-PERF-02), validação tag a tag (R-DUP-05) | Export JSON pela UI enviado pelo cliente (Admin → Exportar container); o Chrome mostra o que dispara, não o que está configurado |
| GA4 Admin/Data API | Volume e duplicidade de `purchase` (R-DUP-01, R-DUP-02, R-DUP-03), cota 360 e subpropriedades (R-FIN-01, R-FIN-02), key events (R-GOV-03), histórico de PII (R-PII-01), uso dos ativos e acessos (R-GOV-04, R-GOV-06) | Chrome prova o hit de uma sessão, não o volume; export do BigQuery, se o cliente der leitura |
| Organização GMP | Acessos dados por grupo da organização (invisíveis na conta: R-GOV-04, parte dos grupos), mapa único de acessos, vínculo das contas GA à organização | Data Access Report da conta: identidade que lê sem permissão na conta = "provável grupo GMP" (achado a validar) |
| Chrome | Funil real: payload de e-commerce (R-DUP-03), conversões de mídia (R-DUP-04), PII no navegador e para terceiros (R-PII-02, R-PII-03), consentimento (R-PII-04), INP/LCP (R-PERF-01) | Vídeo do funil gravado pelo cliente (só mostra a tela, não a rede) |
| Compra até a confirmação | `purchase` com `transaction_id`/`value`/`items`, duplicidade no reload da confirmação, momento do `add_payment_info` | Ir até o pagamento e cruzar com a Data API de produção |
| Mídia (Ads, Meta, TikTok) | Duplicidade nos lances e conta errada recebendo a compra (R-DUP-04), conversões importadas, qualidade de match | Contar no Chrome os hits por conta/label (prova o envio, não o uso no lance) |
| Billing GCP / logs do Cloud Run | Custo do sGTM e do logging (R-FIN-03), perda de hits no servidor (parte de R-PERF-02) | Faixa por premissa (fórmula de `metodo/02`), marcada como estimativa |

No resumo da Etapa 4 para o usuário, liste as fontes sem acesso e as ações relevantes que ficaram impedidas por causa delas.
