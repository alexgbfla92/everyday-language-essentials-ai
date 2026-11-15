# TalkGo — estado da Central

schema: 5
status: not_configured  # not_configured | configured
central_name: null
provider: null  # local | google-drive | onedrive
storage: null  # local-folder | drive | onedrive | manual
root: null  # caminho local ou ID da pasta no Drive/OneDrive
record_format: null  # markdown | native (Google Docs/Sheets, só no adaptador Drive)
native_language: {{native}}  # idioma de todas as mensagens, pastas, arquivos e registros desta Central
default_language: null  # idioma de estudo usado quando nenhum é indicado (Set-Default language)
default_missions: {en-US: null, es-ES: null, fr-FR: null, pt-BR: null, zh-CN: null, it-IT: null, ja-JP: null, de-DE: null, ko-KR: null, hi-IN: null, ar: null}  # missão usada por idioma quando nenhuma é indicada (Set-Default mission)
enabled_languages: [en-US, es-ES, fr-FR, pt-BR, zh-CN, it-IT, ja-JP, de-DE, ko-KR, hi-IN, ar]
chosen_languages: []
phrase_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # último número usado por idioma; só aumenta, nunca é zerado
dialogue_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # último número usado por idioma; só aumenta, nunca é zerado
voice_ids: yes  # yes | no — anunciar os números das frases no modo voz
preferences_confirmed_at: null
last_write_check: null

Preencha só depois de uma configuração real. Nunca copie progresso entre alunos.

## Índice
| Caminho lógico | ID | Formato |
|---|---|---|
