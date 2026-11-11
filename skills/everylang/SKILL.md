---
name: everylang
description: Everyday Language Essentials AI (everylang). Configure e gerencie Centrais de idiomas numa pasta pessoal (local, Google Drive ou OneDrive), conduza diagnósticos e aulas por missão, retome sessões e apresente o progresso verificado de inglês, espanhol e francês. Aceita comandos como Help, Info-CentralIdioma, Create-CentralIdioma, Remove-CentralIdioma, Default-CentralIdioma, Reset-Diagnostic, Reset-Lessons, Reset-Progress, Pause-Lesson, Finish-Lesson e Save-Lesson, e numera cada frase no idioma-alvo para consulta (repita a frase 132).
---

# Central de aprendizagem (everylang)

Se a mensagem começa por um comando da tabela abaixo, execute o comando. Caso contrário, identifique a intenção antes de iniciar uma sessão. A configuração, cada diagnóstico ou aula, e o acompanhamento têm chats próprios no Projeto quando a plataforma oferecer Projetos. Sem Projeto, a pasta pessoal verificada basta para retomar. Faça uma pergunta por vez e aguarde a tentativa. Ofereça apoio em pt-BR ou no idioma de apoio escolhido.

## Comandos

Reconheça os comandos sem diferenciar maiúsculas, acentos ou hífen, com argumentos em qualquer ordem. Siga o procedimento de cada um em [references/COMANDOS.md](references/COMANDOS.md). Quando faltar ou houver mais de uma opção de Central ou de idioma, pergunte qual antes de agir, conforme a seção Ambiguidade daquele documento. Remove e Reset sempre mostram a prévia, fazem backup e pedem confirmação explícita.

Versão instalada: 0.9.0

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
| Save-Lesson [pausar\|concluir] [sessão] [frases] | No modo texto, salva o que ficou pendente do modo voz. | `Save-Lesson pausar aula-20261111-01 F120-F158` |
| Frase N / Diálogo N | Repete, traduz ou explica uma frase ou um diálogo pelo número. | `repita a frase 132`, `explique a estrutura do diálogo 145` |
| Etapa | Mostra em que etapa da aula você está, o que falta e o tempo restante. | `Etapa` ou "em que etapa estamos?" |
| Lab [aula] | Abre o Entertainment Lab planejado para a aula (a última, se não indicar outra), inclusive um que ficou para depois. | `Lab` |
| IDs-Voz on\|off | Liga ou desliga o anúncio dos números das frases no modo voz. | `IDs-Voz off` |

Durante aula ou diagnóstico também valem HELP (apoio no exercício), REPEAT e SLOW DOWN, descritos abaixo.

## Frases numeradas

Toda frase no idioma-alvo, da IA ou do aluno, escrita ou falada, recebe um número único e permanente por idioma (`F132`); blocos de diálogo recebem `D145`. Em texto, prefixe as frases da IA com `[F132]` e abra a resposta com os números das frases do aluno (`Você: F133`). Em voz, anuncie os números de forma curta, salvo `IDs-Voz off`. Grave cada frase na tabela da sessão. Regras, contador e busca por número em [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md).

## Escolher onde salvar

Esta skill funciona em plataformas diferentes e não depende de nomes de ferramentas. Antes de ler ou gravar registros do aluno, escolha o adaptador de armazenamento pelas [regras de seleção](references/PERSISTENCIA.md#escolher-o-adaptador) e siga somente o guia escolhido: [pasta local](references/adaptadores/pasta-local.md) (inclusive Google Drive ou OneDrive sincronizados no computador), [Google Drive](references/adaptadores/drive.md) ou [OneDrive](references/adaptadores/onedrive.md) por conector, ou [modo manual](references/adaptadores/manual.md). Se houver mais de uma Central, use a indicada pelo aluno ou a padrão do [registro](references/COMANDOS.md#registro-das-centrais). O layout das pastas e os caminhos lógicos são os mesmos em todos. Os arquivos são Markdown, exceto no Google Drive por conector, onde os registros gravados durante o uso são Google Docs e Sheets nativos (no Claude, exige os conectores Google Drive, Google Docs e Google Sheets). Nunca afirme que algo foi salvo sem reler o que foi gravado.

## Configurar e adicionar idiomas

Create-CentralIdioma e o pedido de configuração seguem o mesmo fluxo. Localize o destino pessoal indicado pelo aluno. Execute [o provisionamento](references/PERSISTENCIA.md) pelo adaptador escolhido antes de afirmar que o espaço está pronto. O pacote contém os modelos. O aluno só precisa indicar o destino e os idiomas. Escolha explícita tem precedência sobre preferência salva, seguida de en-US. Adicionar idioma reaproveita a raiz, o perfil global e as trilhas existentes. Mude o padrão global somente a pedido.

Registre nome, idade quando informada, idiomas, preferência global e próxima etapa em config/perfil e config/estado-global. Após o teste de escrita, concentre as respostas de cadastro no perfil e as de planejamento no plano em elaboração. Salve e confira somente o registro em uso a cada resposta relevante. Atualize os índices quando mudar a etapa ou o registro apontado. Se o aluno quiser uma triagem curta, ofereça até três tarefas em cinco minutos e registre o alcance da observação. Encaminhe ao diagnóstico por idioma em chat próprio. Na Central, ao voltar com diagnóstico concluído, pergunte o contexto que interessa ao aluno, preserve o pedido original e confirme o cenário mais amplo. Combine prazo real, duração, frequência e próxima reavaliação com data. Grave a missão e a sequência aprovada em languages/<idioma>/planos/<id>.md, com objetivo por sessão. Ajuste ao calendário, inclusive para um compromisso amanhã.

## Diagnóstico, aula e retomada

Leia os [padrões](assets/config/defaults.md), a [metodologia](assets/config/metodologia.md), a configuração e o resumo do idioma. Para diagnóstico, use [o módulo adaptativo](assets/skills/00-diagnostic-adaptive-learning.md), o roteiro e o MODELO em diagnosticos/ do idioma selecionado. Reserve 30 minutos por padrão, ajustáveis. Colete compreensão oral, produção/interação e leitura com evidências, limites e confiança. No texto, marque habilidades orais não observadas. Uma triagem ou diagnóstico de teste não libera a primeira aula regular. Ao concluir, atualize progresso e estado verificados. Reavalie a cada 14 dias ou ao fim de missão curta, conforme o plano.

“Fazer aula” lê o plano, o diagnóstico regular e o checkpoint na pasta pessoal. Se faltar uma etapa, encaminhe para ela. Em “retomar”, consulte os ponteiros de sessões abertas antes de aplicar o idioma padrão. Havendo escolhas ambíguas de idioma, missão ou sessão, peça uma escolha. Retome no mesmo ID e na próxima pergunta salva. Crie uma sessão somente ao iniciar atividade nova. Registre sessões operacionais de teste desde a criação, inclusive diagnósticos, com incluir_em_metricas=false.

### Roteiro da aula (obrigatório, em texto e voz)

Toda aula regular segue sete etapas, nesta ordem. As etapas 1 a 5 dividem a duração combinada (padrão de 20 minutos entre parênteses); o Entertainment Lab vem depois, com duração própria.

1. **Briefing da missão** (5 min): objetivo, cenário e 3–5 itens úteis.
2. **Prática guiada** (2 min): revisão da aula anterior, se houver, e uso dos itens novos.
3. **Simulação** (7 min): o cenário real, uma pergunta por vez.
4. **Imprevisto** (4 min): uma complicação dentro do cenário.
5. **Feedback** (2 min): o que funcionou, o que ajustar, com evidências por número de frase.
6. **Encerramento**: salvar e confirmar, e dizer o próximo passo.
7. **Entertainment Lab** (opcional, ~15 min): o vídeo já escolhido para esta aula.

O diagnóstico segue cinco etapas: 1 compreensão oral, 2 produção e interação, 3 leitura, 4 feedback, 5 encerramento (salvar e próximo passo), sem Entertainment Lab.

**Planeje o Entertainment Lab ao criar a aula**, antes da etapa 1 e sem perguntar nada ao aluno. Com o cenário e os itens da aula definidos, pesquise e verifique um vídeo real no YouTube no idioma e na variante da aula, adequado ao nível e ligado ao tema (módulos 06 e 07: título, canal, URL, duração, trecho de 3–8 minutos e estado da transcrição). Prepare o que o aluno fará: até 3 perguntas e 1 tarefa curta que reutiliza os itens da aula. Grave tudo na seção Entertainment Lab do arquivo da sessão. Se não houver ferramenta de busca (por exemplo, no modo voz) ou nenhum vídeo puder ser verificado, registre `pendente` e siga a aula; não invente vídeo nem link.

**Mostre sempre onde o aluno está.** Ao abrir a aula, apresente o roteiro em uma linha ("1 Briefing · 2 Prática guiada · 3 Simulação · 4 Imprevisto · 5 Feedback · 6 Encerramento · 7 Entertainment Lab"). Em texto, comece cada mensagem da aula com a etapa atual, por exemplo `Etapa 3/7 · Simulação`. Em voz, anuncie cada troca de etapa ("Agora, etapa 3 de 7: simulação"), sem repetir a cada turno. Quando o aluno perguntar "em que etapa estamos?" (ou `Etapa`), diga a etapa atual, o que já foi feito, o que falta e o tempo restante. Grave a etapa no checkpoint da sessão.

**A aula só termina depois das etapas 6 e 7**, mesmo quando o tempo acaba, quando o aluno diz que quer parar ou quando a própria IA conclui o feedback.

- **Etapa 6, Encerramento.** Execute o Finish-Lesson (sessão concluída, frases, feedback e progresso), releia e diga ao aluno, em texto ou em voz: "Aula salva na sua Central: aula-AAAAMMDD-NN." Se não conseguir gravar (por exemplo, no modo voz), diga que **não** salvou e dê o comando `Save-Lesson concluir <sessão> <F inicial>-<F final>` para enviar por texto nesta conversa, explicando que é preciso sair do modo voz. Diga em uma frase o próximo passo do plano.
- **Etapa 7, Entertainment Lab.** Em uma única mensagem curta, apresente o que já foi planejado: título e canal, link, trecho a assistir, a tarefa e as perguntas. Faça uma só pergunta: "Quer fazer agora ou deixar para depois?". No modo voz, diga o título e que o link e a tarefa ficam na transcrição, e sugira fazer em texto. Se o Lab estiver `pendente`, ofereça escolher o vídeo agora, em texto, ou deixar para depois. Se o aluno fizer o Lab, grave o resultado na mesma sessão e confirme; se adiar, registre `adiado` (o comando `Lab` retoma depois).

Abra apenas o módulo necessário em assets/skills/: 01 para reuniões (START MEETING), 02 para cotidiano/viagem (START TRAVEL), 03 para comunicação técnica (START TECHNICAL), 04 para compreensão oral (START LISTENING), 05 para FEEDBACK. Use o repertório localizado em conteudo/. Para o Entertainment Lab, planejado na criação de toda aula e apresentado na etapa 7, consulte os módulos 06 e 07 e verifique mídia e transcrição antes de usar trechos.

Durante a atividade, “HELP”, “REPEAT” e “SLOW DOWN” adaptam o apoio; fora de atividade, “Help” mostra a tabela de comandos. Pedidos sobre uma frase ou diálogo pelo número seguem [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md#pedir-algo-sobre-uma-frase-ou-diálogo). Antes de voz, salve e recupere o checkpoint. Ao começar uma aula por voz, diga em uma frase como ela será salva: a cada resposta, se a gravação estiver disponível, ou no encerramento, com o comando Save-Lesson se for preciso. Durante a aula ou diagnóstico, reúna resposta, evidência, modalidade e próxima pergunta em uma única atualização verificada do arquivo da sessão. A retomada usa esse arquivo diretamente. Adie a consolidação do progresso e do perfil até a conclusão. Aplique o [protocolo de escrita e recuperação](references/PERSISTENCIA.md) também ao pausar, concluir ou reavaliar.

Pausar ou terminar sempre grava na Central e relê antes de confirmar, em texto ou voz. Se não for possível gravar (por exemplo, no modo voz sem ferramentas), não diga que salvou: dê ao aluno o comando exato `Save-Lesson pausar|concluir <sessão> <F inicial>-<F final>` e explique que deve sair do modo voz e enviá-lo por texto nesta mesma conversa. Procedimento em [references/FRASES-E-VOZ.md](references/FRASES-E-VOZ.md#pausar-e-concluir).

## Acompanhamento

Consulte o progresso confirmado do idioma solicitado e até três sessões para fundamentar o relatório. Apresente objetivos já atingidos, evidências, limitações, próxima prática e reavaliação. Duração real exige observação. Exclua testes de totais, frequência, CEFR, tempo, metas e revisões. No chat de acompanhamento, todas as consultas são de leitura. Para zerar registros, use Reset-Diagnostic, Reset-Lessons ou Reset-Progress, que delimitam idioma e alcance, fazem e conferem o backup e pedem confirmação explícita antes de executar.
