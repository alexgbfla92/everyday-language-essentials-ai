# Übung — {{target_name}}

practice_id:
mission_id:  # Mission dieser Übung
situation:  # Situation der Mission, die in dieser Sitzung geübt wird
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no bei Tests)
practice_minutes: 20  # Standard 20, oder die der Mission
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:
module:
overrides:

## Ablauf (die Übung ist abgeschlossen, wenn die Phasen 0–6 erledigt sind; Phase 7 ist das optionale Lab, direkt nach dem Abschluss vorgeschlagen)
| Phase | Erledigt |
|---|---|
| 0 Lab-Material vor Phase 1 bereit und erneut gelesen (oder die lernende Person hat akzeptiert, ohne das Video zu beginnen) | offen |
| 1 Briefing | offen |
| 2 Geführtes Training | offen |
| 3 Simulation | offen |
| 4 Unerwartetes Ereignis | offen |
| 5 Feedback | offen |
| 6 Abschluss (gespeichert und bestätigt) | offen |
| 7 Entertainment Lab nach dem Abschluss vorgeschlagen (optional) | offen |

## Satzverzeichnis (globale F-Nummern dieser Sprache; nie wiederverwendet)
| ID | Dialog | Sprecher | Modus (Text/Sprache) | Satz in der Lernsprache | Verlässlichkeit |
|---|---|---|---|---|---|

## Dialoge
| ID | Szenario | Sätze |
|---|---|---|

## Wiedereinstiegspunkte
| Reihenfolge | Uhrzeit | Block und letzter Zug | Aktivitäten und Belege | Offenes und nächste Frage | Letztes F |
|---|---|---|---|---|---|

## Abschluss
Ergebnis, belegtes Feedback, Grenzen, nächste Aufgabe und Stand der Fortschrittsaktualisierung.
closing_saved_reread:  # yes nachdem Finish-Practice gespeichert und erneut gelesen wurde
closing_next_step:

## Entertainment Lab
Vor Phase 1 vorbereitet und geprüft. Das Lab hat keinen eigenen Status; es gehört zur Übung.
lab_title:
lab_channel:  # unconfirmed nur mit Quelle search
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 20
lab_video_minutes:  # Minuten oder mm:ss; unconfirmed nur mit Quelle search
lab_segment:  # whole | mm:ss-mm:ss
lab_off_range_reason:  # Pflicht, wenn das Angesehene außerhalb von 30–50 % der Übung liegt
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verification_source:  # youtube_page | browser | search
lab_search_evidence:  # nur mit Quelle search: das verwendete Ergebnis (Link, Titel, Kanal, Dauer)
lab_verified_at:  # Datum und Uhrzeit, zu der der gespeicherte Eintrag erneut gelesen wurde
lab_missing_reason:
lab_missing_accepted_by_learner:  # nur wenn die lernende Person akzeptiert hat, ohne das Video zu beginnen
lab_suggested_after_closing:  # yes wenn das Lab direkt nach dem Abschluss vorgeschlagen wurde
lab_result:  # nur wenn die lernende Person das Lab macht
lab_save_confirmed:
