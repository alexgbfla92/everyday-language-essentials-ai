# Adaptador: OneDrive

Use este guia quando a Central estiver no OneDrive. O protocolo geral continua em [PERSISTENCIA.md](../PERSISTENCIA.md).

## Pasta sincronizada no computador (recomendado)

Se a pasta do OneDrive está sincronizada no computador do aluno e a sessão consegue ler e gravar nela, use o [adaptador de pasta local](pasta-local.md) com `provedor: onedrive`. Os comandos de pasta local (`scripts/central.py`) funcionam sem mudança. Espere a sincronização terminar antes de retomar em outro dispositivo e trate cópias de conflito criadas pelo OneDrive como homônimos.

Pastas do tipo "somente online" precisam estar disponíveis no dispositivo antes de ler ou gravar; se a leitura de um arquivo falhar, peça ao aluno para marcar a pasta como "Sempre manter neste dispositivo".

## Conector do OneDrive ou SharePoint

Use um conector somente se ele oferecer, na sessão atual, as mesmas quatro ações exigidas pelo [adaptador Drive](drive.md#verificar-a-capacidade): listar filhos diretos, criar pasta num pai, criar arquivo num pai e atualizar o conteúdo de um arquivo pelo ID. Muitos conectores do Microsoft 365 só leem e buscam; nesse caso, use a pasta sincronizada ou o [modo manual](manual.md).

Com um conector capaz, siga os passos de provisionamento, gravação e releitura do [adaptador Drive](drive.md), trocando o tipo de pasta pelo do OneDrive e usando `text/markdown` nos registros. Registre `armazenamento: onedrive` e `provedor: onedrive` no estado global. Identificadores são os IDs de item do OneDrive.
