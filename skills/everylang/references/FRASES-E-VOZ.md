# Frases numeradas, pausa e conclusão (texto e voz)

## Numeração de frases e diálogos

Toda frase no idioma que o aluno está aprendendo recebe um número, seja da IA ou do aluno, escrita ou falada. Frases em pt-BR ou no idioma de apoio não recebem número.

- **Frase (F):** cada sentença no idioma-alvo. Uma resposta com três sentenças recebe três números. Exemplo: `F132`.
- **Diálogo (D):** um bloco de falas apresentado ou praticado junto (diálogo-modelo, simulação, troca de turnos de um cenário). As frases dentro dele mantêm seus números F. Exemplo: `D145` reúne F140–F151.
- **Únicos por idioma na Central.** A numeração continua de uma sessão para outra e entre diagnóstico e aulas. Nunca volta a 1 e nunca é reaproveitada, nem depois de Reset-Diagnostic, Reset-Lessons ou Reset-Progress. Cada idioma tem a sua sequência.

### Onde fica o contador

`config/estado-global` guarda `contador_frases` e `contador_dialogos`: o último número usado por idioma. Ao criar uma sessão, comece em contador + 1. Se uma sessão anterior tiver números acima do contador (gravação interrompida), comece depois do maior número encontrado nas sessões do idioma. Atualize o contador no estado global ao pausar e ao concluir, depois de gravar a sessão.

Cada sessão registra no cabeçalho o intervalo usado (`F120 – F158 | D12 – D15`), na tabela de frases cada frase (ID, diálogo, falante, modo texto/voz, frase, confiabilidade) e na tabela de diálogos cada diálogo. Assim a frase pode ser encontrada depois pelo número.

### Como mostrar

- **Texto:** prefixe cada frase da IA no idioma-alvo com o número entre colchetes: `[F132] Could you send me the agenda?`. Para as frases do aluno, abra a resposta com uma linha curta que dá os números sem repetir o texto: `Você: F133, F134`. Diálogos começam com `[D145]`.
- **Voz:** com `ids_em_voz: sim` (padrão), diga o número de forma curta antes de cada frase nova da IA ("cento e trinta e dois: Could you send me the agenda?") e confirme o número das frases do aluno no início da resposta ("a sua foi a cento e trinta e três"). O aluno liga e desliga com `IDs-Voz on` e `IDs-Voz off`. Desligado, os números continuam sendo atribuídos e gravados; a IA diz o número quando o aluno perguntar.

### Pedir algo sobre uma frase ou diálogo

O aluno pode citar o número com ou sem a letra, em qualquer idioma: "repita a frase 132", "F132 mais devagar", "explique a estrutura do diálogo 145", "traduza a 132", "como eu poderia dizer a 133 de forma mais natural?", "qual o número da minha última frase?".

- Número sem letra é frase (F). "Diálogo N" é D; se não existir D N mas existir F N, use o diálogo que contém a frase N.
- Ações comuns: repetir, repetir devagar, traduzir, explicar vocabulário, explicar estrutura (gramática, ordem, conectores, registro), dar variações mais naturais ou mais formais, praticar de novo.
- Procure primeiro na conversa atual; depois na sessão ativa; depois nas sessões do idioma, da mais recente para a mais antiga, pelo intervalo do cabeçalho. Se não encontrar, diga isso e peça o trecho; não invente a frase.
- As frases novas que surgirem na explicação (exemplos, variações) também recebem números.
- Fora de uma aula ou diagnóstico, as frases novas no idioma-alvo recebem números do mesmo contador e vão para a tabela de frases avulsas de `estado/contexto-recente` do idioma.

## Pausar e concluir

Comandos: `Pause-Lesson` (ou "pausar", "pausa", "para por aqui") e `Finish-Lesson` (ou "terminar", "encerrar", "concluir a aula"). Valem para aula e diagnóstico.

### Pause-Lesson

1. Monte o checkpoint: etapa e bloco, última troca, última frase (F) e diálogo (D), evidências, pendências e a próxima pergunta exata.
2. Grave na sessão, numa única escrita verificada: estado `pausada`, checkpoint, frases e diálogos ainda não gravados e o intervalo do cabeçalho.
3. Atualize `estado/sessao-ativa` (sessão pausada, ID do arquivo, próxima pergunta) e os contadores no estado global.
4. Releia cada arquivo. Só então diga "Aula pausada e salva" com o ID da sessão e a próxima pergunta. Se qualquer escrita falhar, não diga que salvou: siga o modo sem escrita abaixo.

### Finish-Lesson

O Finish-Lesson é a etapa 6 (encerramento) e roda sempre ao fim da aula, mesmo sem o aluno pedir (veja o roteiro no SKILL.md). Depois de salvar e dizer o próximo passo, siga para a etapa 7, o Entertainment Lab já planejado.


1. Faça o fechamento combinado (feedback com evidências, limitações, próxima tarefa).
2. Grave na sessão, numa única escrita: último turno, fechamento, estado `concluída`, frases e diálogos pendentes.
3. Consolide os derivados do idioma conforme a [persistência](PERSISTENCIA.md#salvar-retomar-e-reparar) (progresso 08, perfil atual, contexto recente). Aula de teste não altera métricas.
4. Atualize os contadores e, por último, `estado/sessao-ativa`.
5. Releia tudo e confirme, em texto ou voz, "Aula concluída e salva na sua Central: <sessão>".

### Finish-Lab

Ao terminar o Entertainment Lab (etapa 7) ou um Lab retomado com o comando `Lab`:

1. Grave na seção Entertainment Lab da sessão, numa única escrita: `lab_status: feito`, `lab_resultado` (respostas, tarefa e feedback breve) e as frases e diálogos numerados. Se o Lab foi adiado ou recusado, grave só o `lab_status`. Em todos os casos, depois da releitura e da confirmação ao aluno, grave `lab_gravacao_confirmada: sim`.
2. Atualize os contadores de frases e diálogos no estado global.
3. Releia e confirme, em texto ou voz: "Lab salvo na sua Central: <sessão>". O Lab não altera as métricas da aula.
4. Sem escrita disponível, siga a seção abaixo com `Save-Lesson lab`.

### Sem escrita disponível (voz e outros casos)

No modo voz, a IA pode não ter acesso às ferramentas de gravação. Tente gravar; se não houver ferramenta ou a escrita falhar:

1. Não diga que salvou.
2. Diga em uma ou duas frases curtas e deixe o mesmo texto na transcrição: "Não consigo salvar no modo voz. Saia do modo voz e envie, por texto, nesta mesma conversa: **Save-Lesson pausar aula-20261111-01 F120-F158**" (ou `concluir`). Use o ID real da sessão e o intervalo real de frases.
3. Em seguida, no modo voz, resuma em uma frase onde a aula parou (próxima pergunta), para o aluno ouvir.

Ao começar uma atividade por voz, avise uma vez, em uma frase, se a gravação a cada resposta não estiver disponível: "Neste modo eu salvo quando você pausar ou terminar; se eu não conseguir, te passo um comando para o modo texto." Antes de entrar em voz, salve o checkpoint por texto quando possível, para que só o trecho falado fique pendente.

### Save-Lesson (no modo texto)

`Save-Lesson [pausar|concluir|lab] [sessão] [intervalo]` grava o que ficou pendente na mesma conversa (pausa, fim da aula ou fim do Lab):

1. Leia a sessão pelo ID e a última revisão confirmada.
2. Reconstrua, a partir da transcrição desta conversa, as falas do intervalo indicado (ou todas após a última frase gravada): número, falante, modo `voz`, texto e evidências. Marque como `transcrição de voz` a confiabilidade das falas do aluno; não avalie pronúncia por transcrição.
3. Execute Pause-Lesson, Finish-Lesson ou Finish-Lab a partir do passo de gravação, com releitura e confirmação ao aluno.
4. Se a transcrição não tiver as falas (outra conversa, transcrição perdida), diga quais números ficaram sem registro, peça que o aluno cole o trecho, ou grave só o checkpoint e marque essas frases como não recuperadas.

Sem argumento, Save-Lesson usa a sessão ativa e a ação pedida por último. Ao retomar uma sessão, se a conversa ou o ponteiro mostrarem frases com número acima do último gravado, ofereça Save-Lesson antes de continuar.
