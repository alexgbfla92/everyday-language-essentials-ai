# Adapter: Google Drive (native format)

Use this guide when the [selection rules](../PERSISTENCE.md#choose-the-adapter) point to Google Drive by connector. Folders and logical paths are the same as in the other adapters, but here files written during use are native Google Docs or Google Sheets. Read-only files stay in Markdown. Record `record_format: native` in the central state. Folder and file names come from the Central's `talkgo.json`, in the learner's native language.

## Check the capability

The adapter passes only if the session has, at the same time:

1. **Drive**: list the direct children of a folder, create a folder in a given parent, create a file with content in a given parent (converting text to a Doc and CSV to a Sheet), copy a file and delete a file (moving it to the trash or, if the connector only offers this, deleting it permanently).
2. **Docs**: read a Google Doc with its current revision and apply a batchUpdate (insert, delete range, replace text).
3. **Sheets**: read and write values by range, append rows and rename or create tabs.

Check by capability, not by tool name. Examples of names:

| Capability | Claude | ChatGPT |
| --- | --- | --- |
| List, create, copy, trash | Google Drive connector: `search_files` (filter `'ID' in parents`), `create_file`, `copy_file`, `trash_file` | Google Drive connector: `list_folder`, `create_folder`, `upload_file` |
| Docs | Google Docs connector: `read_doc`, `update_doc` | the connector's native Docs editing |
| Sheets | Google Sheets connector: `get_values`, `update_values`, `append_values`, `update_spreadsheet`, `batch_clear_values` | the connector's native Sheets editing |

Claude's Google Drive connector `update_file` **only changes metadata** (name, folder, star, lock); it does not rewrite content. The Google Docs connector does not edit `.md` files. So everything updated after creation must be native.

If Docs or Sheets editing is missing, the adapter fails. Tell the learner which connectors to install (in Claude: Google Drive, Google Docs and Google Sheets) and follow the selection rules (local folder or manual mode).

## Formats

| Record (logical name) | Format on Drive | Name on Drive |
| --- | --- | --- |
| `talkgo.json` | JSON | `talkgo.json` |
| central state, learner profile | Google Doc | without `.md` |
| active session, recent context, current profile | Google Doc | without `.md` |
| diagnostic and practice sessions (`<prefix>-YYYYMMDD-NN`) | Google Doc | without `.md` |
| missions (`missions/<id>`) | Google Doc | without `.md` |
| progress log | Google Sheet | without `.md` |
| history README and cycle summaries | Markdown, created once and never edited | with `.md` |

`scripts/layout.py` applies this table (method `classify`). The index in the central state keeps mapping the logical path (with `.md`) to the ID and format.

### Content of the Docs

A Doc keeps the same Markdown as the template as plain text, with the same structure (headings, `field: value` lines and tables with `|`). Do not use Docs formatting. To create a Doc, send the text with content MIME `text/plain` without disabling conversion to a Google type.

### Progress log spreadsheet

| Tab (`tabs` in `talkgo.json`) | Columns | Use |
| --- | --- | --- |
| `summary` | Field \| Value | Fixed rows in the order of the template: language, status, missions, default practice, completed regular practices, observed duration, CEFR by skill, next review, next step, revision. Update column B of the field's row. |
| `practices` | Session ID \| Date \| Goal \| Evidence \| Next task | One row per completed regular practice, appended at the end. Tests never go in. |

Tab names, column titles and field labels come from the progress-log template of the native language, which is the only source: its first table becomes the summary tab and the second the practices tab.

## Identify the root

Get the ID and metadata of the learner's dedicated folder and check the chain of parents. Refuse shortcuts. Never use a global search by name to choose the folder to write to.

## Provision

1. Run from the skill folder: `python scripts/provision.py PERSONAL_ID inventory.json en-US es-ES --native <native language> [--tabs tabs.json] [--manifest talkgo.json]`. The initial inventory is `{}`; `tabs.json` starts empty or absent. For an existing Central, download its `talkgo.json` and pass it with `--manifest`: its names win.
2. `list_parent_ids`: for each parent, list its direct children (including folders, Docs, Sheets, JSON and Markdown) and confirm the listing is complete. Record in the inventory the parent ID as key and the list of objects with `id`, `title` and `mime_type`. A verified empty folder gets `[]`; an incomplete read or a failure never counts as `[]`.
3. `inspect_sheet_ids`: for each spreadsheet, read the tab titles in order and record them in `tabs.json` (ID → list of titles).
4. Run `operations`, only in the given parent:
   - `create_folder`: create the folder.
   - `create_file` with `kind: manifest`: create `talkgo.json` with the text of `content`, MIME `application/json`, without conversion.
   - `create_file` with `kind: markdown`: create the file with the text of `content`, MIME `text/markdown`, without conversion.
   - `create_file` with `kind: google-doc`: create with the text of `content` and content MIME `text/plain`, with conversion; the result must be `application/vnd.google-apps.document`.
   - `create_file` with `kind: google-sheet`: create with the operation's `csv` and content MIME `text/csv`, with conversion; the result must be `application/vnd.google-apps.spreadsheet`.
   - `configure_sheet`: if `rename_first_tab` is set, rename the first tab (conversion creates "Untitled"); for each item of `add_tabs`, create the tab and write its `rows` from A1.
5. Reread each created object (ID, name, MIME, parent and content; for spreadsheets, tabs and values) and update the inventory. Repeat the provisioner until `operations`, `list_parent_ids` and `inspect_sheet_ids` are empty. Reconciliation recognizes Docs and Sheets already created by an interrupted run and does not recreate them; if a name exists with the wrong type, the provisioner stops with a conflict.

Without Python, build the same tree from `Layout.specification` in `scripts/layout.py` and the templates in `assets/locales/<code>/templates/` (replacing `{{native}}`, `{{tag}}` and `{{target_name}}`), parents before children, applying the format table and the same checks.

## Create sessions and missions

When starting a diagnostic or practice, create the Doc `<prefix>-YYYYMMDD-NN` in the language's diagnostics or practices folder with the text of the diagnostic or practice template of the native language (`text/plain`, with conversion). Missions also start as a Doc. Record the ID in the index and in the active session pointer before the first activity.

## Write and reread Docs

Every write to a Doc starts from a recent read, which gives the text, the `revisionId` and the `endIndex` of the last element of the body. Send the write with `writeControl.requiredRevisionId` equal to the revision read. Use one of these two procedures:

- **Full replacement** (e.g. a rewritten checkpoint, a derived record restored to its template): a single batchUpdate with `deleteContentRange` over [1, endIndex − 1) followed by `insertText` at index 1 with the full text. If the body is empty (endIndex − 1 ≤ 1), send only the `insertText`.
- **Targeted edit** (e.g. a `field: value` line, a new row in a table): `replaceAllText` with a snippet that occurs exactly once in the document, such as the whole field line or a unique marker. Confirm in the read that the snippet appears exactly once before sending.

After each write, reread the Doc and compare revision, operation, evidence and next question. If the write is refused because the revision changed, another write intervened: reread, reconcile by operation ID and turns, as in the [protocol](../PERSISTENCE.md#save-resume-and-repair), and only then retry with the new revision. Never retry without rereading.

## Write and reread Sheets

- Summary field: find the field's row by column A and write column B of that row.
- Valid practice: append a row to the practices tab. First check that the session ID is not already in column A, so the same practice is never counted twice.
- Reread the written range and compare.

Value writes have no revision control. Keep a single writing chat per session and per Central.

## Remove and reset

Remove-Central, Remove-Mission and the Reset-* commands (see [commands](../COMMANDS.md)) delete through the action the connector offers, in this order of preference, which also applies to Docs and Sheets:

1. **Trash**, when the connector has this action (in Claude, `trash_file`). The learner can recover it from the Drive trash.
2. **Permanent deletion**, when the connector only offers this (common in ChatGPT). Use it without asking the learner to delete by hand, as long as the preview warned that the deletion is permanent and skips the trash, and the learner confirmed after that warning. Never make a backup before deleting or changing. Reread the folder afterwards to confirm the items are gone.

Ask the learner to delete by hand only when the connector has neither action. Backups only through `Backup-Central`, at the learner's request, as native copies (`copy_file`) in a folder outside the Central. To restore a derived record to its template:

- Doc: full replacement with the text of the template.
- Sheet: clear both tabs and rewrite the two tables of the template from A1.

In Reset-Practices, besides deleting the practice Docs: in each affected mission, remove from the Practices table the rows of those practices (`update_doc`); in the progress Sheet, delete the rows of those practices in the practices tab and restore, in the summary tab, the completed regular practices and the observed duration. Reread each file.

Never overwrite a file to "delete" it.

A Google Drive folder synced to the computer (Google Drive for desktop) can use the [local folder adapter](local-folder.md) with `provider: google-drive`; in that case, everything is Markdown.
