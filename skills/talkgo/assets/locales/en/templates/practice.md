# Practice — {{target_name}}

practice_id:
mission_id:  # mission of this practice
situation:  # mission situation practiced in this session
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no for tests)
practice_minutes: 20  # default 20, or the mission's
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:
module:
overrides:

## Roadmap (the practice is completed when stages 0–6 are done; stage 7 is the optional Lab, suggested right after the closing)
| Stage | Done |
|---|---|
| 0 Lab material ready and reread before stage 1 (or learner accepted starting without the video) | pending |
| 1 Briefing | pending |
| 2 Guided drill | pending |
| 3 Simulation | pending |
| 4 Unexpected event | pending |
| 5 Feedback | pending |
| 6 Closing (saved and confirmed) | pending |
| 7 Entertainment Lab suggested after the closing (optional) | pending |

## Phrase index (global F numbers for this language; never reused)
| ID | Dialogue | Speaker | Mode (text/voice) | Phrase in the target language | Reliability |
|---|---|---|---|---|---|

## Dialogues
| ID | Scenario | Phrases |
|---|---|---|

## Checkpoints
| Sequence | Time | Block and last turn | Activities and evidence | Pending work and next question | Last F |
|---|---|---|---|---|---|

## Closing
Outcome, evidence-based feedback, limitations, next task and progress update status.
closing_saved_reread:  # yes after Finish-Practice is saved and reread
closing_next_step:

## Entertainment Lab
Prepared and verified before stage 1. The Lab has no status of its own; it is part of the practice.
lab_title:
lab_channel:  # unconfirmed only with source search
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 20
lab_video_minutes:  # minutes or mm:ss; unconfirmed only with source search
lab_segment:  # whole | mm:ss-mm:ss
lab_off_range_reason:  # required if what will be watched is outside 30–50% of the practice
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verification_source:  # youtube_page | browser | search
lab_search_evidence:  # only with source search: the result used (link, title, channel, duration)
lab_verified_at:  # date and time the saved record was reread
lab_missing_reason:
lab_missing_accepted_by_learner:  # only if the learner accepted starting without the video
lab_suggested_after_closing:  # yes when the Lab was suggested right after the closing
lab_result:  # only if the learner does the Lab
lab_save_confirmed:
