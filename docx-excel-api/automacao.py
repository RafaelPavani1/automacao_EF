"""
Automação: lê arquivos .docx em sequência, filtra planilha Excel pela coluna I
com os números extraídos do nome de cada arquivo e organiza a saída em pastas.

Para cada .docx é criado um diretório em saida/ contendo:
  - o arquivo .docx original
  - a planilha .xlsx com as linhas filtradas

Uso:
    python automacao.py

Configuração: edite o arquivo config.py antes de executar.
"""

import os
import re
import shutil
import logging
import pandas as pd
from pathlib import Path

from config import CONFIG

# ─── LOGGING ─────────────────────────────────────────────────────────────────

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/automacao.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─── FUNÇÕES ─────────────────────────────────────────────────────────────────

def extrair_numeros(nome_arquivo: str) -> str:
    """Extrai apenas os dígitos do nome do arquivo (sem extensão)."""
    return re.sub(r"\D", "", Path(nome_arquivo).stem)


def carregar_planilha(caminho: str, aba) -> pd.DataFrame:
    """Carrega a planilha Excel inteira como string para evitar perda de zeros à esquerda."""
    df = pd.read_excel(caminho, sheet_name=aba, dtype=str)
    log.info(f"Planilha carregada: {len(df)} linhas | {len(df.columns)} colunas.")
    return df


def filtrar_linhas(df: pd.DataFrame, coluna_indice: int, valor: str) -> pd.DataFrame:
    """
    Retorna todas as linhas onde a coluna contém o valor (match parcial).
    Ex: valor '123' dá match em '123', 'ABC123', '123-XYZ', etc.
    """
    nome_coluna = df.columns[coluna_indice]
    resultado = df[df[nome_coluna].astype(str).str.contains(valor, case=False, na=False)].copy()
    log.info(f"  Coluna '{nome_coluna}' contém '{valor}' → {len(resultado)} linha(s) encontrada(s).")
    return resultado


def preparar_saida(pasta_saida: str, nome_base: str, caminho_docx_original: str, df_filtrado: pd.DataFrame):
    """
    Cria o diretório de saída com o nome do docx e salva dentro dele:
      - o arquivo .docx original
      - a planilha .xlsx filtrada
    """
    diretorio = os.path.join(pasta_saida, nome_base)
    os.makedirs(diretorio, exist_ok=True)

    # Copia o .docx original
    destino_docx = os.path.join(diretorio, Path(caminho_docx_original).name)
    shutil.copy2(caminho_docx_original, destino_docx)
    log.info(f"  .docx copiado  → {destino_docx}")

    # Salva a planilha filtrada
    destino_xlsx = os.path.join(diretorio, f"{nome_base}_filtrado.xlsx")
    df_filtrado.to_excel(destino_xlsx, index=False)
    log.info(f"  .xlsx gerado   → {destino_xlsx}")

    return diretorio


# ─── FLUXO PRINCIPAL ─────────────────────────────────────────────────────────

def main():
    cfg = CONFIG

    pasta = Path(cfg["pasta_docx"])
    arquivos_docx = sorted(pasta.glob("*.docx"))

    if not arquivos_docx:
        log.error(f"Nenhum arquivo .docx encontrado em: {pasta}")
        return

    log.info(f"{'='*60}")
    log.info(f"Iniciando: {len(arquivos_docx)} arquivo(s) encontrado(s).")
    log.info(f"{'='*60}")

    df_planilha = carregar_planilha(cfg["planilha"], cfg["aba_planilha"])
    resultados = {"sucesso": [], "sem_dados": []}

    for i, caminho_docx in enumerate(arquivos_docx, start=1):
        nome_arquivo = caminho_docx.name
        log.info(f"\n[{i}/{len(arquivos_docx)}] {nome_arquivo}")

        # 1. Extrai números do nome do arquivo
        numeros = extrair_numeros(nome_arquivo)
        if not numeros:
            log.warning(f"  Nenhum número encontrado em '{nome_arquivo}'. Pulando.")
            resultados["sem_dados"].append(nome_arquivo)
            continue

        log.info(f"  Números extraídos: {numeros}")

        # 2. Filtra a planilha pela coluna I
        df_filtrado = filtrar_linhas(df_planilha, cfg["coluna_filtro_indice"], numeros)

        if df_filtrado.empty:
            log.warning(f"  Nenhuma correspondência na planilha para '{numeros}'. Pulando.")
            resultados["sem_dados"].append(nome_arquivo)
            continue

        # 3. Cria pasta de saída e salva os arquivos
        nome_base = caminho_docx.stem
        diretorio = preparar_saida(cfg["pasta_saida"], nome_base, str(caminho_docx), df_filtrado)

        log.info(f"  ✅ Pasta gerada: {diretorio}")
        resultados["sucesso"].append(nome_arquivo)

    # ── Relatório final ───────────────────────────────────────────────────────
    log.info(f"\n{'='*60}")
    log.info("RELATÓRIO FINAL")
    log.info(f"  ✅ Processados:      {len(resultados['sucesso'])} arquivo(s)")
    log.info(f"  ⚠️  Sem correspondência: {len(resultados['sem_dados'])} arquivo(s)")

    if resultados["sem_dados"]:
        log.info("  Arquivos sem dados:")
        for f in resultados["sem_dados"]:
            log.info(f"    - {f}")

    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()
