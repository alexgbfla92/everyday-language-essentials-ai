# Adaptador: Google Drive (formato nativo)

Use este guia quando as [regras de seleção](../PERSISTENCIA.md#escolher-o-adaptador) apontarem o Google Drive por conector. Pastas e caminhos lógicos são os mesmos dos outros adaptadores, mas aqui os arquivos gravados durante o uso são Google Docs ou Google Sheets nativos. Os arquivos que só são lidos continuam em Markdown. Registre `formato_registros: nativo` no estado global.

## Verificar a capacidade

O adaptador só passa se a sessão tiver, ao mesmo tempo:

1. **Drive**: listar os filhos diretos de uma pasta, criar pasta num pai indicado, criar arquivo com conteúdo num pai indicado (convertendo texto em Doc e CSV em Sheet), copiar arquivo e mover para a lixeira.
2. **Docs**: ler um Google Doc com a revisão atual e aplicar um batchUpdate (inserir, apagar intervalo, substituir texto).
3. **Sheets**: ler e gravar valores por intervalo, acrescentar linhas e renomear ou criar abas.

Verifique pela capacidade, não pelo nome da ferramenta. Exemplos de nomes:

| Capacidade | Claude | ChatGPT / Codex |
| --- | --- | --- |
| Listar, criar, copiar, lixeira | conector Google Drive: `search_files` (filtro `'ID' in parents`), `create_file`, `copy_file`, `trash_file` | conector Google Drive: `list_folder`, `create_folder`, `upload_file` |
| Docs | conector Google Docs: `read_doc`, `update_doc` | edição nativa de Docs do conector |
| Sheets | conector Google Sheets: `get_values`, `update_values`, `append_values`, `update_spreadsheet`, `batch_clear_values` | edição nativa de Sheets do conector |

O `update_file` do conector Google Drive do Claude **só altera metadados** (nome, pasta, estrela, bloqueio); ele não regrava conteúdo. O conector Google Docs não edita arquivos `.md`. Por isso, tudo o que é atualizado depois de criado precisa ser nativo.

Se faltar a edição de Docs ou de Sheets, o adaptador não passa. Diga ao aluno quais conectores instalar (no Claude: Google Drive, Google Docs e Google Sheets) e siga as regras de seleção (pasta local ou modo manual).

## Formatos

| Caminho lógico | Formato no Drive | Nome no Drive |
| --- | --- | --- |
| config/defaults.md, idiomas.md, metodologia.md | Markdown | com `.md` |
| config/estado-global.md, config/perfil.md | Google Doc | sem `.md` |
| languages/L/config.md, conteudo/*, diagnosticos/MODELO.md, diagnosticos/09-roteiro-diagnostico-inicial.md, aulas/MODELO.md, progresso/historico/README.md | Markdown | com `.md` |
| languages/L/estado/sessao-ativa.md, contexto-recente.md, perfil-atual.md | Google Doc | sem `.md` |
| languages/L/diagnosticos/diagnostico-AAAAMMDD-NN.md, aulas/aula-AAAAMMDD-NN.md | Google Doc | sem `.md` |
| languages/L/planos/&lt;id&gt;.md | Google Doc | sem `.md` |
| languages/L/progresso/08-registro-progresso.md | Google Sheet | sem `.md` |
| languages/L/progresso/historico/&lt;resumo-de-ciclo&gt;.md | Markdown, criado uma vez e nunca editado | com `.md` |

`scripts/provision.py` aplica essa tabela (função `classify`). O índice em `config/estado-global` continua mapeando o caminho lógico (com `.md`) para o ID e o formato.

### Conteúdo dos Docs

O Doc guarda o mesmo Markdown do modelo como texto puro, com a mesma estrutura (títulos, linhas `campo: valor` e tabelas com `|`). Não use formatação do Docs. Para criar um Doc, envie o texto com MIME de conteúdo `text/plain` sem desativar a conversão para tipo Google.

### Planilha 08-registro-progresso

| Aba | Colunas | Uso |
| --- | --- | --- |
| `Resumo` | Campo \| Valor | Linhas fixas na ordem do modelo: idioma, status, missão, aula padrão, ciclo ativo, aulas regulares concluídas, duração real observada, CEFR por habilidade (compreensão oral, produção oral, interação, leitura geral, leitura técnica), próxima reavaliação, próximo passo, revisão. Atualize a célula B da linha do campo. |
| `Aulas` | ID da sessão \| Data \| Objetivo \| Evidência \| Próxima tarefa | Uma linha por aula regular concluída, acrescentada no fim. Testes nunca entram. |

Os nomes das abas são fixos nos três idiomas. Os títulos das colunas e dos campos vêm do modelo do idioma (`assets/languages/L/progresso/08-registro-progresso.md`), que é a única fonte: a primeira tabela do modelo vira a aba `Resumo` e a segunda vira a aba `Aulas`.

## Identificar a raiz

Obtenha o ID e os metadados da pasta dedicada do aluno e verifique a cadeia de pais. Recuse atalhos. Nunca use busca global por nome para escolher a pasta onde vai gravar.

## Provisionar

1. Execute a partir da pasta da skill: `python scripts/provision.py ID_PESSOAL inventario.json en-US es-ES [--abas abas.json]`. O inventário inicial é `{}`; `abas.json` começa vazio ou ausente.
2. `list_parent_ids`: para cada pai, liste seus filhos diretos (inclusive pastas, Docs, Sheets e Markdown) e confirme que a listagem está completa. Registre no inventário o ID do pai como chave e a lista de objetos com `id`, `title` e `mime_type`. Pasta verificada vazia recebe `[]`; leitura incompleta ou falha nunca equivale a `[]`.
3. `inspect_sheet_ids`: para cada planilha, leia os títulos das abas na ordem e registre em `abas.json` (ID → lista de títulos).
4. Execute `operations`, somente no pai indicado:
   - `create_folder`: cria a pasta.
   - `create_file` com `kind: markdown`: cria o arquivo com o texto de `content_file`, MIME `text/markdown`, sem conversão.
   - `create_file` com `kind: google-doc`: cria com o texto de `content_file` e MIME de conteúdo `text/plain`, com conversão; o resultado deve ser `application/vnd.google-apps.document`.
   - `create_file` com `kind: google-sheet`: cria com o `csv` da operação e MIME de conteúdo `text/csv`, com conversão; o resultado deve ser `application/vnd.google-apps.spreadsheet`.
   - `configure_sheet`: se `rename_first_tab` vier preenchido, renomeie a primeira aba (a conversão cria "Untitled"); para cada item de `add_tabs`, crie a aba e grave as `rows` a partir de A1.
5. Releia cada objeto criado (ID, nome, MIME, pai e conteúdo; nas planilhas, abas e valores) e atualize o inventário. Repita o planejador até `operations`, `list_parent_ids` e `inspect_sheet_ids` ficarem vazios. A reconciliação reconhece Docs e Sheets já criados por uma execução interrompida e não os recria; se um nome existir com o tipo errado, o planejador para com conflito.

Sem execução de Python, percorra a árvore assets/config e assets/languages dos idiomas escolhidos na mesma ordem (pais antes dos filhos), incluindo a subpasta planos, aplicando a tabela de formatos e as mesmas verificações.

## Criar sessões e planos

Ao iniciar um diagnóstico ou aula, crie o Doc `diagnostico-AAAAMMDD-NN` ou `aula-AAAAMMDD-NN` na pasta do idioma com o texto do MODELO.md correspondente (`text/plain`, com conversão). Planos (`planos/<id>`) também nascem como Doc. Registre o ID no índice e no ponteiro de sessão ativa antes da primeira atividade.

## Gravar e reler Docs

Toda escrita num Doc parte de uma leitura recente, que dá o texto, o `revisionId` e o `endIndex` do último elemento do corpo. Envie a escrita com `writeControl.requiredRevisionId` igual à revisão lida. Use um destes dois procedimentos:

- **Substituição total** (ex.: checkpoint reescrito, derivado restaurado ao modelo): um único batchUpdate com `deleteContentRange` no intervalo [1, endIndex − 1) e, em seguida, `insertText` no índice 1 com o texto completo. Se o corpo estiver vazio (endIndex − 1 ≤ 1), envie só o `insertText`.
- **Edição pontual** (ex.: um campo `campo: valor`, uma linha nova numa tabela): `replaceAllText` com um trecho que ocorra uma única vez no documento, como a linha inteira do campo ou um marcador único. Confirme na leitura que o trecho aparece exatamente uma vez antes de enviar.

Depois de cada escrita, releia o Doc e compare revisão, operação, evidências e próxima pergunta. Se a escrita for recusada porque a revisão mudou, outra escrita interveio: releia, reconcilie pelo ID da operação e pelas falas, conforme o [protocolo](../PERSISTENCIA.md#salvar-retomar-e-reparar), e só então repita com a nova revisão. Nunca repita a escrita sem reler.

## Gravar e reler Sheets

- Campo do `Resumo`: localize a linha do campo pela coluna A e grave a coluna B dessa linha (`Resumo!B<n>`).
- Aula válida: acrescente uma linha em `Aulas` (acrescentar a partir de `Aulas!A1`). Antes, confira que o ID da sessão ainda não está na coluna A, para não contar a mesma aula duas vezes.
- Releia o intervalo gravado e compare.

A gravação de valores não tem controle de revisão. Mantenha um único chat escritor por sessão e por Central.

## Remover e zerar

Remove-CentralIdioma e os Reset-* (veja [comandos](../COMANDOS.md)) só apagam movendo para a lixeira do Drive, o que vale também para Docs e Sheets. Os backups de reset são cópias nativas (`copy_file`) numa subpasta de `_backups/`. Para devolver um derivado ao modelo:

- Doc: substituição total com o texto do modelo.
- Sheet: limpe as abas `Resumo` e `Aulas` e regrave as duas tabelas do modelo a partir de A1.

Nunca sobrescreva um arquivo para "apagá-lo".

Uma pasta do Google Drive sincronizada no computador (Google Drive para computador) pode usar o [adaptador de pasta local](pasta-local.md) com `provedor: google-drive`; nesse caso, tudo fica em Markdown.
