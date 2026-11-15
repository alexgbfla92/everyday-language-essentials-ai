# Start here

To **install and use** TalkGo, download the .zip from [Releases](https://github.com/alexgbfla92/everyday-language-essentials-ai/releases), follow [How to install](README.md#how-to-install) in the README and send the [first message](FIRST-PROMPT.md) (`Start`).

To **develop**:

- **Structure.** The skill lives entirely in [`skills/talkgo/`](skills/talkgo/): [SKILL.md](skills/talkgo/SKILL.md), `references/` (procedures), `assets/` (templates, locales, reference, target notes and modules) and `scripts/`. Platform manifests live at the root and only point to that folder. See the [architecture](docs/ARCHITECTURE.md).
- **Skill procedures:** [Start wizard](skills/talkgo/references/START.md), [commands](skills/talkgo/references/COMMANDS.md), [missions](skills/talkgo/references/MISSIONS.md), [phrases and voice](skills/talkgo/references/PHRASES-AND-VOICE.md), [Entertainment Lab](skills/talkgo/references/ENTERTAINMENT-LAB.md), [persistence](skills/talkgo/references/PERSISTENCE.md) and [adapters](skills/talkgo/references/adapters/).
- **Native languages.** Central folder and file names and record templates come from `skills/talkgo/assets/locales/<code>/` (`en`, `pt-BR`, `es`, `fr`, `de`). Edit the master templates in `assets/templates/` and the strings in each `locale.json`, then run `python tools/render_locales.py`. To add a native language, copy `locales/en/locale.json` to a new folder, translate every value and render.
- **Development docs:** [architecture](docs/ARCHITECTURE.md), [methodology](docs/METHODOLOGY.md) and [validation](docs/VALIDATION.md).
- **Tests:** `python -B -m unittest discover -s tests`.
- **Package and releases:** `python tools/build_zip.py --plugin` builds and checks `dist/talkgo-plugin-<version>.zip` (`.claude-plugin/`, `.codex-plugin/` and `skills/talkgo/`), the only install path. To publish a version, create the tag `v<version>` or run **Actions → Release**; see [Releases](docs/ARCHITECTURE.md#releases).
- **Version.** `VERSION` is the single source. Every PR bumps it with `python tools/bump_version.py patch|minor|major`, which also updates `plugin.json`, `.claude-plugin/plugin.json` and the "Installed version" line of SKILL.md, shown by `Help`. The GitHub check refuses a PR without a new version or with diverging versions.
- **Translated READMEs.** `README.md` is the source; `README-pt-BR.md`, `README-es.md`, `README-fr.md`, `README-de.md` and `README-zh-CN.md` must keep the same sections (a test checks it).
