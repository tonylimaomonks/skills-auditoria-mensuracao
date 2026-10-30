# Pasta do cliente e `cliente.json`

Cada cliente é uma pasta. A skill trabalha sempre a partir dela:

```
<Cliente>/
├── cliente.json                 configuração lida por todos os scripts (este arquivo)
├── PEDIDO.md                    (opcional) pedido do cliente; vale para todos os países
├── CLAUDE.md                    contexto geral do cliente (a Etapa 0 cria um esqueleto)
├── conhecimento/                lei de dados pessoais de cada país, fórmulas locais, fontes
├── design-system/<marca>/       identidade do cliente: marca.json + tokens + assets (references/identidade-cliente.md)
└── <pais>/                      um por país (iniciar_pais.py)
```

A Monks **não** tem pasta no cliente: o logo e os tokens vêm de `assets/monks/` da skill.

## Campos

| Campo | Obrigatório | O que é | Exemplo (Smart Fit) |
|---|---|---|---|
| `nome` | sim | Nome como aparece nos textos | `"Smart Fit"` |
| `genero` | não (`f`) | Concordância: `f` → "a Smart Fit", "da", "com a"; `m` → "o Itaú" | `"f"` |
| `slug` | sim | Prefixo dos arquivos de entrega (`relatorio-tecnico-<slug>-<cc>.html`) | `"smartfit"` |
| `prefixo` | sim | Prefixo dos achados (`<prefixo>-PII-04`). Duas ou três letras, estável para sempre | `"SF"` |
| `marca` | sim | Pasta da identidade, relativa à pasta do cliente | `"design-system/smartfit"` |
| `sites` | não | Sites informados pelo usuário na Etapa 0 | `["https://www.smartfit.com.br"]` |
| `dominios_internos` | não | Domínios de e-mail do cliente: contam como "Interno" na análise de acessos e podem aparecer no texto | `["smartfit.com", "bioritmo.com.br"]` |
| `acessos_protegidos` | não | E-mail → motivo. Pontos focais do cliente que a análise de acessos nunca sugere remover | `{"fulana@cliente.com": "ponto focal"}` |
| `conta_auditoria` | sim p/ coleta | Conta Google da Monks usada no ADC (a análise de acessos marca como "temporário") | `"nome@monks.com"` |
| `projeto_cota` | sim p/ coleta | Projeto GCP do cabeçalho `x-goog-user-project` (APIs habilitadas nele) | `"apis-511715"` |
| `gmp_org` | não | ID da organização Google Marketing Platform. Vazio = sem acesso (ver `conexoes.md`) | `"3pxldAlsSYyIjTOzr6O-4w"` |
| `teste.marcador` | sim | Texto que marca cadastro/compra de teste no nome | `"Data Test"` |
| `teste.como` | sim | Como o cliente quer o teste (cartão, até onde ir, quem cancela). Vem da pergunta do fluxo de compra | ver Smart Fit |
| `teste.ate_confirmacao` | sim | `true` se pode ir até a confirmação do pedido | `true` |

O fluxo de compra **por país** (URL, etapas, documento pedido) fica no `<pais>/CLAUDE.md`; aqui só a regra de teste, que costuma valer para o cliente todo.

## Exemplo mínimo (cliente novo)

```json
{
  "nome": "Cliente X",
  "genero": "m",
  "slug": "clientex",
  "prefixo": "CX",
  "marca": "design-system/clientex",
  "sites": ["https://www.clientex.com.br"],
  "dominios_internos": ["clientex.com.br"],
  "acessos_protegidos": {},
  "conta_auditoria": "nome.sobrenome@monks.com",
  "projeto_cota": "<projeto-gcp>",
  "gmp_org": "",
  "teste": {"marcador": "Data Test", "como": "<resposta do usuário>", "ate_confirmacao": false}
}
```
