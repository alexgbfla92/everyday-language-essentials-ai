# Diagnostic — {{target_name}}

diagnostic_id:
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no for tests)
status: running  # running | paused | completed
current_stage:  # 1–5
phrase_range:  # F?–F? | D?–D?
created_at:
saved_in_central_at:
finished_at:
result_listening:  # … | not_observed
result_speaking_interaction:  # … | not_observed
result_reading:  # … | not_observed
result_cefr_estimate:  # A1–C2
result_confidence:  # low | medium | high
closing_derived_updated:  # yes
closing_saved_reread:  # yes
closing_next_step:

## Stages
1. Listening: evidence, confidence, provisional CEFR:
2. Speaking and interaction: evidence, confidence, provisional CEFR:
3. Everyday and technical reading: evidence, confidence, provisional CEFR:
4. Feedback: priorities, limitations and goals for the next 14 days:
5. Closing: saved, reread and next step:

Never invent scores or judge pronunciation from a transcript alone.

## Last turn
Last turn, pending step and next question.

## Phrase index (global F numbers for this language; never reused)
| ID | Dialogue | Speaker | Mode (text/voice) | Phrase in the target language | Reliability |
|---|---|---|---|---|---|

## Dialogues
| ID | Scenario | Phrases |
|---|---|---|
