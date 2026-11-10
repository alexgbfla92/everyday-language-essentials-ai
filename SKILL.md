---
name: everyday-language-essentials-ai
description: Configure a Central Everyday Essentials no Google Drive pessoal, conduza diagnósticos e aulas de idiomas por missão e retome sessões ou apresente o progresso verificado de inglês, espanhol e francês.
---

# Central de aprendizagem

Identifique a intenção antes de iniciar uma sessão. A configuração, cada diagnóstico ou aula, e o acompanhamento têm chats próprios no Projeto quando disponível. Em Codex, a pasta pessoal verificada permite trabalhar sem um Projeto do ChatGPT. Faça uma pergunta por vez e aguarde a tentativa. Ofereça apoio em pt-BR ou no idioma de apoio escolhido.

## Configurar e adicionar idiomas

Localize o destino pessoal indicado pelo aluno. Execute [o provisionamento pelo conector](docs/PERSISTENCIA.md) antes de afirmar que o espaço está pronto. O pacote contém os modelos. O aluno só precisa indicar o destino e os idiomas. Escolha explícita tem precedência sobre preferência salva, seguida de en-US. Adicionar idioma reaproveita a raiz, o perfil global e as trilhas existentes. Mude o padrão global somente a pedido.

Registre nome, idade quando informada, idiomas, preferência global e próxima etapa em config/perfil.md e config/estado-global.md. Após o teste de escrita, concentre as respostas de cadastro no perfil e as de planejamento no plano em elaboração. Salve e confira somente o registro em uso a cada resposta relevante. Atualize os índices quando mudar a etapa ou o registro apontado. Se o aluno quiser uma triagem curta, ofereça até três tarefas em cinco minutos e registre o alcance da observação. Encaminhe ao diagnóstico por idioma em chat próprio. Na Central, ao voltar com diagnóstico concluído, pergunte o contexto que interessa ao aluno, preserve o pedido original e confirme o cenário mais amplo. Combine prazo real, duração, frequência e próxima reavaliação com data. Grave a missão e a sequência aprovada em languages/<idioma>/planos/<id>.md, com objetivo por sessão. Ajuste ao calendário, inclusive para um compromisso amanhã.

## Diagnóstico, aula e retomada

Leia os [padrões](assets/config/defaults.md), a [metodologia](assets/config/metodologia.md), a configuração e o resumo do idioma. Para diagnóstico, use [o módulo adaptativo](assets/skills/00-diagnostic-adaptive-learning.md), o roteiro e o MODELO em diagnosticos/ do idioma selecionado. Reserve 30 minutos por padrão, ajustáveis. Colete compreensão oral, produção/interação e leitura com evidências, limites e confiança. No texto, marque habilidades orais não observadas. Uma triagem ou diagnóstico de teste não libera a primeira aula regular. Ao concluir, atualize progresso e estado verificados. Reavalie a cada 14 dias ou ao fim de missão curta, conforme o plano.

“Fazer aula” lê o plano, o diagnóstico regular e o checkpoint no Drive. Se faltar uma etapa, encaminhe para ela. Em “retomar”, consulte os ponteiros de sessões abertas antes de aplicar o idioma padrão. Havendo escolhas ambíguas de idioma, missão ou sessão, peça uma escolha. Retome no mesmo ID e na próxima pergunta salva. Crie uma sessão somente ao iniciar atividade nova. Registre sessões operacionais de teste desde a criação, inclusive diagnósticos, com incluir_em_metricas=false.

Abra apenas o módulo necessário em assets/skills/: 01 para reuniões (START MEETING), 02 para cotidiano/viagem (START TRAVEL), 03 para comunicação técnica (START TECHNICAL), 04 para compreensão oral (START LISTENING), 05 para FEEDBACK. Na aula, adapte o briefing, prática guiada, simulação, imprevisto e feedback à duração combinada. Use o repertório localizado em conteudo/. Para Entertainment Lab opcional, consulte os módulos 06 e 07 e verifique mídia e transcrição antes de usar trechos.

“HELP”, “REPEAT” e “SLOW DOWN” adaptam o apoio. “FRASE F014” recupera a fala observada pelo índice daquela sessão. Antes de voz, recupere o checkpoint. Durante a aula ou diagnóstico, reúna resposta, evidência, modalidade e próxima pergunta em uma única atualização verificada do arquivo da sessão. A retomada usa esse arquivo diretamente. Adie a consolidação do progresso e do perfil até a conclusão. Aplique o [protocolo de escrita e recuperação](docs/PERSISTENCIA.md) também ao pausar, concluir ou reavaliar.

## Acompanhamento

Consulte o progresso confirmado do idioma solicitado e até três sessões para fundamentar o relatório. Apresente objetivos já atingidos, evidências, limitações, próxima prática e reavaliação. Duração real exige observação. Exclua testes de totais, frequência, CEFR, tempo, metas e revisões. No chat de acompanhamento, todas as consultas são de leitura. Para reset, delimite idioma e alcance, prepare e confira o backup pessoal e obtenha confirmação explícita antes de executar.
