# Estado global — modelo inicial

esquema: 4
status: nao_configurado
nome_central: null
provedor: null  # local | google-drive | onedrive
armazenamento: null  # pasta-local | drive | onedrive | manual
raiz: null  # caminho local ou ID da pasta no Drive/OneDrive
formato_registros: null  # markdown | nativo (Google Docs/Sheets, só no adaptador Drive)
idioma_padrao: en-US
idiomas_habilitados: [fr-FR, es-ES, en-US]
idiomas_escolhidos_pelo_aluno: []
idioma_de_apoio: pt-BR
contador_frases: {en-US: 0, es-ES: 0, fr-FR: 0}  # último número F usado por idioma; só aumenta, nunca é zerado
contador_dialogos: {en-US: 0, es-ES: 0, fr-FR: 0}  # último número D usado por idioma; só aumenta, nunca é zerado
ids_em_voz: sim  # sim | nao — anunciar os números das frases no modo voz
preferencias_globais_confirmadas_em: null
ultima_verificacao_de_escrita: null
observacao: Preencher somente após configuração real. Não copiar progresso entre usuários. Preferências por idioma ficam em `languages/<idioma>/estado/perfil-atual.md`.

## Índice
| Caminho lógico | ID | Formato |
|---|---|---|
