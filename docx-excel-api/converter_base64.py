"""
Conversão: percorre as pastas geradas por automacao.py em ordem de criação,
converte o .docx e o .xlsx de cada uma para Base64 e salva dois arquivos
separados dentro da mesma pasta:

  <nome_do_docx>Base64.txt
  <nome_do_xlsx>Base64.txt

Esses arquivos serão lidos por enviar.py para montar o payload da API.

Uso:
    python converter_base64.py
"""

import os
import base64
import logging
from pathlib import Path

from config import CONFIG

# ─── LOGGING ─────────────────────────────────────────────────────────────────

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/base64.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─── FUNÇÕES ─────────────────────────────────────────────────────────────────

def listar_pastas_em_ordem(pasta_saida: str) -> list[Path]:
    """Retorna subpastas ordenadas por data de criação (mais antiga primeiro)."""
    raiz = Path(pasta_saida)
    if not raiz.exists():
        return []
    pastas = [p for p in raiz.iterdir() if p.is_dir()]
    pastas.sort(key=lambda p: p.stat().st_ctime)
    return pastas


def arquivo_para_base64(caminho: Path) -> str:
    """Lê um arquivo binário e retorna sua representação Base64 como string."""
    return base64.b64encode(caminho.read_bytes()).decode("utf-8")


def salvar_base64_separados(
    pasta: Path,
    docx: Path,
    b64_docx: str,
    xlsx: Path,
    b64_xlsx: str,
) -> tuple[Path, Path]:
    """
    Salva dois arquivos .txt separados com o Base64 de cada arquivo.
    Nomes gerados:
      <nome_do_docx>Base64.txt
      <nome_do_xlsx>Base64.txt
    """
    destino_docx = pasta / f"{docx.stem}Base64.txt"
    destino_xlsx = pasta / f"{xlsx.stem}Base64.txt"

    destino_docx.write_text(b64_docx, encoding="utf-8")
    destino_xlsx.write_text(b64_xlsx, encoding="utf-8")

    return destino_docx, destino_xlsx


# ─── FLUXO PRINCIPAL ─────────────────────────────────────────────────────────

def main():
    cfg = CONFIG

    pastas = listar_pastas_em_ordem(cfg["pasta_saida"])

    if not pastas:
        log.error(f"Nenhuma pasta encontrada em '{cfg['pasta_saida']}'. Execute automacao.py primeiro.")
        return

    log.info(f"{'='*60}")
    log.info(f"Convertendo {len(pastas)} pasta(s) para Base64.")
    log.info(f"{'='*60}")

    resultados = {"sucesso": [], "incompleta": []}

    for i, pasta in enumerate(pastas, start=1):
        log.info(f"\n[{i}/{len(pastas)}] {pasta.name}")

        docx = next(pasta.glob("*.docx"), None)
        xlsx = next(pasta.glob("*_filtrado.xlsx"), None)

        if not docx:
            log.warning(f"  .docx não encontrado. Pulando.")
            resultados["incompleta"].append(pasta.name)
            continue

        if not xlsx:
            log.warning(f"  .xlsx não encontrado. Pulando.")
            resultados["incompleta"].append(pasta.name)
            continue

        # Converte para Base64
        log.info(f"  Convertendo {docx.name} ...")
        b64_docx = arquivo_para_base64(docx)

        log.info(f"  Convertendo {xlsx.name} ...")
        b64_xlsx = arquivo_para_base64(xlsx)

        # Salva arquivos separados
        dest_docx, dest_xlsx = salvar_base64_separados(pasta, docx, b64_docx, xlsx, b64_xlsx)
        log.info(f"  ✅ {dest_docx.name} salvo → {dest_docx}")
        log.info(f"  ✅ {dest_xlsx.name} salvo → {dest_xlsx}")

        resultados["sucesso"].append(pasta.name)

    # ── Relatório final ───────────────────────────────────────────────────────
    log.info(f"\n{'='*60}")
    log.info("RELATÓRIO FINAL")
    log.info(f"  ✅ Convertidos:   {len(resultados['sucesso'])} pasta(s)")
    log.info(f"  ⚠️  Incompletas:   {len(resultados['incompleta'])} pasta(s)")

    if resultados["incompleta"]:
        log.info("  Pastas com problema:")
        for nome in resultados["incompleta"]:
            log.info(f"    - {nome}")

    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()
