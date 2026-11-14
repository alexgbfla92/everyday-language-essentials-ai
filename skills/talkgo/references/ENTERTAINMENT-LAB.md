# Entertainment Lab: preparo, apresentação e encerramento

Este é o procedimento único do Entertainment Lab. O SKILL.md resume as regras; em caso de dúvida, vale este documento.

## Princípio

O Lab faz parte da prática e não tem status próprio: a prática é que tem status (veja Status das práticas no SKILL.md). O material é preparado **antes da etapa 1** e só é considerado pronto depois que o registro salvo na sessão é relido e conferido. A prática termina no encerramento (etapa 6), como `Concluída`; logo depois, na mesma mensagem, o Lab é sempre sugerido com o material já salvo. Fazer ou não o Lab não muda a prática. Não existe preparo silencioso no fim: ou o material está pronto antes da etapa 1, ou o aluno foi avisado da falha e aceitou começar sem o vídeo.

## Registro na sessão

A seção Entertainment Lab do arquivo da prática usa campos com nomes fixos (iguais nos três idiomas), um por linha, no formato `campo: valor`:

| Campo | Conteúdo |
| --- | --- |
| `lab_titulo`, `lab_canal` | título e canal como aparecem no YouTube |
| `lab_url` | só `https://www.youtube.com/watch?v=<ID>` (um vídeo; nunca outro site, playlist ou canal) |
| `lab_idioma_variante` | idioma e variante do vídeo (ex.: inglês americano) |
| `lab_duracao_pratica_min` | duração combinada da prática, em minutos |
| `lab_duracao_video_min` | duração do vídeo inteiro, em minutos, como informada pelo YouTube |
| `lab_trecho` | `inteiro` ou `mm:ss-mm:ss` com início e fim confirmados |
| `lab_motivo_fora_da_faixa` | obrigatório se o que será assistido ficar fora de 30–50% da prática |
| `lab_transcricao` | `obtida`, `legendas_indicadas` ou `nao_confirmada` |
| `lab_itens_da_pratica` | itens da prática que o vídeo e a tarefa reutilizam |
| `lab_pergunta_1` a `lab_pergunta_3` | pelo menos uma pergunta, no máximo três |
| `lab_tarefa` | uma tarefa curta |
| `lab_fonte_verificacao` | `pagina_youtube`, `navegador` ou `busca`: de onde vieram título, canal e duração. Só com `busca`, `lab_canal` e `lab_duracao_video_min` podem ser `nao_confirmado(a)` |
| `lab_evidencia_busca` | só com `busca`: o resultado usado (link do YouTube, título, canal e duração como aparecem) |
| `lab_verificado_em` | data e hora da releitura do registro salvo |
| `lab_pendencia_motivo`, `lab_pendencia_aceita_pelo_aluno` | só quando a verificação falhou: por que falhou e quando o aluno aceitou começar sem o vídeo |
| `lab_sugerido_apos_encerramento` | `sim` quando o Lab foi sugerido logo depois do encerramento |
| `lab_resultado` | respostas, tarefa e feedback, só se o aluno fizer o Lab |
| `lab_gravacao_confirmada` | `sim` depois de gravar o resultado de um Lab feito e confirmar ao aluno |

Não há campo de status do Lab. Material preenchido e `lab_verificado_em` indicam que ele está pronto; `lab_resultado` indica que foi feito.

O encerramento da prática usa: `status: Concluída`, `encerramento_pratica_salva_relida` (`sim`), `encerramento_proximo_passo` (texto).

## Preparar (antes da etapa 1)

Faça isto ao criar a prática, sem perguntas ao aluno, e antes de mostrar a etapa 1:

1. Defina cenário e itens da prática. Pesquise no YouTube um vídeo no idioma e na variante da prática, adequado ao nível e ligado ao tema e aos itens.
2. Confirme os dados do vídeo, tentando nesta ordem e parando na primeira que funcionar:
   1. **Página do YouTube.** Com Python: `python scripts/youtube.py info <link> [<link>...]` lê título, canal e duração na página (passe os candidatos de uma vez, para um único pedido de permissão). Sem Python, abra o link do vídeo. Registre `lab_fonte_verificacao: pagina_youtube`.
      - **Sem rede no ambiente de comandos** (resposta com `"sem_rede": true`): se a plataforma permite pedir aprovação para rodar um comando com acesso à internet (por exemplo, o Codex e o app de desktop do ChatGPT, cujo padrão é rede desligada), peça essa aprovação, explicando em uma frase que é para confirmar canal e duração do vídeo, e rode o mesmo comando de novo. Só passe para a busca se a aprovação não existir, for negada ou o acesso continuar bloqueado.
   2. **Navegador** disponível na sessão (navegador do app de desktop, extensão do Chrome): `navegador`.
   3. **Resultado da busca**, quando o YouTube está bloqueado no ambiente. Use um vídeo cujo link do youtube.com (com o ID) apareça num resultado de busca, direto ou numa página que mostre o ID, e cujo título esteja ligado ao tema. Registre `busca` e copie em `lab_evidencia_busca` o que o resultado mostra. O que o resultado não mostrar fica `nao_confirmado`: em geral o canal (`lab_canal: nao_confirmado`) e a duração (`lab_duracao_video_min: nao_confirmada`). Use o vídeo inteiro (`lab_trecho: inteiro`) e a transcrição `nao_confirmada`, salvo se o resultado mostrar que ela existe. Entre os candidatos, prefira títulos que indiquem conversa curta ligada ao tema da prática.

   Não invente duração, canal, transcrição, conteúdo ou timestamps. A verificação só falha se nem a busca trouxer um link do YouTube com título ligado ao tema.

3. Duração: quando a duração é confirmada, o que será assistido (vídeo inteiro ou trecho) deve ter de 30% a 50% da prática (6 a 10 minutos numa prática de 20). Com a duração `nao_confirmada`, a faixa não pode ser conferida: diga isso ao aluno na etapa 7. A ligação com o conteúdo vem primeiro; se nenhum vídeo ligado ao tema couber, escolha o mais próximo e preencha `lab_motivo_fora_da_faixa`. Use trecho só com início e fim confirmados.
4. Prepare até 3 perguntas e 1 tarefa curta que reutilizem os itens da prática.
5. Grave a seção e releia o registro salvo.
6. Confira o registro relido. Com Python: `python scripts/lab.py pronto ARQUIVO` (ou `-` lendo o texto do Doc pela entrada padrão) deve responder `"pode_iniciar": true`. Sem Python, confira os mesmos itens: todos os campos acima preenchidos; link no formato do YouTube; duração dentro da faixa ou motivo preenchido; trecho válido e dentro do vídeo; transcrição com um dos três valores; 1 a 3 perguntas; tarefa.
7. Grave `lab_verificado_em` e marque a etapa 0 da tabela Roteiro. Só então mostre o roteiro, já com o título do vídeo, e comece a etapa 1.

### Se a verificação falhar

Falha é qualquer caso em que o passo 6 não passa: sem ferramenta de busca, nenhum vídeo confirmado por página, navegador ou resultado de busca, link fora do YouTube, duração ou trecho não confirmados, ou registro que não pôde ser gravado e relido.

1. **Antes de iniciar a prática**, diga ao aluno em uma ou duas frases o que falhou e pergunte: "Quer começar a prática sem o vídeo do Entertainment Lab? Eu o preparo depois." Não comece a etapa 1 antes da resposta.
2. Se aceitar: grave `lab_pendencia_motivo` e `lab_pendencia_aceita_pelo_aluno` (com data), releia e siga. Se não aceitar: ofereça tentar de novo ou preparar em texto (`Start-Practice <idioma>`), sem iniciar a prática.
3. Nunca grave `lab_verificado_em` sem o passo 6 e nunca preencha `lab_pendencia_aceita_pelo_aluno` sem a resposta do aluno.

## Etapa 7 (sugerir depois do encerramento)

1. Na mesma mensagem que confirma a prática concluída, leia a seção salva e apresente: título e canal, link, trecho e duração, a tarefa e as perguntas. Se canal ou duração estiverem `nao_confirmado(a)`, diga isso em poucas palavras ("duração não confirmada: o YouTube estava inacessível na preparação"). Não faça nova pesquisa e não pergunte tema nem duração.
2. Faça uma única pergunta: "Quer fazer o Lab agora?".
3. Se a prática começou sem o vídeo (pendência aceita), diga isso e pergunte se o aluno quer que você prepare agora, em texto. Só aqui uma pesquisa no fim é permitida, e só se o aluno pedir.
4. Se o aluno fizer o Lab, grave `lab_resultado` (Finish-Lab), releia e confirme. Se não fizer, não grave nada: a prática continua `Concluída` e o comando `Start-Lab` abre o material depois.

## Encerramento (conferência obrigatória)

Antes de confirmar o encerramento de qualquer prática regular, inclusive quando o aluno pede para encerrar no meio, confira os quatro itens e corrija o que faltar:

1. **Status**: `status: Concluída`.
2. **Prática salva e relida**: `encerramento_pratica_salva_relida: sim`, depois do Finish-Practice.
3. **Próximo passo informado**: `encerramento_proximo_passo` preenchido e dito ao aluno.
4. **Lab sugerido**: `lab_sugerido_apos_encerramento: sim`, gravado na mesma escrita do Finish-Practice, com a sugestão feita na mesma mensagem.

Com Python: `python scripts/lab.py encerramento ARQUIVO` deve responder `"pode_encerrar": true`. O aluno nunca é obrigado a fazer o Lab, e a resposta dele não muda o status da prática. Depois de "quer encerrar?" do aluno, nunca pule a conferência.

## Voz e retomada

- **Início em voz.** Se a sessão consegue pesquisar, gravar e reler em voz, siga o preparo normalmente. Se não consegue, diga que não é possível preparar nem salvar o Lab no modo voz, não afirme que algo está pronto ou salvo, e encaminhe para o texto: "Saia do modo voz e envie `Start-Practice <idioma>` nesta conversa; depois volte ao modo voz." A prática só começa em voz sem o material pronto se o aluno aceitar começar sem o vídeo, e essa aceitação precisa ser gravada (em texto, pelo Save-Practice, se a voz não grava).
- **Retomada.** Ao retomar uma prática, leia a seção do Lab antes de continuar a etapa salva. Se o material não estiver pronto nem houver pendência aceita, faça o preparo agora (ou o caminho de falha) antes de seguir. Se a prática for retomada na etapa 6, faça o encerramento e a conferência.
- **Voz sem acesso ao registro.** Não diga que o material está pronto nem que algo foi salvo. Diga a limitação e dê o comando de texto: `Start-Practice <idioma>` para preparar, ou `Save-Practice pausar|concluir|lab <sessão> <F inicial>-<F final>` para gravar.

## Confirmação de gravação

Só o resultado de um Lab feito é gravado depois do encerramento. Ele segue a Garantia de gravação do SKILL.md: gravar, reler e dizer "Salvo na sua Central: <sessão> — resultado do Lab"; sem gravação possível, dizer que não salvou e dar o `Save-Practice lab`.
