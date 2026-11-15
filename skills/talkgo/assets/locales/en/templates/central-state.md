# TalkGo — central state

schema: 5
status: not_configured  # not_configured | configured
central_name: null
provider: null  # local | google-drive | onedrive
storage: null  # local-folder | drive | onedrive | manual
root: null  # local path or Drive/OneDrive folder ID
record_format: null  # markdown | native (Google Docs/Sheets, Drive adapter only)
native_language: {{native}}  # language of every message, folder, file and record in this Central
default_language: null  # target language used when none is given (Set-Default language)
default_missions: {en-US: null, es-ES: null, fr-FR: null, pt-BR: null, zh-CN: null, it-IT: null, ja-JP: null, de-DE: null, ko-KR: null, hi-IN: null, ar: null}  # mission used per language when none is given (Set-Default mission)
enabled_languages: [en-US, es-ES, fr-FR, pt-BR, zh-CN, it-IT, ja-JP, de-DE, ko-KR, hi-IN, ar]
chosen_languages: []
phrase_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # last number used per language; only grows, never reset
dialogue_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # last number used per language; only grows, never reset
voice_ids: yes  # yes | no — announce phrase numbers in voice mode
preferences_confirmed_at: null
last_write_check: null

Fill in only after a real setup. Never copy progress between learners.

## Index
| Logical path | ID | Format |
|---|---|---|
