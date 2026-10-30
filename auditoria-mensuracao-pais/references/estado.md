# Modelo de `<pais>/auditoria-estado.md`

O `iniciar_pais.py` cria este arquivo. Atualize ao fim de cada etapa; ao retomar, leia primeiro.

```markdown
# Auditoria <Cliente> <País> · estado

Atualizado em: AAAA-MM-DD HH:MM

## Etapa atual
Etapa 0 · Kickoff · identidade, fluxo de compra, conexões e conta principal

## Conexões
| Fonte | Status (ok / pendente / sem acesso) | Conta | Desde |
|---|---|---|---|
| gcloud ADC + projeto de cota | pendente | | |
| GTM (Tag Manager API) | pendente | | |
| GA4 Admin/Data API | pendente | | |
| Organização GMP | pendente | | |
| Chrome (depuração remota) | pendente | | |
| Mídia (Ads, Meta, TikTok) | pendente | | |

## Sem acesso: o que fica impedido
| Fonte | Ações ou hipóteses impedidas | Vai para o relatório como |
|---|---|---|

## Fluxo de compra
- Site e URL de entrada:
- Etapas até a confirmação:
- Modo de teste (marcador, cartão, até onde ir, quem cancela):

## Conta principal
- GTM web: GTM-XXXX (<domínio>) · sGTM: GTM-XXXX · GA4: <prop> (<360|Standard>)
- Justificativa: <volume, domínio, links Ads>

## Coletado
| Etapa | Fonte | Caminho | Data |
|---|---|---|---|

## Hipóteses (catálogo de resoluções)
| Padrão R-xxx | Status (confirmada/descartada/sem dado/impedida) | Evidência |
|---|---|---|

## Bloqueios
- <o que falta, de quem, desde quando>

## Decisões
- AAAA-MM-DD · auditoria iniciada com a skill auditoria-mensuracao-pais
```
