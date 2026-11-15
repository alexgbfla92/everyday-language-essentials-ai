# TalkGo — Status der Zentrale

schema: 5
status: not_configured  # not_configured | configured
central_name: null
provider: null  # local | google-drive | onedrive
storage: null  # local-folder | drive | onedrive | manual
root: null  # lokaler Pfad oder ID des Ordners in Drive/OneDrive
record_format: null  # markdown | native (Google Docs/Sheets, nur mit dem Drive-Adapter)
native_language: {{native}}  # Sprache aller Nachrichten, Ordner, Dateien und Einträge dieser Zentrale
default_language: null  # Lernsprache, wenn keine angegeben wird (Set-Default language)
default_missions: {en-US: null, es-ES: null, fr-FR: null, pt-BR: null, zh-CN: null, it-IT: null, ja-JP: null, de-DE: null, ko-KR: null, hi-IN: null, ar: null}  # Mission pro Sprache, wenn keine angegeben wird (Set-Default mission)
enabled_languages: [en-US, es-ES, fr-FR, pt-BR, zh-CN, it-IT, ja-JP, de-DE, ko-KR, hi-IN, ar]
chosen_languages: []
phrase_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # zuletzt verwendete Nummer pro Sprache; steigt nur, wird nie zurückgesetzt
dialogue_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # zuletzt verwendete Nummer pro Sprache; steigt nur, wird nie zurückgesetzt
voice_ids: yes  # yes | no — Satznummern im Sprachmodus ansagen
preferences_confirmed_at: null
last_write_check: null

Erst nach einer echten Einrichtung ausfüllen. Fortschritt nie zwischen Lernenden kopieren.

## Index
| Logischer Pfad | ID | Format |
|---|---|---|
