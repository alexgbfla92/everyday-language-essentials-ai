# Persistence in the learner's personal folder

This protocol applies to any platform (Claude, ChatGPT or another). Only the adapter that lists, creates, writes and rereads files changes between them. In this document, "ID" is the stable identifier the adapter uses: the file ID on Google Drive or the path relative to the root in a local folder.

## Names come from the Central

Every Central has a fixed file at its root, `talkgo.json`, with the learner's `native_language` and the names of every folder and file of that Central in that language (`paths`), the session ID prefixes (`prefixes`), the target language folders (`targets`), the progress sheet tabs (`tabs`) and the display labels of statuses (`status`, `mission_status`, `stage_status`; a Central created before stage states existed takes `stage_status` from its locale). Read it before any other operation and find every record through it, never through a hard-coded name. In this document records are called by their logical name:

| Logical name | Key in `paths` | Content |
| --- | --- | --- |
| central state | `config` / `central_state` | global state, defaults, counters and index |
| learner profile | `config` / `learner_profile` | name, chosen languages, setup progress |
| language folder | `languages` + `targets[tag]` | one per target language |
| active session, recent context, current profile | `lang_state` / `active_session`, `recent_context`, `current_profile` | derived state of the language |
| diagnostics, practices, missions | `diagnostics`, `practices`, `missions` | session records and missions |
| progress log, history | `progress` / `progress_log`, `history` | confirmed summary (a Sheet on Drive) and cycle summaries |

The templates of every record, already written in the learner's native language, are in `assets/locales/<code>/templates/` (`<code>` is the `locale` of `talkgo.json`). Fields inside records (`status:`, `mission_id:`, `lab_*`…) are machine keys in English and must never be translated; status values are codes (`prepared`, `running`, `paused`, `completed`; missions `active`, `paused`, `completed`; practice stages `pending`, `in_progress`, `completed`). Everything the learner reads (titles, labels, notes, table headers, the Practices column of a mission) is in the native language, and statuses are shown with the labels of `talkgo.json`.

Folders and logical paths are the same in every adapter. The file format too, with one exception: on Google Drive by connector, files written during use are native Google Docs or Google Sheets, without the `.md` extension in the name (see the [format table](adapters/drive.md#formats)). A local folder (including Drive or OneDrive synced to the computer), OneDrive by connector and manual mode use Markdown only. The `record_format` field of the central state says which case applies (`markdown` or `native`).

## Choose the adapter

Follow the first rule that applies:

1. If the central state of the given folder already records `storage`, use that adapter. To switch storage, create another Central.
2. If the learner explicitly chooses Drive or a local folder, use that choice, as long as the adapter passes the capability check of its guide.
3. If the session can read and write in a learner's folder that persists after the chat (the learner's computer, a folder connected to the app, a local repository, a Google Drive or OneDrive folder synced to the computer), use the [local folder](adapters/local-folder.md) adapter and record the `provider` (local, google-drive or onedrive).
4. If the learner gives a cloud folder and the session has a connector that creates and updates files, use [Google Drive](adapters/drive.md) or [OneDrive](adapters/onedrive.md).
5. Otherwise, use [manual mode](adapters/manual.md) and tell the learner, in one sentence, what is missing to save automatically.

Never choose by the platform's name. Choose by what the session demonstrably can do. A temporary chat workspace, which disappears when the conversation ends, is never a write destination. A folder synced by Google Drive for desktop counts as a local folder and lets different platforms read the same records, as long as only one writes at a time.

## Prepare and reconcile

1. Get the identification of the learner's dedicated folder, as the adapter says. If the learner gives only a personal parent, list its children, create or reuse a single `TalkGo` subfolder and use it as the root. The package, original files, backups made by Backup-Central and their descendants are read-only, including the skill folder itself. Refuse an ambiguous destination, a shortcut or a personal folder that cannot be identified. Never use a global search by name to choose a write destination.
2. Before creating any record in an existing folder, read `talkgo.json` and the central state if they exist: indexed IDs, languages, missions and pending steps. Keep unknown fields. A name collision requires the learner to identify the right object.
3. Create the structure with the adapter's provisioning ([Drive](adapters/drive.md#provision) or [local folder](adapters/local-folder.md#provision)), in the learner's native language for a new Central. The rules are shared, and on Drive each item is created in the format of the format table, parents before children. Existing files keep the learner's data: never apply a template over an existing file. With homonyms or an unexpected type (a file where a folder is expected), stop and identify the right object. A lost response requires a new listing before any retry.
4. On reread, check name, type, parent and content of every created object. Repeat the provisioning until it has nothing left to create.
5. Write in the central state `status: configured`, `central_name`, `provider` (local, google-drive or onedrive), the chosen `storage` (local-folder, drive, onedrive or manual), the root, `record_format`, `default_language`, chosen languages, setup step, the confirmed index path → ID and format (Index table) and the date of the last check. Keep previous fields. To add a language, merge the new index into the existing one. Validate writing by recording a unique marker of the run in `last_write_check` of the central state itself, through the adapter's edit (on Drive, native Doc edit with conditional write), then reread and compare. Confirm the setup only after the reread. Tell the learner where the personal folder is (Drive link or local path) so it can be linked to the Project or resumed in another chat.

## Authority of the records

Preferences, missions and reviews belong to the language branch. The package provides the shared teaching modules in `assets/modules/`, the defaults and methodology in `assets/reference/` and the notes of each target language in `assets/targets/`; they are read from the skill, never copied into the Central. Suggestions and defaults become the learner's facts only after confirmation.

A session uses `<prefix>-YYYYMMDD-NN` (the `practice` or `diagnostic` prefix of `talkgo.json`; `.md` in Markdown, no extension for a Drive Doc), with a free NN in the right parent, created from the practice or diagnostic template of the native language. Record the logical path, file ID, mission ID, variety, modality, test/regular, eligibility, revision, last operation, status and observed time. Number each phrase in the target language with the language's global number (F) and each dialogue (D), as in [phrases and voice](PHRASES-AND-VOICE.md), and keep speaker, mode and support. The checkpoint includes the seven stage states and their evidence, `checkpoint_seq`, `last_activity` (last activity actually done), `next_activity`, `pending_items`, last exchange, last F and next question. Session and diagnostic files are the sources of the observations. The progress log is the confirmed summary of the language. The three state files of the language are derived and keep ID, source revision and date. Use the history folder for summaries of long cycles, keeping the sources: each summary is a new Markdown file, created once and never edited. Preferences and adjustments of the language (duration, pace, variety) live in the current profile.

## Save, resume and repair

**Official session and checkpoints.** The Google Drive (or the Central's adapter) is the official store; the conversation memory is never the source. Before starting or resuming a practice, read the practice record and its checkpoint from the Central; if they cannot be read, it is not an official session: say what failed, never invent the state, and offer to try again. Each checkpoint written increases `checkpoint_seq` by one; before writing, reread the record and never write a checkpoint whose `checkpoint_seq` is lower than or equal to the saved one (`python scripts/practice.py newer CURRENT CANDIDATE`), so an older record never replaces a newer one. Never delete or rewrite checkpoints, evaluations, dialogues, evidence or progress rows, never renumber practices, and keep the original practice ID when resuming. A practice written by an earlier version keeps every existing line: `python scripts/practice.py migrate FILE` only appends the missing stage fields (inferred from the roadmap table and `current_stage`) to an open practice, is safe to run again and never touches a completed one.

**Failures.** If a read or write fails, or the reread differs, tell the learner what failed and never say it was saved; write `save_error` when the file can still be written, keep the checkpoint copyable in the conversation and give `/talkgo Save-Practice` for when access returns.


Read the record and its base revision. Prepare an operation with a stable ID per answer or completion. Reread right before writing. If another revision intervened, reconcile by the operation ID and the turns before combining changes. Where there is a conditional write (Google Docs with `requiredRevisionId`), send the write conditioned on the revision read; if it is refused, reread and reconcile before retrying. Where there is none (local folder, Sheets, Markdown), use a single writing chat per session and a single provisioner per root. Never promise mutual exclusion between devices. If there is a conflict, suspend writes until the right version is reconciled.

Update the same ID, in the same format, through the adapter's edit operation. Reread revision, operation, evidence and next question. The next question can be shown as soon as the session is confirmed. An ordinary answer updates only the active source. Requests such as repeating or explaining require a write only when they change the evidence, the recorded support or the resume point.

When creating or switching sessions, publish and check the active session pointer before the first activity. Keep the file ID in it. On every resume, read the source by that ID and use the source's last revision and next question even if the summary lags behind. If creation was interrupted before the pointer was published, look for open sessions in the language folder before creating another. If the conversation has numbered phrases above the last one saved in the session (for example, a voice segment that was not saved), offer Save-Practice before going on.

When pausing, write the resume point in the source and adjust only the pointer whose state changed. On completion, gather the last turn, feedback and final status in the same write of the source, then consolidate the affected derived records as a logical batch. Each changed file gets its own update and check. Never rewrite defaults, global configuration, indexes or caches whose data did not change. Keep the pointer until the progress and other derived records are confirmed, so an interruption allows the closing to be repaired; finalize the pointer last. If the source is completed while the pointer is still active, reconcile the completion before starting the next session. During setup, publish the pointer of the mission being built before collecting answers and use the pointed document to resume the pending question.

For independent events, run reads in parallel when the interface allows. The confirmed record remains the durability limit: never keep answers only in the conversation nor announce a later sync. The current interface requires the agent to finish the operation and check the content.

When consolidating derived records of the same language: update by session ID and revision, replacing the previous entry; reread each derived record. A diagnostic updates the assessment by skill, a completed regular practice counts once, a pause only updates the resume point and a test never changes the metrics. If an intermediate write fails, resume from the confirmed session and repair only the missing derived records. In a report chat, flag divergences and route the repair to the resume flow.

If there is no write or reread, show the exact stage, the last confirmed ID/revision and a copyable checkpoint of the pending answer. Offer manual import of the content. When access returns, confirm the file in storage before announcing saved progress.
