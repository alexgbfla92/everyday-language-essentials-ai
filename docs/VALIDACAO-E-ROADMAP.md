# Validação do beta

Rode `python -B -m unittest discover -s tests` na raiz. A suíte usa listagens fictícias e testa as operações propostas ao conector, inclusive o formato de cada caminho no Drive (Markdown, Google Doc ou Google Sheet), o CSV e as abas gerados do modelo, a reconciliação com MIMEs nativos sem recriar, o conflito de tipo trocado e a configuração de abas após interrupção. Também cria pastas locais temporárias para testar o modo `--local`: mesma árvore do Drive, cópia fiel dos modelos, repetição sem sobrescrever, conflitos e recusa de links simbólicos e da pasta da skill. A suíte de comandos (tests/test_central.py) cobre registro e Central padrão, perguntas de ambiguidade, criação e adição de idioma, prévia, confirmação e backup dos três resets, e as recusas de Remove em pastas que não são Centrais. Ela não mede confiabilidade de rede nem verifica a interação do modelo com um aluno.

## Ensaio do Drive nativo

1. No Claude, com os conectores Google Drive, Google Docs e Google Sheets ativos, rode `Create-CentralIdioma googledrive` com uma pasta vazia e Inglês. Confira na pasta: `estado-global`, `perfil`, os três arquivos de `estado/` como Google Docs sem `.md`; `08-registro-progresso` como Google Sheet com as abas `Resumo` e `Aulas` (sem "Untitled"); os demais arquivos como `.md`.
2. Abra o `estado-global` e confira o marcador do teste de escrita e a tabela Índice com IDs e formatos.
3. Interrompa um setup no meio (feche o chat) e rode de novo: nada pode ser duplicado e as abas da planilha devem ser completadas.
4. Faça um diagnóstico curto e uma aula: os Docs `diagnostico-*` e `aula-*` devem receber cada resposta, mantendo o mesmo ID. Edite o Doc da sessão à mão durante a aula e confirme que a próxima escrita da skill é recusada pela revisão, relida e reconciliada.
5. Conclua a aula: uma linha nova na aba `Aulas` e a contagem no `Resumo`, sem duplicar ao repetir a consolidação.
6. Retome pelo celular e pelo tablet: mesma pergunta pendente.
7. `Reset-Lessons Inglês`: backup nativo em `_backups/`, Docs das aulas na lixeira, `contexto-recente` devolvido ao modelo. `Reset-Progress Inglês`: abas `Resumo` e `Aulas` iguais ao modelo.
8. `Remove-CentralIdioma`: pasta raiz na lixeira do Drive.
9. Repita 1, 4 e 5 no ChatGPT na mesma Central e numa Central nova criada por ele.

## Aceite em pasta pessoal de ensaio

Repita o roteiro abaixo em cada combinação de plataforma e adaptador que for publicada: primeiro app do Claude com Google Drive nativo, depois ChatGPT com Google Drive nativo, Claude Code e Codex com pasta local.

1. Pelo mecanismo de instalação disponível na conta, invoque a skill sem o clone aberto. Informe um destino vazio. Crie espanhol e inglês. Confira metadados, pais, MIME, bytes, IDs e revisão da configuração após nova leitura.
2. Repita o setup. Compare os IDs. Adicione francês; confira que os dados anteriores continuam íntegros.
3. Peça aula sem diagnóstico e depois com triagem breve. Observe o encaminhamento. Conclua um diagnóstico regular em texto, confira as limitações anotadas e aprove o plano. Faça uma sessão de teste e compare as métricas antes e depois.
4. Pause uma aula após a segunda frase do aluno. No celular, recupere o mesmo ID, revisão e pergunta. Em voz, confirme o que foi efetivamente observado. Encerre e verifique uma única contribuição ao progresso.
5. Interrompa o acesso após salvar a sessão e antes de atualizar o progresso. Confira o checkpoint, reconcilie pelo ID de operação e valide o reparo. Com um segundo escritor ativo, registre conflitos e suspenda a operação se o conector não oferecer garantias suficientes.
6. Em chat de progresso, compare as evidências de um idioma sem alterar notas. No Lab, teste um vídeo sem transcrição acessível.

Registre interface, versão, data, ações e resultados em ambiente de teste. A publicação e a distribuição em outras contas dependem desse ensaio.

## Latência e recuperação

Em pasta pessoal de ensaio, anote operações e tempo de espera de três turnos comuns antes e depois da mudança, na mesma interface. Durante uma aula aberta, uma resposta que altere o estado deve produzir uma única escrita no arquivo da sessão, com verificação por leitura. Confira pelos IDs que o resumo, o perfil e o índice global não receberam escrita naquele turno. Em outro chat, use o ponteiro existente e confira se a próxima pergunta recuperada corresponde à última resposta confirmada. Interrompa a conclusão depois da fonte e antes do registro 08; ao retomar, verifique reparo, uma única contabilização e encerramento do ponteiro.

## Ensaio de frases numeradas e voz

1. Em texto, confira que cada frase da IA no idioma-alvo vem com `[Fn]`, que cada resposta abre com os números das frases do aluno e que diálogos vêm com `[Dn]`. Peça "repita a frase N", "explique a estrutura do diálogo N" e "traduza a N", inclusive de uma sessão anterior.
2. Faça Reset-Lessons e uma aula nova: os números continuam de onde pararam.
3. Em voz, confira o anúncio curto dos números e `IDs-Voz off`.
4. Em voz, diga "pausar": se a gravação funcionar, a sessão fica `pausada` com a próxima pergunta; se não, a IA não diz que salvou e passa o comando Save-Lesson. Saia do modo voz, envie o comando e confira as falas do trecho em voz gravadas com modo `voz`.
5. Repita com "terminar a aula": sessão `concluída`, progresso consolidado uma única vez.
6. Feche o modo voz sem pausar e volte ao texto: a skill deve oferecer Save-Lesson.

## Ensaio do roteiro da aula

1. Ao abrir a aula, o roteiro das sete etapas aparece em uma linha; em texto, cada mensagem começa com `Etapa n/7 · nome`; em voz, cada troca de etapa é anunciada.
2. Antes da etapa 1, sem perguntas ao aluno, a sessão já tem a seção Entertainment Lab preenchida com um vídeo verificado (título, canal, URL, trecho, transcrição, perguntas, tarefa) ou `pendente` se não houver busca.
3. Pergunte "em que etapa estamos?" no meio da simulação: etapa atual, o que falta e tempo restante.
4. Deixe a aula chegar ao fim sem pedir para terminar: depois do feedback, a IA entra sozinha na etapa 6, salva e confirma ("Aula salva na sua Central: …") ou, sem gravação, diz que não salvou e passa o comando Save-Lesson.
5. Etapa 7: uma única mensagem curta com o Lab já planejado e uma só pergunta ("agora ou depois?"). Adie e depois use `Lab`: o mesmo plano volta sem novas perguntas.
6. Repita 4 e 5 no modo voz.
