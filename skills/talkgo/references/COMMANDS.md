# Commands

Commands work on any platform. They are text: the learner types them after calling the skill (`/talkgo Get-Practices` in Claude and `@TalkGo Get-Practices` or `$talkgo:talkgo Get-Practices` in ChatGPT) or in any message of a conversation where the skill is already active. Requests in natural language, in any language ("I want to practice English", "which practices did I do?"), follow the same procedure as the matching command. Command names always stay in English; everything else said to the learner is in the learner's native language.

## Naming convention

Every command is `Verb-Entity`, in English, with a verb from a short list:

| Verb | Meaning |
| --- | --- |
| `Get` | show or list, without changing anything |
| `New` | create |
| `Set` | change (including the default) |
| `Remove` | delete one item, with preview and confirmation |
| `Reset` | delete all records of one type in a language, with preview and confirmation |
| `Backup` | copy the whole Central outside it, only when the learner asks |
| `Start`, `Pause`, `Resume`, `Finish`, `Save` | run a session or the setup |

Entities: `Central` (personal folder with the records), `Language` (target language studied in a Central), `Mission` (scenario with a target date in a language), `Practice` (practice session of a mission), `Diagnostic`, `Progress`, `Lab`, `Stage` (stage of the session), `Phrase` (numbered phrase or dialogue). Commands that list use the plural (`Get-Missions`, `Get-Practices`); those acting on one item use the singular. `Start` alone runs the first-setup wizard (see [START.md](START.md)).

## How to recognize them

- Ignore case, accents, spaces and the hyphen: `Get-Practices`, `get practices` and `GETPRACTICES` are the same command.
- Arguments come in any order after the command, as free text or with a label (`central Personal`, `language English`, `mission london-trip`, `status paused`). A language accepts its name in any language or the tag (`English`, `Inglês`, `inglés`, `en`, `en-US`). `All` applies to every language of the Central. A Central is given by name or by root path/ID; a mission by `mission_id` or title; a practice by its ID (`practice-20261114-01`, prefix from `talkgo.json`).
- During a practice or diagnostic, `HELP` still means asking for help in the exercise (see SKILL.md). To see the command list in the middle of an activity, use `Help-Commands`.

## Context and defaults

The entities form a chain: **Central → Language → Mission → Practice**. Before running a command, resolve only the levels it uses, top to bottom, one at a time:

1. **Given in the command**: use it.
   A context line (`TalkGo · Central: <name> · <link or path> · ...`) in the message, in the project instructions or in the project files counts as given: open that Central, and its language and mission if the line has them. This is how a new chat finds the Central of the previous one.
2. **A single option**: use it and say which one in the answer, without asking.
3. **Several options**: ask, with numbered options and the default first, marked as default and preselected: the learner confirms with "ok" or "yes" (in any language), or picks another. With no default, ask without marking any.
4. **No option**: route to the command that creates it (`New-Central` or `Start`, `Add-Language`, `New-Mission`).

Defaults, set with `Set-Default`:

| Level | Where it lives | When it is set automatically |
| --- | --- | --- |
| Central | Central registry (`default`) | the first Central registered |
| Language | `default_language` in the central state | the first language chosen when creating the Central |
| Mission | `default_missions` in the central state (one per language) | the first mission created in the language |

Exceptions: `Remove-Central` and `Remove-Mission` always ask when there is more than one option, even with a default; and in the `Reset-*` commands the language question also offers `All`. In a conversation where the context was already chosen, reuse it without asking again, unless the learner asks for another. With a local folder, the script returns `"status": "ambiguous"` and the `options` (with `default`) to ask; never choose on your own.

## Run

With a reachable local folder and Python available, use `scripts/central.py` from the skill folder. Output is JSON. Destructive commands always run first without `--confirm` to show the preview.

| Learner's command | Local folder (`python scripts/central.py ...`) |
| --- | --- |
| Get-Central [central] | `info [--central NAME]` |
| New-Central [provider] [folder] [languages] | `create --root PATH [--name NAME] [--provider local\|google-drive\|onedrive] --native CODE LANGUAGE...` |
| Add-Language [languages] [central] | `create --root CENTRAL_PATH LANGUAGE...` |
| Set-Default central\|language\|mission [name] | `default [NAME]`; `default --language LANGUAGE [--central NAME]`; `default --mission ID --language LANGUAGE [--central NAME]` |
| Remove-Central [central] | `remove --central NAME`, then `--confirm NAME` |
| Backup-Central [central] [destination] | `backup [--central NAME] [--destination PATH]` |
| Get-Missions [language] | `info [--central NAME]` (lists `mission_list` per language) |
| Remove-Mission [mission] | `remove-mission ID --language LANGUAGE [--central NAME]`, then `--confirm ID` |
| Get-Practices [language] [mission] [status] | `practices [LANGUAGE] [--mission ID] [--status CODE] [--central NAME]` |
| Reset-Diagnostics [language] | `reset diagnostics [LANGUAGE] [--central NAME]`, then `--confirm` |
| Reset-Practices [language] | `reset practices [LANGUAGE] [--central NAME]`, then `--confirm` |
| Reset-Progress [language] | `reset progress [LANGUAGE] [--central NAME]`, then `--confirm` |

Script messages and keys are in English: translate what you show to the learner into the native language, and show statuses with the `status_label` the script returns. With Google Drive or OneDrive by connector, or in manual mode, follow the same rules with the operations of the [adapter](adapters/) and the sections below.

## Central registry

The registry keeps name, provider (local, google-drive, onedrive), access (local-folder, drive, onedrive, manual), root, languages, native language and which one is the default. It keeps no progress.

- With a persistent file system, the registry lives in `~/.talkgo/centrals.json` (or in the folder given by `TALKGO_HOME`, or in `--registry`). If only one learner folder is connected, use `--registry CONNECTED_FOLDER/.talkgo/centrals.json`.
- A Central created by connector joins the registry with `register --root ID --name NAME --provider google-drive|onedrive --access drive|onedrive --native CODE LANGUAGE...`.
- Without a file system, keep the registry in the platform memory or in the Project instructions, with the learner's agreement, as "TalkGo Centrals: NAME → provider, root, native language; default: NAME". Without either, ask for the Central at the start of the conversation.
- Each Central also describes itself in `talkgo.json` and in the central state (`central_name`, `provider`, `storage`, `root`, `native_language`, `chosen_languages`, `default_language`, `default_missions`). If the registry and the Central disagree, the Central wins; update the registry.

## Help

Show first the installed version ("TalkGo vX.Y.Z", from the "Installed version" line of SKILL.md) and then the table of the Commands section of SKILL.md, grouped by entity, with one example per command, and the current default context (Central, language and mission), if known. Keep the command names and examples in English and write the descriptions in the learner's native language. Run nothing.

## Central

### Get-Central

Read only. For each Central (or only the given one) show: name, whether it is the default, native language, provider (Local, Google Drive, OneDrive), access mode, record format (Markdown or native Google Docs/Sheets), folder path or link, setup status and the languages (marking the default), each with the number of diagnostics and practices and the missions (title, target date, status label, marking the default). If the folder is unreachable, say so instead of omitting the Central. By connector, read `talkgo.json` and the central state and list the languages folder; on Drive, count the session Docs by their prefix.

### New-Central

Creates the Central folder with its whole structure, in the learner's native language. For a new learner, prefer `Start`, which runs this step inside the full setup.

1. Get the native language (from the conversation or by asking, as in [START.md](START.md#1-native-language)), provider, folder and languages (ask what is missing). Default name: the folder name. If the folder is already a Central (it has `talkgo.json`), treat it as `Add-Language`.
2. Choose the adapter with the [selection rules](PERSISTENCE.md#choose-the-adapter). A Google Drive or OneDrive folder synced to the computer uses the local folder adapter with `--provider google-drive` or `onedrive`.
3. Local folder: `create ... --native CODE`. Connector: provisioning of [Drive](adapters/drive.md#provision) or [OneDrive](adapters/onedrive.md) with `--native`, then fill `status: configured`, `central_name`, `provider`, `storage`, `root`, `record_format` (`native` on Drive, `markdown` elsewhere), `chosen_languages` and `default_language` (the first language chosen) in the central state, and then `register`.
4. The first Central registered becomes the default. Give the path or link and go on to the setup in [SKILL.md](../SKILL.md#set-up-and-add-languages).

### Remove-Central

Deletes the whole Central folder. It is irreversible in a local folder.

1. Resolve the Central (with several, always ask). Show the preview: name, provider, path or link, languages and numbers of missions, practices and diagnostics. Say how it will be deleted: trash (recoverable) or permanent deletion (when the connector only offers that).
2. Ask the learner to type the Central name to confirm. Any other answer cancels. Make no backup: if the learner wants a copy, they ask for `Backup-Central` first.
3. Local folder: `remove --confirm NAME`. The script refuses folders without `talkgo.json`, symbolic links, the user's home folder, the drive root and the skill folder.
4. Connector: delete the root folder through the connector's action, as in the [adapter](adapters/drive.md#remove-and-reset): trash, if available (in Claude, `trash_file`); otherwise permanent deletion, already warned in the preview and confirmed by name. Confirm on reread that the folder is gone and update the registry (`remove --confirm NAME --registry-only`). Ask the learner to delete by hand only if the connector cannot delete in any way.
5. If the removed one was the default and a single Central is left, it becomes the default; with several, warn that there is no default.

### Backup-Central

`Backup-Central [central] [destination]` copies the whole Central outside it. It runs only when the learner explicitly asks for a backup; no other command makes backups, and nothing is copied inside the Central.

1. Resolve the Central as in Context and defaults. Destination: the one given by the learner or, without it, the folder that contains the Central (never the Central itself or a subfolder of it). Say the destination and the name of the copy before starting.
2. Local folder: `backup [--central NAME] [--destination PATH]` creates `<folder>-backup-YYYYMMDD-HHMMSS.zip` and checks that every file went in.
3. Connector: create, in the destination, the folder `<Central name> backup YYYYMMDD-HHMMSS` and copy the Central tree into it, folder by folder, with the connector's native copy (Docs and Sheets stay native; in Claude, `copy_file`). Reread and check the number of files per folder.
4. Say where the copy is and how many files it has. The skill never reads backups to answer the learner; they are only for the learner to restore by hand.

## Language

### Add-Language

Adds one or more target languages to an existing Central, without overwriting anything: the same structure as `New-Central`, only for the new languages, with the names of the Central's `talkgo.json`. Local folder: `create --root` with the Central root. Connector: the same provisioning with `--manifest`, which does not recreate what exists. Update `chosen_languages`. The default language does not change; say how to change it with `Set-Default language`. Then route to the diagnostic of the new language (`Start-Diagnostic`).

## Set-Default

`Set-Default central|language|mission [name]` sets the default of one level of the context (see Context and defaults). Without a name, list the options with the current default marked and ask which one. For `mission`, first resolve Central and language: the default mission applies to that language. Write, reread and show the previous and the new default. Local folder: `default ...` (Run table); connector: edit `default_language` or `default_missions` in the central state, and the registry for the Central.

## Mission

Full procedure, template fields and review rules in [MISSIONS.md](MISSIONS.md).

- **`Get-Missions [language] [status]`**: lists the missions of the language (or of every language of the Central, if the learner asks for `All`): title, target date, status label, situations and how many completed practices in each, marking the default. Read only.
- **`New-Mission [language]`**: creates a mission (title, description, required target date, situations, length, frequency and review). The first mission of the language becomes the default.
- **`Set-Mission [mission]`**: changes an existing mission (any field, situations or status `active`, `paused`, `completed`), with revision and history.
- **`Remove-Mission [mission]`**: deletes the mission and its practices, with the same care as the resets: preview (mission, situations, practices to delete and how) and confirmation by `mission_id`, without backup. The deleted practices follow the rule of deleted practices (they leave the progress and every list; see the Reset section). If it was the language's default and a single mission is left, that one becomes the default. To end a mission without deleting its history, first suggest `Set-Mission <mission> status completed`.

## Practice

### Get-Practices

`Get-Practices [language] [mission] [status]` lists the practice sessions, grouped by mission and, inside each mission, by status (in progress first, then completed), with ID, date, situation and, for those in progress, the saved stage, always with the native-language status labels. Without a mission, show every mission of the language (the default first); `status` filters (`prepared`, `running`, `paused`, `completed`, or their labels). Use only the session files that exist in the practices folder and the Practices table of the missions; deleted practices never appear. Read only. End with the next useful step (resume the paused one or start the next).

### Start-Practice

`Start-Practice [language] [mission] [situation] [length]` prepares a new regular practice session of a mission. Also triggered by requests such as "next practice" or "a 5-minute practice".

**One-off length.** If the learner gives a length (`5`, `5min`, `5 minutes`, "half an hour"), it applies only to this practice: the default of the mission and language does not change. Without it, use the mission's length (default 20 minutes). Record the length in `practice_minutes`, `overrides` and `lab_practice_minutes`. Stages 1 to 5 are redistributed in the proportion of the default (briefing 25%, guided drill 10%, simulation 35%, unexpected event 20%, feedback 10%); in very short practices, simplify the scenario, but keep the seven stages, the feedback and the closing. The Lab video follows 30% to 50% of that length (1.5 to 2.5 minutes in a 5-minute practice): with no video linked to the topic in that range, use the closest and record the reason, or give a segment with confirmed start and end.

1. **Context.** Resolve Central, language and mission as in Context and defaults (only `active` missions). No active mission: route to `New-Mission`.
2. **Practice in progress.** If there is a practice in progress in that language (prepared, running or paused), do not create another. Say which one (session, mission and stage) and offer to resume it (`Resume-Practice`) or close it now (`Finish-Practice`, with the [closing check](ENTERTAINMENT-LAB.md#closing-mandatory-check)). Go on to the next only after it is `completed`. The Lab of a completed practice never blocks the next.
3. **Prerequisites.** Without a completed regular diagnostic in the language (closing check passing), route to `Start-Diagnostic`; with a diagnostic `running` or `paused`, offer to resume it first (`Resume-Practice <diagnostic ID>`).
4. **Situation.** The one the learner gives or, without it, the first situation of the mission with the fewest completed practices, as in [MISSIONS.md](MISSIONS.md#choose-the-mission-in-start-practice). When creating the session, write `mission_id` and `situation` in the practice and add its row to the mission's Practices table, with the label for `prepared`.
5. **Create and prepare.** Create the practice session from the practice template of the native language and do the [Entertainment Lab preparation](ENTERTAINMENT-LAB.md#prepare-before-stage-1): YouTube video chosen and verified, record written, reread and checked (`lab.py ready`). If the verification fails, say what failed and ask whether the learner accepts starting without the video.
6. **Stage summary.** Show, in a single message, the mission (title and target date), the situation of this practice, the session ID, the length (saying whether it is one-off) and the roadmap of the seven stages with the time of each: 1 Briefing (goal, scenario and items), 2 Guided drill, 3 Simulation (scenario and role), 4 Unexpected event (without revealing which), 5 Feedback, 6 Closing and 7 Entertainment Lab, optional and suggested after the closing (title, channel, length and link of the verified video).
7. **Save and confirm.** Save the session with `status: prepared`, the practice row in the mission and the active session pointer, reread and confirm that the practice was prepared and saved in the Central, with the session ID. Suggest, in one line, the name of the chat for this practice: `Practice-NNNN-<situation>`, with NNNN the number of this practice in the mission, with four digits (the first is `Practice-0001-Airport check-in`; the word "Practice" and the situation can be in the native language), and, if the current chat is not in a project or already has another activity, recommend opening a new chat in the project with that name and resuming there with `Resume-Practice`. Ask only whether to start with stage 1. If the learner switches to voice mode, the practice starts there with everything ready.

At the end of the practice, after the closing, stage 7 only suggests the video already saved, without preparing anything.

### Resume-Practice

`Resume-Practice [practice]` resumes a practice in progress (prepared or paused) with the same ID. Without arguments, use the language's active session pointer; with more than one practice in progress in the Central, ask which one, listing language, mission and stage. Read the session, check the Lab material (prepare it first, if missing), write `status: running` in the session and the label in the mission, show where it stopped and continue from the saved next question. Also triggered by "resume" or "continue the practice".

### Pause-Practice, Finish-Practice and Save-Practice

They pause, close or save the practice or diagnostic in progress, in text or voice. If more than one session is open and the learner does not say which, ask. The full procedure, including what to do when voice mode cannot write, is in [PHRASES-AND-VOICE.md](PHRASES-AND-VOICE.md#pause-and-complete).

### Start-Lab

`Start-Lab [practice]` opens the Entertainment Lab of the given practice or, without arguments, of the last completed practice of the language. Show the saved material, without a new search, and ask only whether the learner wants to do it now. If the practice started without the video (accepted absence), prepare it now, in text, as in the preparation. The Lab has no status: the command works as many times as the learner wants, and the practice status does not change. If the learner does it, save the result in the same session and confirm, or give `Save-Practice lab` if writing is not possible (see [Finish-Lab](PHRASES-AND-VOICE.md#finish-lab)).

### Get-Stage and Get-Phrase

- **`Get-Stage`**: during a practice or diagnostic, shows the current stage (for example, "Stage 3/7 · Simulation", in the native language), what was done, what is left and the remaining time. Also answers "which stage are we at?". The roadmap and the rule for announcing stages are in SKILL.md (section Practice roadmap).
- **`Get-Phrase <F|D number>`**: repeats, translates or explains a phrase (`Get-Phrase F132`) or a dialogue (`Get-Phrase D145`), including from earlier sessions. Natural requests ("repeat phrase 132", "explain dialogue 145") do the same. Rules in [PHRASES-AND-VOICE.md](PHRASES-AND-VOICE.md#numbering-phrases-and-dialogues).

### Set-VoiceIds

`Set-VoiceIds on|off` turns on or off the announcement of phrase numbers in voice mode and saves the preference in `voice_ids` in the central state.

## Diagnostic and Progress

- **`Start-Diagnostic [language]`**: starts (or resumes, if one is paused) the diagnostic of the language, as in SKILL.md (sections Diagnostic, practice and resume, and Diagnostic saving): the file is created in the Central before the first question, every answer is saved and the closing saves results and derived records and confirms. Pause-Practice, Finish-Practice and Save-Practice also apply to the diagnostic. If the setup is not finished, the closing points back to `Start`.
- **`Get-Progress [language]`**: shows the confirmed progress of the language: missions with target date and completed practices per situation, CEFR by skill with evidence, observed duration, limitations, next practice and next review, as in the Follow-up section of SKILL.md. Read only; tests stay out of the totals.

## Reset-Diagnostics, Reset-Practices and Reset-Progress

They wipe one type of record of a language (or of all) and restore the derived files to their templates. Learner profile and language configuration are not touched; in the missions, only Reset-Practices changes anything, and only the rows of the deleted practices.

Records deleted by a reset or by Remove-Mission stop existing for the skill: they do not appear in any command, list, status, total or summary, and never get marks such as "deleted in reset". No reset makes a backup or creates copies inside the Central; if the learner wants a copy, they ask for `Backup-Central` first.

| Command | Removes | Restored to the template |
| --- | --- | --- |
| Reset-Diagnostics | diagnostic sessions of the language | current profile; active session if it points to a diagnostic |
| Reset-Practices | practice sessions of the language | recent context; active session if it points to a practice; and adjusts, without deleting: in the missions, the rows of those practices leave the Practices table; in the progress log, the practice rows leave and the completed regular practices and observed duration go back to the template |
| Reset-Progress | files of the history folder (except its README) | progress log, current profile, recent context |

Templates are never in the Central, so nothing else is removed. On Drive, sessions and derived records are Docs and the progress log is a Sheet, with the same names without `.md`.

1. Resolve Central and language as in Context and defaults.
2. Show the preview: Central (and whether it is the default), language, list of what will be removed and what goes back to the template, and how the removed items will be deleted (trash or permanent deletion, if the connector only offers that). Say there is no automatic backup. In Reset-Practices, the preview also lists the missions whose practice rows leave and the practice rows that leave the progress log. If Reset-Diagnostics leaves the progress computed with deleted diagnostics, the preview warns about it; also offer Reset-Progress.
3. Ask for explicit confirmation ("yes", in any language). Without it, change nothing.
4. Local folder: `reset ... --confirm`.
5. Connector: delete the removed items through the trash or, if the connector only offers that, by permanent deletion (without asking the learner to delete by hand), reread the folder to confirm and restore the derived records to the template of the native language, rereading each. On Drive: Doc by full replacement; Sheet by clearing both tabs and rewriting the template tables (see the [adapter](adapters/drive.md#remove-and-reset)). In Reset-Practices, also edit the Doc of each affected mission (remove the rows of the deleted practices from the Practices table) and, in the progress Sheet, delete the rows of those practices in the practices tab and restore, in the summary tab, the completed regular practices and the observed duration; reread each one.
6. Say what was reset and what the language's next step is (after Reset-Diagnostics, the initial diagnostic).

Resets never reset `phrase_counter` or `dialogue_counter`: phrase and dialogue numbers stay unique after any reset.
