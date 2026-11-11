# Começar

A skill **everylang** (Everyday Language Essentials AI) é um único pacote que funciona no Claude, no ChatGPT e no Codex. Instale a pasta completa, com SKILL.md, docs/, assets/ e scripts/ lado a lado, pelo mecanismo da sua plataforma. Onde a plataforma exigir que o nome da pasta seja igual ao da skill, use `everylang`.

- **Codex**: copie o conteúdo do repositório para o diretório de skills do ambiente, por exemplo .agents/skills/everylang/. Chame com `$everylang`.
- **ChatGPT**: envie o pacote pelo mecanismo de skills habilitado na conta e conecte o Google Drive; a Central no Drive usa Google Docs e Sheets nativos, que o conector precisa editar.
- **Claude Code**: adicione o repositório como marketplace e instale o plugin:
  ```
  /plugin marketplace add alexgbfla92/everyday-language-essentials-ai
  /plugin install everylang@everyday-essentials
  ```
  Chame com `/everylang:everylang`. Para chamar só com `/everylang`, copie o conteúdo do repositório para ~/.claude/skills/everylang/ (usuário) ou .claude/skills/everylang/ (projeto) em vez de instalar o plugin.
- **App do Claude (web, desktop)**: em Configurações → Plugins, adicione o marketplace `alexgbfla92/everyday-language-essentials-ai` e instale **everylang**. Outra opção é enviar o .zip como skill, que fica disponível como `/everylang`:
  ```
  git archive --format=zip --prefix=everylang/ -o everylang.zip HEAD
  ```
  Para usar 100% na nuvem (celular, PC e tablet), ative os conectores **Google Drive**, **Google Docs** e **Google Sheets** em Configurações → Conectores; a Central fica no seu Drive com os registros em Google Docs e Sheets. Sem eles, conecte ao app uma pasta do seu computador.

Se você já tinha instalado a versão com o nome everyday-language-essentials-ai, desinstale o plugin antigo e instale **everylang**. Suas Centrais não são afetadas: elas ficam na sua pasta pessoal, fora do pacote.

Depois, abra uma conversa com a skill disponível e use o [primeiro pedido](FIRST-PROMPT.md) da sua plataforma, ou `Help` para ver os [comandos](docs/COMANDOS.md). A skill escolhe como salvar conforme o que a sessão consegue fazer; veja [persistência](docs/PERSISTENCIA.md#escolher-o-adaptador).

Para desenvolver, consulte a [arquitetura](docs/ARQUITETURA.md), a [metodologia](docs/METODOLOGIA.md), os [comandos](docs/COMANDOS.md), o [protocolo de persistência](docs/PERSISTENCIA.md), os [adaptadores](docs/adaptadores/) e a [validação](docs/VALIDACAO-E-ROADMAP.md). O [README](README.md) apresenta o manifesto do produto.
