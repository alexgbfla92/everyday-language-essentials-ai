# Adaptador: Google Drive

Use este guia quando as [regras de seleção](../PERSISTENCIA.md#escolher-o-adaptador) apontarem o Drive. O protocolo geral continua em [PERSISTENCIA.md](../PERSISTENCIA.md); aqui ficam só as operações específicas.

## Verificar a capacidade

O conector precisa oferecer quatro ações: listar os filhos diretos de uma pasta, criar pasta num pai indicado, criar arquivo num pai indicado e atualizar o conteúdo de um arquivo existente pelo ID. No conector do ChatGPT e do Codex essas ações aparecem como `list_folder`, `create_folder`, `upload_file` e `update_file`. No conector Google Drive do Claude aparecem ações como `search_files`, `create_file`, `update_file` e `trash_file`; confirme na sessão que `create_file` aceita pasta pai e cria pastas antes de usar. Em outra plataforma os nomes podem ser diferentes: confira a lista de ferramentas da sessão. Se o conector só busca ou lê, não use o Drive para escrita; volte às regras de seleção e use pasta local ou modo manual.

Identificadores: o ID de cada pasta ou arquivo no Drive. Tipos: pastas usam `application/vnd.google-apps.folder`; registros usam `text/markdown` (aceite `text/plain` em registros antigos).

## Identificar a raiz

Obtenha o ID e os metadados da pasta dedicada do aluno e verifique a cadeia de pais. Recuse atalhos. Nunca use busca global por nome para escolher a pasta onde vai gravar.

## Provisionar

1. Execute a partir da pasta da skill: `python scripts/provision.py ID_PESSOAL inventario.json en-US es-ES`, usando os idiomas escolhidos. O inventário inicial é `{}`.
2. O resultado pede listagens pelos IDs em `list_parent_ids`. Para cada pai, liste seus filhos diretos e confirme que a listagem está completa (use paginação, se necessário). Registre no JSON o ID do pai como chave e a lista de objetos com `id`, `title` e `mime_type` como valor. Uma pasta verificada vazia recebe `[]`. Uma leitura incompleta ou falha nunca equivale a `[]`.
3. Execute os pedidos em `operations`, somente no pai indicado. `create_folder` cria a pasta. `upload_file` cria o arquivo Markdown com o conteúdo do asset indicado em `file_uri`; se o conector não aceitar um caminho local, leia o asset e envie o texto UTF-8 como conteúdo.
4. Confira ID, nome, MIME e pai na releitura e compare o conteúdo dos arquivos novos. Atualize as listagens afetadas e repita o planejador até `operations` e `list_parent_ids` ficarem vazios.

Em interface sem execução de Python, percorra a árvore assets/config e assets/languages dos idiomas escolhidos na mesma ordem (pais antes dos filhos), incluindo a subpasta planos, com as mesmas verificações.

## Gravar e reler

Atualize sempre o mesmo ID e MIME com a ação de atualização do conector (no ChatGPT e no Codex, `update_file(fileId, file_uri, mime_type)`). Depois releia pelo ID e compare revisão, operação, evidências e próxima pergunta. Se o aluno preferir Google Docs, use a edição nativa do mesmo documento e releia o conteúdo.

## Remover

Remove-CentralIdioma e os Reset-* (veja [comandos](../COMANDOS.md)) só apagam pela ação de lixeira do conector, quando existir (no Claude, `trash_file`), para que o aluno possa recuperar pela lixeira do Drive. Sem essa ação, liste os itens com link e peça que o aluno os apague. Nunca sobrescreva um arquivo para "apagá-lo".

Uma pasta do Google Drive sincronizada no computador (Google Drive para computador) pode usar o [adaptador de pasta local](pasta-local.md) com `provedor: google-drive`.
