"""
Configurações da automação.
Edite este arquivo antes de executar o projeto.
"""

CONFIG = {
    # ── Etapa 1: automacao.py ─────────────────────────────────────────────────

    # Pasta que contém os arquivos .docx a serem processados
    "pasta_docx": r"C:\Users\rpsilva20\OneDrive - Stefanini\Área de Trabalho\Bdpds (1)",

    # Caminho completo da planilha Excel de referência
    "planilha": r"C:\Users\rpsilva20\OneDrive - Stefanini\Área de Trabalho\POTENCIAL AGRO - Lista de GAPs (2) 1.xlsx",

    # Índice da aba da planilha (0 = primeira aba, 1 = segunda, etc.)
    "aba_planilha": 0,

    # Índice da coluna a filtrar (0=A, 1=B, ..., 8=I, 9=J ...)
    "coluna_filtro_indice": 8,  # coluna I

    # Pasta raiz onde serão criados os subdiretórios de saída
    "pasta_saida": "saida",

    # ── Etapas 2 e 3: converter_base64.py / enviar.py ────────────────────────

    # URL do endpoint da API
    "api_url":  "https://d192j9eqnpou3o.cloudfront.net/ef/v1/gerar-ef",

    # Headers HTTP adicionais (autenticação, etc.)
    "api_headers": {
        # "Authorization": "Bearer SEU_TOKEN",
        # "x-api-key": "SUA_CHAVE_AQUI",
    },

    # Campos do payload
    "email_destinatario": "rpsilva20@stefanini.com",
    "cod_cliente":        "003",
    "str_idioma":         "pt-BR",

    # Comportamento de retry
    "retry_espera":   5,   # segundos entre tentativas
    "max_tentativas": 3,   # tentativas antes de pular para a próxima pasta
}
