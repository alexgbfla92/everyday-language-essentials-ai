# Prática — {{target_name}}

practice_id:
mission_id:  # missão desta prática
situation:  # situação da missão praticada nesta sessão
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no para testes)
practice_minutes: 30  # padrão 30, no máximo 35, ou o da missão
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
checkpoint_seq: 0  # sobe a cada ponto de retomada salvo; um menor nunca sobrescreve um maior
last_activity:  # última atividade efetivamente realizada
next_activity:  # próxima atividade obrigatória (onde retomar)
pending_items:  # o que falta quando pausada
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:  # só medida ou confirmada pelo aluno; senão, vazio
observed_minutes_source:  # measured | learner_estimate
module:
overrides:

## Etapas
Cada etapa só é concluída com evidência de execução. A prática só é concluída depois da etapa 7 e do Finish-Practice.
stage_1_status: pending  # 1 Briefing · pending | in_progress | completed
stage_1_evidence:
stage_2_status: pending  # 2 Treino guiado
stage_2_evidence:
stage_3_status: pending  # 3 Simulação
stage_3_evidence:
stage_4_status: pending  # 4 Imprevisto
stage_4_evidence:
stage_5_status: pending  # 5 Feedback
stage_5_evidence:
stage_6_status: pending  # 6 Encerramento (recapitulação, frases e próximo passo)
stage_6_evidence:
stage_7_status: pending  # 7 Entertainment Lab (parte da prática, antes da conclusão)
stage_7_evidence:

## Índice de frases (números F globais deste idioma; nunca reutilizados)
| ID | Diálogo | Quem fala | Modo (texto/voz) | Frase no idioma de estudo | Confiabilidade |
|---|---|---|---|---|---|

## Diálogos
| ID | Cenário | Frases |
|---|---|---|

## Pontos de retomada
| Sequência | Hora | Bloco e último turno | Atividades e evidências | Pendências e próxima pergunta | Última F |
|---|---|---|---|---|---|

## Encerramento
Recapitulação, feedback com evidências, limitações e próxima tarefa. A prática só é concluída depois da etapa 7 (Entertainment Lab).
closing_next_step:
closing_saved_reread:  # yes depois que a gravação final do Finish-Practice foi relida
save_error:  # o que falhou ao salvar; nunca dizer que foi salvo

## Entertainment Lab
Preparado e verificado antes da etapa 1. O Lab é a etapa 7: parte da prática e da sua duração.
lab_title:
lab_channel:
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 30
lab_max_video_seconds: 450  # 25% da prática: practice_minutes × 60 × 0,25
lab_video_seconds:  # duração verificada, em segundos; nunca desconhecida
lab_duration_source:  # youtube_page | browser | search_result_with_duration
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verified_at:  # data e hora da releitura do registro salvo
lab_blocked_reason:  # só quando nenhum vídeo válido foi encontrado; a etapa 7 fica pendente
lab_result:  # respostas, tarefa e feedback do Lab feito
lab_done_at:
