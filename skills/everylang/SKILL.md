---
name: everylang
description: Everyday Language Essentials AI (everylang). Configure e gerencie Centrais de idiomas numa pasta pessoal (local, Google Drive ou OneDrive), conduza diagnósticos e aulas por missão, retome sessões e apresente o progresso verificado de inglês, espanhol e francês. Aceita comandos como Help, Info-CentralIdioma, Create-CentralIdioma, Remove-CentralIdioma, Default-CentralIdioma, Reset-Diagnostic, Reset-Lessons, Reset-Progress, Pause-Lesson, Finish-Lesson e Save-Lesson, e numera cada frase no idioma-alvo para consulta (repita a frase 132).
---

# Central de aprendizagem (everylang)

**Regras que nunca podem ser puladas em uma aula regular, em texto, voz ou retomada:**

1. **Lab pronto antes da etapa 1.** Ao criar a aula, pesquise e verifique o vídeo do YouTube (pela página do vídeo com `scripts/youtube.py info`, pedindo aprovação de acesso à internet para esse comando quando a plataforma exigir, pelo navegador ou, se o YouTube estiver bloqueado, por um resultado de busca com o link do vídeo, marcando canal e duração como não confirmados quando a busca não os mostrar), grave a seção Entertainment Lab da sessão e releia. O Lab só está pronto depois da conferência do registro relido (`python scripts/lab.py pronto <sessão>` deve dar `"pode_iniciar": true`, ou a mesma conferência feita à mão). Sem isso, a etapa 1 não começa.
2. **Falha não é silenciosa.** Se a verificação falhar, diga ao aluno o que falhou **antes** de iniciar e pergunte se ele aceita começar com o Lab pendente. Só com a resposta "sim" gravada (`pendente_aceito`) a aula começa sem o Lab pronto.
3. **Sete etapas, sempre.** 1 Briefing · 2 Prática guiada · 3 Simulação · 4 Imprevisto · 5 Feedback · 6 Encerramento · 7 Entertainment Lab. A etapa atual aparece em cada mensagem, e o roteiro da abertura já mostra o título do vídeo.
4. **Etapa 7 só apresenta.** Mostre imediatamente o material salvo (título, canal, link, trecho, tarefa, perguntas) e pergunte apenas "agora ou depois?". Não pesquise de novo nem peça tema ou duração.
5. **Conferência antes de encerrar**, também quando o aluno pede para parar: aula salva e relida, próximo passo informado, Lab oferecido e decisão registrada (`python scripts/lab.py encerramento <sessão>`). O aluno não é obrigado a fazer o Lab; se ele pediu para parar, grave `adiado` como decisão provisória e ainda assim faça a pergunta "agora ou depois?". Nunca troque as etapas 6 e 7 por "quer encerrar?".
6. **Gravação confirmada.** Pausar, terminar a aula e concluir, adiar ou recusar o Lab terminam com "Salvo na sua Central" ou, sem gravação possível, com o comando `Save-Lesson`. Em voz sem acesso ao registro, nunca diga que algo está pronto ou salvo: diga a limitação e encaminhe ao texto.

O procedimento completo do Lab está em [references/ENTERTAINMENT-LAB.md](references/ENTERTAINMENT-LAB.md).

Se a mensagem começa por um comando da tabela abaixo, execute o comando. Caso contrário, identifique a intenção antes de iniciar uma sessão. A configuração, cada diagnóstico ou aula, e o acompanhamento têm chats próprios no Projeto quando a plataforma oferecer Projetos. Sem Projeto, a pasta pessoal verificada basta para retomar. Faça uma pergunta por vez e aguarde a tentativa. Ofereça apoio em pt-BR ou no idioma de apoio escolhido.

## Comandos

Reconheça os comandos sem diferenciar maiúsculas, acentos ou hífen, com argumentos em qualquer ordem. Siga o procedimento de cada um em [references/COMANDOS.md](references/COMANDOS.md). Quando faltar ou houver mais de uma opção de Central ou de idioma, pergunte qual antes de agir, conforme a seção Ambiguidade daquele documento. Remove e Reset sempre mostram a prévia, fazem backup e pedem confirmação explícita.

Versão instalada: 0.12.0

`Help` (ou `Help-Comandos`, que funciona também no meio de uma atividade) mostra ao aluno a versão instalada (linha acima, no formato "everylang vX.Y.Z") e esta tabela, sem executar nada:

| Comando | O que faz | Exemplo |
| --- | --- | --- |
| Help | Lista os comandos da skill. | `Help` |
| Info-CentralIdioma [central] | Mostra cada Central: nome, se é a padrão, armazenamento (Local, Google Drive ou OneDrive), caminho ou link da pasta e idiomas em estudo, com totais de diagnósticos e aulas. | `Info-CentralIdioma` |
| Create-CentralIdioma [local\|googledrive\|onedrive] [pasta] [idiomas] | Cria a pasta da Central com todas as subpastas e arquivos, ou adiciona idiomas a uma Central existente sem apagar nada. | `Create-CentralIdioma local C:\Estudos\Idiomas Inglês Espanhol` |
| Remove-CentralIdioma [central] | Apaga a pasta da Central inteira, depois de prévia, backup opcional e confirmação pelo nome. | `Remove-CentralIdioma Trabalho` |
| Default-CentralIdioma [central] | Define a Central usada quando há mais de uma e nenhuma é indicada. | `Default-CentralIdioma Pessoal` |
| Reset-Diagnostic [idioma\|Todos] | Apaga os diagnósticos do idioma e zera o perfil derivado. | `Reset-Diagnostic Francês` |
| Reset-Lessons [idioma\|Todos] | Apaga as aulas do idioma e zera o contexto recente. | `Reset-Lessons Inglês` |
| Reset-Progress [idioma\|Todos] | Zera o registro de progresso, o histórico e os resumos derivados do idioma. | `Reset-Progress Espanhol` |
| Pause-Lesson | Pausa a aula ou o diagnóstico e salva o ponto exato na Central. | `Pause-Lesson` ou "pausar" |
| Finish-Lesson | Encerra a aula ou o diagnóstico com feedback e salva tudo, inclusive o progresso. | `Finish-Lesson` ou "terminar a aula" |
| Save-Lesson [pausar\|concluir\|lab] [sessão] [frases] | No modo texto, salva o que ficou pendente do modo voz (pausa, fim da aula ou fim do Lab). | `Save-Lesson lab aula-20261111-01 F159-F170` |
| Frase N / Diálogo N | Repete, traduz ou explica uma frase ou um diálogo pelo número. | `repita a frase 132`, `explique a estrutura do diálogo 145` |
| Etapa | Mostra em que etapa da aula você está, o que falta e o tempo restante. | `Etapa` ou "em que etapa estamos?" |
| Next-Lesson [idioma] [duração] [plano] | Prepara a próxima aula do plano, com duração avulsa opcional só para ela (ex.: 5 min): confirma o idioma e, se houver mais de um plano ativo, o plano; pede para encerrar uma aula pendente antes; escolhe e verifica o vídeo do Entertainment Lab e mostra o resumo das sete etapas. | `Next-Lesson Inglês 5min plano viagem-eua` |
| Plan-Mission [idioma] [novo\|atualizar] [plano] | Cria um plano de missão novo ou atualiza um existente (objetivo, prazo, duração, frequência, reavaliação e sequência de aulas). Sem ação, lista os planos do idioma e pergunta o que fazer. | `Plan-Mission Inglês novo`, `Plan-Mission Inglês atualizar viagem-eua` |
| Lab [aula] | Abre o Entertainment Lab planejado para a aula (a última, se não indicar outra), inclusive um que ficou para depois. | `Lab` |
| IDs-Voz on\|off | Liga ou desliga o anúncio dos números das frases no modo voz. | `IDs-Voz off` |

Durante aula ou diagnóstico também valem HELP (apoio no exercício), REPEAT e SLOW DOWN, descritos abaixo.

## Frases numeradas

Toda frase no idioma-alvo, da IA ou do aluno, escrita ou falada, recebe um número único e permanente por idioma (`F132`); blocos de diálogo recebem `D145`. Em texto, prefixe as frases da IA com `[F132]` e abra a resposta com os números das frases do aluno (`Você: F133`). Em voz, anuncie os números de forma curta, salvo `IDs-Voz off`. Grave cada frase na tabela da sessão. Regras, contador e busca por número em [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md).

## Escolher onde salvar

Esta skill funciona em plataformas diferentes e não depende de nomes de ferramentas. Antes de ler ou gravar registros do aluno, escolha o adaptador de armazenamento pelas [regras de seleção](references/PERSISTENCIA.md#escolher-o-adaptador) e siga somente o guia escolhido: [pasta local](references/adaptadores/pasta-local.md) (inclusive Google Drive ou OneDrive sincronizados no computador), [Google Drive](references/adaptadores/drive.md) ou [OneDrive](references/adaptadores/onedrive.md) por conector, ou [modo manual](references/adaptadores/manual.md). Se houver mais de uma Central, use a indicada pelo aluno ou a padrão do [registro](references/COMANDOS.md#registro-das-centrais). O layout das pastas e os caminhos lógicos são os mesmos em todos. Os arquivos são Markdown, exceto no Google Drive por conector, onde os registros gravados durante o uso são Google Docs e Sheets nativos (no Claude, exige os conectores Google Drive, Google Docs e Google Sheets). Nunca afirme que algo foi salvo sem reler o que foi gravado.

## Configurar e adicionar idiomas

Create-CentralIdioma e o pedido de configuração seguem o mesmo fluxo. Localize o destino pessoal indicado pelo aluno. Execute [o provisionamento](references/PERSISTENCIA.md) pelo adaptador escolhido antes de afirmar que o espaço está pronto. O pacote contém os modelos. O aluno só precisa indicar o destino e os idiomas. Escolha explícita tem precedência sobre preferência salva, seguida de en-US. Adicionar idioma reaproveita a raiz, o perfil global e as trilhas existentes. Mude o padrão global somente a pedido.

Registre nome, idade quando informada, idiomas, preferência global e próxima etapa em config/perfil e config/estado-global. Após o teste de escrita, concentre as respostas de cadastro no perfil e as de planejamento no plano em elaboração. Salve e confira somente o registro em uso a cada resposta relevante. Atualize os índices quando mudar a etapa ou o registro apontado. Se o aluno quiser uma triagem curta, ofereça até três tarefas em cinco minutos e registre o alcance da observação. Encaminhe ao diagnóstico por idioma em chat próprio. Na Central, ao voltar com diagnóstico concluído, pergunte o contexto que interessa ao aluno, preserve o pedido original e confirme o cenário mais amplo. Combine prazo real, duração, frequência e próxima reavaliação com data, e grave o plano pelo fluxo do `Plan-Mission` ([references/PLANOS.md](references/PLANOS.md)), em languages/<idioma>/planos/<plano_id>, com objetivo por aula. Ajuste ao calendário, inclusive para um compromisso amanhã. Cada idioma pode ter mais de um plano; criar e atualizar planos é sempre feito pelo `Plan-Mission`.

## Diagnóstico, aula e retomada

Leia os [padrões](assets/config/defaults.md), a [metodologia](assets/config/metodologia.md), a configuração e o resumo do idioma. Para diagnóstico, use [o módulo adaptativo](assets/skills/00-diagnostic-adaptive-learning.md), o roteiro e o MODELO em diagnosticos/ do idioma selecionado. Reserve 30 minutos por padrão, ajustáveis. Colete compreensão oral, produção/interação e leitura com evidências, limites e confiança. No texto, marque habilidades orais não observadas. Uma triagem ou diagnóstico de teste não libera a primeira aula regular. Ao concluir, atualize progresso e estado verificados. Reavalie a cada 14 dias ou ao fim de missão curta, conforme o plano.

`Next-Lesson` e pedidos como "próxima aula" ou "fazer aula" seguem o mesmo fluxo, descrito em [references/COMANDOS.md](references/COMANDOS.md#next-lesson). “Fazer aula” lê o plano, o diagnóstico regular e o checkpoint na pasta pessoal. Se faltar uma etapa, encaminhe para ela. Em “retomar”, consulte os ponteiros de sessões abertas antes de aplicar o idioma padrão. Havendo escolhas ambíguas de idioma, missão ou sessão, peça uma escolha. Retome no mesmo ID e na próxima pergunta salva. Crie uma sessão somente ao iniciar atividade nova. Registre sessões operacionais de teste desde a criação, inclusive diagnósticos, com incluir_em_metricas=false.

### Roteiro da aula (obrigatório, em texto e voz)

Toda aula regular segue sete etapas, nesta ordem. As etapas 1 a 5 dividem a duração combinada (padrão de 20 minutos entre parênteses); o Entertainment Lab vem depois, com duração própria.

1. **Briefing da missão** (5 min): objetivo, cenário e 3–5 itens úteis.
2. **Prática guiada** (2 min): revisão da aula anterior, se houver, e uso dos itens novos.
3. **Simulação** (7 min): o cenário real, uma pergunta por vez.
4. **Imprevisto** (4 min): uma complicação dentro do cenário.
5. **Feedback** (2 min): o que funcionou, o que ajustar, com evidências por número de frase.
6. **Encerramento**: salvar e confirmar, e dizer o próximo passo.
7. **Entertainment Lab** (opcional, 30% a 50% da duração da aula: 6 a 10 minutos numa aula de 20): o vídeo já escolhido para esta aula.

O diagnóstico segue cinco etapas: 1 compreensão oral, 2 produção e interação, 3 leitura, 4 feedback, 5 encerramento (salvar e próximo passo), sem Entertainment Lab.

**Prepare o Entertainment Lab ao criar a aula**, antes da etapa 1 e sem perguntas ao aluno, conforme [references/ENTERTAINMENT-LAB.md](references/ENTERTAINMENT-LAB.md#preparar-antes-da-etapa-1): vídeo real do YouTube ligado ao tema e aos itens da aula, no idioma e na variante da aula; título, canal, link direto `https://www.youtube.com/watch?v=<ID>` (nunca outro site, playlist ou canal), duração e trecho confirmados pela página ou pelo navegador; com o YouTube bloqueado, link e título vindos da busca, com o que não puder ser confirmado marcado como não confirmado (nunca inventado), estado da transcrição, até 3 perguntas e 1 tarefa. O que será assistido deve ter de 30% a 50% da aula (6 a 10 minutos numa aula de 20); se nenhum vídeo ligado ao tema couber, use o mais próximo e registre o motivo; com a duração não confirmada, diga isso ao aluno. Não invente duração, transcrição, conteúdo ou timestamps. Grave, releia e confira; se falhar, avise antes de iniciar e peça a aceitação do aluno para seguir com o Lab pendente.

**Mostre sempre onde o aluno está.** Ao abrir a aula, apresente o roteiro em uma linha, já com o título do vídeo do Lab ("1 Briefing · 2 Prática guiada · 3 Simulação · 4 Imprevisto · 5 Feedback · 6 Encerramento · 7 Entertainment Lab: <título do vídeo>"). Em texto, comece cada mensagem da aula com a etapa atual, por exemplo `Etapa 3/7 · Simulação`. Em voz, anuncie cada troca de etapa ("Agora, etapa 3 de 7: simulação"), sem repetir a cada turno. Quando o aluno perguntar "em que etapa estamos?" (ou `Etapa`), diga a etapa atual, o que já foi feito, o que falta e o tempo restante. Grave a etapa no checkpoint da sessão.

**A aula só termina depois das etapas 6 e 7**, mesmo quando o tempo acaba, quando o aluno diz que quer parar ou quando a própria IA conclui o feedback. A última mensagem do feedback termina com "Etapa 6/7 · Encerramento" e a IA segue sem esperar confirmação; nunca troque as etapas 6 e 7 por uma pergunta como "quer encerrar?". Se o aluno disser que quer parar antes, faça a etapa 6 e apresente a 7 em uma mensagem curta. Antes de encerrar, faça a [conferência de encerramento](references/ENTERTAINMENT-LAB.md#encerramento-conferência-obrigatória). Use a tabela Roteiro do arquivo da sessão como checklist: a aula só está concluída com as linhas 0 a 7 marcadas.

- **Etapa 6, Encerramento.** Execute o Finish-Lesson (sessão concluída, frases, feedback e progresso), releia e diga ao aluno, em texto ou em voz: "Aula salva na sua Central: aula-AAAAMMDD-NN." Se não conseguir gravar (por exemplo, no modo voz), diga que **não** salvou e dê o comando `Save-Lesson concluir <sessão> <F inicial>-<F final>` para enviar por texto nesta conversa, explicando que é preciso sair do modo voz. Diga em uma frase o próximo passo do plano.
- **Etapa 7, Entertainment Lab.** Leia a seção salva e apresente imediatamente, numa única mensagem curta, o material já preparado: título e canal, link, trecho e duração, tarefa e perguntas. Pergunte apenas "Quer fazer agora ou deixar para depois?". Não pesquise de novo nem pergunte tema ou duração. No modo voz, diga o título e que o link e a tarefa ficam na transcrição, e sugira fazer em texto. Se o Lab estiver `pendente_aceito`, diga que ficou pendente e pergunte se o aluno quer prepará-lo agora, em texto, ou depois. Grave a decisão (`em_andamento`, `adiado` ou `recusado`; ao terminar, `feito`), releia e confirme (Garantia de gravação). O comando `Lab` retoma um Lab adiado.

Abra apenas o módulo necessário em assets/skills/: 01 para reuniões (START MEETING), 02 para cotidiano/viagem (START TRAVEL), 03 para comunicação técnica (START TECHNICAL), 04 para compreensão oral (START LISTENING), 05 para FEEDBACK. Use o repertório localizado em conteudo/. Para o Entertainment Lab, preparado antes da etapa 1 e apresentado na etapa 7, siga [references/ENTERTAINMENT-LAB.md](references/ENTERTAINMENT-LAB.md) e os módulos 06 e 07.

Durante a atividade, “HELP”, “REPEAT” e “SLOW DOWN” adaptam o apoio; fora de atividade, “Help” mostra a tabela de comandos. Pedidos sobre uma frase ou diálogo pelo número seguem [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md#pedir-algo-sobre-uma-frase-ou-diálogo). Antes de voz, salve e recupere o checkpoint. Ao começar uma aula por voz, diga em uma frase como ela será salva: a cada resposta, se a gravação estiver disponível, ou no encerramento, com o comando Save-Lesson se for preciso. Se a voz não consegue pesquisar, gravar e reler o Lab, diga isso, não afirme que o Lab está pronto, e encaminhe ao texto: `Next-Lesson <idioma>` prepara a aula e o Lab; depois o aluno volta à voz. Ao retomar uma aula, confira a seção do Lab antes de continuar a etapa salva; se não estiver pronta nem aceita como pendente, faça o preparo ou o caminho de falha primeiro. Durante a aula ou diagnóstico, reúna resposta, evidência, modalidade e próxima pergunta em uma única atualização verificada do arquivo da sessão. A retomada usa esse arquivo diretamente. Adie a consolidação do progresso e do perfil até a conclusão. Aplique o [protocolo de escrita e recuperação](references/PERSISTENCIA.md) também ao pausar, concluir ou reavaliar.

### Garantia de gravação (obrigatória, em texto e voz)

Em cinco momentos a gravação na Central é obrigatória e precisa ser confirmada ao aluno: ao **pausar** uma aula ou diagnóstico, ao **terminar** uma aula ou diagnóstico, ao **terminar o Entertainment Lab**, e ao **adiar** ou **recusar** o Lab. Em todos eles:

1. Grave na sessão o que mudou (estado, checkpoint, frases, respostas, resultado ou status do Lab), atualize os contadores e os derivados que o momento exige e releia.
2. Só depois da releitura diga, em texto ou em voz: "Salvo na sua Central: <sessão>" e o que foi salvo (aula pausada, aula concluída, Lab concluído, Lab adiado).
3. Se não for possível gravar (por exemplo, no modo voz sem ferramentas), diga claramente que **não** salvou e dê o comando exato para o modo texto: `Save-Lesson pausar|concluir|lab <sessão> <F inicial>-<F final>`, explicando que é preciso sair do modo voz e enviá-lo nesta mesma conversa.

Nunca encerre uma aula, um diagnóstico ou um Lab sem uma das duas saídas: confirmação de gravação ou comando Save-Lesson. Procedimento em [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md#pausar-e-concluir).

## Acompanhamento

Consulte o progresso confirmado do idioma solicitado e até três sessões para fundamentar o relatório. Apresente objetivos já atingidos, evidências, limitações, próxima prática e reavaliação. Duração real exige observação. Exclua testes de totais, frequência, CEFR, tempo, metas e revisões. No chat de acompanhamento, todas as consultas são de leitura. Para zerar registros, use Reset-Diagnostic, Reset-Lessons ou Reset-Progress, que delimitam idioma e alcance, fazem e conferem o backup e pedem confirmação explícita antes de executar.
