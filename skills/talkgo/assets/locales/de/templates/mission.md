# Mission

mission_id:  # kurz, in kebab-case, eindeutig in der Sprache; zugleich der Dateiname
mission_title:  # worauf sich die lernende Person vorbereiten will
mission_description:  # Szenario und Kontext, in den Worten der lernenden Person
mission_target_date:  # TT/MM/JJJJ, Pflicht: bis wann die lernende Person bereit sein will
mission_status: active  # active | paused | completed
mission_language:  # en-US | es-ES | fr-FR
mission_diagnostic:  # reguläre Diagnosesitzung, auf der die Mission beruht
mission_practice_minutes: 20
mission_frequency:  # z. B. 3 Übungen pro Woche
mission_next_review:  # TT/MM/JJJJ (Standard: alle 14 Tage)
mission_revision: 1
mission_approved_at:

## Situationen
| Nr. | Situation | Was die lernende Person können muss |
|---|---|---|

Beispiel: 1 Flughafen · 2 Einreise · 3 Öffentlicher Verkehr · 4 Restaurants. Die nächste Übung behandelt die gewählte Situation oder, ohne Wahl, die erste Situation mit den wenigsten abgeschlossenen Übungen.

## Übungen
| Übung | Datum | Situation | Status |
|---|---|---|---|

Eine Zeile pro Übungssitzung dieser Mission, angelegt zusammen mit der Sitzung. Status: Läuft (vorbereitet), Läuft (in Ausführung), Läuft (pausiert) oder Abgeschlossen. Eine durch Reset-Practices gelöschte Übung verschwindet aus dieser Tabelle.

## Revisionsverlauf
| Revision | Datum | Was sich geändert hat | Grund |
|---|---|---|---|
| 1 |  | Mission angelegt |  |
