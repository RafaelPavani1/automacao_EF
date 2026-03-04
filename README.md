# 📂 docx-excel-api

Automação em Python dividida em **três etapas independentes**:

1. **`automacao.py`** — Lê os `.docx`, filtra a planilha e organiza as pastas de saída
2. **`converter_base64.py`** — Converte o `.docx` e o `.xlsx` de cada pasta para Base64 e salva em `base64.txt`
3. **`enviar.py`** — Lê os `base64.txt` e envia os dados para a API via JSON

---

## 📁 Estrutura do Projeto

```
docx-excel-api/
│
├── automacao.py           # Etapa 1: lê, filtra e organiza as pastas
├── converter_base64.py    # Etapa 2: converte arquivos para Base64
├── enviar.py              # Etapa 3: envia para a API
├── config.py              # Todas as configurações
├── requirements.txt       # Dependências Python
│
├── logs/                  # Criado automaticamente
│   ├── automacao.log
│   ├── base64.log
│   └── envio.log
│
└── saida/                 # Criado automaticamente pela etapa 1
    └── contrato_00123/
        ├── contrato_00123.docx
        ├── contrato_00123_filtrado.xlsx
        └── base64.txt          ← gerado pela etapa 2
```

---

## ⚙️ Etapas

### Etapa 1 — automacao.py
Para cada `.docx` na pasta configurada:
```
Extrai números do nome → filtra coluna I (match parcial)
→ cria pasta saida/nome/ → copia .docx → salva .xlsx filtrado
```

### Etapa 2 — converter_base64.py
Para cada pasta em `saida/`:
```
Lê o .docx e o .xlsx → converte ambos para Base64
→ salva base64.txt com o formato:
    DOCX_BASE64=<valor>
    XLSX_BASE64=<valor>
```

### Etapa 3 — enviar.py
Para cada pasta em `saida/` (ordem de criação):
```
Lê o base64.txt → envia via POST JSON para a API:
    { "docx_base64": "...", "xlsx_base64": "...", "email": "..." }
→ aguarda status 200 antes de avançar
```

---

## 🚀 Como Usar

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Configure o projeto em `config.py`
```python
CONFIG = {
    # Etapa 1
    "pasta_docx":           r"C:\caminho\dos\docx",
    "planilha":             r"C:\caminho\da\planilha.xlsx",
    "aba_planilha":         0,
    "coluna_filtro_indice": 8,          # coluna I
    "pasta_saida":          "saida",

    # Etapas 2 e 3
    "api_url":     "https://sua-api.com/endpoint",
    "api_headers": { "Authorization": "Bearer SEU_TOKEN" },
    "email":          "seuemail@exemplo.com",
    "retry_espera":   5,
    "max_tentativas": 3,
}
```

### 3. Execute as etapas em ordem
```bash
python automacao.py          # gera as pastas com .docx e .xlsx
python converter_base64.py   # gera base64.txt em cada pasta
python enviar.py             # envia para a API
```

> As etapas são independentes — você pode inspecionar os arquivos entre elas.

---

## 📤 Payload enviado para a API

```json
{
  "docx_base64": "<base64 do .docx>",
  "xlsx_base64": "<base64 do .xlsx>",
  "email":       "seuemail@exemplo.com"
}
```

> Se a sua API usar nomes de campo diferentes, edite o dicionário `payload` dentro da função `enviar()` em `enviar.py`.

---

## 🛠️ Dependências

| Biblioteca | Uso                              |
|------------|----------------------------------|
| `pandas`   | Leitura e filtragem da planilha  |
| `openpyxl` | Leitura/escrita de arquivos xlsx |
| `requests` | Envio dos dados para a API       |
