# Adaptador: pasta local

Use este guia quando as [regras de seleção](../PERSISTENCIA.md#escolher-o-adaptador) apontarem uma pasta local. Ele serve para qualquer agente com acesso a arquivos: Claude Code, o app do Claude com uma pasta conectada, o Codex na linha de comando ou outro ambiente com leitura e escrita em disco. O protocolo geral continua em [PERSISTENCIA.md](../PERSISTENCIA.md).

## Verificar a capacidade

A pasta precisa pertencer ao aluno e continuar existindo depois do chat. Confirme com o aluno o caminho completo. Não use diretórios temporários, a área de trabalho efêmera da sessão nem a própria pasta da skill. Se a sessão só consegue ler a pasta, use o modo manual.

Identificadores: o caminho relativo à raiz, com `/` como separador (por exemplo `languages/english/estado/sessao-ativa.md`). Ele substitui o ID do Drive em todos os registros e índices.

## Identificar a raiz

Use a pasta dedicada indicada pelo aluno. Se ele indicar só um pai, crie ou reutilize uma única subpasta EverydayEssentials. Recuse links simbólicos e caminhos dentro da pasta da skill.

## Provisionar

Com Python disponível, execute a partir da pasta da skill:

```
python scripts/provision.py --local CAMINHO_DA_RAIZ en-US es-ES
```

O script cria somente o que falta, pais antes dos filhos, e nunca sobrescreve um arquivo existente. Ele para com erro se encontrar um tipo inesperado (arquivo onde se espera pasta, ou o contrário), um link simbólico ou uma raiz dentro da pasta da skill. A saída JSON lista `created`, `existing` e o índice `ids` (caminho → caminho). Pode ser executado de novo após interrupção ou para adicionar idiomas.

Sem Python, crie a mesma árvore com as ferramentas de arquivo da sessão, copiando assets/config e assets/languages dos idiomas escolhidos e criando a subpasta planos de cada idioma. Antes de criar cada item, confira se ele já existe.

Depois, abra alguns arquivos criados e compare com os modelos em assets/ para confirmar que a cópia é fiel.

## Gravar e reler

Atualize o arquivo no próprio caminho, preservando o que não mudou. Depois releia o arquivo e compare revisão, operação, evidências e próxima pergunta. Se a releitura divergir, não anuncie o salvamento: aplique o reparo do protocolo geral.

Não há trava entre processos. Mantenha um único chat escritor por sessão. Se a pasta estiver sincronizada por um serviço de nuvem, espere a sincronização terminar antes de retomar em outro dispositivo e trate cópias de conflito criadas pelo serviço como homônimos: pare e peça ao aluno para identificar a versão correta.
