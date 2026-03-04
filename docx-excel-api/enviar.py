"""
Envio: lê as pastas geradas em ordem de criação, carrega os arquivos Base64
de cada uma e envia para a API via POST JSON.

Payload enviado:
  {
    "bpd_base64":         <base64 do .docx>,
    "bpd_file_extension": "docx",
    "gap_file_base64":    <base64 do .xlsx>,
    "gap_file_extension": "xlsx",
    "str_idioma":         <definido em config.py>,
    "email_destinatario": <definido em config.py>,
    "cod_cliente":        <definido em config.py>
  }

Só avança para a próxima pasta após receber status 200.

Uso:
    python enviar.py

Pré-requisito: execute automacao.py e converter_base64.py antes.
"""

import os
import time
import logging
import requests
from pathlib import Path

from config import CONFIG

# ─── LOGGING ─────────────────────────────────────────────────────────────────

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/envio.log", encoding="utf-8"),
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


def ler_base64_da_pasta(pasta: Path) -> tuple[str | None, str | None]:
    """
    Localiza os dois arquivos *Base64.txt na pasta e lê seus conteúdos.
    Retorna (b64_docx, b64_xlsx) ou None em cada posição se não encontrado.
    """
    docx_orig = next(pasta.glob("*.docx"), None)
    xlsx_orig = next(pasta.glob("*_filtrado.xlsx"), None)

    if not docx_orig or not xlsx_orig:
        return None, None

    txt_docx = pasta / f"{docx_orig.stem}Base64.txt"
    txt_xlsx = pasta / f"{xlsx_orig.stem}Base64.txt"

    if not txt_docx.exists():
        log.warning(f"  Arquivo não encontrado: {txt_docx.name}")
        return None, None

    if not txt_xlsx.exists():
        log.warning(f"  Arquivo não encontrado: {txt_xlsx.name}")
        return None, None

    return (
        txt_docx.read_text(encoding="utf-8").strip(),
        txt_xlsx.read_text(encoding="utf-8").strip(),
    )


def enviar(
    api_url: str,
    headers: dict,
    b64_docx: str,
    b64_xlsx: str,
    idioma: str,
    email_destinatario: str,
    cod_cliente: str,
    max_tentativas: int,
    retry_espera: int,
) -> bool:
    """
    Envia o payload para a API via POST JSON.
    Retorna True ao receber status 200, False após esgotar as tentativas.
    """
    payload = {
        "bpd_base64":         b64_docx,
        "bpd_file_extension": "docx",
        "gap_file_base64":    b64_xlsx,
        "gap_file_extension": "xlsx",
        "str_idioma":         idioma,
        "email_destinatario": email_destinatario,
        "cod_cliente":        cod_cliente,
        "img_files_base64_list": [],  # campo obrigatório, mas vazio neste contexto
       " transcriptions_base64_list": [],  # campo obrigatório, mas vazio neste contexto
        "transcriptions_base64_extension": "",
        "filename": "SLA.b64_docx"
#     "bpd_base64": "UEsDBBQABgAIAAAAIQ...",
#   "bpd_file_extension": "docx",
#   "gap_file_base64": "eGxz...",
#   "gap_file_extension": "xlsx",
#   "img_files_base64_list": [
#     "iVBORw0KGgoAAAANSUhEUg...",
#     "R0lGODlhAQABAIAAAAAAAP..."
#   ],
#   "transcriptions_base64_list": [
#     {
#       "filename": "reuniao_kickoff.docx",
#       "content_base64": "UEsDBBQABgAIAAAAIQ..."
#     }
#   ],
#   "transcriptions_base64_extension": "docx",
#   "str_idioma": "pt-BR",
#   "email_destinatario": "cliente.final@example.com",
#   "cod_cliente": "stf_internal"
     }






    for tentativa in range(1, max_tentativas + 1):
        try:
            log.info(f"  Tentativa {tentativa}/{max_tentativas}...")

            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json", **headers},
                json=payload,
                timeout=60,
            )

            log.info(f"  Status: {response.status_code}")

            if response.status_code == 202:
                log.info("  ✅ Enviado com sucesso.")
                return True
            else:
                log.warning(f"  ⚠️  Resposta inesperada: {response.status_code} | {response.text[:300]}")

        except requests.exceptions.RequestException as e:
            log.error(f"  ❌ Erro na requisição: {e}")

        if tentativa < max_tentativas:
            log.info(f"  Aguardando {retry_espera}s...")
            time.sleep(retry_espera)

    log.error(f"  ❌ Falha após {max_tentativas} tentativa(s).")
    return False


# ─── FLUXO PRINCIPAL ─────────────────────────────────────────────────────────

def main():
    cfg = CONFIG

    pastas = listar_pastas_em_ordem(cfg["pasta_saida"])

    if not pastas:
        log.error(f"Nenhuma pasta encontrada em '{cfg['pasta_saida']}'. Execute automacao.py primeiro.")
        return

    log.info(f"{'='*60}")
    log.info(f"Iniciando envio: {len(pastas)} pasta(s) encontrada(s).")
    log.info(f"E-mail destinatário: {cfg['email_destinatario']}")
    log.info(f"Código cliente:      {cfg['cod_cliente']}")
    log.info(f"Idioma:              {cfg['str_idioma']}")
    log.info(f"{'='*60}")

    resultados = {"sucesso": [], "falha": [], "sem_base64": []}

    for i, pasta in enumerate(pastas, start=1):
        log.info(f"\n[{i}/{len(pastas)}] {pasta.name}")

        b64_docx, b64_xlsx = ler_base64_da_pasta(pasta)

        if not b64_docx or not b64_xlsx:
            log.warning(f"  Arquivos Base64 ausentes. Execute converter_base64.py primeiro. Pulando.")
            resultados["sem_base64"].append(pasta.name)
            continue

        log.info(f"  Arquivos Base64 lidos.")

        sucesso = enviar(
            api_url=cfg["api_url"],
            headers=cfg["api_headers"],
            b64_docx=b64_docx,
            b64_xlsx=b64_xlsx,
            idioma=cfg["str_idioma"],
            email_destinatario=cfg["email_destinatario"],
            cod_cliente=cfg["cod_cliente"],
            max_tentativas=cfg["max_tentativas"],
            retry_espera=cfg["retry_espera"],
        )

        if sucesso:
            resultados["sucesso"].append(pasta.name)
        else:
            resultados["falha"].append(pasta.name)

    # ── Relatório final ───────────────────────────────────────────────────────
    log.info(f"\n{'='*60}")
    log.info("RELATÓRIO FINAL")
    log.info(f"  ✅ Enviados:        {len(resultados['sucesso'])} pasta(s)")
    log.info(f"  ❌ Falha no envio:  {len(resultados['falha'])} pasta(s)")
    log.info(f"  ⚠️  Sem Base64:      {len(resultados['sem_base64'])} pasta(s)")

    for categoria, itens in resultados.items():
        if itens and categoria != "sucesso":
            label = {"falha": "Falhas", "sem_base64": "Sem Base64"}[categoria]
            log.info(f"\n  {label}:")
            for nome in itens:
                log.info(f"    - {nome}")

    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()
