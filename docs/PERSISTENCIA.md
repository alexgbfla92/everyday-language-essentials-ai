# Persistência da pasta pessoal

Este protocolo vale para qualquer plataforma (Claude, ChatGPT, Codex ou outra). O que muda entre elas é só o adaptador que lista, cria, grava e relê os arquivos. Neste documento, "ID" é o identificador estável que o adaptador usa: o ID do arquivo no Google Drive ou o caminho relativo à raiz na pasta local.

## Escolher o adaptador

Siga a primeira regra que se aplicar:

1. Se config/estado-global.md da pasta indicada já registra `armazenamento`, use esse adaptador. Trocar de armazenamento é uma migração: só com pedido explícito do aluno, copiando, comparando e trocando o ponteiro como no passo 2 abaixo.
2. Se o aluno escolher explicitamente Drive ou pasta local, use a escolha, desde que o adaptador passe na verificação de capacidade do seu guia.
3. Se o aluno indicar uma pasta do Google Drive e a sessão tiver um conector do Drive que cria e atualiza arquivos, use [Google Drive](adaptadores/drive.md).
4. Se a sessão puder ler e gravar numa pasta do aluno que continua existindo depois do chat (computador do aluno, pasta conectada ao app, repositório local), use [pasta local](adaptadores/pasta-local.md).
5. Caso contrário, use o [modo manual](adaptadores/manual.md) e diga ao aluno, em uma frase, o que falta para salvar automaticamente.

Não escolha pelo nome da plataforma. Escolha pelo que a sessão comprovadamente consegue fazer. Uma área de trabalho temporária do chat, que some ao fim da conversa, nunca é destino de escrita. Uma pasta sincronizada pelo Google Drive para computador conta como pasta local e permite que plataformas diferentes leiam os mesmos registros, desde que só uma escreva por vez.

## Preparar e reconciliar

1. Obtenha a identificação da pasta dedicada do aluno, conforme o adaptador. Caso ele indique apenas um pai pessoal, liste os filhos, crie ou reutilize uma única subpasta EverydayEssentials e use-a como raiz. Distribuição, original, backups de referência e seus descendentes são somente leitura, inclusive a própria pasta da skill. Recuse destino ambíguo, atalho ou pasta pessoal que não possa identificar. Nunca use busca global por nome para escolher um destino de escrita.
2. Antes de criar qualquer registro em pasta existente, procure configuração anterior na raiz (inclusive configuracao.md ou Google Doc) e em config/. Leia IDs indexados, idioma, missões e etapas pendentes. No legado plano mantenha a leitura pelos IDs de origem e a etapa salva. Associe registros ao idioma verificado, preserve campos desconhecidos. Para migração, copie para o ramo pessoal correto, compare respostas, evidências, revisão e próxima etapa, depois troque o ponteiro. Falta de idioma ou colisão requer identificação pelo aluno. Preserve o original. Para converter Docs em Markdown, aguarde solicitação específica.
3. Crie a estrutura com o provisionamento do adaptador ([Drive](adaptadores/drive.md#provisionar) ou [pasta local](adaptadores/pasta-local.md#provisionar)). As regras são comuns: copie somente assets/config e assets/languages dos idiomas escolhidos, pais antes dos filhos, incluindo a subpasta planos de cada idioma. Existing files retain learner data: nunca reaplique um modelo sobre um arquivo existente. Com homônimos ou tipo inesperado (arquivo onde se espera pasta), pare e identifique o objeto correto. Uma resposta perdida exige nova listagem antes de qualquer repetição.
4. Confira, na releitura, nome, tipo, pai e conteúdo de cada objeto criado. Repita o provisionamento até ele não ter mais nada a criar.
5. Grave em config/estado-global.md a versão de esquema 3, o `armazenamento` escolhido (drive, pasta-local ou manual), a identificação da raiz, preferência global, idiomas ativos, etapa de setup, índice caminho → ID confirmado e data da última verificação. Preserve campos anteriores; um registro de esquema 2 sem `armazenamento` é do adaptador Drive. Para adicionar idioma, mescle o novo índice ao existente. Valide escrita alterando um marcador único da execução no mesmo ID pela operação de atualização do adaptador, depois releia e compare. Confirme setup somente após releitura. Informe ao aluno onde está a pasta pessoal (link do Drive ou caminho local) para vincular ao Projeto ou retomar em outro chat.

## Layout e autoridade dos registros

config/ contém defaults, catálogo, perfil do aluno e estado global. languages/{english,spanish,french}/ contém config.md, conteudo/, diagnosticos/, aulas/, planos/, progresso/historico/ e estado/. Preferências, missões e reavaliações pertencem ao ramo do idioma. O pacote fornece os módulos pedagógicos compartilhados em assets/skills/. Os modelos MODELO.md e o roteiro 09 são materiais de apoio, excluídos de contagens. Sugestões e defaults só passam a ser fatos do aluno depois de confirmados.

A sessão usa aula-YYYYMMDD-NN.md ou diagnostico-YYYYMMDD-NN.md, com NN livre no pai correto. Registre caminho lógico, ID do arquivo, ID do plano, variante, modalidade, teste/regular, elegibilidade, revisão, última operação, estado e horário observado. Indexe falas F001… por sessão e preserve interlocutor e apoio. O checkpoint inclui bloco, última troca, último Fxxx, evidências, pendências e próxima pergunta. Os arquivos da sessão e do diagnóstico são as fontes das observações. O registro 08 é o resumo confirmado do idioma. Os três arquivos de estado são derivados e guardam ID, revisão da fonte e data. Use histórico para resumos de ciclos longos, preservando as fontes.

## Salvar, retomar e reparar

Leia o registro e a revisão de base. Prepare uma operação de ID estável por resposta ou conclusão. Releia imediatamente antes de escrever. Se outra revisão interveio, reconcilie pelo ID da operação e pelas falas antes de combinar mudanças. Na ausência de escrita condicional no conector, use um único chat escritor por sessão e um único provisionador por raiz. Não prometa exclusão mútua entre dispositivos. Havendo disputa, suspenda escritas até reconciliar a versão correta.

Atualize os bytes do mesmo ID e MIME. Releia a revisão, operação, evidências e próxima pergunta. A próxima pergunta pode ser apresentada assim que a sessão estiver confirmada. Uma resposta comum atualiza exclusivamente a fonte ativa. Pedidos como repetir ou explicar só exigem escrita quando mudam a evidência, o apoio registrado ou o ponto de retomada.

Ao criar ou trocar de sessão, publique e confira o ponteiro de sessão ativa antes da primeira atividade. Mantenha nele o ID do arquivo. Em cada retomada, leia a fonte por esse ID e use a última revisão e a próxima pergunta da fonte mesmo se o resumo estiver atrasado. Se a criação foi interrompida antes da publicação do ponteiro, procure sessões abertas na pasta do idioma antes de criar outra.

Ao pausar, grave o ponto de retomada na fonte e ajuste apenas o ponteiro cujo estado mudou. Na conclusão, reúna o último turno, feedback e estado final na mesma escrita da fonte, depois consolide em lote lógico os derivados afetados. Cada arquivo alterado recebe uma atualização e verificação próprias. Não regrave defaults, configuração global, índices ou caches cujos dados não mudaram. Conserve o ponteiro até confirmar o progresso e os demais derivados para que uma interrupção permita reparar o fechamento; finalize o ponteiro por último. Se a fonte estiver concluída com ponteiro ainda ativo, reconcilie a conclusão antes de iniciar a próxima sessão. No cadastro, publique o ponteiro do plano em elaboração antes de coletar respostas e use o documento apontado para retomar a pergunta pendente.

Para eventos independentes, paralelize leituras quando a interface permitir. O registro confirmado continua sendo o limite de durabilidade: não acumule respostas apenas na conversa nem anuncie sincronização em segundo plano. A interface atual exige que o agente termine a operação e verifique o conteúdo. Uma implementação futura que responda antes da sincronização precisará de uma fila durável e de um executor independente; para retomada imediata em outro dispositivo, a fila também deverá ser compartilhada e acessível na retomada.

Ao consolidar os derivados do mesmo idioma: Atualize por ID de sessão e revisão, substituindo a entrada anterior; faça a releitura de cada derivado. Diagnóstico atualiza avaliação por habilidade, aula regular concluída conta uma vez, pausa apenas atualiza retomada e teste nunca altera as métricas. Se uma escrita intermediária falhar, retome pela sessão confirmada e repare apenas os derivados faltantes. Em chat de relatório, sinalize divergências e encaminhe o reparo ao fluxo de retomada.

Se não houver escrita ou releitura, apresente a etapa exata, último ID/revisão confirmados e checkpoint copiável da resposta pendente. Ofereça importação manual do Markdown ou, quando disponível, Google Docs por escolha registrada. Em Docs use edição nativa do mesmo documento e releitura de conteúdo. Ao recuperar o acesso, confirme o arquivo no Drive antes de anunciar progresso salvo.
