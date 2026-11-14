# Missões

Uma missão é o cenário e o contexto para o qual o aluno quer se preparar num idioma, com uma data para estar pronto. Ela tem título, descrição, data-alvo e as situações a praticar. Exemplo: "Me preparar para uma viagem a Londres" até 20/04/2027, nas situações aeroporto, migração, transporte público e restaurantes.

O aluno faz sessões de prática ligadas a uma missão, e cada missão pertence a um idioma. Cada idioma pode ter mais de uma missão (por exemplo, "Viagem a Londres" e "Reuniões com o time de Dublin"). O modelo fica em `assets/modelos/missao.md` e a missão gravada fica em `languages/<idioma>/missoes/<missao_id>` (Google Doc no Drive, `.md` nos demais armazenamentos).

## Comandos

- `Get-Missions [idioma] [status]` lista as missões do idioma (título, data-alvo, status, situações e práticas concluídas), marcando a padrão.
- `New-Mission [idioma]` cria uma missão (abaixo).
- `Set-Mission [missão]` atualiza uma missão (abaixo).
- `Remove-Mission [missão]` apaga a missão e as práticas dela (veja [COMANDOS.md](COMANDOS.md#mission)).
- `Set-Default mission [missão]` define a missão assumida quando o aluno não indica uma.

Resolva Central, idioma e missão conforme [Contexto e padrões](COMANDOS.md#contexto-e-padrões).

### New-Mission

1. Exija um diagnóstico regular concluído no idioma; sem ele, encaminhe ao diagnóstico.
2. Pergunte, uma coisa por vez, só o que ainda não se sabe: título (o que o aluno quer se preparar para fazer), descrição (cenário e contexto), data-alvo, situações a praticar, duração das práticas, frequência e data da primeira reavaliação. A data-alvo é obrigatória: se o aluno não tiver uma, sugira uma e peça a confirmação. Para duração, frequência e reavaliação, use os padrões (20 minutos, reavaliação a cada 14 dias) quando o aluno não tiver preferência e diga isso.
3. Proponha as situações, cada uma com o que o aluno precisa conseguir fazer nela, ajustadas ao diagnóstico e ao tempo até a data-alvo (inclusive uma data muito próxima, como uma viagem amanhã).
4. Com a aprovação do aluno, copie o modelo, preencha os campos e a tabela de situações, defina um `missao_id` único no idioma e grave em `languages/<idioma>/missoes/<missao_id>` com `missao_status: ativa`. Se for a primeira missão do idioma, grave-a também como padrão (`missoes_padrao`). Releia e confirme: "Missão salva na sua Central: <missao_titulo>".
5. Diga que a primeira prática sai com `Start-Practice <idioma>`.

### Set-Mission

1. Mostre um resumo da missão escolhida: título, descrição, data-alvo, duração, frequência, reavaliação, situações e práticas com status.
2. Pergunte o que mudar. Pode ser qualquer campo, incluir, retirar ou reordenar situações, ou mudar o status da missão (`ativa`, `pausada`, `concluida`). Práticas já feitas não são apagadas da tabela.
3. Com a aprovação do aluno, grave a nova versão no mesmo arquivo: some 1 em `missao_revisao`, preencha `missao_aprovada_em` e acrescente uma linha ao Histórico de revisões (o que mudou e por quê). Releia e confirme: "Missão atualizada na sua Central: <missao_titulo>, revisão N".
4. Uma reavaliação (a cada 14 dias ou perto da data-alvo) atualiza a missão por este mesmo fluxo.

## Escolher a missão no Start-Practice

1. Considere só as missões `ativa` do idioma.
2. Nenhuma: encaminhe ao `New-Mission <idioma>`.
3. Uma: use essa e diga qual é no resumo da prática.
4. Mais de uma: use a indicada no comando (`Start-Practice Inglês missao viagem-londres`, pelo `missao_id` ou pelo título); sem indicação, pergunte qual, listando título, data-alvo e próxima situação de cada uma, com a padrão do idioma em primeiro lugar, marcada "(padrão)" e já assumida. Sem padrão, não escolha sozinho.
5. A situação da prática é a indicada pelo aluno ou, sem indicação, a primeira situação da tabela com menos práticas concluídas. Ao criar a sessão, grave `missao_id` e a situação no arquivo da prática e acrescente a linha da prática na tabela Práticas da missão, com status `Em andamento (preparada)`.

## Status das práticas na missão

A linha da prática acompanha o status da sessão (veja Status das práticas no SKILL.md): `Em andamento (em execução)` ao começar a etapa 1, `Em andamento (pausada)` no Pause-Practice e `Concluída` no Finish-Practice, relendo depois de cada mudança. O Lab não altera a linha. Para treinar de novo uma situação, basta fazer outra prática nela.

## Depois do Reset-Practices

O Reset-Practices tira da tabela Práticas as linhas das sessões que apagou. Nada na missão indica que houve práticas apagadas: nem status como "excluída no reset", nem notas no Histórico de revisões. Uma linha que ainda aponte para uma sessão inexistente é ignorada.
