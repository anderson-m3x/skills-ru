# Формат MISSION.md

`MISSION.md` лежит в корне рабочего пространства. Он фиксирует _причину_, по которой пользователь изучает эту тему. Каждое учебное решение (чему учить дальше, какие ресурсы поднимать, какие упражнения проектировать) должно восходить к этому документу.

## Шаблон

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X"; push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now, protecting the zone of proximal development}
```

## Правила

- **Одна миссия на рабочее пространство.** Если пользователь хочет изучить две несвязанные вещи, это два рабочих пространства.
- **Конкретное важнее абстрактного.** «Пробежать полумарафон к октябрю» лучше, чем «стать в форме». «Выпустить Rust CLI для моей команды» лучше, чем «выучить Rust».
- **Возражайте против расплывчатости.** Если пользователь не может сформулировать почему, проведите с ним интервью, прежде чем что-то писать. Плохая миссия хуже, чем отсутствие миссии.
- **Пересматривайте, когда меняется реальность.** Миссии меняются. Когда цель пользователя сдвигается, обновите этот файл: не оставляйте устаревшую миссию рулить будущими сессиями.
- **Держите его коротким.** Если `MISSION.md` выходит за пределы экрана, он перестал быть компасом и стал планом.
