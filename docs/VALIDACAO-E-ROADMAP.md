# Validação do beta

Rode `python -B -m unittest discover -s tests` na raiz. A suíte usa listagens fictícias e testa as operações propostas ao conector. Também cria pastas locais temporárias para testar o modo `--local`: mesma árvore do Drive, cópia fiel dos modelos, repetição sem sobrescrever, conflitos e recusa de links simbólicos e da pasta da skill. Ela não mede confiabilidade de rede nem verifica a interação do modelo com um aluno.

## Aceite em pasta pessoal de ensaio

Repita o roteiro abaixo em cada combinação de plataforma e adaptador que for publicada (por exemplo ChatGPT com Drive, Codex com pasta local, Claude Code com pasta local, app do Claude com pasta conectada). No app do Claude, confira também se o conector Drive da conta cria e atualiza arquivos antes de usar o adaptador Drive; se não, valide o encaminhamento para pasta local ou modo manual.

1. Pelo mecanismo de instalação disponível na conta, invoque a skill sem o clone aberto. Informe um destino vazio. Crie espanhol e inglês. Confira metadados, pais, MIME, bytes, IDs e revisão da configuração após nova leitura.
2. Repita o setup. Compare os IDs. Adicione francês; confira que os dados anteriores continuam íntegros. Em cópia de um beta plano, verifique leitura por ID, migração interrompida e retomada sem duplicação.
3. Peça aula sem diagnóstico e depois com triagem breve. Observe o encaminhamento. Conclua um diagnóstico regular em texto, confira as limitações anotadas e aprove o plano. Faça uma sessão de teste e compare as métricas antes e depois.
4. Pause uma aula após F002. No celular, recupere o mesmo ID, revisão e pergunta. Em voz, confirme o que foi efetivamente observado. Encerre e verifique uma única contribuição ao progresso.
5. Interrompa o acesso após salvar a sessão e antes de atualizar o progresso. Confira o checkpoint, reconcilie pelo ID de operação e valide o reparo. Com um segundo escritor ativo, registre conflitos e suspenda a operação se o conector não oferecer garantias suficientes.
6. Em chat de progresso, compare as evidências de um idioma sem alterar notas. No Lab, teste um vídeo sem transcrição acessível.

Registre interface, versão, data, ações e resultados em ambiente de teste. A publicação e a distribuição em outras contas dependem desse ensaio.

## Latência e recuperação

Em pasta pessoal de ensaio, anote operações e tempo de espera de três turnos comuns antes e depois da mudança, na mesma interface. Durante uma aula aberta, uma resposta que altere o estado deve produzir uma única escrita no arquivo da sessão, com verificação por leitura. Confira pelos IDs que o resumo, o perfil e o índice global não receberam escrita naquele turno. Em outro chat, use o ponteiro existente e confira se a próxima pergunta recuperada corresponde à última resposta confirmada. Interrompa a conclusão depois da fonte e antes do registro 08; ao retomar, verifique reparo, uma única contabilização e encerramento do ponteiro.
