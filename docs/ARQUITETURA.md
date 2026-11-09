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

Na Central, o aluno escolhe Google Drive e uma pasta pessoal. A configuração só termina após uma gravação de teste seguida de leitura. O aluno informa o idioma e seu objetivo. Em um novo chat, pede o diagnóstico. A Skill localiza o perfil, conduz a atividade e registra a próxima etapa. Quando o aluno volta pelo celular e diz “quero continuar”, o novo chat recupera a missão e o ponto de pausa.

O Google Drive é o destino preferencial. O OneDrive é uma alternativa a validar. Uma pasta local atende a testes no computador com acesso a ela. Retomar em outro aparelho exige que ele consiga ler o mesmo registro atualizado.

## Portabilidade

Planejar um núcleo comum para ChatGPT, Claude e Gemini. Separar permissões de arquivos, voz e execução de scripts por ambiente. Cada integração só entra no guia de uso depois de um teste reproduzível. O formato final de instalação e o mecanismo de identificação do espaço do aluno permanecem em aberto.
