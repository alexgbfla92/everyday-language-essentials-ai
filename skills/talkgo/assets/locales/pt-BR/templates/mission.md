# Missão

mission_id:  # curto, em kebab-case, único no idioma; também é o nome do arquivo
mission_title:  # para o que o aluno quer se preparar
mission_description:  # cenário e contexto, nas palavras do aluno
mission_target_date:  # DD/MM/AAAA, obrigatória: quando o aluno quer estar preparado
mission_status: active  # active | paused | completed
mission_language:  # en-US | es-ES | fr-FR
mission_diagnostic:  # sessão de diagnóstico regular em que a missão se baseia
mission_practice_minutes: 20
mission_frequency:  # ex.: 3 práticas por semana
mission_next_review:  # DD/MM/AAAA (padrão: a cada 14 dias)
mission_revision: 1
mission_approved_at:

## Situações
| Nº | Situação | O que o aluno precisa conseguir fazer |
|---|---|---|

Exemplo: 1 Aeroporto · 2 Imigração · 3 Transporte público · 4 Restaurantes. A próxima prática trabalha a situação escolhida pelo aluno ou, sem escolha, a primeira situação com menos práticas concluídas.

## Práticas
| Prática | Data | Situação | Status |
|---|---|---|---|

Uma linha por sessão de prática desta missão, criada junto com a sessão. Status: Em andamento (preparada), Em andamento (em execução), Em andamento (pausada) ou Concluída. Uma prática apagada pelo Reset-Practices sai desta tabela.

## Histórico de revisões
| Revisão | Data | O que mudou | Motivo |
|---|---|---|---|
| 1 |  | Missão criada |  |
