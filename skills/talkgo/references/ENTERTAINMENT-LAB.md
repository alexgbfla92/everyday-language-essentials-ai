# Entertainment Lab: preparation, suggestion and closing

This is the single procedure of the Entertainment Lab. SKILL.md summarizes the rules; when in doubt, this document wins. Everything said to the learner is in the learner's native language; the video is in the target language.

## Principle

The Lab is part of the practice and has no status of its own: the practice has the status (see Practice status in SKILL.md). The material is prepared **before stage 1** and counts as ready only after the record saved in the session has been reread and checked. The practice ends at the closing (stage 6), as `completed`; right after, in the same message, the Lab is always suggested with the material already saved. Doing the Lab or not never changes the practice. There is no silent preparation at the end: either the material is ready before stage 1, or the learner was told about the failure and accepted starting without the video.

## Record in the session

The Entertainment Lab section of the practice file uses fields with fixed English names (the same in every native language), one per line, as `field: value`:

| Field | Content |
| --- | --- |
| `lab_title`, `lab_channel` | title and channel as they appear on YouTube |
| `lab_url` | only `https://www.youtube.com/watch?v=<ID>` (one video; never another site, a playlist or a channel) |
| `lab_language_variant` | language and variety of the video (e.g. American English) |
| `lab_practice_minutes` | agreed practice length, in minutes |
| `lab_video_minutes` | length of the whole video, in minutes, as shown by YouTube |
| `lab_segment` | `whole` or `mm:ss-mm:ss` with confirmed start and end |
| `lab_off_range_reason` | required if what will be watched is outside 30–50% of the practice |
| `lab_transcript` | `obtained`, `captions_indicated` or `unconfirmed` |
| `lab_practice_items` | items of the practice that the video and the task reuse |
| `lab_question_1` to `lab_question_3` | at least one question, at most three |
| `lab_task` | one short task |
| `lab_verification_source` | `youtube_page`, `browser` or `search`: where title, channel and length came from. Only with `search` can `lab_channel` and `lab_video_minutes` be `unconfirmed` |
| `lab_search_evidence` | only with `search`: the result used (YouTube link, title, channel and length as shown) |
| `lab_verified_at` | date and time the saved record was reread |
| `lab_missing_reason`, `lab_missing_accepted_by_learner` | only when the verification failed: why it failed and when the learner accepted starting without the video |
| `lab_suggested_after_closing` | `yes` when the Lab was suggested right after the closing |
| `lab_result` | answers, task and feedback, only if the learner does the Lab |
| `lab_save_confirmed` | `yes` after saving the result of a Lab done and confirming it to the learner |

There is no Lab status field. Filled material and `lab_verified_at` mean it is ready; `lab_result` means it was done.

The closing of the practice uses: `status: completed`, `closing_saved_reread` (`yes`), `closing_next_step` (text).

## Prepare (before stage 1)

Do this when the practice is created, without questions to the learner, and before showing stage 1:

1. Define the scenario and items of the practice. Search YouTube for a video in the language and variety of the practice, suited to the level and linked to the topic and items.
2. Confirm the video data, trying in this order and stopping at the first that works:
   1. **YouTube page.** With Python: `python scripts/youtube.py info <link> [<link>...]` reads title, channel and length from the page (pass the candidates at once, for a single permission request). Without Python, open the video link. Record `lab_verification_source: youtube_page`.
      - **No network in the command environment** (answer with `"no_network": true`): if the platform lets you ask for approval to run a command with internet access (for example, the ChatGPT desktop app, whose default is network off), ask for it, explaining in one sentence that it is to confirm the channel and length of the video, and run the same command again. Move to search only if approval does not exist, is denied or access stays blocked.
   2. **Browser** available in the session (desktop app browser, Chrome extension): `browser`.
   3. **Search result**, when YouTube is blocked in the environment. Use a video whose youtube.com link (with the ID) appears in a search result, directly or on a page that shows the ID, and whose title is linked to the topic. Record `search` and copy into `lab_search_evidence` what the result shows. What the result does not show stays `unconfirmed`: usually the channel (`lab_channel: unconfirmed`) and the length (`lab_video_minutes: unconfirmed`). Use the whole video (`lab_segment: whole`) and transcript `unconfirmed`, unless the result shows that it exists. Among the candidates, prefer titles that suggest a short conversation linked to the topic of the practice.

   Never invent length, channel, transcript, content or timestamps. The verification fails only if not even search brings a YouTube link with a title linked to the topic.

3. Length: when the length is confirmed, what will be watched (whole video or segment) must be 30% to 50% of the practice (6 to 10 minutes in a 20-minute practice). With length `unconfirmed`, the range cannot be checked: tell the learner at stage 7. The link with the content comes first; if no video linked to the topic fits, choose the closest and fill `lab_off_range_reason`. Use a segment only with confirmed start and end.
4. Prepare up to 3 questions and 1 short task that reuse the items of the practice.
5. Write the section and reread the saved record.
6. Check the reread record. With Python: `python scripts/lab.py ready FILE` (or `-` reading the text of the Doc from standard input) must answer `"can_start": true`. Without Python, check the same items: all fields above filled; link in YouTube format; length within range or reason filled; valid segment inside the video; transcript with one of the three values; 1 to 3 questions; task.
7. Write `lab_verified_at` and mark stage 0 of the roadmap table. Only then show the roadmap, with the title of the video, and start stage 1.

### If the verification fails

Failure is any case in which step 6 does not pass: no search tool, no video confirmed by page, browser or search result, a link outside YouTube, unconfirmed length or segment, or a record that could not be written and reread.

1. **Before starting the practice**, tell the learner in one or two sentences what failed and ask whether they want to start the practice without the Entertainment Lab video, to be prepared later. Do not start stage 1 before the answer.
2. If they accept: write `lab_missing_reason` and `lab_missing_accepted_by_learner` (with the date), reread and go on. If not: offer to try again or to prepare it in text (`Start-Practice <language>`), without starting the practice.
3. Never write `lab_verified_at` without step 6 and never fill `lab_missing_accepted_by_learner` without the learner's answer.

## Stage 7 (suggest after the closing)

1. In the same message that confirms the completed practice, read the saved section and show: title and channel, link, segment and length, the task and the questions. If channel or length are `unconfirmed`, say so in a few words (for example, that the length is unconfirmed because YouTube was unreachable during preparation). Do no new search and do not ask about topic or length.
2. Ask a single question: whether the learner wants to do the Lab now.
3. If the practice started without the video (accepted absence), say so and ask whether the learner wants you to prepare it now, in text. Only here is a search at the end allowed, and only if the learner asks.
4. If the learner does the Lab, write `lab_result` (Finish-Lab), reread and confirm. If not, write nothing: the practice stays `completed` and `Start-Lab` opens the material later.

## Closing (mandatory check)

Before confirming the closing of any regular practice, including when the learner asks to stop in the middle, check the four items and fix what is missing:

1. **Status**: `status: completed`.
2. **Practice saved and reread**: `closing_saved_reread: yes`, after Finish-Practice.
3. **Next step given**: `closing_next_step` filled and told to the learner.
4. **Lab suggested**: `lab_suggested_after_closing: yes`, written in the same write as Finish-Practice, with the suggestion made in the same message.

With Python: `python scripts/lab.py closing FILE` must answer `"can_close": true`. The learner is never required to do the Lab, and the answer never changes the practice status. After a "do you want to stop?" from the learner, never skip the check.

## Voice and resume

- **Starting in voice.** If the session can search, write and reread in voice, prepare as usual. If it cannot, say that the Lab cannot be prepared or saved in voice mode, never claim anything is ready or saved, and route to text: leave voice mode and send `Start-Practice <language>` in this conversation, then go back to voice. The practice starts in voice without the material only if the learner accepts starting without the video, and that acceptance must be recorded (in text, with Save-Practice, if voice cannot write).
- **Resume.** When resuming a practice, read the Lab section before continuing the saved stage. If the material is not ready and no absence was accepted, prepare it now (or follow the failure path) before going on. If the practice is resumed at stage 6, do the closing and the check.
- **Voice without access to the record.** Never say the material is ready or that anything was saved. State the limitation and give the text command: `Start-Practice <language>` to prepare, or `Save-Practice pause|finish|lab <session> <first F>-<last F>` to save.

## Save confirmation

Only the result of a Lab done is saved after the closing. It follows the save guarantee of SKILL.md: write, reread and confirm it was saved in the Central (session and "Lab result"); with no write possible, say it was not saved and give `Save-Practice lab`.
