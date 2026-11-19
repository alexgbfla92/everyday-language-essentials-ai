# Practice — {{target_name}}

practice_id:
mission_id:  # mission of this practice
situation:  # mission situation practiced in this session
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no for tests)
practice_minutes: 30  # default 30, at most 35, or the mission's
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
checkpoint_seq: 0  # goes up at every saved checkpoint; a lower one never overwrites a higher one
last_activity:  # last activity actually done
next_activity:  # next mandatory activity (where to resume)
pending_items:  # what is left when paused
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:  # only measured or confirmed by the learner; otherwise empty
observed_minutes_source:  # measured | learner_estimate
module:
overrides:

## Stages
Each stage is completed only with evidence of execution. The practice is completed only after stage 7 and Finish-Practice.
stage_1_status: pending  # 1 Briefing · pending | in_progress | completed
stage_1_evidence:
stage_2_status: pending  # 2 Guided drill
stage_2_evidence:
stage_3_status: pending  # 3 Simulation
stage_3_evidence:
stage_4_status: pending  # 4 Unexpected event
stage_4_evidence:
stage_5_status: pending  # 5 Feedback
stage_5_evidence:
stage_6_status: pending  # 6 Closing (recap, phrases and next step)
stage_6_evidence:
stage_7_status: pending  # 7 Entertainment Lab (part of the practice, before the completion)
stage_7_evidence:

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
Recap, feedback with evidence, limitations and next task. The practice is completed only after stage 7 (Entertainment Lab).
closing_next_step:
closing_saved_reread:  # yes after the final write of Finish-Practice was reread
save_error:  # what failed when saving; never say it was saved

## Entertainment Lab
Prepared and verified before stage 1. The Lab is stage 7: part of the practice and of its length.
lab_title:
lab_channel:
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 30
lab_max_video_seconds: 450  # 25% of the practice: practice_minutes × 60 × 0.25
lab_video_seconds:  # verified duration, in seconds; never unknown
lab_duration_source:  # youtube_page | browser | search_result_with_duration
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verified_at:  # date and time the saved record was reread
lab_blocked_reason:  # only when no valid video was found; stage 7 stays pending
lab_result:  # answers, task and feedback of the Lab done
lab_done_at:
