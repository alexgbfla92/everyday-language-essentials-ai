# Planos de missão

Um plano diz o que o aluno quer conseguir num idioma e a sequência de aulas para chegar lá. Cada idioma pode ter mais de um plano (por exemplo, "Viagem aos EUA" e "Reuniões de trabalho"). O modelo fica em `assets/modelos/plano-missao.md` e o plano gravado fica em `languages/<idioma>/planos/<plano_id>` (Google Doc no Drive, `.md` nos demais armazenamentos).

## Plan-Mission

`Plan-Mission [idioma] [novo|atualizar] [plano]` cria ou atualiza um plano. Resolva as ambiguidades uma de cada vez: idioma (se houver mais de um em andamento), ação (sem ação indicada, liste os planos do idioma com nome, status e próxima aula, e pergunte se é para criar um novo ou atualizar qual) e plano (ao atualizar com mais de um plano no idioma).

### Criar um plano

1. Exija um diagnóstico regular concluído no idioma; sem ele, encaminhe ao diagnóstico.
2. Pergunte, uma coisa por vez, só o que ainda não se sabe: objetivo e contexto (preserve o pedido original e confirme o cenário mais amplo), prazo real, duração das aulas, frequência e data da primeira reavaliação. Use os padrões (90 dias, 20 minutos, reavaliação a cada 14 dias) quando o aluno não tiver preferência e diga isso.
3. Proponha a sequência de aulas, com tema e objetivo de cada uma, ajustada ao diagnóstico e ao calendário (inclusive um compromisso próximo, como uma viagem amanhã).
4. Com a aprovação do aluno, copie o modelo, preencha os campos e a tabela de aulas (todas `Pendente`), defina um `plano_id` único no idioma e grave em `languages/<idioma>/planos/<plano_id>` com `plano_status: ativo`. Releia e confirme: "Plano salvo na sua Central: <plano_nome>".
5. Diga que a próxima aula sai com `Next-Lesson <idioma>` (e `plano <plano_id>`, se houver mais de um plano ativo no idioma).

### Atualizar um plano

1. Mostre um resumo do plano escolhido: objetivo, prazo, duração, frequência, reavaliação e aulas com status.
2. Pergunte o que mudar. Pode ser qualquer campo, incluir, retirar ou reordenar aulas `Pendente`, ou mudar o status do plano (`ativo`, `pausado`, `concluido`). Aulas `Concluída` e `Em andamento (...)` não são apagadas nem renumeradas; só a parte `Pendente` muda.
3. Com a aprovação do aluno, grave a nova versão no mesmo arquivo: some 1 em `plano_revisao`, preencha `plano_aprovado_em` e acrescente uma linha ao Histórico de revisões (o que mudou e por quê). Releia e confirme: "Plano atualizado na sua Central: <plano_nome>, revisão N".
4. Uma reavaliação (a cada 14 dias ou ao fim de missão curta) atualiza o plano por este mesmo fluxo.

## Escolher o plano no Next-Lesson

1. Considere só os planos `ativo` do idioma.
2. Nenhum: encaminhe ao `Plan-Mission <idioma> novo`.
3. Um: use esse e diga qual é no resumo da aula.
4. Mais de um: use o indicado no comando (`Next-Lesson Inglês plano viagem-eua`, pelo `plano_id` ou pelo nome); sem indicação, pergunte qual, listando nome e próxima aula de cada um. Não escolha sozinho.
5. A aula nova é a primeira linha `Pendente` da tabela. Ao criar a sessão, marque essa linha como `Em andamento (preparada)` com o ID da sessão e grave `plano_id` no arquivo da aula. Se não houver linha `Pendente`, diga que o plano terminou e ofereça atualizá-lo ou criar outro.

## Status das aulas no plano

A linha do plano acompanha o status da sessão (veja Status das aulas no SKILL.md): `Em andamento (em execução)` ao começar a etapa 1, `Em andamento (pausada)` no Pause-Lesson e `Concluída` no Finish-Lesson, relendo depois de cada mudança. O Lab não altera a linha. Se o aluno quiser refazer o tema de uma aula concluída, acrescente uma linha `Pendente` nova pelo `Plan-Mission`.

## Depois do Reset-Lessons

O Reset-Lessons devolve a `Pendente` todas as linhas cujas sessões apagou e limpa a coluna Sessão. Nada no plano indica que houve aulas apagadas: nem status como "excluída no reset", nem notas no Histórico de revisões. Uma linha que ainda aponte para uma sessão inexistente é tratada como `Pendente`.
