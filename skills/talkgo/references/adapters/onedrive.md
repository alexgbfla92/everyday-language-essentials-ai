# Adapter: OneDrive

Use this guide when the Central is on OneDrive. The general protocol stays in [PERSISTENCE.md](../PERSISTENCE.md).

## Folder synced to the computer (recommended)

If the OneDrive folder is synced to the learner's computer and the session can read and write it, use the [local folder adapter](local-folder.md) with `provider: onedrive`. The local folder commands (`scripts/central.py`) work unchanged. Wait for the sync to finish before resuming on another device and treat conflict copies created by OneDrive as homonyms.

"Online-only" folders must be available on the device before reading or writing; if reading a file fails, ask the learner to mark the folder as "Always keep on this device".

## OneDrive or SharePoint connector

On OneDrive records stay 100% Markdown (`record_format: markdown`). Use a connector only if, in the current session, it offers: list the direct children of a folder, create a folder in a parent, create a file with content in a parent, **rewrite the content of an existing file by ID** and move to the trash. Many Microsoft 365 connectors only read and search; in that case, use the synced folder or [manual mode](manual.md).

With a capable connector, follow the provisioning order of the [provisioner](drive.md#provision), treating every file as `markdown` (MIME `text/markdown`, name with `.md`, and `talkgo.json` as JSON), write by updating the same ID and reread each write. Record `storage: onedrive` and `provider: onedrive` in the central state. Identifiers are the OneDrive item IDs.
