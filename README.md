# Shared engineering toolkit — Claude Code + Codex

Основа: [citypaul/.dotfiles](https://github.com/citypaul/.dotfiles).
Общий рабочий процесс: выбранные и адаптированные навыки
[obra/superpowers](https://github.com/obra/superpowers), встроенные в этот репозиторий.
Стек: **KiCad, C/C++, STM32, FreeRTOS, Renode и Python**.

**Один каталог `skills/`, одна политика, одни скрипты и общая память.**
Настройки обоих клиентов ссылаются на те же физические файлы. Изменение навыка
сразу доступно обоим без повторной установки; клиенту может потребоваться новая
сессия для обновления кэша. Нет переключателя агентов или координатора задач.

## Установка один раз

Требуются Python **3.11+**, Git и отдельно установленные Claude Code/Codex.
Установщик не скачивает пакеты и не меняет модель или режим разрешений. Он добавляет только каталог общей памяти в разрешённые рабочие каталоги клиентов; исходные конфиги сохраняются в резервных файлах.
Сохраните checkout в постоянном локальном каталоге: ссылки зависят от его пути.

Linux:

```sh
git clone https://github.com/60north/.dotfiles-embedded.git
cd .dotfiles-embedded
python3 install-embedded.py --dry-run
python3 install-embedded.py
python3 scripts/doctor.py
```

Windows (PowerShell):

```powershell
git clone https://github.com/60north/.dotfiles-embedded.git
cd .dotfiles-embedded
py -3 install-embedded.py --dry-run
py -3 install-embedded.py
py -3 scripts/doctor.py
```

В Linux используются symlink; в Windows — локальные directory junction через
встроенный Windows PowerShell, без требования Developer Mode для symlink.
Windows-ветка реализована и включена в CI, но локально здесь запускалась только Linux.
Не используйте сетевой диск/cloud-sync для SQLite-памяти. Windows и WSL считайте
отдельными средами; не открывайте один WAL-файл одновременно из двух ОС.

Если в каталогах skills уже есть старые установки:

```sh
python3 install-embedded.py --migrate --dry-run
python3 install-embedded.py --migrate
```

`--migrate` переносит конфликтующие каталоги в соседние `*.before-embedded-*`,
затем ставит ссылки. Содержимое сохраняется, но старые навыки больше не активны.
Точно распознанная старая TypeScript-политика тоже архивируется. Произвольные
существующие инструкции сохраняются; настройки модели, режим разрешений и чужие hooks
не изменяются. Для памяти добавляются Claude `additionalDirectories` и Codex
`writable_roots`. Если уже используются новые именованные permission profiles
Codex, установка остановится до записи: их нельзя смешивать с legacy sandbox
настройками, требуется отдельно проверенное правило для каталога памяти. Отдельный marketplace Superpowers или старые web hooks могут
конфликтовать — `doctor` сообщает замеченные признаки, но не отключает плагины.

Для одного проекта вместо глобальной установки:

```sh
python3 install-embedded.py --project /path/to/project
```

Выберите один scope установки. Проектный вариант может дублироваться с ранее
установленными глобальными навыками; глобальная установка рекомендуется для
обычной работы в нескольких проектах. Она не требует настройки каждого проекта.
`CLAUDE_CONFIG_DIR` и `CODEX_HOME` учитываются. `--memory PATH` выбирает общую
локальную память; по умолчанию используется `experience/` этого checkout.

После установки открывайте Claude Code и Codex в отдельных окнах одного проекта.
При первом запуске остаются обычные механизмы доверия/разрешений самих клиентов.
Дайте каждому свой scope — например, железо и прошивку. Worktree необязательны.

## Архитектура

| Компонент | Каноническое место |
|---|---|
| Все активные навыки | `skills/` |
| Инженерные правила | `policies/ENGINEERING.md` |
| Правила общей памяти | `policies/MEMORY.md` |
| Проверки, память, doctor, обновление | `scripts/` |
| Локальный журнал и evidence | `experience/` (gitignored) |
| Версия/происхождение Superpowers | `vendor/superpowers.json`, `vendor/SUPERPOWERS-LICENSE` |
| Исходный набор citypaul | `legacy/citypaul/` (не загружается) |

`~/.claude/skills` и `~/.agents/skills` ссылаются на **один `skills/` целиком**:
новые каталоги навыков тоже появляются без переустановки. Тонкие блоки в
`~/.claude/CLAUDE.md` и `~/.codex/AGENTS.md` указывают на общую политику и память.
Установщик не делает копий навыков. Автоматический выбор идёт по описаниям и
общему bootstrap; модель должна загрузить минимум релевантных навыков.

Superpowers ведёт отладку, пропорциональное планирование, выполнение, тестирование
и ревью. Маленькое понятное изменение не требует отдельного плана. Автоматическое
создание субагентов, обязательные worktree и повторные согласования убраны.
Адаптации и исходные конфликты описаны в [аудите](docs/AUDIT.md).

Инженерные навыки: `engineering-c-cpp`, `engineering-embedded`,
`engineering-stm32`, `engineering-freertos`, `engineering-python`,
`engineering-hardware-review`, `engineering-kicad-schematic`,
`engineering-kicad-pcb`, `engineering-renode`.

## Общая память и скрипты

При начале задачи агент должен найти релевантный опыт, при завершении — записать
полезные приёмы, неудачи, успешные скрипты и evidence. Это часть политики, а не
ручная команда пользователя. Скрипты могут вызываться агентами из любого проекта
по абсолютному пути из установленного блока настройки.

Память — SQLite с WAL и таймаутом блокировки: два независимых клиента могут писать
одновременно. Записи разделены на `observation`, `failure` и `practice`.
Практика требует существующего успешного отчёта с командой, ревизией и проверяемыми
хэшами лога/артефактов. Проверка целостности не доказывает инженерную корректность:
агент обязан проверить узкий смысл подтверждённого утверждения. Чужие проекты
не попадают в поиск, кроме явно обобщённых `global`-практик. Исправления сохраняют
историю через `--supersedes`. При изменении evidence практика отмечается устаревшей.

```sh
# Эти команды обычно выполняет агент, вручную активировать навык не нужно.
python3 scripts/experience.py --project /path/to/project recall --skill engineering-python
python3 scripts/check.py --project /path/to/project run --skill engineering-python --claim "unit tests" -- python3 -m unittest discover
python3 scripts/check.py --project /path/to/project kicad erc /path/to/design.kicad_sch
python3 scripts/check.py --project /path/to/project kicad drc /path/to/design.kicad_pcb
python3 scripts/check.py --project /path/to/project renode /path/to/scenario.robot
```

`check.py` сохраняет реальный результат и запись опыта автоматически. Общий режим
`run` фиксирует exit code команды; для утверждения «все тесты выполнены» отдельно
проверьте количество/результаты тестов. Renode-режим требует непустой Robot XML
без failed/skipped тестов. KiCad-режим требует JSON-отчёт и поддержку
`--exit-code-violations`, для DRC также `--refill-zones`.
Логи остаются локально; не передавайте секреты в команды, которые записываются.
Успешные повторно используемые скрипты добавляйте в `scripts/` с тестами, не в
отдельную базу каждого клиента.

Инструкции требуют автоматической записи, но не могут гарантировать послушание
модели. Поэтому реальная проверка клиентов выделена отдельно, а не подменена
проверкой содержимого Markdown.

## Проверки и текущий статус

```sh
python3 -m unittest discover -s tests -v
python3 scripts/live_acceptance.py          # только доступность, без платных запусков
python3 scripts/live_acceptance.py --run    # реальные авторизованные клиенты
```

Живой тест не включает навыки вручную: он даёт обычную задачу, проверяет чтение
общего опыта и появление новых записей. Он запускает реальные клиенты без обхода
их разрешений; нужны рабочая аутентификация и доступные модели.

Репрезентативные сценарии: [KiCad](fixtures/kicad/README.md),
[Renode](fixtures/renode/README.md). Они не заменяют тестирование вашей реальной
платы и firmware ELF. [Отчёт проверки](docs/VERIFICATION.md) отделяет выполненные
тесты от блокировок. **Приёмка на настоящих клиентах и инженерных инструментах
ещё не подтверждена в этой среде.**

## Обновление Superpowers

Встроен выбранный набор файлов, не второй экземпляр плагина. Зафиксированный
upstream и локальные адаптации отслеживаются в manifest. Для обновления:

```sh
git clone https://github.com/obra/superpowers.git /path/to/superpowers-upstream
python3 scripts/update_superpowers.py --source /path/to/superpowers-upstream --ref REVIEWED_40_CHARACTER_COMMIT
python3 scripts/update_superpowers.py --source /path/to/superpowers-upstream --ref REVIEWED_40_CHARACTER_COMMIT --apply
python3 -m unittest discover -s tests -v
```

Checkout upstream должен содержать старый и новый коммиты. Обновление делает
трёхстороннее слияние: локальный файл / прежний upstream / новый upstream.
Конфликт останавливает весь update до записи. Новые файлы и новые зависимости
upstream требуют отдельного просмотра, не включаются автоматически. После merge
проверьте инструкции на возврат конфликтующих правил и выполните живой smoke.
Изменения становятся доступны обоим клиентам через существующие ссылки.

## Лицензия

Сохранены корневая [MIT License](LICENSE), вложенные лицензии citypaul и
[MIT License Superpowers](vendor/SUPERPOWERS-LICENSE). Благодарности: Paul Hammond
(citypaul), Jesse Vincent и авторы obra/superpowers. Вложенные лицензии исторического
набора продолжают действовать в соответствующих каталогах `legacy/citypaul/`.
