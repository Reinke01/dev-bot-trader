Você criará um CALENDÁRIO EDITORIAL com base nos insumos do usuário e nas regras abaixo.
Escreva o resultado em `docs/output/content/social/<N>_calendar_plan.md`. Se houver um arquivo existente, utilize o N+1 para o novo arquivo.

ENTRADAS (o usuário informará, quando possível):
- Objetivo do período (ex.: leads, vendas, awareness) e oferta(s)/produto(s)
- Persona(s) e dores/objeções principais
- Período (datas), canais (IG, YT, Email, Blog, LinkedIn, etc.) e frequência desejada
- Temas macro obrigatórios e restrições (compliance, palavras vetadas)
- Datas/gancho externos (lançamentos, feriados, eventos)

O QUE GERAR:
1) Resumo executivo (5–8 bullets)
   - Meta do período, mensagem central, distribuição por funil (TOFU/MOFU/BOFU) e por canal
2) Diretrizes de cadência e mix
   - Proporção sugerida (ex.: 50% TOFU / 30% MOFU / 20% BOFU)
   - Regras simples de alternância (evitar 2 BOFU seguidos, etc.)
3) Tabela do calendário (MARKDOWN) com, no mínimo, as colunas:
   - Data (YYYY-MM-DD) | Canal | Tema/Ângulo | Formato (Reel, Carrossel, Short, Live, Email, Blog, etc.)
   - Etapa do Funil (TOFU/MOFU/BOFU) | Objetivo | Gancho (Hook) | CTA
   - Prova/Asset (ex.: depoimento, case, demo) | KPI primária | Observações | Reaproveitamento
4) Backlog de ideias (10–20 linhas)
   - Ideia | Funil | Canal sugerido | Gancho | Prova | Nota de impacto (1–5)
5) Experimentos A/B (opcional)
   - Hipótese | Variação de hook/copy/thumbnail | Métrica-guia
6) Checklist de assets por formato
   - Roteiro/Script, Thumbnail/Arte, Copy/Hashtags, Links UTM, Endscreen/Chamada, Captions/Legendas

CONVENÇÕES:
- Linguagem clara, direta e orientada a ação. Evite jargão vazio.
- Ganchos específicos (evite “genéricos”); sempre inclua CTA mensurável.
- Use datas absolutas; semana começa na segunda-feira.
- Se um canal não tiver conteúdo no período, indique “—”.
- Não inclua conteúdo além do solicitado.

SAÍDA:
- Seção 1: “Resumo do período”
- Seção 2: “Regras de cadência e mix”
- Seção 3: “Calendário” (tabela markdown)
- Seção 4: “Backlog”
- Seção 5: “Experimentos A/B”
- Seção 6: “Checklist de assets por formato”