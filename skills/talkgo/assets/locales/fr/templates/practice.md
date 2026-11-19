# Pratique — {{target_name}}

practice_id:
mission_id:  # mission de cette pratique
situation:  # situation de la mission travaillée dans cette séance
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no pour les tests)
practice_minutes: 30  # 30 par défaut, 35 au maximum, ou celle de la mission
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
checkpoint_seq: 0  # augmente à chaque point de reprise enregistré ; un plus petit n'écrase jamais un plus grand
last_activity:  # dernière activité réellement faite
next_activity:  # prochaine activité obligatoire (où reprendre)
pending_items:  # ce qui reste en cas de pause
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:  # seulement mesurée ou confirmée par l'apprenant ; sinon vide
observed_minutes_source:  # measured | learner_estimate
module:
overrides:

## Étapes
Chaque étape n'est terminée qu'avec une preuve d'exécution. La pratique n'est terminée qu'après l'étape 7 et Finish-Practice.
stage_1_status: pending  # 1 Briefing · pending | in_progress | completed
stage_1_evidence:
stage_2_status: pending  # 2 Entraînement guidé
stage_2_evidence:
stage_3_status: pending  # 3 Simulation
stage_3_evidence:
stage_4_status: pending  # 4 Imprévu
stage_4_evidence:
stage_5_status: pending  # 5 Retour
stage_5_evidence:
stage_6_status: pending  # 6 Clôture (récapitulatif, phrases et prochaine étape)
stage_6_evidence:
stage_7_status: pending  # 7 Entertainment Lab (partie de la pratique, avant la conclusion)
stage_7_evidence:

## Index des phrases (numéros F globaux de cette langue ; jamais réutilisés)
| ID | Dialogue | Qui parle | Mode (texte/voix) | Phrase dans la langue étudiée | Fiabilité |
|---|---|---|---|---|---|

## Dialogues
| ID | Scénario | Phrases |
|---|---|---|

## Points de reprise
| Séquence | Heure | Bloc et dernier tour | Activités et preuves | À faire et prochaine question | Dernière F |
|---|---|---|---|---|---|

## Clôture
Récapitulatif, retours avec preuves, limites et prochaine tâche. La pratique n'est terminée qu'après l'étape 7 (Entertainment Lab).
closing_next_step:
closing_saved_reread:  # yes après relecture de l'écriture finale de Finish-Practice
save_error:  # ce qui a échoué à l'enregistrement ; ne jamais dire que c'est enregistré

## Entertainment Lab
Préparé et vérifié avant l'étape 1. Le Lab est l'étape 7 : il fait partie de la pratique et de sa durée.
lab_title:
lab_channel:
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 30
lab_max_video_seconds: 450  # 25 % de la pratique : practice_minutes × 60 × 0,25
lab_video_seconds:  # durée vérifiée, en secondes ; jamais inconnue
lab_duration_source:  # youtube_page | browser | search_result_with_duration
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verified_at:  # date et heure de la relecture de l'enregistrement
lab_blocked_reason:  # seulement si aucune vidéo valide n'a été trouvée ; l'étape 7 reste à faire
lab_result:  # réponses, tâche et retours du Lab fait
lab_done_at:
