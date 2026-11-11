# Entertainment Lab: preparo, apresentação e encerramento

Este é o procedimento único do Entertainment Lab. O SKILL.md resume as regras; em caso de dúvida, vale este documento.

## Princípio

O Lab é preparado **antes da etapa 1** e só é considerado pronto depois que o registro salvo na sessão é relido e conferido. No fim da aula, a etapa 7 apenas apresenta o que já está salvo. Não existe preparo silencioso no fim: ou o Lab está `pronto` antes da etapa 1, ou o aluno foi avisado da falha e aceitou começar com o Lab pendente (`pendente_aceito`).

## Registro na sessão

A seção Entertainment Lab do arquivo da aula usa campos com nomes fixos (iguais nos três idiomas), um por linha, no formato `campo: valor`:

| Campo | Conteúdo |
| --- | --- |
| `lab_status` | `a_preparar` (padrão do modelo), `pronto`, `pendente_aceito`, `em_andamento`, `feito`, `adiado` ou `recusado` |
| `lab_titulo`, `lab_canal` | título e canal como aparecem no YouTube |
| `lab_url` | só `https://www.youtube.com/watch?v=<ID>` (um vídeo; nunca outro site, playlist ou canal) |
| `lab_idioma_variante` | idioma e variante do vídeo (ex.: inglês americano) |
| `lab_duracao_aula_min` | duração combinada da aula, em minutos |
| `lab_duracao_video_min` | duração do vídeo inteiro, em minutos, como informada pelo YouTube |
| `lab_trecho` | `inteiro` ou `mm:ss-mm:ss` com início e fim confirmados |
| `lab_motivo_fora_da_faixa` | obrigatório se o que será assistido ficar fora de 30–50% da aula |
| `lab_transcricao` | `obtida`, `legendas_indicadas` ou `nao_confirmada` |
| `lab_itens_da_aula` | itens da aula que o vídeo e a tarefa reutilizam |
| `lab_pergunta_1` a `lab_pergunta_3` | pelo menos uma pergunta, no máximo três |
| `lab_tarefa` | uma tarefa curta |
| `lab_fonte_verificacao` | `pagina_youtube`, `navegador` ou `busca`: de onde vieram título, canal e duração. Só com `busca`, `lab_canal` e `lab_duracao_video_min` podem ser `nao_confirmado(a)` |
| `lab_evidencia_busca` | só com `busca`: o resultado usado (link do YouTube, título, canal e duração como aparecem) |
| `lab_verificado_em` | data e hora da releitura do registro salvo |
| `lab_pendencia_motivo`, `lab_pendencia_aceita_pelo_aluno` | só para `pendente_aceito`: por que falhou e quando o aluno aceitou |
| `lab_oferecido_na_etapa_7` | `sim` depois da apresentação na etapa 7 |
| `lab_resultado` | respostas, tarefa e feedback, quando o Lab é feito |
| `lab_gravacao_confirmada` | `sim` depois de gravar e confirmar ao aluno o status final do Lab |

O encerramento da aula usa: `encerramento_aula_salva_relida` (`sim`), `encerramento_proximo_passo` (texto).

## Preparar (antes da etapa 1)

Faça isto ao criar a aula, sem perguntas ao aluno, e antes de mostrar a etapa 1:

1. Defina cenário e itens da aula. Pesquise no YouTube um vídeo no idioma e na variante da aula, adequado ao nível e ligado ao tema e aos itens.
2. Confirme os dados do vídeo, tentando nesta ordem e parando na primeira que funcionar:
   1. **Página do YouTube.** Com Python: `python scripts/youtube.py info <link>` lê título, canal e duração na página. Sem Python, abra o link do vídeo. Registre `lab_fonte_verificacao: pagina_youtube`.
   2. **Navegador** disponível na sessão (navegador do app de desktop, extensão do Chrome): `navegador`.
   3. **Resultado da busca**, quando o YouTube está bloqueado no ambiente. Use um vídeo cujo link do youtube.com (com o ID) apareça num resultado de busca, direto ou numa página que mostre o ID, e cujo título esteja ligado ao tema. Registre `busca` e copie em `lab_evidencia_busca` o que o resultado mostra. O que o resultado não mostrar fica `nao_confirmado`: em geral o canal (`lab_canal: nao_confirmado`) e a duração (`lab_duracao_video_min: nao_confirmada`). Use o vídeo inteiro (`lab_trecho: inteiro`) e a transcrição `nao_confirmada`, salvo se o resultado mostrar que ela existe. Entre os candidatos, prefira títulos que indiquem conversa curta ligada ao tema da aula.

   Não invente duração, canal, transcrição, conteúdo ou timestamps. A verificação só falha se nem a busca trouxer um link do YouTube com título ligado ao tema.

3. Duração: quando a duração é confirmada, o que será assistido (vídeo inteiro ou trecho) deve ter de 30% a 50% da aula (6 a 10 minutos numa aula de 20). Com a duração `nao_confirmada`, a faixa não pode ser conferida: diga isso ao aluno na etapa 7. A ligação com o conteúdo vem primeiro; se nenhum vídeo ligado ao tema couber, escolha o mais próximo e preencha `lab_motivo_fora_da_faixa`. Use trecho só com início e fim confirmados.
4. Prepare até 3 perguntas e 1 tarefa curta que reutilizem os itens da aula.
5. Grave a seção com `lab_status: pronto` e releia o registro salvo.
6. Confira o registro relido. Com Python: `python scripts/lab.py pronto ARQUIVO` (ou `-` lendo o texto do Doc pela entrada padrão) deve responder `"pode_iniciar": true`. Sem Python, confira os mesmos itens: todos os campos acima preenchidos; link no formato do YouTube; duração dentro da faixa ou motivo preenchido; trecho válido e dentro do vídeo; transcrição com um dos três valores; 1 a 3 perguntas; tarefa.
7. Grave `lab_verificado_em` e marque a etapa 0 da tabela Roteiro. Só então mostre o roteiro, já com o título do vídeo, e comece a etapa 1.

### Se a verificação falhar

Falha é qualquer caso em que o passo 6 não passa: sem ferramenta de busca, nenhum vídeo confirmado por página, navegador ou resultado de busca, link fora do YouTube, duração ou trecho não confirmados, ou registro que não pôde ser gravado e relido.

1. **Antes de iniciar a aula**, diga ao aluno em uma ou duas frases o que falhou e pergunte: "Quer começar a aula com o Entertainment Lab pendente? Eu o preparo depois." Não comece a etapa 1 antes da resposta.
2. Se aceitar: grave `lab_status: pendente_aceito`, `lab_pendencia_motivo` e `lab_pendencia_aceita_pelo_aluno` (com data), releia e siga. Se não aceitar: ofereça tentar de novo ou preparar em texto (`Next-Lesson <idioma>`), sem iniciar a aula.
3. Nunca marque `pronto` sem o passo 6 e nunca use `pendente_aceito` sem a resposta do aluno.

## Etapa 7 (apresentar)

1. Leia a seção salva. Se `lab_status` for `pronto`, apresente imediatamente, numa única mensagem curta: título e canal, link, trecho e duração, a tarefa e as perguntas. Se canal ou duração estiverem `nao_confirmado(a)`, diga isso em poucas palavras ("duração não confirmada: o YouTube estava inacessível na preparação"). Não faça nova pesquisa e não pergunte tema nem duração.
2. Faça uma única pergunta: "Quer fazer agora ou deixar para depois?".
3. Se for `pendente_aceito`, diga que o Lab ficou pendente e pergunte: "Quer que eu prepare agora (em texto) ou deixamos para depois?". Só aqui uma pesquisa no fim é permitida, e só se o aluno pedir.
4. Grave `lab_oferecido_na_etapa_7: sim`. Conforme a resposta: `em_andamento` (fazer agora), `adiado` (depois) ou `recusado`. Grave, releia e confirme ao aluno.
5. Ao terminar um Lab feito, grave `feito` e `lab_resultado` (Finish-Lab), releia e confirme.

## Encerramento (conferência obrigatória)

Antes de encerrar qualquer aula regular, inclusive quando o aluno pede para encerrar no meio, confira os quatro itens e corrija o que faltar:

1. **Aula salva e relida**: `encerramento_aula_salva_relida: sim`, depois do Finish-Lesson.
2. **Próximo passo informado**: `encerramento_proximo_passo` preenchido e dito ao aluno.
3. **Lab oferecido**: `lab_oferecido_na_etapa_7: sim`.
4. **Decisão registrada**: `lab_status` em `feito`, `adiado` ou `recusado`, com `lab_gravacao_confirmada: sim`.

Com Python: `python scripts/lab.py encerramento ARQUIVO` deve responder `"pode_encerrar": true`. O aluno nunca é obrigado a fazer o Lab. Se ele pediu para encerrar, grave `adiado` como decisão provisória, confirme a gravação e, mesmo assim, faça a pergunta única ("Quer fazer agora ou deixar para depois?"); não decida por ele sem perguntar. Se ele responder "agora", mude para `em_andamento`; se não responder, o `adiado` já gravado vale. Depois de "quer encerrar?" do aluno, nunca pule a conferência.

## Voz e retomada

- **Início em voz.** Se a sessão consegue pesquisar, gravar e reler em voz, siga o preparo normalmente. Se não consegue, diga que não é possível preparar nem salvar o Lab no modo voz, não afirme que algo está pronto ou salvo, e encaminhe para o texto: "Saia do modo voz e envie `Next-Lesson <idioma>` nesta conversa; depois volte ao modo voz." A aula só começa em voz sem o Lab pronto se o aluno aceitar o Lab pendente, e essa aceitação precisa ser gravada (em texto, pelo Save-Lesson, se a voz não grava).
- **Retomada.** Ao retomar uma aula, leia a seção do Lab antes de continuar a etapa salva. Se não estiver `pronto` nem `pendente_aceito`, faça o preparo agora (ou o caminho de falha) antes de seguir. Se a aula for retomada na etapa 6 ou 7, faça a conferência de encerramento.
- **Voz sem acesso ao registro.** Não diga que o material está pronto nem que algo foi salvo. Diga a limitação e dê o comando de texto: `Next-Lesson <idioma>` para preparar, ou `Save-Lesson pausar|concluir|lab <sessão> <F inicial>-<F final>` para gravar.

## Confirmação de gravação

Concluir, adiar ou recusar o Lab segue a Garantia de gravação do SKILL.md: gravar, reler e dizer "Salvo na sua Central: <sessão> — Lab concluído | adiado | recusado"; sem gravação possível, dizer que não salvou e dar o `Save-Lesson lab`.
