# Misión

mission_id:  # corto, en kebab-case, único en el idioma; también es el nombre del archivo
mission_title:  # para qué quiere prepararse el alumno
mission_description:  # escenario y contexto, con las palabras del alumno
mission_target_date:  # DD/MM/AAAA, obligatoria: cuándo quiere estar preparado el alumno
mission_status: active  # active | paused | completed
mission_language:  # en-US | es-ES | fr-FR | pt-BR | zh-CN | it-IT | ja-JP | de-DE | ko-KR | hi-IN | ar
mission_diagnostic:  # sesión de diagnóstico regular en la que se basa la misión
mission_practice_minutes: 30
mission_frequency:  # p. ej.: 3 prácticas por semana
mission_next_review:  # DD/MM/AAAA (por defecto: cada 14 días)
mission_revision: 1
mission_approved_at:

## Situaciones
| N.º | Situación | Lo que el alumno necesita poder hacer |
|---|---|---|

Ejemplo: 1 Aeropuerto · 2 Inmigración · 3 Transporte público · 4 Restaurantes. La siguiente práctica trabaja la situación elegida por el alumno o, si no elige, la primera situación con menos prácticas completadas.

## Prácticas
| Práctica | Fecha | Situación | Estado |
|---|---|---|---|

Una fila por sesión de práctica de esta misión, creada junto con la sesión. Estado: En curso (preparada), En curso (en ejecución), En curso (en pausa) o Completada. Una práctica borrada por Reset-Practices sale de esta tabla.

## Historial de revisiones
| Revisión | Fecha | Qué cambió | Motivo |
|---|---|---|---|
| 1 |  | Misión creada |  |
