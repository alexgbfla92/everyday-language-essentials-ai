# Language catalog

## Target languages (what the learner practices)

| Tag | Default variety | Status | Specific notes |
|---|---|---|---|
| en-US | United States | enabled and DEFAULT | [targets/english](../targets/english/) |
| es-ES | Spain | enabled | [targets/spanish](../targets/spanish/) |
| fr-FR | France | enabled | [targets/french](../targets/french/) |
| pt-BR | Brazil | enabled | [targets/portuguese](../targets/portuguese/) |
| zh-CN | Mandarin, simplified characters, pinyin | enabled | [targets/chinese](../targets/chinese/) |
| it-IT | Italy | enabled | [targets/italian](../targets/italian/) |
| ja-JP | Standard Japanese (Tokyo), kana and romaji support | enabled | [targets/japanese](../targets/japanese/) |
| de-DE | Germany | enabled | [targets/german](../targets/german/) |
| ko-KR | Standard Korean (Seoul), Revised Romanization support | enabled | [targets/korean](../targets/korean/) |
| hi-IN | Standard Hindi, Devanagari with transliteration | enabled | [targets/hindi](../targets/hindi/) |
| ar | Modern Standard Arabic, dialects on request | enabled | [targets/arabic](../targets/arabic/) |

Display order (the order of the options when the learner chooses): English, Spanish, French, Portuguese, Chinese, Italian, Japanese, German, Korean, Hindi, Arabic. The first six were chosen by the project; the last five are the most studied languages worldwide after them (Duolingo Language Report 2025: Japanese, German, Korean, Hindi; Arabic, the fastest-growing language among learners, completes the list). Never offer the learner's own native language as a target language. Automatic selection when no language is given: the Central's default language. For languages written in another script (Chinese, Japanese, Korean, Hindi, Arabic), the notes say how to show romanization; Arabic is written right to left.

A new target language needs a folder in `targets/` (notes, essentials, diagnostic roadmap), an entry in every `locales/<code>/locale.json` (`targets`), `TARGETS` in `scripts/layout.py`, the aliases in `scripts/central.py`, tests and an updated Help.

## Native languages (what the learner speaks)

Folder, file and record names come from `locales/<code>/locale.json`: `en`, `pt-BR`, `es`, `fr`, `de`. For any other native language, the Central uses the `en` names and records, and the conversation still happens in the learner's native language.
