# Mission

mission_id:  # short, kebab-case, unique in the language; also the file name
mission_title:  # what the learner wants to get ready for
mission_description:  # scenario and context, in the learner's words
mission_target_date:  # DD/MM/YYYY, required: when the learner wants to be ready
mission_status: active  # active | paused | completed
mission_language:  # en-US | es-ES | fr-FR | pt-BR | zh-CN | it-IT | ja-JP | de-DE | ko-KR | hi-IN | ar
mission_diagnostic:  # regular diagnostic session the mission is based on
mission_practice_minutes: 30
mission_frequency:  # e.g. 3 practices per week
mission_next_review:  # DD/MM/YYYY (default: every 14 days)
mission_revision: 1
mission_approved_at:

## Situations
| No. | Situation | What the learner needs to be able to do |
|---|---|---|

Example: 1 Airport · 2 Immigration · 3 Public transport · 4 Restaurants. The next practice works on the situation the learner chooses or, if none, the first situation with the fewest completed practices.

## Practices
| Practice | Date | Situation | Status |
|---|---|---|---|

One row per practice session of this mission, added when the session is created. Status: In progress (prepared), In progress (running), In progress (paused) or Completed. A practice deleted by Reset-Practices leaves this table.

## Revision history
| Revision | Date | What changed | Reason |
|---|---|---|---|
| 1 |  | Mission created |  |
