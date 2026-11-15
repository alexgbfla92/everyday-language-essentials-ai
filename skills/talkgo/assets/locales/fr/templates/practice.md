# Pratique — {{target_name}}

practice_id:
mission_id:  # mission de cette pratique
situation:  # situation de la mission travaillée dans cette séance
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no pour les tests)
practice_minutes: 20  # 20 par défaut, ou celle de la mission
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:
module:
overrides:

## Feuille de route (la pratique est terminée avec les étapes 0–6 faites ; l'étape 7 est le Lab facultatif, proposé juste après la clôture)
| Étape | Fait |
|---|---|
| 0 Matériel du Lab prêt et relu avant l'étape 1 (ou l'apprenant a accepté de commencer sans la vidéo) | à faire |
| 1 Briefing | à faire |
| 2 Entraînement guidé | à faire |
| 3 Simulation | à faire |
| 4 Imprévu | à faire |
| 5 Retour | à faire |
| 6 Clôture (enregistrée et confirmée) | à faire |
| 7 Entertainment Lab proposé après la clôture (facultatif) | à faire |

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
Résultat, retour fondé sur des preuves, limites, prochaine tâche et état de la mise à jour de la progression.
closing_saved_reread:  # yes après l'enregistrement et la relecture du Finish-Practice
closing_next_step:

## Entertainment Lab
Préparé et vérifié avant l'étape 1. Le Lab n'a pas de statut propre ; il fait partie de la pratique.
lab_title:
lab_channel:  # unconfirmed seulement avec la source search
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 20
lab_video_minutes:  # minutes ou mm:ss ; unconfirmed seulement avec la source search
lab_segment:  # whole | mm:ss-mm:ss
lab_off_range_reason:  # obligatoire si ce qui sera regardé sort de 30–50 % de la pratique
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verification_source:  # youtube_page | browser | search
lab_search_evidence:  # seulement avec la source search : le résultat utilisé (lien, titre, chaîne, durée)
lab_verified_at:  # date et heure de la relecture de l'enregistrement
lab_missing_reason:
lab_missing_accepted_by_learner:  # seulement si l'apprenant a accepté de commencer sans la vidéo
lab_suggested_after_closing:  # yes quand le Lab a été proposé juste après la clôture
lab_result:  # seulement si l'apprenant fait le Lab
lab_save_confirmed:
