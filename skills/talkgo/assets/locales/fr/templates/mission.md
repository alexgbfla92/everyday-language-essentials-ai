# Mission

mission_id:  # court, en kebab-case, unique dans la langue ; c'est aussi le nom du fichier
mission_title:  # ce à quoi l'apprenant veut se préparer
mission_description:  # scénario et contexte, avec les mots de l'apprenant
mission_target_date:  # JJ/MM/AAAA, obligatoire : quand l'apprenant veut être prêt
mission_status: active  # active | paused | completed
mission_language:  # en-US | es-ES | fr-FR | pt-BR | zh-CN | it-IT | ja-JP | de-DE | ko-KR | hi-IN | ar
mission_diagnostic:  # séance de diagnostic régulière sur laquelle repose la mission
mission_practice_minutes: 30
mission_frequency:  # ex. : 3 pratiques par semaine
mission_next_review:  # JJ/MM/AAAA (par défaut : tous les 14 jours)
mission_revision: 1
mission_approved_at:

## Situations
| N° | Situation | Ce que l'apprenant doit savoir faire |
|---|---|---|

Exemple : 1 Aéroport · 2 Immigration · 3 Transports en commun · 4 Restaurants. La prochaine pratique travaille la situation choisie par l'apprenant ou, sans choix, la première situation avec le moins de pratiques terminées.

## Pratiques
| Pratique | Date | Situation | Statut |
|---|---|---|---|

Une ligne par séance de pratique de cette mission, créée avec la séance. Statut : En cours (préparée), En cours (en exécution), En cours (en pause) ou Terminée. Une pratique supprimée par Reset-Practices sort de ce tableau.

## Historique des révisions
| Révision | Date | Ce qui a changé | Raison |
|---|---|---|---|
| 1 |  | Mission créée |  |
