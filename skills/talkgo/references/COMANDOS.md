# Comandos

Os comandos funcionam em qualquer plataforma. São texto: o aluno digita depois de chamar a skill (`/talkgo Get-Practices` no Claude e `@TalkGo Get-Practices` ou `$talkgo:talkgo Get-Practices` no ChatGPT) ou em qualquer mensagem de uma conversa em que a skill já esteja ativa. Pedidos em linguagem natural ("quero praticar inglês", "quais práticas eu fiz?") seguem os mesmos procedimentos do comando correspondente.

## Convenção de nomes

Todo comando é `Verbo-Entidade`, em inglês, com o verbo de uma lista curta:

| Verbo | Significado |
| --- | --- |
| `Get` | mostrar ou listar, sem alterar nada |
| `New` | criar |
| `Set` | alterar (inclusive o padrão) |
| `Remove` | apagar um item, com prévia, backup e confirmação |
| `Reset` | apagar todos os registros de um tipo num idioma, com prévia, backup e confirmação |
| `Start`, `Pause`, `Resume`, `Finish`, `Save` | conduzir uma sessão |

Entidades: `Central` (pasta pessoal com os registros), `Language` (idioma estudado numa Central), `Mission` (cenário com data-alvo num idioma), `Practice` (sessão de prática de uma missão), `Diagnostic`, `Progress`, `Lab`, `Stage` (etapa da sessão), `Phrase` (frase ou diálogo numerado). Comandos que listam usam o plural (`Get-Missions`, `Get-Practices`); os que agem sobre um item usam o singular.

## Como reconhecer

- Ignore maiúsculas, acentos, espaços e o hífen: `Get-Practices`, `get practices` e `GETPRACTICES` são o mesmo comando.
- Argumentos vêm em qualquer ordem depois do comando, como texto livre ou com rótulo (`central Pessoal`, `idioma Inglês`, `missao viagem-londres`, `status pausada`). Idioma aceita o nome em português, inglês, espanhol ou francês, ou a tag (`Inglês`, `ingles`, `English`, `en`, `en-US`). `Todos` vale para todos os idiomas da Central. Central é indicada pelo nome ou pelo caminho/ID da raiz; missão, pelo `missao_id` ou pelo título; prática, pelo ID (`pratica-20261114-01`).
- Durante uma prática ou diagnóstico, `HELP` continua sendo pedido de apoio no exercício (veja o SKILL.md). Para ver a lista de comandos no meio de uma atividade, use `Help-Commands`.

## Contexto e padrões

As entidades formam uma cadeia: **Central → Idioma → Missão → Prática**. Antes de executar, resolva só os níveis que o comando usa, de cima para baixo, um por vez:

1. **Indicado no comando**: use o indicado.
2. **Uma única opção**: use essa e diga qual é na resposta, sem perguntar.
3. **Várias opções**: pergunte, com as opções numeradas e a padrão em primeiro lugar, marcada "(padrão)" e já assumida: o aluno confirma com "ok" ou "sim", ou escolhe outra. Sem padrão definida, pergunte sem marcar nenhuma.
4. **Nenhuma opção**: encaminhe ao comando que cria (`New-Central`, `Add-Language`, `New-Mission`).

Padrões, definidos pelo `Set-Default`:

| Nível | Onde fica | Quando é definida automaticamente |
| --- | --- | --- |
| Central | registro das Centrais (`padrao`) | a primeira Central registrada |
| Idioma | `idioma_padrao` em `config/estado-global` | o primeiro idioma escolhido na criação da Central |
| Missão | `missoes_padrao` em `config/estado-global` (uma por idioma) | a primeira missão criada no idioma |

Exceções: `Remove-Central` e `Remove-Mission` perguntam sempre que houver mais de uma opção, mesmo com padrão; e nos `Reset-*` a pergunta de idioma oferece também `Todos`. Numa conversa em que o contexto já foi escolhido, reaproveite-o sem perguntar de novo, salvo se o aluno pedir outro. Com pasta local, o script devolve `"status": "ambiguo"` e as `opcoes` (com `padrao`) para perguntar; não escolha por conta própria.

## Executar

Com uma pasta local acessível e Python disponível, use `scripts/central.py` a partir da pasta da skill. A saída é JSON. Comandos destrutivos sempre rodam primeiro sem `--confirmar` para mostrar a prévia.

| Comando do aluno | Pasta local (`python scripts/central.py ...`) |
| --- | --- |
| Get-Central [central] | `info [--central NOME]` |
| New-Central [provedor] [pasta] [idiomas] | `create --raiz PASTA [--nome NOME] [--provedor local\|google-drive\|onedrive] IDIOMA...` |
| Add-Language [idiomas] [central] | `create --raiz PASTA_DA_CENTRAL IDIOMA...` |
| Set-Default central\|language\|mission [nome] | `default [NOME]`; `default --idioma IDIOMA [--central NOME]`; `default --missao ID --idioma IDIOMA [--central NOME]` |
| Remove-Central [central] | `remove --central NOME`, depois `--confirmar NOME` (e opcional `--backup ARQUIVO.zip`) |
| Get-Missions [idioma] | `info [--central NOME]` (lista `lista_missoes` por idioma) |
| Remove-Mission [missão] | `remove-mission ID --idioma IDIOMA [--central NOME]`, depois `--confirmar ID` |
| Get-Practices [idioma] [missão] [status] | `practices [IDIOMA] [--missao ID] [--status TEXTO] [--central NOME]` |
| Reset-Diagnostics [idioma] | `reset diagnostico [IDIOMA] [--central NOME]`, depois `--confirmar` |
| Reset-Practices [idioma] | `reset praticas [IDIOMA] [--central NOME]`, depois `--confirmar` |
| Reset-Progress [idioma] | `reset progresso [IDIOMA] [--central NOME]`, depois `--confirmar` |

Com Google Drive ou OneDrive por conector, ou no modo manual, siga as mesmas regras com as operações do [adaptador](adaptadores/) e as seções abaixo.

## Registro das Centrais

O registro guarda nome, provedor (local, google-drive, onedrive), acesso (pasta-local, drive, onedrive, manual), raiz, idiomas e qual é a padrão. Ele não guarda progresso.

- Com sistema de arquivos persistente, o registro fica em `~/.talkgo/centrais.json` (ou na pasta indicada por `TALKGO_HOME`, ou em `--registro`). Se só uma pasta do aluno estiver conectada, use `--registro PASTA_CONECTADA/.talkgo/centrais.json`.
- Uma Central criada por conector entra no registro com `register --raiz ID --nome NOME --provedor google-drive|onedrive --acesso drive|onedrive IDIOMA...`.
- Sem sistema de arquivos, guarde o registro na memória da plataforma ou nas instruções do Projeto, com a concordância do aluno, no formato "Centrais TalkGo: NOME → provedor, raiz; padrão: NOME". Sem nenhum desses, pergunte a Central no início da conversa.
- Cada Central também se descreve em `config/estado-global.md` (`nome_central`, `provedor`, `armazenamento`, `raiz`, `idiomas_escolhidos_pelo_aluno`, `idioma_padrao`, `missoes_padrao`). Se o registro e a Central divergirem, a Central vale; atualize o registro.

## Help

Mostre primeiro a versão instalada ("TalkGo vX.Y.Z", da linha "Versão instalada" do SKILL.md) e depois a tabela da seção Comandos do SKILL.md, agrupada por entidade, com uma linha de exemplo por comando, e o contexto padrão atual (Central, idioma e missão), se conhecido. Não execute nada.

## Central

### Get-Central

Leitura apenas. Para cada Central (ou só a indicada) mostre: nome, se é a padrão, provedor (Local, Google Drive, OneDrive), modo de acesso, formato dos registros (Markdown ou nativo Google Docs/Sheets), caminho ou link da pasta, status da configuração e os idiomas (marcando o padrão), cada um com a quantidade de diagnósticos e práticas e as missões (título, data-alvo, status, marcando a padrão), sem contar MODELO.md e o roteiro 09, e a quantidade de backups de reset. Se a pasta estiver inacessível, diga isso em vez de omitir a Central. Por conector, leia `config/estado-global` e liste `languages/`; no Drive, conte os Docs `pratica-*` e `diagnostico-*`.

### New-Central

Cria a pasta da Central com toda a estrutura de subpastas e modelos.

1. Obtenha provedor, pasta e idiomas (pergunte o que faltar). Nome padrão: o nome da pasta. Se a pasta já for uma Central, trate como `Add-Language`.
2. Escolha o adaptador pelas [regras de seleção](PERSISTENCIA.md#escolher-o-adaptador). Uma pasta do Google Drive ou do OneDrive sincronizada no computador usa o adaptador de pasta local com `--provedor google-drive` ou `onedrive`.
3. Pasta local: `create`. Conector: provisionamento do [Drive](adaptadores/drive.md#provisionar) ou do [OneDrive](adaptadores/onedrive.md), preencha `nome_central`, `provedor`, `armazenamento`, `raiz`, `formato_registros` (`nativo` no Drive, `markdown` nos demais), `idiomas_escolhidos_pelo_aluno` e `idioma_padrao` (o primeiro idioma escolhido) no estado global, e depois `register`.
4. A primeira Central registrada vira a padrão. Informe o caminho ou link e siga para o cadastro do [SKILL.md](../SKILL.md#configurar-e-adicionar-idiomas).

### Remove-Central

Apaga a pasta da Central inteira. É irreversível na pasta local.

1. Resolva a Central (com várias, pergunte sempre). Mostre a prévia: nome, provedor, caminho ou link, idiomas e quantidades de missões, práticas e diagnósticos. Diga como será apagada: lixeira (recuperável) ou exclusão definitiva (quando o conector só oferecer essa).
2. Ofereça um backup em .zip fora da Central (`--backup`).
3. Peça que o aluno digite o nome da Central para confirmar. Qualquer outra resposta cancela.
4. Pasta local: `remove --confirmar NOME`. O script recusa pastas sem a estrutura de uma Central, links simbólicos, a pasta pessoal do usuário, a raiz do disco e a pasta da skill.
5. Conector: apague a pasta raiz pela ação do conector, conforme o [adaptador](adaptadores/drive.md#remover-e-zerar): lixeira, se houver (no Claude, `trash_file`); senão, exclusão definitiva, já avisada na prévia e confirmada pelo nome. Confirme pela releitura que a pasta não está mais na Central e atualize o registro (`remove --confirmar NOME --somente-registro`). Só peça que o aluno apague à mão se o conector não puder apagar de nenhuma forma.
6. Se a removida era a padrão e sobrou uma única Central, ela vira a padrão; com várias, avise que não há padrão.

## Language

### Add-Language

Adiciona um ou mais idiomas a uma Central existente, sem sobrescrever nada: mesma estrutura do `New-Central`, só para os idiomas novos. Pasta local: `create --raiz` com a raiz da Central. Conector: o mesmo provisionamento, que não recria o que já existe. Atualize `idiomas_escolhidos_pelo_aluno`. O padrão de idioma não muda; diga como mudar com `Set-Default language`. Em seguida, encaminhe ao diagnóstico do idioma novo (`Start-Diagnostic`).

## Set-Default

`Set-Default central|language|mission [nome]` define o padrão de um nível do contexto (veja Contexto e padrões). Sem nome, liste as opções com a padrão atual marcada e pergunte qual. Para `mission`, resolva antes Central e idioma: a missão padrão vale para aquele idioma. Grave, releia e mostre a padrão anterior e a nova. Pasta local: `default ...` (tabela Executar); conector: edite `idioma_padrao` ou `missoes_padrao` no `config/estado-global` e o registro, no caso da Central.

## Mission

Procedimento completo, campos do modelo e regras de revisão em [MISSOES.md](MISSOES.md).

- **`Get-Missions [idioma] [status]`**: lista as missões do idioma (ou de todos os idiomas da Central, se o aluno pedir `Todos`): título, data-alvo, status, situações e quantas práticas concluídas em cada uma, marcando a padrão. Leitura apenas.
- **`New-Mission [idioma]`**: cria uma missão (título, descrição, data-alvo obrigatória, situações, duração, frequência e reavaliação). A primeira missão do idioma vira a padrão.
- **`Set-Mission [missão]`**: altera uma missão existente (qualquer campo, situações ou status `ativa`, `pausada`, `concluida`), com revisão e histórico.
- **`Remove-Mission [missão]`**: apaga a missão e as práticas dela, com o mesmo cuidado dos resets: prévia (missão, situações, práticas que serão apagadas e como), backup em `_backups/` conferido antes de apagar, e confirmação pelo `missao_id`. As práticas apagadas seguem a regra das práticas apagadas (somem do progresso e de qualquer lista; veja a seção Reset). Se era a padrão do idioma e sobrou uma única missão, ela vira a padrão. Para encerrar uma missão sem apagar o histórico, sugira antes `Set-Mission <missão> status concluida`.

## Practice

### Get-Practices

`Get-Practices [idioma] [missão] [status]` lista as sessões de prática, agrupadas por missão e, dentro de cada missão, por status (`Em andamento (...)` primeiro, depois `Concluída`), com ID, data, situação e, para as em andamento, a etapa salva. Sem missão indicada, mostra todas as missões do idioma (com a padrão primeiro); `status` filtra (`em andamento`, `pausada`, `concluida`). Use só os arquivos de sessão que existem em `praticas/` e a tabela Práticas das missões; práticas apagadas nunca aparecem. Leitura apenas. Termine com o próximo passo útil (retomar a pausada ou começar a próxima).

### Start-Practice

`Start-Practice [idioma] [missão] [situação] [duração]` prepara uma nova sessão de prática regular de uma missão. Também acionado por pedidos como "próxima prática" ou "fazer uma prática de 5 minutos".

**Duração avulsa.** Se o aluno indicar uma duração (`5`, `5min`, `5 minutos`, `meia hora`), ela vale só para esta prática: o padrão da missão e do idioma não muda. Sem indicação, use a duração da missão (padrão de 20 minutos). Registre a duração em `Overrides` da sessão e em `lab_duracao_pratica_min`. As etapas 1 a 5 são redistribuídas na proporção do padrão (briefing 25%, treino guiado 10%, simulação 35%, imprevisto 20%, feedback 10%); em práticas muito curtas, simplifique o cenário, mas mantenha as sete etapas, o feedback e o encerramento. O vídeo do Lab segue 30% a 50% dessa duração (1,5 a 2,5 minutos numa prática de 5): sem vídeo ligado ao tema nessa faixa, use o mais próximo e registre o motivo, ou indique um trecho com início e fim confirmados.

1. **Contexto.** Resolva Central, idioma e missão conforme Contexto e padrões (só missões `ativa`). Nenhuma missão ativa: encaminhe ao `New-Mission`.
2. **Prática em andamento.** Se houver prática `Em andamento` nesse idioma (preparada, em execução ou pausada), não crie outra. Diga qual é (sessão, missão e etapa) e ofereça retomá-la (`Resume-Practice`) ou encerrá-la agora (`Finish-Practice`, com a [conferência de encerramento](ENTERTAINMENT-LAB.md#encerramento-conferência-obrigatória)). Só depois que ela estiver `Concluída` siga para a próxima. O Lab de uma prática concluída nunca bloqueia a próxima.
3. **Pré-requisitos.** Sem diagnóstico regular no idioma, encaminhe ao `Start-Diagnostic`.
4. **Situação.** A indicada pelo aluno ou, sem indicação, a primeira situação da missão com menos práticas concluídas, conforme [MISSOES.md](MISSOES.md#escolher-a-missão-no-start-practice). Ao criar a sessão, grave `missao_id` e `situacao` na prática e acrescente a linha dela na tabela Práticas da missão, com status `Em andamento (preparada)`.
5. **Criar e preparar.** Crie a sessão de prática e faça o [preparo do Entertainment Lab](ENTERTAINMENT-LAB.md#preparar-antes-da-etapa-1): vídeo do YouTube escolhido e verificado, registro gravado, relido e conferido (`lab.py pronto`). Se a verificação falhar, diga o que falhou e pergunte se o aluno aceita começar sem o vídeo.
6. **Resumo das etapas.** Mostre, numa única mensagem, a missão (título e data-alvo), a situação desta prática, o ID da sessão, a duração (dizendo se é avulsa) e o roteiro das sete etapas com o tempo de cada uma: 1 Briefing (objetivo, cenário e itens), 2 Treino guiado, 3 Simulação (cenário e papel), 4 Imprevisto (sem revelar qual), 5 Feedback, 6 Encerramento e 7 Entertainment Lab, opcional e sugerido depois do encerramento (título, canal, duração e link do vídeo já verificado).
7. **Gravar e confirmar.** Grave a sessão com status `Em andamento (preparada)`, a linha da prática na missão e o ponteiro de sessão ativa, releia e diga "Prática preparada e salva na sua Central: <sessão>". Pergunte apenas: "Começamos pela etapa 1?". Se o aluno for para o modo voz, a prática começa lá já com tudo pronto.

No fim da prática, depois do encerramento, a etapa 7 só sugere o vídeo já salvo, sem preparar nada.

### Resume-Practice

`Resume-Practice [prática]` retoma uma prática `Em andamento` (preparada ou pausada) no mesmo ID. Sem argumento, use o ponteiro de sessão ativa do idioma; com mais de uma prática em andamento na Central, pergunte qual, listando idioma, missão e etapa. Leia a sessão, confira o material do Lab (prepare-o antes, se faltar), grave `Em andamento (em execução)` na sessão e na missão, mostre em que etapa parou e continue pela próxima pergunta salva. Também acionado por "retomar" ou "continuar a prática".

### Pause-Practice, Finish-Practice e Save-Practice

Pausam, encerram ou salvam a prática ou o diagnóstico em andamento, em texto ou voz. Se houver mais de uma sessão aberta e o aluno não indicar qual, pergunte. O procedimento completo, inclusive o que fazer quando o modo voz não consegue gravar, está em [FRASES-E-VOZ.md](FRASES-E-VOZ.md#pausar-e-concluir).

### Start-Lab

`Start-Lab [prática]` abre o Entertainment Lab da prática indicada ou, sem argumento, da última prática concluída do idioma. Apresente o material salvo, sem nova pesquisa, e pergunte só se o aluno quer fazer agora. Se a prática começou sem o vídeo (pendência aceita), prepare agora, em texto, conforme o preparo. O Lab não tem status: o comando funciona quantas vezes o aluno quiser, e o status da prática não muda. Se o aluno fizer, grave o resultado na mesma sessão e confirme, ou dê o comando `Save-Practice lab` se não for possível gravar (veja [Finish-Lab](FRASES-E-VOZ.md#finish-lab)).

### Get-Stage e Get-Phrase

- **`Get-Stage`**: durante uma prática ou diagnóstico, mostra a etapa atual (por exemplo, "Etapa 3/7 · Simulação"), o que já foi feito, o que falta e o tempo restante. Também responde a "em que etapa estamos?". O roteiro e a regra de anunciar as etapas estão no SKILL.md (seção Roteiro da prática).
- **`Get-Phrase <F|D número>`**: repete, traduz ou explica uma frase (`Get-Phrase F132`) ou um diálogo (`Get-Phrase D145`), inclusive de sessões anteriores. Pedidos naturais ("repita a frase 132", "explique o diálogo 145") fazem o mesmo. Regras em [FRASES-E-VOZ.md](FRASES-E-VOZ.md#numeração-de-frases-e-diálogos).

### Set-VoiceIds

`Set-VoiceIds on|off` liga ou desliga o anúncio dos números das frases no modo voz e grava a preferência em `ids_em_voz` no estado global.

## Diagnostic e Progress

- **`Start-Diagnostic [idioma]`**: inicia (ou retoma, se houver um pausado) o diagnóstico do idioma, conforme o SKILL.md (seção Diagnóstico, prática e retomada). Pause-Practice, Finish-Practice e Save-Practice também valem para o diagnóstico.
- **`Get-Progress [idioma]`**: mostra o progresso confirmado do idioma: missões com data-alvo e práticas concluídas por situação, CEFR por habilidade com evidências, duração real observada, limitações, próxima prática e próxima reavaliação, conforme a seção Acompanhamento do SKILL.md. Leitura apenas; testes ficam fora dos totais.

## Reset-Diagnostics, Reset-Practices e Reset-Progress

Zeram um tipo de registro de um idioma (ou de todos) e devolvem os arquivos derivados ao modelo. Perfil global e configuração do idioma não são tocados; nas missões, só o Reset-Practices mexe, e apenas nas linhas das práticas apagadas.

Registros apagados por um reset ou pelo Remove-Mission deixam de existir para a skill: não aparecem em nenhum comando, lista, status, total ou resumo, e não recebem marcas como "excluída no reset". Os backups em `_backups/` servem só para restauração manual e nunca são lidos para responder ao aluno.

| Comando | Remove | Volta ao modelo |
| --- | --- | --- |
| Reset-Diagnostics | `diagnosticos/diagnostico-*.md` | `estado/perfil-atual.md`; `estado/sessao-ativa.md` se apontar para um diagnóstico |
| Reset-Practices | `praticas/pratica-*.md` | `estado/contexto-recente.md`; `estado/sessao-ativa.md` se apontar para uma prática; e ajusta, sem apagar: nas missões, saem da tabela Práticas as linhas dessas práticas; no progresso 08, saem as linhas das práticas e voltam ao modelo o total de práticas regulares e a duração real |
| Reset-Progress | arquivos de `progresso/historico/` (exceto README.md) | `progresso/08-registro-progresso.md`, `estado/perfil-atual.md`, `estado/contexto-recente.md` |

MODELO.md e o roteiro 09 nunca são removidos. No Drive, sessões e derivados são Docs e o 08 é uma Sheet, com o mesmo nome sem `.md`.

1. Resolva Central e idioma conforme Contexto e padrões.
2. Mostre a prévia: Central (e se é a padrão), idioma, lista do que será removido e do que volta ao modelo, e como os removidos serão apagados (lixeira ou exclusão definitiva, se o conector só oferecer essa; o backup em `_backups/` é feito antes de qualquer forma). No Reset-Practices, a prévia lista também as missões cujas linhas de prática saem e as linhas de prática que saem do progresso. Se o Reset-Diagnostics deixar o progresso calculado com diagnósticos apagados, a prévia traz o aviso; ofereça também Reset-Progress.
3. Peça confirmação explícita ("sim"). Sem ela, não altere nada.
4. Antes de apagar, copie tudo o que muda para `_backups/AAAAMMDD-HHMMSS-reset-TIPO-IDIOMA/` dentro da Central e confira a cópia. Pasta local: `reset ... --confirmar` faz isso.
5. Conector: crie a pasta de backup, copie cada arquivo com a cópia nativa do conector (Docs e Sheets continuam nativos) e confira, apague os removidos pela lixeira ou, se o conector só oferecer essa ação, por exclusão definitiva, somente depois do backup conferido (sem pedir que o aluno apague à mão), e releia a pasta para confirmar e devolva os derivados ao modelo do pacote, relendo cada um. No Drive: Doc por substituição total; Sheet limpando as abas `Resumo` e `Práticas` e regravando as tabelas do modelo (veja o [adaptador](adaptadores/drive.md#remover-e-zerar)). No Reset-Practices, edite também o Doc de cada missão afetada (tire da tabela Práticas as linhas das práticas apagadas) e, na Sheet do progresso, apague as linhas dessas práticas na aba `Práticas` e devolva ao modelo, na aba `Resumo`, o total de práticas regulares e a duração real; releia cada um.
6. Informe o que foi zerado, onde está o backup e qual é a próxima etapa do idioma (depois de Reset-Diagnostics, o diagnóstico inicial).

Os resets nunca zeram `contador_frases` nem `contador_dialogos`: os números de frases e diálogos continuam únicos depois de qualquer reset.
