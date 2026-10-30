# Skills de auditoria de mensuração (Monks)

Skills do Claude Code instaladas em `~/.claude/skills/`, que valem em qualquer projeto:

- `auditoria-mensuracao-pais/`: auditoria de GTM/GA4/Firebase de qualquer cliente, país a país (diagnóstico, relatório técnico e deck executivo). Inclui o catálogo de resoluções (`references/catalogo-resolucoes.md`), que é compartilhado por todos os clientes.
- `relatorios-execucao-pais/`: deck de execução e relatório de evidências das Fases 1–3.

Cada cliente fica numa pasta própria com `cliente.json` e `design-system/<marca>/marca.json` (ver `auditoria-mensuracao-pais/references/cliente-schema.md`). A primeira cliente é a Smart Fit.

## Antes de commitar mudança no motor

```
testes/regressao.sh            # usa ~/Documents/obsidian/Dia-a-dia/clients/Smart-Fit por padrão
```

Gera a auditoria BR (exemplo), a auditoria MX e a execução BR da Smart Fit numa pasta temporária e compara byte a byte com `testes/base-smartfit.sha`. Diferença = a mudança altera o HTML de um cliente: confira se é intencional.

Atenção: a auditoria MX e a execução BR usam o conteúdo vivo do vault. Quando esse conteúdo mudar, regenere a base com o código do commit anterior e commite a base nova à parte.
