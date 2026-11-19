# Práctica — {{target_name}}

practice_id:
mission_id:  # misión de esta práctica
situation:  # situación de la misión practicada en esta sesión
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no para pruebas)
practice_minutes: 30  # por defecto 30, como máximo 35, o la de la misión
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
checkpoint_seq: 0  # sube en cada punto de reanudación guardado; uno menor nunca sobrescribe uno mayor
last_activity:  # última actividad realmente hecha
next_activity:  # próxima actividad obligatoria (dónde reanudar)
pending_items:  # lo que falta cuando está en pausa
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:  # solo medida o confirmada por el alumno; si no, vacío
observed_minutes_source:  # measured | learner_estimate
module:
overrides:

## Etapas
Cada etapa solo se completa con evidencia de ejecución. La práctica solo se completa después de la etapa 7 y de Finish-Practice.
stage_1_status: pending  # 1 Briefing · pending | in_progress | completed
stage_1_evidence:
stage_2_status: pending  # 2 Entrenamiento guiado
stage_2_evidence:
stage_3_status: pending  # 3 Simulación
stage_3_evidence:
stage_4_status: pending  # 4 Imprevisto
stage_4_evidence:
stage_5_status: pending  # 5 Comentarios
stage_5_evidence:
stage_6_status: pending  # 6 Cierre (recapitulación, frases y próximo paso)
stage_6_evidence:
stage_7_status: pending  # 7 Entertainment Lab (parte de la práctica, antes de la conclusión)
stage_7_evidence:

## Índice de frases (números F globales de este idioma; nunca se reutilizan)
| ID | Diálogo | Quién habla | Modo (texto/voz) | Frase en el idioma de estudio | Fiabilidad |
|---|---|---|---|---|---|

## Diálogos
| ID | Escenario | Frases |
|---|---|---|

## Puntos de reanudación
| Secuencia | Hora | Bloque y último turno | Actividades y evidencias | Pendientes y siguiente pregunta | Última F |
|---|---|---|---|---|---|

## Cierre
Recapitulación, retroalimentación con evidencias, limitaciones y próxima tarea. La práctica solo se completa después de la etapa 7 (Entertainment Lab).
closing_next_step:
closing_saved_reread:  # yes después de releer la escritura final de Finish-Practice
save_error:  # lo que falló al guardar; nunca decir que se guardó

## Entertainment Lab
Preparado y verificado antes de la etapa 1. El Lab es la etapa 7: parte de la práctica y de su duración.
lab_title:
lab_channel:
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 30
lab_max_video_seconds: 450  # 25% de la práctica: practice_minutes × 60 × 0,25
lab_video_seconds:  # duración verificada, en segundos; nunca desconocida
lab_duration_source:  # youtube_page | browser | search_result_with_duration
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verified_at:  # fecha y hora de la relectura del registro guardado
lab_blocked_reason:  # solo cuando no se encontró ningún vídeo válido; la etapa 7 queda pendiente
lab_result:  # respuestas, tarea y retroalimentación del Lab hecho
lab_done_at:
