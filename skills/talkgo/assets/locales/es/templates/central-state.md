# TalkGo — estado de la Central

schema: 5
status: not_configured  # not_configured | configured
central_name: null
provider: null  # local | google-drive | onedrive
storage: null  # local-folder | drive | onedrive | manual
root: null  # ruta local o ID de la carpeta en Drive/OneDrive
record_format: null  # markdown | native (Google Docs/Sheets, solo en el adaptador Drive)
native_language: {{native}}  # idioma de todos los mensajes, carpetas, archivos y registros de esta Central
default_language: null  # idioma de estudio usado cuando no se indica ninguno (Set-Default language)
default_missions: {en-US: null, es-ES: null, fr-FR: null, pt-BR: null, zh-CN: null, it-IT: null, ja-JP: null, de-DE: null, ko-KR: null, hi-IN: null, ar: null}  # misión usada por idioma cuando no se indica ninguna (Set-Default mission)
enabled_languages: [en-US, es-ES, fr-FR, pt-BR, zh-CN, it-IT, ja-JP, de-DE, ko-KR, hi-IN, ar]
chosen_languages: []
phrase_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # último número usado por idioma; solo aumenta, nunca se pone a cero
dialogue_counter: {en-US: 0, es-ES: 0, fr-FR: 0, pt-BR: 0, zh-CN: 0, it-IT: 0, ja-JP: 0, de-DE: 0, ko-KR: 0, hi-IN: 0, ar: 0}  # último número usado por idioma; solo aumenta, nunca se pone a cero
voice_ids: yes  # yes | no — anunciar los números de las frases en modo voz
preferences_confirmed_at: null
last_write_check: null

Rellenar solo después de una configuración real. Nunca copiar el progreso entre alumnos.

## Índice
| Ruta lógica | ID | Formato |
|---|---|---|
