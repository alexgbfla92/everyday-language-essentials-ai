# Architecture

SKILL.md in `skills/talkgo/` handles discovery and routes to setup (`Start`), diagnostic, missions, practice, resume or follow-up. The package carries instructions and empty templates. The learner's personal folder (the Central, on Google Drive or the learner's computer) keeps what happened to the learner. The project or chat keeps a reference to that folder.

## Repository structure

```
everyday-language-essentials-ai/
├── skills/talkgo/                 # the skill: single source, the same for every platform
│   ├── SKILL.md                   # instructions and Help table (with the installed version)
│   ├── references/                # procedures read on demand (Start, commands, missions, phrases and voice, Lab, persistence, adapters)
│   ├── assets/
│   │   ├── templates/             # master templates of the Central records, with [[tokens]]
│   │   ├── locales/<code>/        # per native language: locale.json (names, labels) and rendered templates
│   │   ├── reference/             # defaults, methodology and language catalog (read from the skill)
│   │   ├── targets/<language>/    # notes, essentials and diagnostic roadmap of each target language
│   │   └── modules/               # teaching modules 00–07
│   └── scripts/                   # layout.py, provision.py, central.py, lab.py, diagnostic.py, youtube.py (no network, except youtube info)
├── plugin.json                    # portable manifest (Agent Plugins 1.0) with OpenAI extensions
├── .claude-plugin/plugin.json     # plugin manifest for Claude
├── tools/                         # bump_version.py, build_zip.py, render_locales.py
├── .github/workflows/             # ci.yml (tests, versions, rendered locales) and release.yml (release with the .zip)
├── tests/                         # layout, provisioning, commands, Lab, YouTube and packaging tests
├── docs/                          # development documentation (this folder)
└── README.md (+ README-pt-BR/es/fr/de/zh-CN), START-HERE.md, FIRST-PROMPT.md, AGENTS.md, VERSION
```

Everything the skill uses at run time is inside `skills/talkgo/` and only references files in that folder (a test checks it). Each platform has only a thin manifest at the root pointing to the same folder.

| Layer | Implementation and responsibility |
| --- | --- |
| Central | SKILL.md decides the intent, language and eligible step. It names no platform or tool. |
| Native language | `talkgo.json` at the Central root stores the learner's native language and the names of every folder and file (from `assets/locales/<code>/locale.json`). `scripts/layout.py` resolves every logical path through it. Messages, Help descriptions, folder and file names and record contents are in the native language; command names, target-language content and machine keys (`status:`, `mission_id:`, `lab_*`) are not translated. Status values are codes shown with native labels. |
| Method | `assets/reference` holds defaults, methodology and the language catalog; `assets/modules` holds the eight selectable modules; `assets/targets` holds what is specific to each target language. These are read from the skill and never copied into the Central. |
| Commands | [references/COMMANDS.md](../skills/talkgo/references/COMMANDS.md) defines the `Verb-Entity` convention (Get, New, Set, Remove, Reset, Backup, Start, Pause, Resume, Finish, Save on Central, Language, Mission, Practice, Diagnostic, Progress, Lab, Stage and Phrase), context resolution Central → Language → Mission → Practice with defaults (`Set-Default`) and the procedure of each command. `scripts/central.py` runs the management commands in a local folder (`info`, `create`, `register`, `default`, `practices`, `remove`, `remove-mission`, `backup`, `reset`) and keeps the Central registry (`~/.talkgo/centrals.json`). |
| Start | [references/START.md](../skills/talkgo/references/START.md) is the first-setup wizard: native language, Central, languages, diagnostic, first mission, first practice, then projects and chats. Its step is saved in `setup_step` of the learner profile so it can resume. |
| Questions | [references/CHOICES.md](../skills/talkgo/references/CHOICES.md) makes every question with likely answers a choice (single or multiple, recommended first, "Other" for free text): the platform's option card when the session has one, a numbered list otherwise. Answers in the target language stay free. |
| Missions | [references/MISSIONS.md](../skills/talkgo/references/MISSIONS.md) and the mission template define missions per language (title, description, target date, situations, status, practices and revision history), created and changed by `New-Mission` and `Set-Mission`; `Start-Practice` picks the mission and situation and records the session in the mission's Practices table. |
| Phrases and voice | [references/PHRASES-AND-VOICE.md](../skills/talkgo/references/PHRASES-AND-VOICE.md) defines the global numbering of phrases (F) and dialogues (D) per language, lookup by number and saving when pausing or finishing, with Save-Practice in text when voice mode cannot write. |
| Provisioning | `scripts/provision.py` builds the localized tree from `Layout.specification`, classifies each path (Markdown, JSON, Google Doc or Google Sheet) and computes the Drive connector operations from verified listings and tabs or, with `--local`, creates the structure directly in a local folder without overwriting. It can run again after an interruption. |
| Persistence | [references/PERSISTENCE.md](../skills/talkgo/references/PERSISTENCE.md) defines the adapter choice, reading and updating by ID, isolation and repair of derived records. |
| Adapters | `references/adapters/` holds the specific operations of the [local folder](../skills/talkgo/references/adapters/local-folder.md), [Google Drive](../skills/talkgo/references/adapters/drive.md), [OneDrive](../skills/talkgo/references/adapters/onedrive.md) and [manual mode](../skills/talkgo/references/adapters/manual.md). |

## Platform compatibility

The same package serves Claude and ChatGPT. SKILL.md follows the common skill format (a folder with SKILL.md and `name` and `description` frontmatter), read by both platforms. Everything platform-dependent lives in the adapters, and the model chooses the adapter by what the session demonstrably can do, not by the platform's name. Layout and logical paths are identical in every adapter. The format too, except on Google Drive by connector, which writes the records updated during use as native Google Docs and Sheets, because Claude's connector does not rewrite the content of existing files. A Central on Drive can be used by Claude and ChatGPT, which both edit native Docs and Sheets.

The only supported install path is uploading `talkgo-plugin-<version>.zip` through the browser, because the plugin then stays in the account and works on every device. The .zip carries `.claude-plugin/plugin.json` (Claude), `.codex-plugin/plugin.json` (ChatGPT, generated from the root `plugin.json`) and `skills/talkgo/`.

| Platform | Install | Call | Expected storage |
| --- | --- | --- | --- |
| Claude (web, desktop, phone) | Settings → Customize → Plugins → Add → Upload plugin | `/talkgo` | Google Drive with the Google Drive, Google Docs and Google Sheets connectors. |
| ChatGPT (web, desktop, phone) | Plugins → Add | `@TalkGo` or `$talkgo:talkgo` | Google Drive (native Docs and Sheets). |

## Releases

Each published version is a GitHub release with two files: `talkgo-plugin-<version>.zip` and a copy with a fixed name, `talkgo-plugin.zip`, which the README uses in the link `releases/latest/download/talkgo-plugin.zip`. The workflow `.github/workflows/release.yml` runs the tests, checks the rendered locales, checks that the tag equals `VERSION`, builds the .zip and creates the release with notes generated from the PRs. To publish the version on main:

```
git tag v$(cat VERSION) && git push origin v$(cat VERSION)
```

or use **Actions → Release → Run workflow**, which creates the tag from `VERSION`. A version already published is never published again: bump `VERSION` first.

## State of the capabilities

- Proven by the author in Claude: the Google Drive connector `update_file` only changes metadata; the Google Docs connector does not edit `.md`; creating a Doc with `text/plain` and a Sheet with `text/csv` through `create_file`, editing with `update_doc` and `update_values`/`append_values` and rereading work while keeping the same ID.
- Tested in this repository: `claude plugin validate --strict` on the repository and on the extracted .zip, and the .zip loaded in Claude Code (`--plugin-dir`).
- Automated tests: packaging (folder name equal to the skill, consistent manifests, versions equal to VERSION, links that never leave the skill, English-only outside translations, rendered locales), localized layout for every native language, format classification, Drive provisioning with Docs and Sheets (including resume after interruption and tab setup), local mode and management commands (`scripts/central.py`) with fictional folders.
- To be tested: install through ChatGPT and use on web and phone; full setup with `Start`, practice, reset and remove on native Drive through Claude; the same flow through ChatGPT, including whether its connector converts `text/plain` and `text/csv` into a Doc and a Sheet on creation.

Opening a GitHub link or adding a folder to a Project's sources does not, by itself, prove installation or write capability. Check these capabilities in the interface actually used.
