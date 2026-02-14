O usuário fornecerá uma descrição da funcionalidade. Seu trabalho é:

1. Criar um plano técnico que descreva de forma concisa a funcionalidade que o usuário deseja construir.
2. Pesquisar os arquivos e funções que precisam ser modificados para implementar a funcionalidade.
3. Evitar seções no estilo de gerente de produto (sem critérios de sucesso, cronograma, migração, etc).
4. Evitar escrever qualquer código real no plano.
5. Incluir detalhes específicos e literais do prompt do usuário para garantir que o plano seja preciso.

Este é estritamente um documento de requisitos técnicos que deve:
1. Incluir uma breve descrição para contextualizar no topo.
2. Apontar todos os arquivos e funções relevantes que precisam ser alterados ou criados.
3. Explicar qualquer algoritmo utilizado passo a passo.
4. Se necessário, dividir o trabalho em fases lógicas. Idealmente, isso deve ser feito de forma que tenha uma fase inicial de "camada de dados", que define os tipos e alterações no banco de dados que precisam ser feitas, seguida de N fases que podem ser executadas em paralelo (ex: Fase 2A - UI, Fase 2B - API). Incluir fases apenas se for uma funcionalidade REALMENTE grande.

Se os requisitos do usuário estiverem pouco claros, especialmente após pesquisar os arquivos relevantes, você pode fazer até 5 perguntas de esclarecimento antes de escrever o plano. Se fizer isso, incorpore as respostas do usuário ao plano.

Priorize ser conciso e preciso. Faça o plano o mais direto possível, sem perder nenhum dos detalhes críticos dos requisitos do usuário.

Escreva o plano em um arquivo docs/output/features/FEATURE_<N>_PLAN.md com o próximo número de funcionalidade disponível.