# Beta validation

Run `python -B -m unittest discover -s tests` at the root. The suite uses fictional listings and tests the operations proposed to the connector: the localized layout of every native language (`talkgo.json`), the format of each path on Drive (Markdown, JSON, Google Doc or Google Sheet), the CSV and tabs generated from the template, reconciliation with native MIME types without recreating, the wrong-type conflict and tab setup after an interruption. It also creates temporary local folders to test `--local` mode: the same tree as Drive, faithful copies of the templates, repeated runs without overwriting, conflicts and refusal of symbolic links and of the skill folder. The command suite (`tests/test_central.py`) covers the registry and default Central, ambiguity questions, creating a Central and adding a language, preview and confirmation of the three resets (no backup), Backup-Central outside the Central and the refusals of Remove on folders that are not Centrals. `python3 tools/render_locales.py --check` confirms the rendered templates match the masters and the locales. The suite does not measure network reliability or check the model's interaction with a learner.

The names below are the English ones (native language `en`). With another native language, folder, file, tab and status names follow `assets/locales/<code>/locale.json`.

## Start wizard and native language

1. In a new chat, send only `Start`: the first message asks the native language in English, Spanish, Portuguese and French, and never says it was read from the browser or account.
2. Start again by writing a sentence in Portuguese ("Quero começar a praticar inglês"): the question comes in Portuguese, with Portuguese (Brazil) offered to confirm.
3. With native `pt-BR`, follow the wizard: Central created with `talkgo.json` at the root, folder, file and tab names as in `assets/locales/pt-BR/locale.json` (for example `Idiomas/Inglês/Missões`). Every message is in Portuguese; command names stay in English.
4. `Help` in that Central: descriptions and examples in Portuguese, commands in English, installed version shown.
5. Right after choosing the languages, the diagnostic of the default language starts in the same chat, with no question about chat, length or whether to start.
6. Close the chat after step 3 of the wizard and send `Start` in another chat: it resumes from the saved `setup_step` instead of starting over.
7. At the end, the wizard suggests a project named after the mission (for example `English-Travel`), a `Progress` chat, one `Practice-0001-<situation>` chat with `Resume-Practice <ID>` and how to rename chats in Claude and ChatGPT. Stage 1 of the practice did not start in the wizard.
8. Every question of the wizard with likely answers (native language, storage, folder, languages, default language) comes as options to pick, single or multiple, with "Other" for free text: as an option card where the platform shows one, as a numbered list otherwise (a number answers it).
9. With a native language without a locale (for example `ja`): the wizard says once that folder and file names will be in English and keeps every message in Japanese.

## Native Drive rehearsal

1. In Claude, with the Google Drive, Google Docs and Google Sheets connectors on, run `New-Central` on Google Drive with an empty folder and English. Check the folder: `talkgo.json`; `central-state`, `learner-profile` and the three files of `State/` as Google Docs without `.md`; `progress-log` as a Google Sheet with the tabs `Summary` and `Practices` (no "Untitled"); `History/README.md` as Markdown. No reference assets are copied into the Central.
2. Open `central-state` and check the write-check marker and the Index table with IDs and formats.
3. Interrupt a setup in the middle (close the chat) and run it again: nothing may be duplicated and the sheet tabs must be completed.
4. Do a short diagnostic and a practice: the `diagnostic-*` and `practice-*` Docs receive every answer, keeping the same ID. Edit the session Doc by hand during the practice and confirm that the skill's next write is refused by the revision, reread and reconciled.
5. Finish the practice: one new row in the `Practices` tab and the count in `Summary`, without duplicating when the consolidation is repeated.
6. Resume from a phone and a tablet: the same pending question.
7. `Reset-Practices English`: no backup or copy created in the Central, practice Docs in the trash, `recent-context` back to the template, rows of those practices out of the missions' Practices table and out of the `Practices` tab. Afterwards, `Get-Central` and "which practices did I do in English?" never mention the deleted practices or any "deleted in reset" status. `Reset-Progress English`: `Summary` and `Practices` tabs equal to the template.
8. `Remove-Central`: root folder in the Drive trash.
9. Repeat 1, 4 and 5 in ChatGPT on the same Central and on a new Central created by it.

## Acceptance in a personal rehearsal folder

Repeat the script below for each combination of platform and adapter that is published: first the Claude app with native Google Drive, then ChatGPT with native Google Drive, then Claude Code and Codex with a local folder.

1. Through the account's install mechanism, call the skill without the clone open. Give an empty destination. Create Spanish and English. Check metadata, parents, MIME type, bytes, IDs and the configuration revision after rereading.
2. Repeat the setup. Compare the IDs. Add French; check that the previous data is intact.
3. Ask for a practice without a diagnostic and then with a short screening. Observe the routing. Complete a regular diagnostic in text, check the noted limitations and approve the mission. Do a test session and compare the metrics before and after.
4. Pause a practice after the learner's second sentence. On the phone, recover the same ID, revision and question. In voice, confirm what was actually observed. Finish and check a single contribution to progress.
5. Cut access after saving the session and before updating progress. Check the checkpoint, reconcile by operation ID and validate the repair. With a second writer active, record conflicts and suspend the operation if the connector does not give enough guarantees.
6. In a progress chat, compare the evidence of one language without changing scores. In the Lab, test a video without an accessible transcript.

Record interface, version, date, actions and results in a test environment. Publishing to other accounts depends on this rehearsal.

## Latency and recovery

In a personal rehearsal folder, note the operations and waiting time of three ordinary turns before and after a change, in the same interface. During an open practice, an answer that changes the state must produce a single write to the session file, checked by rereading. Check by ID that the summary, the profile and the global index received no write in that turn. In another chat, use the existing pointer and check that the next recovered question matches the last confirmed answer. Interrupt the closing after the source and before the progress log; when resuming, check the repair, a single count and the closing of the pointer.

## Numbered phrases and voice rehearsal

1. In text, check that every AI sentence in the target language comes with `[Fn]`, that every answer opens with the numbers of the learner's sentences and that dialogues come with `[Dn]`. Ask "repeat sentence N", "explain the structure of dialogue N" and "translate N", including from an earlier session.
2. Run Reset-Practices and a new practice: the numbers continue from where they stopped.
3. In voice, check the short announcement of the numbers and `Set-VoiceIds off`.
4. In voice, say "pause": if writing works, the session becomes `paused` with the next question; if not, the AI does not say it saved and gives the Save-Practice command. Leave voice mode, send the command and check that the voice turns were saved with mode `voice`.
5. Repeat with "finish the practice": session `completed`, progress consolidated once.
6. Close voice mode without pausing and go back to text: the skill must offer Save-Practice.

## Practice roadmap and Entertainment Lab rehearsal

The mechanical check is in `skills/talkgo/scripts/lab.py` (`ready` before stage 1, `closing` before closing) and is covered by `tests/test_lab.py`. On each platform, also rehearse the behavior:

1. **Video available** (also with YouTube blocked: the confirmation comes from a youtube.com search result, with `lab_verification_source: search`). Before stage 1, the session has status `prepared` and the Lab section has a link `https://www.youtube.com/watch?v=…`, length of 30–50% of the practice (or the closest, with a reason), questions, task and `lab_verified_at`; `lab.py ready` passes; the opening roadmap shows the title.
2. **Search failure.** Without search (or without a confirmed video), the AI says what failed and asks whether the learner accepts starting without the video **before** stage 1; stage 1 starts only after the "yes", saved in `lab_missing_accepted_by_learner`.
3. **Start in voice.** Without search and write access, the AI states the limitation, never claims anything is ready or saved and routes to `Start-Practice <language>` in text.
4. **Resume.** When resuming a practice without the Lab material prepared, the AI prepares it (or follows the failure path) before continuing the saved stage.
5. **Request to stop.** "I want to stop" in the middle of the practice leads to stage 6 (save, reread, next step) and stage 7 (saved material, no new search, one single question).
6. **Lab after the closing.** The practice becomes `completed` at the closing, with `lab_suggested_after_closing: yes`, and `lab.py closing` passes before the learner answers; the same message suggests the Lab. Declining writes nothing; doing it writes only `lab_result`. No Lab status appears. `Start-Lab` opens the same material later.
7. **Start-Practice.** With two languages in progress, it asks which one; with a paused practice in the language, it asks to finish (or resume) it first; otherwise it creates the practice, prepares and verifies the Lab, shows the seven-stage summary with the video link, saves, confirms and asks only "Shall we start with stage 1?". With a one-off length (`Start-Practice English 5min`), the summary shows 5 minutes and proportional stages, the Lab aims at 1.5–2.5 minutes and the mission default stays 20 minutes.

## Missions rehearsal

1. `Get-Missions English` lists the missions (title, target date, status and completed practices), with the default marked.
2. `New-Mission English` without a diagnostic routes to the diagnostic; with a diagnostic, it asks only what is missing (title, description, required target date, situations), proposes the situations and saves `Missions/<mission_id>` after approval, confirming that the mission was saved.
3. `Set-Mission` with two missions asks which one, with the default marked and preselected; it shows the summary, applies the approved change without deleting practices done, adds one to the revision and records the history.
4. `Start-Practice English` with two active missions asks which one; with `mission <id>` it uses that one; it picks the situation with the fewest completed practices (or the one asked for); the practice saves `mission_id` and `situation`, and its row in the mission goes `prepared`, then `running` and, when paused, `paused`; when finished, `completed` (always shown with the native labels).
5. `Get-Central` lists the missions of each language with target date and status.

## Commands and context rehearsal

1. `Help` shows the version, the default context (Central, language and mission) and the table grouped by entity, only with `Verb-Entity` names, descriptions in the native language.
2. With two Centrals, `Get-Practices` asks for the Central with the default marked "(default)"; "ok" confirms the default. With one Central and one language, it asks nothing and says which ones it used.
3. `Set-Default mission <id>` writes `default_missions` for the language; the next `Start-Practice` preselects that mission in its question.
4. `Get-Practices English` groups by mission and status, shows the stage of practices in progress and never shows deleted practices.
5. `Resume-Practice` without an argument resumes the practice of the active-session pointer; with two practices in progress in different languages, it asks which one.
6. `Remove-Mission` shows the preview with the practices that will be deleted, makes no backup and deletes only after the `mission_id` is typed; afterwards, `Get-Practices` and `Get-Progress` never mention those practices.
7. No Reset-* or Remove-* creates a backup folder or file. `Backup-Central` runs only when asked, writes outside the Central and says where the copy is and how many files it has.
