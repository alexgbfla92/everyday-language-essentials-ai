# Language catalog

## Target languages (what the learner practices)

| Tag | Default variety | Status | Specific notes |
|---|---|---|---|
| fr-FR | France | enabled | [targets/french](../targets/french/) |
| es-ES | Spain | enabled | [targets/spanish](../targets/spanish/) |
| en-US | United States | enabled and DEFAULT | [targets/english](../targets/english/) |

Display order: French, Spanish, English. Automatic selection when no language is given: the Central's default language. A new target language needs a folder in `targets/` (notes, essentials, diagnostic roadmap), an entry in every `locales/<code>/locale.json` (`targets`), tests and an updated Help.

## Native languages (what the learner speaks)

Folder, file and record names come from `locales/<code>/locale.json`: `en`, `pt-BR`, `es`, `fr`, `de`. For any other native language, the Central uses the `en` names and records, and the conversation still happens in the learner's native language.
