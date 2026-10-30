> Modelo de pedido (escopo da auditoria aprovada na Smart Fit BR, 2026). Use quando o cliente não mandar um pedido próprio; confirme com quem pediu.

Descrição & Expectativa Geral

O objetivo desta iniciativa é a execução de uma auditoria técnica profunda e o levantamento exaustivo de 100% da infraestrutura atual de mensuração (Google Tag Manager, Google Analytics 4, GA 360 e Firebase).
Não buscamos uma revisão superficial ou por amostragem, mas sim um raio-X completo do estado de saúde dos ativos de {PAIS} e sua conexão com o ambiente Global (áreas logadas e App). A entrega deve ser dividida em duas fases claras de análise:
Entregável Fase 1: Levantamento do Todo (Inventário Técnico)
Esperamos um diagnóstico qualitativo e quantitativo que responda pela totalidade do ecossistema:
• Google Tag Manager (GTM Web & Server-Side):
Inventário total de containers (quantidade existente, quais estão ativos, inativos ou obsoletos).
Avaliação de performance e volume: peso dos containers no DOM, quantidade de tags, gatilhos (triggers) redundantes, variáveis sem uso e o impacto do tempo de carregamento dos scripts na experiência do usuário (Core Web Vitals).
Arquitetura Server-Side: mapeamento de Clients configurados, fluxo de dados entrante no servidor e avaliação do consumo de infraestrutura que possa gerar custos desnecessários em nuvem (Google Cloud / App Engine).
• Google Analytics (GA4 Standard, GA 360 & Firebase):
Inventário total de propriedades de {PAIS} e mapeamento do fluxo de dados das áreas logadas (Global).
Classificação clara de propriedades ativas vs. inativas, e distinção explícita entre licenças GA4 Standard (Gratuitas) e GA 360 (Pagas).
Mapeamento do volume de coleta de dados, identificação de eventos duplicados (múltiplos disparos de conversões, transações ou interações por sessão) e redundância entre ativos.
Vinculação com projetos do Firebase (iOS/Android) e validação da paridade de dados e eventos entre o ambiente Web e App.
Segurança, Privacidade & Conformidade (Compliance):
Vazamento de PII (Personally Identifiable Information): Auditoria rigorosa em URLs, parâmetros de eventos, Data Layer e tags de terceiros para garantir que nenhum dado pessoal identificável (e-mail, documento pessoal, telefone, nome) esteja sendo enviado descriptografado ao GA4, GTM ou parceiros de mídia.
Injeção de Scripts de Terceiros: Mapeamento de segurança sobre tags HTML personalizadas e scripts externos injetados via GTM Web/Server-Side sem governança ou controle de origem.
Acessos & Permissões: Mapeamento de usuários com nível de administração/edição nos containers e propriedades para identificação de acessos indevidos ou ex-colaboradores.
Com base no levantamento integral da Fase 1, a Monks deverá classificar cada achado dentro de uma Matriz de Criticidade (Alta, Média, Baixa) sustentada nos seguintes pilares de impacto:

Impacto Financeiro / Licenciamento: Identificação de eventos de altíssimo volume que inflam desnecessariamente a cota da licença GA 360 ou executem chamadas Server-Side redundantes.
Duplicidade & Integridade de Dados: Pontos onde ocorram disparos duplicados de conversões, transações ou contaminação de dados entre canais (Web/App/Cross-channel).
Performance & Governança: Scripts pesados no GTM gerando latência no site, containers sobrecarregados ou inconsistências na taxonomia.
Critérios de Aceite (Acceptance Criteria)

[ ] Relatório/Documento com o inventário de 100% dos containers GTM (Web/SS) e propriedades GA4/Firebase ({PAIS}/Global).
[ ] Relatório detalhado de saúde técnica (eventos duplicados, redundância de dados e impacto de performance dos scripts).
[ ] Matriz de Criticidade (Alta, Média, Baixa) consolidada com a priorização e o plano de recomendação técnica para as correções.
Fica sob responsabilidade e critérios da agência a inclusão de qualquer material, documento, mapeamento ou diagnóstico adicional que seja considerado relevante para enriquecer e complementar este levantamento inicial.