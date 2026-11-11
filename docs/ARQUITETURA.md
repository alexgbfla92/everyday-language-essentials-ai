# Arquitetura da Central

O SKILL.md na raiz define a descoberta e encaminha configuração, diagnóstico, aula, retomada ou acompanhamento. A distribuição leva instruções e modelos vazios. O Projeto ou chat guarda uma referência à pasta pessoal. A pasta pessoal (no Google Drive ou no computador do aluno) guarda o que aconteceu com o aluno.

| Camada | Implementação e responsabilidade |
| --- | --- |
| Central | SKILL.md decide a intenção, o idioma e a etapa elegível. Não cita plataformas nem nomes de ferramentas. |
| Método | assets/config contém padrões e metodologia. assets/skills contém os oito módulos selecionáveis. |
| Recursos por idioma | assets/languages contém exemplos, roteiros e modelos localizados. O aluno pode escolher uma ou várias trilhas. |
| Comandos | docs/COMANDOS.md define Help, Info, Create, Remove, Default e os três Reset-*. scripts/central.py executa esses comandos em pasta local e mantém o registro das Centrais (~/.everylang/centrais.json) com a padrão. |
| Frases e voz | docs/FRASES-E-VOZ.md define a numeração global de frases (F) e diálogos (D) por idioma, a busca por número e o salvamento ao pausar ou terminar, com Save-Lesson no texto quando o modo voz não consegue gravar. |
| Provisionamento | scripts/provision.py classifica cada caminho (Markdown, Google Doc ou Google Sheet) e planeja operações do conector Drive a partir de listagens e abas verificadas ou, com `--local`, cria a estrutura diretamente numa pasta local sem sobrescrever. Pode ser executado novamente após interrupção. |
| Persistência | docs/PERSISTENCIA.md define a escolha do adaptador, leitura e atualização por ID, isolamento, migração e reparação dos registros derivados. |
| Adaptadores | docs/adaptadores/ contém as operações específicas de [pasta local](adaptadores/pasta-local.md), [Google Drive](adaptadores/drive.md), [OneDrive](adaptadores/onedrive.md) e [modo manual](adaptadores/manual.md). |

## Compatibilidade entre plataformas

O mesmo pacote atende Claude, ChatGPT e Codex. O SKILL.md segue o formato comum de skills (pasta com SKILL.md e frontmatter `name` e `description`), lido pelas três plataformas. Tudo o que depende da plataforma fica nos adaptadores, e o modelo escolhe o adaptador pelo que a sessão comprovadamente consegue fazer, não pelo nome da plataforma. Layout e caminhos lógicos são idênticos em todos os adaptadores. O formato também, exceto no Google Drive por conector, que grava os registros atualizados durante o uso como Google Docs e Sheets nativos, porque o conector do Claude não regrava o conteúdo de arquivos existentes. Uma Central no Drive pode ser usada pelo Claude e pelo ChatGPT, que editam Docs e Sheets nativos.

| Plataforma | Instalação | Armazenamento esperado |
| --- | --- | --- |
| Codex | Pasta completa no diretório de skills do ambiente, por exemplo .agents/skills/everylang/. | Pasta local ou Drive conectado. |
| ChatGPT | Mesmo pacote pelo mecanismo de skills habilitado na conta. | Drive conectado (Docs e Sheets nativos). |
| Claude Code | Plugin everylang pelo marketplace do repositório (/everylang:everylang) ou pasta em .claude/skills/everylang/ (/everylang). | Pasta local. |
| App do Claude (web, desktop, celular) | Plugin everylang pelo marketplace do repositório ou pacote .zip enviado como skill (/everylang). | Google Drive com os conectores Google Drive, Google Docs e Google Sheets (funciona 100% na nuvem); ou pasta conectada ao app; senão modo manual. |

Estado das capacidades:

- Comprovado pelo autor no Claude: o `update_file` do conector Google Drive só altera metadados; o conector Google Docs não edita `.md`; criar Doc com `text/plain` e Sheet com `text/csv` via `create_file`, editar com `update_doc` e `update_values`/`append_values` e reler funcionam mantendo o mesmo ID.
- Testes automatizados: classificação de formatos, planejamento do Drive com Docs e Sheets (inclusive retomada após interrupção e configuração de abas), modo local e comandos de gestão (scripts/central.py) com pastas fictícias.
- Pendente de ensaio: setup completo, aula, reset e remove no Drive nativo pelo Claude; o mesmo fluxo pelo ChatGPT, inclusive se o conector dele converte `text/plain` e `text/csv` em Doc e Sheet na criação.

A abertura de um link do GitHub ou a inclusão de uma pasta nas fontes de um Projeto, por si só, não comprova instalação nem capacidade de escrita. Verifique essas capacidades na interface efetivamente usada.

A instalação pública, permissões na conta de um novo aluno, a experiência móvel e voz exigem ensaio de ponta a ponta. A integração usa as ações oferecidas pela conexão do aluno, sem credenciais no repositório.
