# Adapter: local folder

Use this guide when the [selection rules](../PERSISTENCE.md#choose-the-adapter) point to a local folder. It works for any agent with file access: Claude Code, the Claude app with a connected folder, or another environment that reads and writes to disk. The general protocol stays in [PERSISTENCE.md](../PERSISTENCE.md).

## Check the capability

The folder must belong to the learner and persist after the chat. Confirm the full path with the learner. Never use temporary directories, the session's ephemeral workspace or the skill folder itself. If the session can only read the folder, use manual mode.

Identifiers: the path relative to the root, with `/` as separator (for example `Languages/English/State/active-session.md` in a Central whose native language is English). It replaces the Drive ID in every record and index.

## Identify the root

Use the dedicated folder given by the learner. If only a parent is given, create or reuse a single `TalkGo` subfolder. Refuse symbolic links and paths inside the skill folder.

## Provision

With Python available, run from the skill folder:

```
python scripts/provision.py --local ROOT_PATH en-US es-ES --native <native language>
```

`scripts/central.py create` (New-Central and Add-Language) calls it and also fills the central state and the registry. The script creates only what is missing, parents before children, writes `talkgo.json` with the names in the native language and never overwrites an existing file. In an existing Central it keeps the native language and names of its `talkgo.json`. It stops with an error on an unexpected type (a file where a folder is expected, or the opposite), a symbolic link or a root inside the skill folder. The JSON output lists `created`, `existing` and the `ids` index (path → path). It can run again after an interruption or to add languages.

Without Python, build the same tree with the session's file tools from `Layout.specification` in `scripts/layout.py` and the templates in `assets/locales/<code>/templates/`, replacing `{{native}}`, `{{tag}}` and `{{target_name}}`. Before creating each item, check whether it already exists.

Then open a few created files and compare them with the templates to confirm the copy is faithful.

## Write and reread

Update the file at its own path, keeping what did not change. Then reread the file and compare revision, operation, evidence and next question. If the reread differs, do not announce the save: apply the repair of the general protocol.

There is no lock between processes. Keep a single writing chat per session. If the folder is synced by a cloud service, wait for the sync to finish before resuming on another device and treat conflict copies created by the service as homonyms: stop and ask the learner to identify the right version.
