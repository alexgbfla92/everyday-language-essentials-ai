# Arquitetura da Central

O SKILL.md na raiz define a descoberta e encaminha configuração, diagnóstico, aula, retomada ou acompanhamento. A distribuição leva instruções e modelos vazios. O Projeto ou chat guarda uma referência à pasta pessoal. A pasta pessoal (no Google Drive ou no computador do aluno) guarda o que aconteceu com o aluno.

| Camada | Implementação e responsabilidade |
| --- | --- |
| Central | SKILL.md decide a intenção, o idioma e a etapa elegível. Não cita plataformas nem nomes de ferramentas. |
| Método | assets/config contém padrões e metodologia. assets/skills contém os oito módulos selecionáveis. |
| Recursos por idioma | assets/languages contém exemplos, roteiros e modelos localizados. O aluno pode escolher uma ou várias trilhas. |
| Comandos | docs/COMANDOS.md define Help, Info, Create, Remove, Default e os três Reset-*. scripts/central.py executa esses comandos em pasta local e mantém o registro das Centrais (~/.everylang/centrais.json) com a padrão. |
| Provisionamento | scripts/provision.py planeja operações do conector Drive a partir de listagens verificadas ou, com `--local`, cria a estrutura diretamente numa pasta local sem sobrescrever. Pode ser executado novamente após interrupção. |
| Persistência | docs/PERSISTENCIA.md define a escolha do adaptador, leitura e atualização por ID, isolamento, migração e reparação dos registros derivados. |
| Adaptadores | docs/adaptadores/ contém as operações específicas de [pasta local](adaptadores/pasta-local.md), [Google Drive](adaptadores/drive.md), [OneDrive](adaptadores/onedrive.md) e [modo manual](adaptadores/manual.md). |

## Compatibilidade entre plataformas

O mesmo pacote atende Claude, ChatGPT e Codex. O SKILL.md segue o formato comum de skills (pasta com SKILL.md e frontmatter `name` e `description`), lido pelas três plataformas. Tudo o que depende da plataforma fica nos adaptadores, e o modelo escolhe o adaptador pelo que a sessão comprovadamente consegue fazer, não pelo nome da plataforma. Layout e formato dos registros são idênticos em todos os adaptadores, então uma pasta criada numa plataforma pode ser lida em outra quando as duas alcançam o mesmo armazenamento.

| Plataforma | Instalação | Armazenamento esperado |
| --- | --- | --- |
| Codex | Pasta completa no diretório de skills do ambiente, por exemplo .agents/skills/everylang/. | Pasta local ou Drive conectado. |
| ChatGPT | Mesmo pacote pelo mecanismo de skills habilitado na conta. | Drive conectado. |
| Claude Code | Plugin everylang pelo marketplace do repositório (/everylang:everylang) ou pasta em .claude/skills/everylang/ (/everylang). | Pasta local. |
| App do Claude | Plugin everylang pelo marketplace do repositório ou pacote .zip enviado como skill (/everylang). | Pasta conectada ao app (inclusive pasta sincronizada do Google Drive ou OneDrive); conector somente se oferecer escrita; senão modo manual. |

Estado das capacidades: o fluxo do Drive com as ações do ChatGPT e do Codex é o mesmo da versão 0.2.0. O modo local e os comandos de gestão (scripts/central.py) têm testes automatizados com pastas fictícias. Pelos conectores, Remove e Reset seguem o procedimento documentado sem teste automatizado. A escrita pelo conector Drive do Claude não foi verificada; por isso o adaptador exige conferir a capacidade na sessão antes de usar.

A abertura de um link do GitHub ou a inclusão de uma pasta nas fontes de um Projeto, por si só, não comprova instalação nem capacidade de escrita. Verifique essas capacidades na interface efetivamente usada.

A instalação pública, permissões na conta de um novo aluno, a experiência móvel e voz exigem ensaio de ponta a ponta. A integração usa as ações oferecidas pela conexão do aluno, sem credenciais no repositório.
