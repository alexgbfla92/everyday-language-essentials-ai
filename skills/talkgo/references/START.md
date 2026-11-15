# Start: first-setup wizard

`Start` is the first command a new learner runs. It guides the learner, one question at a time, through every step needed to begin practicing: native language → Central → target languages → diagnostic → first mission → first practice → projects and chats. Each step reuses the procedure of the matching command; this document only sets the order, what to ask and what to say.

Rules for the whole wizard:

- One question per message, short, in the learner's native language (from step 1 on). Show progress as "Step N of 7" in the native language.
- Record the current step in `setup_step` of the learner profile as soon as the Central exists, and reread it. `Start` again (in this or another chat) resumes from the saved step instead of starting over; before the Central exists, ask whether a Central already exists and, if so, read it.
- If the learner already has a Central with languages, missions or practices, skip what is done, say so in one line and go to the first missing step. If everything is done, go straight to step 7.
- Never skip the confirmations of the underlying commands (the write check, the save confirmations, the Lab verification).

## 1. Native language

1. Detect the language of the learner's messages. If the learner wrote a sentence, ask in that language: "Which is your native language? I will use it for every message, folder and file of your Central. Commands stay in English." Offer it as the detected option to confirm.
2. If the learner wrote only `Start` (or anything that does not reveal a language), ask the same question in English, Spanish, Portuguese and French in one message, one short line each.
3. Never say the language was read from the browser or account settings: the skill cannot access them.
4. Keep the answer as a language tag (`pt-BR`, `es`, `fr`, `de`, `en`, `ja`…). Folder and file names follow `assets/locales/` for `en`, `pt-BR`, `es`, `fr` and `de`; for any other language, say once that folder and file names will be in English and that everything else will be in the native language.
5. From this answer on, speak only the native language (plus the target language inside practices).

## 2. Central

1. Explain in two sentences what the Central is: a folder of the learner's own that keeps diagnostics, missions, practices and progress, so any chat and any device can resume.
2. Ask where to create it, recommending Google Drive because it works on web, desktop and phone:
   - **Google Drive** by connector (in Claude: the Google Drive, Google Docs and Google Sheets connectors; in ChatGPT: the Google Drive app with edit permission). If the connectors are missing, say exactly which ones to turn on, and wait.
   - **Folder on the computer** (including a Google Drive or OneDrive folder synced to it), when the session can write there.
   - **Manual mode**, only if neither works.
3. Ask for the folder (or offer to create a `TalkGo` folder in the root of the learner's Drive) and the Central name (default: the folder name).
4. Run `New-Central` with the native language from step 1 ([COMMANDS.md](COMMANDS.md#new-central)), then confirm with the folder link or path. Save `setup_step: languages`.

## 3. Target languages

1. Ask which languages the learner wants to practice: English (American), Spanish (Spain) and French (France), one or more.
2. Add them (`New-Central` already created the first ones; others with `Add-Language`). The first one chosen becomes the default language; if there are several, say which one is the default and that `Set-Default language` changes it.
3. Save `setup_step: diagnostic`.

## 4. Diagnostic

1. Explain in one or two sentences that a short diagnostic (30 minutes by default, adjustable) shows the learner's level in each skill and is needed before the first mission, so missions and practices fit the learner.
2. Offer two options: do it now, in this chat, or in a chat of its own (recommended, named for example `English-Diagnostic`), started with `Start-Diagnostic <language>` and then `Start` again to continue the setup.
3. Run `Start-Diagnostic` for the default language. With more than one language, do one diagnostic now and say that the others can be done later with `Start-Diagnostic <language>`.
4. When it is completed and saved, save `setup_step: mission`.

## 5. First mission

1. Explain that a mission is what the learner wants to get ready for, by a date, in concrete situations. Give one example in the native language: "Get ready for a trip to London by 20/04/2027: airport, immigration, public transport and restaurants".
2. Run `New-Mission` for the default language ([MISSIONS.md](MISSIONS.md#new-mission)): title, description, target date (required), situations, length and frequency. It becomes the default mission.
3. Save `setup_step: practice`.

## 6. First practice

1. Run `Start-Practice` for the new mission ([COMMANDS.md](COMMANDS.md#start-practice)): first situation, Lab prepared and verified, seven-stage summary, practice saved as prepared.
2. Do not start stage 1 here. Save `setup_step: projects` and go to step 7: the practice is meant to run in its own chat.

## 7. Projects and chats

Close the wizard with one organized message, in the native language, that the learner can follow on any platform. Use the learner's real data (language, mission, practice ID, Central). Save `setup_step: done` before sending it.

1. **Create a project.** Explain that Claude and ChatGPT both let you create projects, and that a project keeps the chats of one goal together. Suggest a name linked to the mission, in the form `<Language>-<Mission>`, short and without spaces, for example `English-Travel` (mission "Trip to London") or `English-Meeting`. Say where to create it:
   - Claude: in the side bar, **Projects → New project**.
   - ChatGPT: in the side bar, **Projects → New project**.
   Suggest pasting into the project instructions one line with the learner's context, for example: "Use TalkGo. Central: <name>. Language: English. Mission: <mission_id>." so every chat of the project starts with the right context.
2. **One chat per purpose, inside the project.** Give a table with name, purpose and the command to send first in each chat:

   | Chat name | Purpose | First command |
   | --- | --- | --- |
   | `Progress` (in the native language) | follow-up and management of the mission: progress, practice list, mission changes, reviews | `Get-Progress`, then `Get-Practices`, `Get-Missions`, `Set-Mission` |
   | `Practice-0001-<situation>` (for example `Practice-0001-Airport check-in`) | the first practice, already prepared | `Resume-Practice <practice ID>` |
   | `Practice-0002-<situation>`, `Practice-0003-…` | each next practice, one chat each | `Start-Practice` |

   The word "Progress" and "Practice" can be written in the native language; keep the four-digit number, which follows the order of the practices in the mission. Optionally, a `Setup` chat for configuration commands (`Get-Central`, `Add-Language`, `Set-Default`, `Backup-Central`).
3. **How to name or rename a chat.** New chats get an automatic title; rename them so they match the table:
   - Claude: open the chat, click its title at the top (or the **…** menu next to it in the side bar) → **Rename**.
   - ChatGPT: in the side bar, **…** next to the chat → **Rename**. To move an existing chat into the project, use **…** → **Move to project** (or drag it).
4. **Next step.** End with a single suggestion: open the `Practice-0001-<situation>` chat in the project and send `Resume-Practice <practice ID>`. Remind in one line that `Help` shows every command and that `Start` can be run again any time to review the setup.
