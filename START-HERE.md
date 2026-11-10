# Começar

A skill é um único pacote que funciona no Claude, no ChatGPT e no Codex. Instale a pasta completa everyday-language-essentials-ai, com SKILL.md, docs/, assets/ e scripts/ lado a lado, pelo mecanismo da sua plataforma:

- **Codex**: copie a pasta para o diretório de skills do ambiente. Um destino por projeto é .agents/skills/everyday-language-essentials-ai/.
- **ChatGPT**: envie o pacote pelo mecanismo de skills habilitado na conta e conecte o Google Drive.
- **Claude Code**: adicione o repositório como marketplace e instale o plugin:
  ```
  /plugin marketplace add alexgbfla92/everyday-language-essentials-ai
  /plugin install everyday-language-essentials-ai@everyday-essentials
  ```
  Ou copie a pasta para .claude/skills/everyday-language-essentials-ai/ (projeto) ou ~/.claude/skills/everyday-language-essentials-ai/ (usuário).
- **App do Claude (web, desktop)**: gere o .zip e envie como skill nas configurações da conta:
  ```
  git archive --format=zip --prefix=everyday-language-essentials-ai/ -o everyday-language-essentials-ai.zip HEAD
  ```
  Para salvar o progresso automaticamente, conecte ao app uma pasta do seu computador.

Depois, abra uma conversa com a skill disponível e use o [primeiro pedido](FIRST-PROMPT.md) da sua plataforma. Escolha uma pasta pessoal dedicada, no Google Drive ou no seu computador. A skill escolhe como salvar conforme o que a sessão consegue fazer; veja [persistência](docs/PERSISTENCIA.md#escolher-o-adaptador).

Para desenvolver, consulte a [arquitetura](docs/ARQUITETURA.md), a [metodologia](docs/METODOLOGIA.md), o [protocolo de persistência](docs/PERSISTENCIA.md), os [adaptadores](docs/adaptadores/) e a [validação](docs/VALIDACAO-E-ROADMAP.md). O [README](README.md) apresenta o manifesto do produto.
