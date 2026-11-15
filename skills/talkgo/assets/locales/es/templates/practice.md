# Práctica — {{target_name}}

practice_id:
mission_id:  # misión de esta práctica
situation:  # situación de la misión practicada en esta sesión
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no para pruebas)
practice_minutes: 20  # 20 por defecto, o el de la misión
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:
module:
overrides:

## Hoja de ruta (la práctica se completa con las etapas 0–6 hechas; la etapa 7 es el Lab opcional, sugerido justo después del cierre)
| Etapa | Hecho |
|---|---|
| 0 Material del Lab listo y releído antes de la etapa 1 (o el alumno aceptó empezar sin el vídeo) | pendiente |
| 1 Briefing | pendiente |
| 2 Entrenamiento guiado | pendiente |
| 3 Simulación | pendiente |
| 4 Imprevisto | pendiente |
| 5 Comentarios | pendiente |
| 6 Cierre (guardado y confirmado) | pendiente |
| 7 Entertainment Lab sugerido después del cierre (opcional) | pendiente |

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
Resultado, comentarios con evidencias, limitaciones, siguiente tarea y estado de la actualización del progreso.
closing_saved_reread:  # yes después de guardar y releer el Finish-Practice
closing_next_step:

## Entertainment Lab
Preparado y verificado antes de la etapa 1. El Lab no tiene estado propio; forma parte de la práctica.
lab_title:
lab_channel:  # unconfirmed solo con fuente search
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 20
lab_video_minutes:  # minutos o mm:ss; unconfirmed solo con fuente search
lab_segment:  # whole | mm:ss-mm:ss
lab_off_range_reason:  # obligatorio si lo que se verá queda fuera del 30–50 % de la práctica
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verification_source:  # youtube_page | browser | search
lab_search_evidence:  # solo con fuente search: el resultado usado (enlace, título, canal, duración)
lab_verified_at:  # fecha y hora de la relectura del registro guardado
lab_missing_reason:
lab_missing_accepted_by_learner:  # solo si el alumno aceptó empezar sin el vídeo
lab_suggested_after_closing:  # yes cuando el Lab se sugirió justo después del cierre
lab_result:  # solo si el alumno hace el Lab
lab_save_confirmed:
