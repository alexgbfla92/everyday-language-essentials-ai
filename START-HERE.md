# Começar

Para **instalar e usar**, baixe o .zip em [Releases](https://github.com/alexgbfla92/everyday-language-essentials-ai/releases) e siga a seção [Como instalar](README.md#como-instalar) do README e o [primeiro pedido](FIRST-PROMPT.md).

Para **desenvolver**:

- **Estrutura.** A skill fica inteira em [`skills/talkgo/`](skills/talkgo/): [SKILL.md](skills/talkgo/SKILL.md), `references/` (procedimentos), `assets/` (modelos e módulos) e `scripts/`. Os manifestos de cada plataforma ficam na raiz e só apontam para essa pasta. Veja a [arquitetura](docs/ARQUITETURA.md).
- **Procedimentos da skill:** [comandos](skills/talkgo/references/COMANDOS.md), [frases e voz](skills/talkgo/references/FRASES-E-VOZ.md), [persistência](skills/talkgo/references/PERSISTENCIA.md) e [adaptadores](skills/talkgo/references/adaptadores/).
- **Documentação de desenvolvimento:** [arquitetura](docs/ARQUITETURA.md), [metodologia](docs/METODOLOGIA.md) e [validação](docs/VALIDACAO-E-ROADMAP.md).
- **Testes:** `python -B -m unittest discover -s tests`.
- **Pacote e releases:** `python tools/build_zip.py --plugin` gera e confere `dist/talkgo-plugin-<versão>.zip` (`.claude-plugin/`, `.codex-plugin/` e `skills/talkgo/`), a única forma de instalação. Para publicar uma versão para os usuários, crie a tag `v<versão>` ou rode **Actions → Release**; veja [Releases](docs/ARQUITETURA.md#releases).
- **Versão.** `VERSION` é a fonte única. Todo PR sobe a versão com `python tools/bump_version.py patch|minor|major`, que atualiza também `plugin.json`, `.claude-plugin/plugin.json` e a linha "Versão instalada" do SKILL.md, mostrada no `Help`. A verificação do GitHub recusa PR sem versão nova ou com versões divergentes.
