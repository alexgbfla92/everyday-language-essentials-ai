# Missão

missao_id:  # curto, em kebab-case, único no idioma (ex.: viagem-londres); é também o nome do arquivo em missoes/
missao_titulo:  # o que o aluno quer se preparar para fazer (ex.: Me preparar para uma viagem a Londres)
missao_descricao:  # cenário e contexto, nas palavras do aluno
missao_data_alvo:  # DD/MM/AAAA, data em que o aluno quer estar preparado (obrigatória)
missao_status: ativa  # ativa | pausada | concluida
missao_idioma:  # en-US | es-ES | fr-FR
missao_diagnostico:  # sessão de diagnóstico regular em que a missão se baseia
missao_duracao_pratica_min: 20
missao_frequencia:  # ex.: 3 práticas por semana
missao_proxima_reavaliacao:  # DD/MM/AAAA (padrão: a cada 14 dias)
missao_revisao: 1
missao_aprovada_em:  # DD/MM/AAAA HH:MM, quando o aluno aprovou esta revisão

## Situações

| Nº | Situação | O que o aluno precisa conseguir fazer |
|---|---|---|

Exemplo: 1 Aeroporto · 2 Migração · 3 Transporte público · 4 Restaurantes. A próxima prática trabalha a situação indicada pelo aluno ou, sem indicação, a primeira situação com menos práticas concluídas.

## Práticas

| Prática | Data | Situação | Status |
|---|---|---|---|

Uma linha por sessão de prática desta missão, criada junto com a sessão. Status: `Em andamento (preparada)`, `Em andamento (em execução)`, `Em andamento (pausada)` ou `Concluída` (os mesmos do arquivo da prática). Uma prática apagada pelo Reset-Practices sai desta tabela.

## Histórico de revisões

| Revisão | Data | O que mudou | Motivo |
|---|---|---|---|
| 1 |  | Missão criada |  |
