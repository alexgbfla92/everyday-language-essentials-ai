# Arquitetura da Central

O SKILL.md na raiz define a descoberta e encaminha configuração, diagnóstico, aula, retomada ou acompanhamento. A distribuição leva instruções e modelos vazios. O Projeto ou chat guarda uma referência à pasta pessoal. O Drive guarda o que aconteceu com o aluno.

| Camada | Implementação e responsabilidade |
| --- | --- |
| Central | SKILL.md decide a intenção, o idioma e a etapa elegível. |
| Método | assets/config contém padrões e metodologia. assets/skills contém os oito módulos selecionáveis. |
| Recursos por idioma | assets/languages contém exemplos, roteiros e modelos localizados. O aluno pode escolher uma ou várias trilhas. |
| Provisionamento | scripts/provision.py transforma listagens verificadas em operações do conector com pai explícito. Pode ser executado novamente após interrupção. |
| Persistência | docs/PERSISTENCIA.md define leitura e atualização por ID, isolamento, migração e reparação dos registros derivados. |

No Codex, disponibilize a pasta completa como skill no diretório de skills do ambiente. No ChatGPT, disponibilize o mesmo pacote pelo mecanismo de skills habilitado na conta e conecte o Drive. A abertura de um link do GitHub ou a inclusão de uma pasta nas fontes de um Projeto, por si só, não comprova instalação nem capacidade de escrita. Verifique essas capacidades na interface efetivamente usada.

A instalação pública, permissões na conta de um novo aluno, a experiência móvel e voz exigem ensaio de ponta a ponta. A integração usa as ações oferecidas pela conexão do aluno, sem credenciais no repositório.
