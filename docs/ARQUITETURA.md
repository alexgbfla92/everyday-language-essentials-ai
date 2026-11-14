# Arquitetura da Central

O SKILL.md em `skills/talkgo/` define a descoberta e encaminha configuração, diagnóstico, aula, retomada ou acompanhamento. A distribuição leva instruções e modelos vazios. O Projeto ou chat guarda uma referência à pasta pessoal. A pasta pessoal (no Google Drive ou no computador do aluno) guarda o que aconteceu com o aluno.

## Estrutura do repositório

```
everyday-language-essentials-ai/
├── skills/talkgo/          # a skill: única fonte, igual para todas as plataformas
│   ├── SKILL.md               # instruções e tabela do Help (com a versão instalada)
│   ├── references/            # procedimentos lidos sob demanda (comandos, persistência, frases e voz, adaptadores)
│   ├── assets/                # modelos copiados para a Central e módulos pedagógicos
│   └── scripts/               # provision.py e central.py (sem rede)
├── plugin.json                # manifesto portátil (Agent Plugins 1.0) com extensões da OpenAI
├── .claude-plugin/plugin.json # manifesto do plugin para Claude
├── tools/bump_version.py      # sobe e propaga a versão a partir de VERSION
├── tools/build_zip.py         # gera e confere o talkgo-plugin-<versão>.zip
├── .github/workflows/ci.yml   # testes, versões consistentes e versão nova em cada PR
├── .github/workflows/release.yml  # publica a release com o .zip do plugin a cada tag v<versão>
├── tests/                     # testes do planejador, dos comandos e do empacotamento
├── docs/                      # documentação de desenvolvimento (esta pasta)
└── README.md, START-HERE.md, FIRST-PROMPT.md, VERSION
```

Tudo o que a skill usa em tempo de execução fica dentro de `skills/talkgo/` e só referencia arquivos dessa pasta (há teste para isso). Cada plataforma tem apenas um manifesto fino na raiz apontando para a mesma pasta. Para incluir outra plataforma no futuro (por exemplo, Gemini), acrescente o manifesto dela na raiz apontando para `skills/talkgo/`, sem duplicar a skill.

| Camada | Implementação e responsabilidade |
| --- | --- |
| Central | SKILL.md decide a intenção, o idioma e a etapa elegível. Não cita plataformas nem nomes de ferramentas. |
| Método | assets/config contém padrões e metodologia. assets/skills contém os oito módulos selecionáveis. |
| Recursos por idioma | assets/languages contém exemplos, roteiros e modelos localizados. O aluno pode escolher uma ou várias trilhas. |
| Comandos | [references/COMANDOS.md](../skills/talkgo/references/COMANDOS.md) define Help, Info, Create, Remove, Default, os três Reset-* e Pause/Finish/Save-Lesson. scripts/central.py executa os comandos de gestão em pasta local e mantém o registro das Centrais (~/.talkgo/centrais.json) com a padrão. |
| Planos | [references/PLANOS.md](../skills/talkgo/references/PLANOS.md) e o modelo `assets/modelos/plano-missao.md` definem planos de missão por idioma (vários por idioma, com status e histórico de revisões), criados e atualizados pelo `Plan-Mission`; o `Next-Lesson` escolhe o plano e marca a aula na tabela do plano. |
| Frases e voz | [references/FRASES-E-VOZ.md](../skills/talkgo/references/FRASES-E-VOZ.md) define a numeração global de frases (F) e diálogos (D) por idioma, a busca por número e o salvamento ao pausar ou terminar, com Save-Lesson no texto quando o modo voz não consegue gravar. |
| Provisionamento | scripts/provision.py classifica cada caminho (Markdown, Google Doc ou Google Sheet) e planeja operações do conector Drive a partir de listagens e abas verificadas ou, com `--local`, cria a estrutura diretamente numa pasta local sem sobrescrever. Pode ser executado novamente após interrupção. |
| Persistência | [references/PERSISTENCIA.md](../skills/talkgo/references/PERSISTENCIA.md) define a escolha do adaptador, leitura e atualização por ID, isolamento e reparação dos registros derivados. |
| Adaptadores | references/adaptadores/ contém as operações específicas de [pasta local](../skills/talkgo/references/adaptadores/pasta-local.md), [Google Drive](../skills/talkgo/references/adaptadores/drive.md), [OneDrive](../skills/talkgo/references/adaptadores/onedrive.md) e [modo manual](../skills/talkgo/references/adaptadores/manual.md). |

## Compatibilidade entre plataformas

O mesmo pacote atende Claude e ChatGPT. O SKILL.md segue o formato comum de skills (pasta com SKILL.md e frontmatter `name` e `description`), lido pelas duas plataformas. Tudo o que depende da plataforma fica nos adaptadores, e o modelo escolhe o adaptador pelo que a sessão comprovadamente consegue fazer, não pelo nome da plataforma. Layout e caminhos lógicos são idênticos em todos os adaptadores. O formato também, exceto no Google Drive por conector, que grava os registros atualizados durante o uso como Google Docs e Sheets nativos, porque o conector do Claude não regrava o conteúdo de arquivos existentes. Uma Central no Drive pode ser usada pelo Claude e pelo ChatGPT, que editam Docs e Sheets nativos.

A única forma de instalação suportada é o envio do `talkgo-plugin-<versão>.zip` pelo navegador, porque assim o plugin fica na conta e vale em todos os dispositivos. O .zip leva `.claude-plugin/plugin.json` (Claude), `.codex-plugin/plugin.json` (ChatGPT, gerado a partir do `plugin.json` da raiz) e `skills/talkgo/`.

| Plataforma | Instalação | Chamada | Armazenamento esperado |
| --- | --- | --- | --- |
| Claude (web, desktop, celular) | Configurações → Personalização → Plugins → Adicionar → Enviar plugin | `/talkgo` | Google Drive com os conectores Google Drive, Google Docs e Google Sheets. |
| ChatGPT (web, desktop, celular) | Plugins → Adicionar | `@TalkGo` ou `$talkgo:talkgo` | Google Drive (Docs e Sheets nativos). |

## Releases

Cada versão publicada é uma release do GitHub com dois arquivos: `talkgo-plugin-<versão>.zip` e uma cópia com nome fixo, `talkgo-plugin.zip`, que o README usa no link `releases/latest/download/talkgo-plugin.zip`. O workflow `.github/workflows/release.yml` roda os testes, confere se a tag é igual ao `VERSION`, gera o .zip e cria a release com as notas geradas a partir dos PRs. Para publicar a versão que está na main:

```
git tag v$(cat VERSION) && git push origin v$(cat VERSION)
```

ou use **Actions → Release → Run workflow**, que cria a tag a partir do `VERSION`. Uma versão já publicada não é publicada de novo: suba o `VERSION` antes.

Estado das capacidades:

- Comprovado pelo autor no Claude: o `update_file` do conector Google Drive só altera metadados; o conector Google Docs não edita `.md`; criar Doc com `text/plain` e Sheet com `text/csv` via `create_file`, editar com `update_doc` e `update_values`/`append_values` e reler funcionam mantendo o mesmo ID.
- Testado neste repositório: `claude plugin validate --strict` no repositório e no .zip extraído, e o .zip carregado no Claude Code (`--plugin-dir`) e no Codex CLI.
- Testes automatizados: empacotamento (nome da pasta igual ao da skill, manifestos coerentes, versões iguais ao VERSION, links que não saem da skill), classificação de formatos, planejamento do Drive com Docs e Sheets (inclusive retomada após interrupção e configuração de abas), modo local e comandos de gestão (scripts/central.py) com pastas fictícias.
- Pendente de ensaio: instalação pelo ChatGPT (workspace e desktop) e uso na web e no celular; setup completo, aula, reset e remove no Drive nativo pelo Claude; o mesmo fluxo pelo ChatGPT, inclusive se o conector dele converte `text/plain` e `text/csv` em Doc e Sheet na criação.

A abertura de um link do GitHub ou a inclusão de uma pasta nas fontes de um Projeto, por si só, não comprova instalação nem capacidade de escrita. Verifique essas capacidades na interface efetivamente usada.

A instalação pública, permissões na conta de um novo aluno, a experiência móvel e voz exigem ensaio de ponta a ponta. A integração usa as ações oferecidas pela conexão do aluno, sem credenciais no repositório.
