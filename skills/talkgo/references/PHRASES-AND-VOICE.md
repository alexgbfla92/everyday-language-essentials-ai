# Numbered phrases, pause and completion (text and voice)

## Numbering phrases and dialogues

Every phrase in the language the learner is studying gets a number, whether from the AI or the learner, written or spoken. Phrases in the learner's native language do not get a number.

- **Phrase (F):** each sentence in the target language. An answer with three sentences gets three numbers. Example: `F132`.
- **Dialogue (D):** a block of turns presented or practiced together (model dialogue, simulation, exchange of turns in a scenario). The phrases inside keep their F numbers. Example: `D145` gathers F140–F151.
- **Unique per language in the Central.** Numbering continues from one session to the next and between diagnostic and practices. It never goes back to 1 and is never reused, not even after Reset-Diagnostics, Reset-Practices or Reset-Progress. Each language has its own sequence.

### Where the counter lives

The central state keeps `phrase_counter` and `dialogue_counter`: the last number used per language. When creating a session, start at counter + 1. If an earlier session has numbers above the counter (interrupted write), start after the highest number found in the language's sessions. Update the counter in the central state when pausing and completing, after writing the session.

Each session records the range used in `phrase_range` (`F120–F158 | D12–D15`), each phrase in the phrase table (ID, dialogue, speaker, text/voice mode, phrase, reliability) and each dialogue in the dialogue table. That way a phrase can be found later by its number.

### How to show them

- **Text:** prefix each AI phrase in the target language with its number in brackets: `[F132] Could you send me the agenda?`. For the learner's phrases, open the answer with a short line giving the numbers without repeating the text, in the native language (for example "You: F133, F134"). Dialogues start with `[D145]`.
- **Voice:** with `voice_ids: yes` (default), say the number briefly before each new AI phrase ("one hundred thirty-two: Could you send me the agenda?", the number in the native language) and confirm the number of the learner's phrases at the start of the answer. The learner turns this on and off with `Set-VoiceIds on` and `Set-VoiceIds off`. When off, numbers are still assigned and saved; the AI says the number when asked.

### Asking about a phrase or dialogue

The learner can give the number with or without the letter, in any language: "repeat phrase 132", "F132 slower", "explain the structure of dialogue 145", "translate 132", "how could I say 133 more naturally?", "what is the number of my last phrase?", or `Get-Phrase F132`.

- A number without a letter is a phrase (F). "Dialogue N" is D; if D N does not exist but F N does, use the dialogue that contains phrase N.
- Common actions: repeat, repeat slowly, translate into the native language, explain vocabulary, explain structure (grammar, order, connectors, register), give more natural or more formal variations, practice again.
- Look first in the current conversation; then in the active session; then in the language's sessions, from the most recent to the oldest, by the `phrase_range`. If it is not found, say so and ask for the excerpt; never invent the phrase.
- New phrases that appear in the explanation (examples, variations) also get numbers.
- Outside a practice or diagnostic, new phrases in the target language get numbers from the same counter and go to the standalone phrases table of the language's recent context.

## Pause and complete

Commands: `Pause-Practice` (or "pause", "stop here" in any language) and `Finish-Practice` (or "finish", "end the practice"). They apply to practices and diagnostics.

### Pause-Practice

1. Build the checkpoint: stage and block, last exchange, last phrase (F) and dialogue (D), evidence, pending work and the exact next question.
2. Write to the session, in a single verified write: `status: paused`, checkpoint, phrases and dialogues not yet saved and the `phrase_range`.
3. Update the active session (paused session, file ID, next question), the practice row in the mission (status label for `paused` from `talkgo.json`) and the counters in the central state.
4. Reread each file. Only then say, in the native language, that the practice was paused and saved, with the session ID and the next question. If any write fails, do not say it was saved: follow the no-write mode below.

### Finish-Practice

Finish-Practice is stage 6 (closing) and always runs at the end of the practice, even if the learner does not ask (see the roadmap in SKILL.md). The practice becomes `completed` here; in the same message as the confirmation, suggest the Entertainment Lab already prepared (stage 7).

1. Do the agreed closing (feedback with evidence, limitations, next task).
2. Write to the session, in a single write: last turn, closing, `status: completed`, `closing_saved_reread: yes`, `closing_next_step`, `lab_suggested_after_closing: yes`, pending phrases and dialogues.
3. Consolidate the language's derived records as in [persistence](PERSISTENCE.md#save-resume-and-repair) (progress log, current profile, recent context) and mark the practice as completed in the Practices table of the mission ([missions](MISSIONS.md#practice-status-in-the-mission)). A test practice never changes the metrics.
4. Update the counters and, last, the active session.
5. Reread everything and confirm, in text or voice and in the native language, that the practice was completed and saved in the Central, with the session ID, followed by the next step and the Lab suggestion.

### Finish-Lab

When the learner does the Entertainment Lab (right after the closing or later, with `Start-Lab`):

1. Write to the Entertainment Lab section of the session, in a single write: `lab_result` (answers, task and brief feedback) and the numbered phrases and dialogues. After the reread and the confirmation to the learner, write `lab_save_confirmed: yes`. The practice status does not change (it stays `completed`), and the Lab has no status of its own. If the learner does not do the Lab, nothing is written.
2. Update the phrase and dialogue counters in the central state.
3. Reread and confirm, in text or voice, that the Lab result was saved in the Central. The Lab never changes the practice metrics.
4. With no write available, follow the section below with `Save-Practice lab`.

### No write available (voice and other cases)

In voice mode, the AI may not have access to the writing tools. Try to write; if there is no tool or the write fails:

1. Do not say it was saved.
2. Say it in one or two short sentences, in the native language, and leave the same text in the transcript: that it cannot save in voice mode and that the learner should leave voice mode and send, as text, in this same conversation: **Save-Practice pause practice-20261111-01 F120-F158** (or `finish`). Use the real session ID and the real phrase range.
3. Then, in voice mode, summarize in one sentence where the practice stopped (next question), so the learner hears it.

When starting an activity by voice, say once, in one sentence, if saving after each answer is not available: in this mode the practice is saved when the learner pauses or finishes, and if that fails, a command for text mode will be given. Before entering voice, save the checkpoint by text when possible, so only the spoken part stays pending.

### Save-Practice (in text mode)

`Save-Practice [pause|finish|lab] [session] [range]` writes what was left pending in the same conversation (pause, end of practice or end of Lab):

1. Read the session by ID and the last confirmed revision.
2. Rebuild, from the transcript of this conversation, the turns of the given range (or all after the last saved phrase): number, speaker, mode `voice`, text and evidence. Mark the learner's turns with reliability "voice transcript"; never assess pronunciation from a transcript.
3. Run Pause-Practice, Finish-Practice or Finish-Lab from the write step, with reread and confirmation to the learner.
4. If the transcript does not have the turns (another conversation, lost transcript), say which numbers were not recorded, ask the learner to paste the excerpt, or save only the checkpoint and mark those phrases as not recovered.

Without arguments, Save-Practice uses the active session and the last action requested. When resuming a session, if the conversation or the pointer show phrase numbers above the last saved one, offer Save-Practice before going on.
