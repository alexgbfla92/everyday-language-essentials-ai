# Plano de missão

plano_id:  # curto, em kebab-case, único no idioma (ex.: viagem-eua); é também o nome do arquivo em planos/
plano_nome:  # como o aluno chama o plano (ex.: Viagem aos EUA)
plano_status: ativo  # ativo | pausado | concluido
plano_idioma:  # en-US | es-ES | fr-FR
plano_diagnostico:  # sessão de diagnóstico regular em que o plano se baseia
plano_objetivo:  # o que o aluno quer conseguir fazer no idioma
plano_contexto:  # cenários e interesses confirmados (viagem, reuniões, cotidiano...)
plano_inicio:  # AAAA-MM-DD
plano_prazo:  # AAAA-MM-DD ou duração da missão (padrão 90 dias)
plano_duracao_aula_min: 20
plano_frequencia:  # ex.: 3 aulas por semana
plano_proxima_reavaliacao:  # AAAA-MM-DD (padrão: a cada 14 dias)
plano_revisao: 1
plano_aprovado_em:  # AAAA-MM-DD HH:MM, quando o aluno aprovou esta revisão

## Aulas

| Nº | Tema | Objetivo da aula | Status | Sessão |
|---|---|---|---|---|

Status de cada aula: `pendente`, `em_andamento` ou `concluida`. A próxima aula é a primeira linha `pendente`.

## Histórico de revisões

| Revisão | Data | O que mudou | Motivo |
|---|---|---|---|
| 1 |  | Plano criado |  |
