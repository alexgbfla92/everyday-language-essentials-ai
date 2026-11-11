# Comandos da Central

Os comandos funcionam em qualquer plataforma. São texto: o aluno digita depois de chamar a skill (`/everylang:everylang Reset-Lessons Inglês` no Claude e `$everylang:everylang Reset-Lessons Inglês` no ChatGPT e no Codex, quando instalada como plugin; `/everylang` e `$everylang` quando instalada como skill avulsa) ou em qualquer mensagem de uma conversa em que a skill já esteja ativa.

## Como reconhecer

- Ignore maiúsculas, acentos e o hífen: `Reset-Lessons`, `reset lessons` e `RESET-LESSONS` são o mesmo comando.
- Os argumentos podem vir em qualquer ordem depois do comando. Idioma aceita o nome em português, inglês, espanhol ou francês, ou a tag (`Inglês`, `ingles`, `English`, `en`, `en-US`). `Todos` vale para todos os idiomas da Central.
- Central é indicada pelo nome ou pelo caminho/ID da raiz.
- Durante uma aula ou diagnóstico, `HELP` continua sendo pedido de apoio no exercício (veja o SKILL.md). Para ver a lista de comandos no meio de uma atividade, use `Help-Comandos`.

## Ambiguidade

Antes de executar, resolva Central e idioma nesta ordem e faça uma única pergunta por vez, com as opções numeradas:

1. **Central.** Se o aluno indicou, use a indicada. Se só existe uma, use essa. Se há várias, use a padrão em Info, Create (para adicionar idioma) e nos Reset-*, dizendo qual é na prévia. Se não há padrão, pergunte. Em Remove-CentralIdioma, com mais de uma Central, pergunte sempre, mesmo havendo padrão.
2. **Idioma** (só nos Reset-*). Se o aluno indicou, use o indicado. Se a Central tem um único idioma, use esse. Se tem mais de um, pergunte qual, oferecendo também `Todos`.
3. **Destino** (só no Create). Se faltar provedor, pasta ou idiomas, pergunte o que faltar.

Com pasta local, o script já devolve `"status": "ambiguo"` e as `opcoes` para perguntar; não escolha por conta própria.

## Executar

Com uma pasta local acessível e Python disponível, use `scripts/central.py` a partir da pasta da skill. A saída é JSON. Comandos destrutivos sempre rodam primeiro sem `--confirmar` para mostrar a prévia.

| Comando do aluno | Pasta local (`python scripts/central.py ...`) |
| --- | --- |
| Info-CentralIdioma [central] | `info [--central NOME]` |
| Create-CentralIdioma [provedor] [pasta] [idiomas] | `create --raiz PASTA [--nome NOME] [--provedor local\|google-drive\|onedrive] IDIOMA...` |
| Default-CentralIdioma [central] | `default [NOME]` |
| Remove-CentralIdioma [central] | `remove --central NOME`, depois `--confirmar NOME` (e opcional `--backup ARQUIVO.zip`) |
| Reset-Diagnostic [idioma] | `reset diagnostico [IDIOMA] [--central NOME]`, depois `--confirmar` |
| Reset-Lessons [idioma] | `reset aulas [IDIOMA] [--central NOME]`, depois `--confirmar` |
| Reset-Progress [idioma] | `reset progresso [IDIOMA] [--central NOME]`, depois `--confirmar` |

Com Google Drive ou OneDrive por conector, ou no modo manual, siga as mesmas regras com as operações do [adaptador](adaptadores/) e as seções abaixo.

## Registro das Centrais

O registro guarda nome, provedor (local, google-drive, onedrive), acesso (pasta-local, drive, onedrive, manual), raiz, idiomas e qual é a padrão. Ele não guarda progresso.

- Com sistema de arquivos persistente, o registro fica em `~/.everylang/centrais.json` (ou na pasta indicada por `EVERYLANG_HOME`, ou em `--registro`). Se só uma pasta do aluno estiver conectada, use `--registro PASTA_CONECTADA/.everylang/centrais.json`.
- Uma Central criada por conector entra no registro com `register --raiz ID --nome NOME --provedor google-drive|onedrive --acesso drive|onedrive IDIOMA...`.
- Sem sistema de arquivos, guarde o registro na memória da plataforma ou nas instruções do Projeto, com a concordância do aluno, no formato "Centrais everylang: NOME → provedor, raiz; padrão: NOME". Sem nenhum desses, pergunte a Central no início da conversa.
- Cada Central também se descreve em `config/estado-global.md` (`nome_central`, `provedor`, `armazenamento`, `raiz`, `idiomas_escolhidos_pelo_aluno`). Se o registro e a Central divergirem, a Central vale; atualize o registro.

## Help

Mostre primeiro a versão instalada ("everylang vX.Y.Z", da linha "Versão instalada" do SKILL.md) e depois a tabela da seção Comandos do SKILL.md, com uma linha de exemplo por comando e a Central padrão atual, se conhecida. Não execute nada.

## Info-CentralIdioma

Leitura apenas. Para cada Central (ou só a indicada) mostre: nome, se é a padrão, provedor (Local, Google Drive, OneDrive), modo de acesso, formato dos registros (Markdown ou nativo Google Docs/Sheets), caminho ou link da pasta, status da configuração e os idiomas, cada um com quantidade de diagnósticos, aulas e planos (sem contar MODELO.md e o roteiro 09) e de backups de reset. Se a pasta estiver inacessível, diga isso em vez de omitir a Central. Por conector, leia `config/estado-global` e liste `languages/`; no Drive, conte os Docs `aula-*` e `diagnostico-*`.

## Create-CentralIdioma

Cria a pasta da Central com toda a estrutura de subpastas e modelos, ou adiciona idiomas a uma Central existente sem sobrescrever nada.

1. Obtenha provedor, pasta e idiomas (pergunte o que faltar). Nome padrão: o nome da pasta.
2. Escolha o adaptador pelas [regras de seleção](PERSISTENCIA.md#escolher-o-adaptador). Uma pasta do Google Drive ou do OneDrive sincronizada no computador usa o adaptador de pasta local com `--provedor google-drive` ou `onedrive`.
3. Pasta local: `create`. Conector: provisionamento do [Drive](adaptadores/drive.md#provisionar) ou do [OneDrive](adaptadores/onedrive.md), preencha `nome_central`, `provedor`, `armazenamento`, `raiz`, `formato_registros` (`nativo` no Drive, `markdown` nos demais) e `idiomas_escolhidos_pelo_aluno` no estado global, e depois `register`.
4. A primeira Central registrada vira a padrão. Informe o caminho ou link e siga para o cadastro do [SKILL.md](../SKILL.md#configurar-e-adicionar-idiomas).

## Default-CentralIdioma

Define qual Central é usada quando o aluno não indica uma. Sem argumento e com várias Centrais, pergunte qual. Mostre a padrão anterior e a nova.

## Remove-CentralIdioma

Apaga a pasta da Central inteira. É irreversível na pasta local.

1. Resolva a Central (com várias, pergunte sempre). Mostre a prévia: nome, provedor, caminho ou link, idiomas e quantidades de aulas e diagnósticos.
2. Ofereça um backup em .zip fora da Central (`--backup`).
3. Peça que o aluno digite o nome da Central para confirmar. Qualquer outra resposta cancela.
4. Pasta local: `remove --confirmar NOME`. O script recusa pastas sem a estrutura de uma Central, links simbólicos, a pasta pessoal do usuário, a raiz do disco e a pasta da skill.
5. Conector: mova a pasta raiz para a lixeira com a ação de lixeira do conector, se houver (no conector Google Drive do Claude, `trash_file`), e confirme pela releitura que ela está na lixeira. Sem essa ação, informe o link e peça que o aluno apague a pasta; depois de ele confirmar, rode `remove --confirmar NOME --somente-registro`.
6. Se a removida era a padrão e sobrou uma única Central, ela vira a padrão; com várias, avise que não há padrão.

## Reset-Diagnostic, Reset-Lessons e Reset-Progress

Zeram um tipo de registro de um idioma (ou de todos) e devolvem os arquivos derivados ao modelo. Planos (`planos/`), perfil global e configuração do idioma não são tocados.

| Comando | Remove | Volta ao modelo |
| --- | --- | --- |
| Reset-Diagnostic | `diagnosticos/diagnostico-*.md` | `estado/perfil-atual.md`; `estado/sessao-ativa.md` se apontar para um diagnóstico |
| Reset-Lessons | `aulas/aula-*.md` | `estado/contexto-recente.md`; `estado/sessao-ativa.md` se apontar para uma aula |
| Reset-Progress | arquivos de `progresso/historico/` (exceto README.md) | `progresso/08-registro-progresso.md`, `estado/perfil-atual.md`, `estado/contexto-recente.md` |

MODELO.md e o roteiro 09 nunca são removidos. No Drive, sessões e derivados são Docs e o 08 é uma Sheet, com o mesmo nome sem `.md`.

1. Resolva Central e idioma conforme a seção Ambiguidade.
2. Mostre a prévia: Central (e se é a padrão), idioma, lista do que será removido e do que volta ao modelo. Se Reset-Diagnostic ou Reset-Lessons deixarem o progresso calculado com registros apagados, a prévia traz o aviso; ofereça também Reset-Progress.
3. Peça confirmação explícita ("sim"). Sem ela, não altere nada.
4. Antes de apagar, copie tudo o que muda para `_backups/AAAAMMDD-HHMMSS-reset-TIPO-IDIOMA/` dentro da Central e confira a cópia. Pasta local: `reset ... --confirmar` faz isso.
5. Conector: crie a pasta de backup, copie cada arquivo com a cópia nativa do conector (Docs e Sheets continuam nativos) e confira, mova os removidos para a lixeira (ou, sem essa ação, liste-os para o aluno apagar) e devolva os derivados ao modelo do pacote, relendo cada um. No Drive: Doc por substituição total; Sheet limpando as abas `Resumo` e `Aulas` e regravando as tabelas do modelo (veja o [adaptador](adaptadores/drive.md#remover-e-zerar)).
6. Informe o que foi zerado, onde está o backup e qual é a próxima etapa do idioma (depois de Reset-Diagnostic, o diagnóstico inicial).

Os resets nunca zeram `contador_frases` nem `contador_dialogos`: os números de frases e diálogos continuam únicos depois de qualquer reset.

## Pause-Lesson, Finish-Lesson e Save-Lesson

Pausam, encerram ou salvam a aula ou o diagnóstico em andamento, em texto ou voz. Se houver mais de uma sessão aberta e o aluno não indicar qual, pergunte. O procedimento completo, inclusive o que fazer quando o modo voz não consegue gravar, está em [FRASES-E-VOZ.md](FRASES-E-VOZ.md#pausar-e-concluir).

## Frase N, Diálogo N e IDs-Voz

Pedidos sobre uma frase ou diálogo pelo número ("repita a frase 132", "explique o diálogo 145") e o anúncio dos números no modo voz seguem [FRASES-E-VOZ.md](FRASES-E-VOZ.md#numeração-de-frases-e-diálogos). `IDs-Voz on|off` grava a preferência em `ids_em_voz` no estado global.

## Etapa

Durante uma aula ou diagnóstico, mostra a etapa atual (por exemplo, "Etapa 3/7 · Simulação"), o que já foi feito, o que falta e o tempo restante. Também responde a "em que etapa estamos?" ou "em que parte da aula estou?". O roteiro e a regra de anunciar as etapas estão no SKILL.md (seção Roteiro da aula).

## Next-Lesson

`Next-Lesson [idioma] [duração]` prepara a próxima aula regular. Também aceito como `Prepare-Lesson` e acionado por pedidos como "próxima aula" ou "fazer aula de 5 minutos".

**Duração avulsa.** Se o aluno indicar uma duração (`5`, `5min`, `5 minutos`, `meia hora`), ela vale só para esta aula: o padrão do plano e do idioma não muda. Sem indicação, use a duração do plano (padrão de 20 minutos). Registre a duração em `Overrides` da sessão e em `lab_duracao_aula_min`. As etapas 1 a 5 são redistribuídas na proporção do padrão (briefing 25%, prática guiada 10%, simulação 35%, imprevisto 20%, feedback 10%); em aulas muito curtas, simplifique o cenário, mas mantenha as sete etapas, o feedback e o encerramento. O vídeo do Lab segue 30% a 50% dessa duração (1,5 a 2,5 minutos numa aula de 5): sem vídeo ligado ao tema nessa faixa, use o mais próximo e registre o motivo, ou indique um trecho com início e fim confirmados.

1. **Idioma.** Use o idioma indicado. Sem indicação e com mais de um idioma em andamento na Central, pergunte qual; com um só, use esse.
2. **Aula pendente.** Se houver aula pausada ou aberta nesse idioma (ponteiro de sessão ativa ou sessão não concluída), não crie outra. Diga qual é (sessão e etapa) e peça para encerrá-la antes: ofereça encerrar agora (Finish-Lesson com a [conferência de encerramento](ENTERTAINMENT-LAB.md#encerramento-conferência-obrigatória)) ou retomá-la. Só depois que ela estiver concluída siga para a próxima. Um Lab apenas adiado não bloqueia a próxima aula; mencione-o em uma linha.
3. **Pré-requisitos.** Sem diagnóstico regular ou sem plano aprovado, encaminhe para a etapa que falta.
4. **Criar e preparar.** Crie a sessão da próxima aula do plano e faça o [preparo do Entertainment Lab](ENTERTAINMENT-LAB.md#preparar-antes-da-etapa-1): vídeo do YouTube escolhido e verificado, registro gravado, relido e conferido (`lab.py pronto`). Se a verificação falhar, diga o que falhou e pergunte se o aluno aceita seguir com o Lab pendente.
5. **Resumo das etapas.** Mostre, numa única mensagem, a duração da aula (dizendo se é avulsa) e o plano das sete etapas com o tempo de cada uma: 1 Briefing (objetivo, cenário e itens), 2 Prática guiada, 3 Simulação (cenário e papel), 4 Imprevisto (sem revelar qual), 5 Feedback, 6 Encerramento e 7 Entertainment Lab (título, canal, duração e link do vídeo já verificado).
6. **Gravar e confirmar.** Grave a sessão como planejada e o ponteiro de sessão ativa, releia e diga "Aula preparada e salva na sua Central: <sessão>". Pergunte apenas: "Começamos pela etapa 1?". Se o aluno for para o modo voz, a aula começa lá já com tudo pronto.

No fim da aula, a etapa 7 só indica o link do vídeo já salvo, sem preparar nada.

## Lab

Abre o Entertainment Lab da aula indicada ou, sem argumento, da última aula do idioma com Lab `pronto`, `adiado` ou `pendente_aceito`. Com mais de um idioma possível, pergunte qual. Se estiver pronto ou adiado, apresente o material salvo, sem nova pesquisa, e pergunte só se o aluno quer fazer agora. Se estiver `pendente_aceito`, prepare agora, em texto, conforme o preparo. Ao terminar, adiar ou recusar, grave na mesma sessão e confirme ao aluno, ou dê o comando `Save-Lesson lab` se não for possível gravar (veja [Finish-Lab](FRASES-E-VOZ.md#finish-lab)).
