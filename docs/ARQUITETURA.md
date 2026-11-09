# Arquitetura da experiência de aprendizagem

## Decisões do planejamento

O aluno escolhe um nome para seu Projeto no ChatGPT. Um chat permanente, a Central de Aprendizagem, orienta o setup, apresenta o progresso e permite gerenciar missões. Cada aula tem seu próprio chat. Se o ambiente exigir que o aluno crie o chat manualmente, a Central indica em qual Projeto abri-lo e qual mensagem enviar.

O GitHub distribui o beta. O Codex é a ferramenta de desenvolvimento. O autor cria a skill e publica suas atualizações no GitHub. Para validar o primeiro percurso, ele assume o papel de novo aluno na própria conta, abre o link da versão publicada e usa o ChatGPT pelo navegador, aplicativo de desktop ou celular. O modo de instalação em cada interface é uma questão aberta.

## Componentes propostos

| Componente | Responsabilidade |
| --- | --- |
| Pacote da Skill | Reunir instruções em SKILL.md, metodologia, modelos vazios e exemplos fictícios sob controle de versão. |
| Projeto do aluno | Organizar os chats e guardar uma referência curta ao espaço de aprendizagem escolhido no setup. |
| Núcleo pedagógico | Interpretar pedidos naturais, conduzir diagnóstico e aulas e gerar evidências de progresso. |
| Camada de armazenamento | Localizar o espaço do aluno, ler e gravar registros, identificar conflitos e conferir o que foi salvo. |
| Integração com o ambiente | Informar que operações de arquivo, interação por voz e autorizações estão disponíveis naquela sessão. |

## Percurso de referência

O aluno começa em um chat pela URL da skill e confirma se o chat está no Projeto. A Central orienta a criação do Projeto e a movimentação desse chat quando necessário. O aluno escolhe onde salvar seus dados e indica a pasta privada do Drive. Vinculá-la às fontes facilita sua localização futura. A Central cria ou localiza o documento permanente Configuração, atualiza o campo de verificação e relê seu valor pelo ID na pasta indicada. Após inicializar os registros, coleta nome, idade e idioma e conduz o diagnóstico geral. Com o resultado salvo, combina contexto, prazo, duração e frequência das aulas e registra o plano e a data de reavaliação. Em outro chat, “fazer aula” consulta os registros para iniciar ou retomar a sessão adequada.

O Google Drive é o destino preferencial. O OneDrive é uma alternativa a validar. Uma pasta local atende a testes no computador com acesso a ela. Retomar em outro aparelho exige que ele consiga ler o mesmo registro atualizado.

## Portabilidade

Planejar um núcleo comum para ChatGPT, Claude e Gemini. Separar permissões de arquivos, voz e execução de scripts por ambiente. Cada integração só entra no guia de uso depois de um teste reproduzível. O formato final de instalação e o mecanismo de identificação do espaço do aluno permanecem em aberto.
