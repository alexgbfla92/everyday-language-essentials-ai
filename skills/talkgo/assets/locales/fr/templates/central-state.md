# TalkGo — état de la Centrale

schema: 5
status: not_configured  # not_configured | configured
central_name: null
provider: null  # local | google-drive | onedrive
storage: null  # local-folder | drive | onedrive | manual
root: null  # chemin local ou ID du dossier sur Drive/OneDrive
record_format: null  # markdown | native (Google Docs/Sheets, uniquement avec l'adaptateur Drive)
native_language: {{native}}  # langue de tous les messages, dossiers, fichiers et enregistrements de cette Centrale
default_language: null  # langue étudiée utilisée quand aucune n'est indiquée (Set-Default language)
default_missions: {en-US: null, es-ES: null, fr-FR: null}  # mission utilisée par langue quand aucune n'est indiquée (Set-Default mission)
enabled_languages: [fr-FR, es-ES, en-US]
chosen_languages: []
phrase_counter: {en-US: 0, es-ES: 0, fr-FR: 0}  # dernier numéro utilisé par langue ; il ne fait qu'augmenter, jamais remis à zéro
dialogue_counter: {en-US: 0, es-ES: 0, fr-FR: 0}  # dernier numéro utilisé par langue ; il ne fait qu'augmenter, jamais remis à zéro
voice_ids: yes  # yes | no — annoncer les numéros des phrases en mode vocal
preferences_confirmed_at: null
last_write_check: null

À remplir seulement après une vraie configuration. Ne jamais copier la progression entre apprenants.

## Index
| Chemin logique | ID | Format |
|---|---|---|
