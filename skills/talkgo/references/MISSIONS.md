# Missions

A mission is the scenario and context the learner wants to get ready for in a language, with a date to be ready by. It has a title, a description, a target date and the situations to practice. Example: "Get ready for a trip to London" by 20/04/2027, in the situations airport, immigration, public transport and restaurants.

The learner does practice sessions linked to a mission, and each mission belongs to one language. Each language can have more than one mission (for example, "Trip to London" and "Meetings with the Dublin team"). The template is `assets/locales/<code>/templates/mission.md` (in the learner's native language) and the saved mission lives in the missions folder of the language, `<missions>/<mission_id>` (a Google Doc on Drive, `.md` elsewhere; folder name from `talkgo.json`).

## Commands

- `Get-Missions [language] [status]` lists the missions of the language (title, target date, status, situations and completed practices), marking the default.
- `New-Mission [language]` creates a mission (below).
- `Set-Mission [mission]` updates a mission (below).
- `Remove-Mission [mission]` deletes the mission and its practices (see [COMMANDS.md](COMMANDS.md#mission)).
- `Set-Default mission [mission]` sets the mission used when the learner does not give one.

Resolve Central, language and mission as in [Context and defaults](COMMANDS.md#context-and-defaults).

### New-Mission

1. Require a completed regular diagnostic in the language: read the language's diagnostics folder; a diagnostic counts only when it is `completed` and passes the closing check (with Python: `python scripts/diagnostic.py closing FILE`). Never create the mission on the learner's word alone.
   - Latest diagnostic `running` or `paused`: do not create the mission. Say at which stage it stopped and resume it now (`Resume-Practice <diagnostic ID>`) until the closing; then come back to step 2.
   - Stages 1 to 4 done but the closing incomplete (results, derived records or `closing_saved_reread` missing): run the closing now from the saved file ([Diagnostic saving](../SKILL.md#diagnostic-saving-mandatory)), confirm, then go on.
   - None: route to `Start-Diagnostic <language>`.
2. Ask, one thing at a time, only what is still unknown: title (what the learner wants to get ready for), description (scenario and context), target date, situations to practice, practice length, frequency and date of the first review. The target date is required: if the learner has none, suggest one and ask for confirmation. For length, frequency and review, use the defaults (20 minutes, review every 14 days) when the learner has no preference, and say so.
3. Propose the situations, each with what the learner needs to be able to do in it, adjusted to the diagnostic and to the time left until the target date (including a very close date, such as a trip tomorrow).
4. With the learner's approval, copy the template, fill the fields (`mission_id`, `mission_title`, `mission_description`, `mission_target_date`, `mission_language`…) and the situations table, choose a `mission_id` unique in the language (short, kebab-case, in the learner's native language) and save it in the language's missions folder with `mission_status: active`. If it is the first mission of the language, save it as the default too (`default_missions` in the central state). Reread and confirm, in the native language, that the mission was saved in the Central.
5. Say that the first practice starts with `Start-Practice <language>`.

### Set-Mission

1. Show a summary of the chosen mission: title, description, target date, length, frequency, review, situations and practices with their status labels.
2. Ask what to change. It can be any field, adding, removing or reordering situations, or the mission status (`active`, `paused`, `completed`, shown with the labels of `talkgo.json`). Practices already done are never deleted from the table.
3. With the learner's approval, save the new version in the same file: add 1 to `mission_revision`, fill `mission_approved_at` and add a row to the revision history (what changed and why). Reread and confirm that the mission was updated, with the revision number.
4. A review (every 14 days or near the target date) updates the mission through this same flow.

## Choose the mission in Start-Practice

1. Consider only the `active` missions of the language.
2. None: route to `New-Mission <language>`.
3. One: use it and say which one in the practice summary.
4. More than one: use the one given in the command (`Start-Practice English mission london-trip`, by `mission_id` or title); without it, ask which one, listing title, target date and next situation of each, with the language's default first, marked as default and preselected. Without a default, never choose alone.
5. The situation of the practice is the one the learner gives or, without it, the first situation in the table with the fewest completed practices. When creating the session, write `mission_id` and `situation` in the practice file and add the practice row to the mission's Practices table, with the status label for `prepared`.

## Practice status in the mission

The practice row follows the session status (see Practice status in SKILL.md), always shown with the labels of `talkgo.json`: running when stage 1 starts, paused at Pause-Practice and completed at Finish-Practice, rereading after each change. The Lab never changes the row. To train a situation again, simply do another practice in it.

## After Reset-Practices

Reset-Practices removes from the Practices table the rows of the sessions it deleted. Nothing in the mission shows that practices were deleted: no status such as "deleted in reset", no note in the revision history. A row that still points to a session that no longer exists is ignored.
