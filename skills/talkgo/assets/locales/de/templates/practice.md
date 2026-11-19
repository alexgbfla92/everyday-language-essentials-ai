# Übung — {{target_name}}

practice_id:
mission_id:  # Mission dieser Übung
situation:  # Situation der Mission, die in dieser Sitzung geübt wird
language: {{tag}}
type: regular  # regular | test
include_in_metrics: yes  # yes | no (no bei Tests)
practice_minutes: 30  # Standard 30, höchstens 35, oder die der Mission
status: prepared  # prepared | running | paused | completed
current_stage:  # 1–7
checkpoint_seq: 0  # steigt bei jedem gespeicherten Wiederaufnahmepunkt; ein kleinerer überschreibt nie einen größeren
last_activity:  # zuletzt tatsächlich durchgeführte Aktivität
next_activity:  # nächste Pflichtaktivität (wo fortgesetzt wird)
pending_items:  # was beim Pausieren noch offen ist
phrase_range:  # F?–F? | D?–D?
created_at:
started_at:
finished_at:
observed_minutes:  # nur gemessen oder von der lernenden Person bestätigt; sonst leer
observed_minutes_source:  # measured | learner_estimate
module:
overrides:

## Phasen
Jede Etappe ist nur mit Nachweis der Durchführung abgeschlossen. Die Übung ist erst nach Etappe 7 und Finish-Practice abgeschlossen.
stage_1_status: pending  # 1 Briefing · pending | in_progress | completed
stage_1_evidence:
stage_2_status: pending  # 2 Geführtes Training
stage_2_evidence:
stage_3_status: pending  # 3 Simulation
stage_3_evidence:
stage_4_status: pending  # 4 Unerwartetes Ereignis
stage_4_evidence:
stage_5_status: pending  # 5 Feedback
stage_5_evidence:
stage_6_status: pending  # 6 Abschluss (Zusammenfassung, Sätze und nächster Schritt)
stage_6_evidence:
stage_7_status: pending  # 7 Entertainment Lab (Teil der Übung, vor dem Abschluss)
stage_7_evidence:

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
Zusammenfassung, Feedback mit Belegen, Grenzen und nächste Aufgabe. Die Übung ist erst nach Etappe 7 (Entertainment Lab) abgeschlossen.
closing_next_step:
closing_saved_reread:  # yes nachdem das letzte Speichern von Finish-Practice erneut gelesen wurde
save_error:  # was beim Speichern fehlgeschlagen ist; nie sagen, dass gespeichert wurde

## Entertainment Lab
Vor Etappe 1 vorbereitet und geprüft. Das Lab ist Etappe 7: Teil der Übung und ihrer Dauer.
lab_title:
lab_channel:
lab_url:  # https://www.youtube.com/watch?v=<ID>
lab_language_variant:
lab_practice_minutes: 30
lab_max_video_seconds: 450  # 25 % der Übung: practice_minutes × 60 × 0,25
lab_video_seconds:  # geprüfte Dauer in Sekunden; nie unbekannt
lab_duration_source:  # youtube_page | browser | search_result_with_duration
lab_transcript:  # obtained | captions_indicated | unconfirmed
lab_practice_items:
lab_question_1:
lab_question_2:
lab_question_3:
lab_task:
lab_verified_at:  # Datum und Uhrzeit, zu der der gespeicherte Eintrag erneut gelesen wurde
lab_blocked_reason:  # nur wenn kein gültiges Video gefunden wurde; Etappe 7 bleibt offen
lab_result:  # Antworten, Aufgabe und Feedback des durchgeführten Labs
lab_done_at:
