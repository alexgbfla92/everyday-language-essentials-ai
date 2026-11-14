# Começar

Para **instalar e usar**, siga a seção [Como instalar](README.md#como-instalar) do README e o [primeiro pedido](FIRST-PROMPT.md).

Para **desenvolver**:

- **Estrutura.** A skill fica inteira em [`skills/talkgo/`](skills/talkgo/): [SKILL.md](skills/talkgo/SKILL.md), `references/` (procedimentos), `assets/` (modelos e módulos) e `scripts/`. Os manifestos de cada plataforma ficam na raiz e só apontam para essa pasta. Veja a [arquitetura](docs/ARQUITETURA.md).
- **Procedimentos da skill:** [comandos](skills/talkgo/references/COMANDOS.md), [frases e voz](skills/talkgo/references/FRASES-E-VOZ.md), [persistência](skills/talkgo/references/PERSISTENCIA.md) e [adaptadores](skills/talkgo/references/adaptadores/).
- **Documentação de desenvolvimento:** [arquitetura](docs/ARQUITETURA.md), [metodologia](docs/METODOLOGIA.md) e [validação](docs/VALIDACAO-E-ROADMAP.md).
- **Testes:** `python -B -m unittest discover -s tests`.
- **Pacote .zip** (envio pelo navegador no Claude e no ChatGPT): `python tools/build_zip.py` gera e confere `dist/talkgo-skill-<versão>.zip` (skill); com `--plugin`, gera `dist/talkgo-plugin-<versão>.zip` (plugin com `.claude-plugin/plugin.json` e `.codex-plugin/plugin.json`, para Plugins > Adicionar no Claude e no ChatGPT).
- **Versão.** `VERSION` é a fonte única. Todo PR sobe a versão com `python tools/bump_version.py patch|minor|major`, que atualiza também `plugin.json`, `.claude-plugin/plugin.json` e a linha "Versão instalada" do SKILL.md, mostrada no `Help`. A verificação do GitHub recusa PR sem versão nova ou com versões divergentes.
