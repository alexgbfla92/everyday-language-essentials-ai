# Entertainment Lab: preparation, stage 7 and completion

This is the single procedure of the Entertainment Lab. SKILL.md summarizes the rules; when in doubt, this document wins. Everything said to the learner is in the learner's native language; the video is in the target language.

## Principle

The Lab is **stage 7 of the practice**, part of the practice and of its length. It is not an optional suggestion after the end: the practice is completed only after stage 7, by Finish-Practice. The material is prepared **before stage 1** and counts as valid only after the record saved in the session has been reread and checked. Stage 7 has a state like every stage (`stage_7_status`: `pending`, `in_progress`, `completed`), and becomes `completed` only with the Lab result written.

## Length rules

- Practice: 30 minutes by default, never more than 35 (`practice_minutes`); the Lab is inside that length.
- Video: at most 25% of the planned length: `max_video_seconds = practice_minutes × 60 × 0.25` (450 s = 7 min 30 s in 30 minutes; 300 s in 20 minutes). Record it in `lab_max_video_seconds`.
- The **whole** video must fit the limit; segments of longer videos are not used.
- A video with an unknown duration, or longer than the limit, is never official material. Search another one; if none fits, record the block (below).

Check with `python scripts/practice.py video <practice minutes> <video seconds> <source>`.

## Record in the session

The Entertainment Lab section of the practice file uses fields with fixed English names (the same in every native language), one per line, as `field: value`:

| Field | Content |
| --- | --- |
| `lab_title`, `lab_channel` | title and channel as they appear on YouTube (the channel may stay empty if the source does not show it) |
| `lab_url` | only `https://www.youtube.com/watch?v=<ID>` (one video; never another site, a playlist or a channel) |
| `lab_language_variant` | language and variety of the video (e.g. American English) |
| `lab_practice_minutes` | agreed practice length, in minutes (the same as `practice_minutes`) |
| `lab_max_video_seconds` | `practice_minutes × 60 × 0.25` |
| `lab_video_seconds` | real duration of the whole video, in seconds, verified; never empty, estimated or `unconfirmed` |
| `lab_duration_source` | `youtube_page` (`scripts/youtube.py info`), `browser`, or `search_result_with_duration` (a search result that shows the exact duration of that video) |
| `lab_transcript` | `obtained`, `captions_indicated` or `unconfirmed` |
| `lab_practice_items` | items of the practice that the video and the activity reuse |
| `lab_question_1` to `lab_question_3` | comprehension questions: at least one, at most three |
| `lab_task` | one short task |
| `lab_verified_at` | date and time the saved record was reread |
| `lab_blocked_reason` | only when no valid video was found: why (stage 7 stays `pending`) |
| `lab_result` | answers, task and brief feedback of the Lab done (stage 7 evidence) |
| `lab_done_at` | date and time the Lab was done |

## Prepare (before stage 1)

Do this when the practice is created, without questions to the learner, and before showing stage 1:

1. Define the scenario and items of the practice. Search YouTube for a video in the language and variety of the practice, suited to the level, linked to the topic and items, and short enough for the limit.
2. Verify the real duration, trying in this order and stopping at the first that works:
   1. **YouTube page.** With Python: `python scripts/youtube.py info <link> [<link>...]` reads title, channel and duration (pass the candidates at once, for a single permission request). If the command has no network (`"no_network": true`) and the platform lets you ask for approval to run it with internet access, ask for it in one sentence and run it again. Record `lab_duration_source: youtube_page`.
   2. **Browser** available in the session: open the video page and read the duration. Record `browser`.
   3. **Search result that shows the exact duration** of that video (for example "7:12" next to the YouTube link). Record `search_result_with_duration`. A result without the duration does not verify anything.
3. Reject every candidate whose duration is unknown or above `lab_max_video_seconds`, and try another one. Never invent duration, channel, transcript, content or timestamps, and never present a video as verified when its duration was not confirmed.
4. Prepare 1 to 3 comprehension questions and 1 short task that reuse the items of the practice.
5. Write the section and reread the saved record. Check it: `python scripts/practice.py lab FILE` (or `-` with the text of the Doc) must answer `"can_start": true`; without Python, check the same items by hand.
6. Write `lab_verified_at`. Only then show the roadmap (with the title, link and verified duration of the video) and start stage 1.

### If no valid video is found

1. **Before stage 1**, tell the learner in one or two sentences what blocked the Lab (no video with a verified duration of at most N minutes, no search tool…).
2. Write `lab_blocked_reason`, reread, and say that the practice can run stages 1 to 6 now, but will only be completed after the Lab: stage 7 stays `pending` and the practice is paused at the end of stage 6 until a valid video is prepared (`/talkgo Start-Lab` or `/talkgo Resume-Practice <session>` searches again).
3. Never fill `lab_video_seconds` or `lab_verified_at` without a verified duration.

## Stage 7 (inside the practice, right after stage 6)

1. In the message that ends stage 6, start stage 7: read the saved section and show the title, the direct clickable link, the verified duration, the questions and the task. Do no new search and do not ask about topic or length.
2. Write `stage_7_status: in_progress` (silently) and wait for the learner to watch and answer. Answer questions about the video only from text actually accessed.
3. Give brief feedback on the answers and the task. Write, in one write: `lab_result`, `lab_done_at`, `stage_7_status: completed` and `stage_7_evidence`, plus the numbered phrases of the Lab. Reread.
4. Go straight on to the completion (below).
5. If the learner cannot do it now (has to leave, cannot watch in voice mode, the material is blocked), run Pause-Practice: `status: paused`, stage 7 `pending`, `pending_items` with what is missing, reread and confirm, and say how to finish it later. The practice is **not** completed.

## Completion (Finish-Practice, mandatory check)

Finish-Practice records `completed` only after stage 7. Before confirming, check:

1. **Seven stages**: `stage_1_status` to `stage_7_status` all `completed`, each with `stage_N_evidence`.
2. **Lab done**: `lab_result` and `lab_done_at` filled.
3. **Length**: `practice_minutes` at most 35; `observed_minutes` only with `observed_minutes_source` (`measured`, or `learner_estimate` after asking the learner); otherwise empty.
4. **Next step**: `closing_next_step` filled and told to the learner.
5. **Saved**: the final write reread (`closing_saved_reread: yes`) and no `save_error`.

With Python: `python scripts/practice.py finish FILE` (also `python scripts/lab.py closing FILE`) must answer `"can_complete": true`. If it does not, do not write `status: completed`: say which stages are pending and continue from the first one. If the final write fails, say it was not saved and give `/talkgo Save-Practice finish`.

## Voice and resume

- **Starting in voice.** If the session can search, write and reread in voice, prepare as usual. If it cannot, say that the Lab cannot be prepared or saved in voice mode, never claim anything is ready or saved, and route to text: leave voice mode and send `/talkgo Start-Practice <language>` in this conversation, then go back to voice.
- **Resume.** When resuming a practice, read the stage states and the Lab section before continuing. If the material is not valid, prepare it now (or record the block) before going on. If stages 1 to 6 are completed, resume directly at stage 7.
- **Voice without access to the record.** Never say the material is ready or that anything was saved. State the limitation and give the text command: `/talkgo Start-Practice <language>` to prepare, or `/talkgo Save-Practice pause|finish|lab <session> <first F>-<last F>` to save.
