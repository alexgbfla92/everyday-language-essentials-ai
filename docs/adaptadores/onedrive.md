# Adaptador: OneDrive

Use este guia quando a Central estiver no OneDrive. O protocolo geral continua em [PERSISTENCIA.md](../PERSISTENCIA.md).

## Pasta sincronizada no computador (recomendado)

Se a pasta do OneDrive está sincronizada no computador do aluno e a sessão consegue ler e gravar nela, use o [adaptador de pasta local](pasta-local.md) com `provedor: onedrive`. Os comandos de pasta local (`scripts/central.py`) funcionam sem mudança. Espere a sincronização terminar antes de retomar em outro dispositivo e trate cópias de conflito criadas pelo OneDrive como homônimos.

Pastas do tipo "somente online" precisam estar disponíveis no dispositivo antes de ler ou gravar; se a leitura de um arquivo falhar, peça ao aluno para marcar a pasta como "Sempre manter neste dispositivo".

## Conector do OneDrive ou SharePoint

No OneDrive os registros continuam 100% em Markdown (`formato_registros: markdown`). Use um conector somente se ele oferecer, na sessão atual: listar os filhos diretos de uma pasta, criar pasta num pai, criar arquivo com conteúdo num pai, **regravar o conteúdo de um arquivo existente pelo ID** e mover para a lixeira. Muitos conectores do Microsoft 365 só leem e buscam; nesse caso, use a pasta sincronizada ou o [modo manual](manual.md).

Com um conector capaz, siga a ordem de provisionamento do [planejador](drive.md#provisionar) tratando todo arquivo como `markdown` (MIME `text/markdown`, nome com `.md`), grave atualizando o mesmo ID e releia cada escrita. Registre `armazenamento: onedrive` e `provedor: onedrive` no estado global. Identificadores são os IDs de item do OneDrive.
