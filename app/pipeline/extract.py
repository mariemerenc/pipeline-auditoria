from pathlib import Path

import pdfplumber


class PDFSemTexto(Exception):
    """Provavelmente PDF digitalizado"""

def extrair_texto(caminho: Path | str) -> str:
    partes: list[str] = []

    with pdfplumber.open(caminho) as pdf:
        for pg in pdf.pages:
            partes.append(pg.extract_text() or "")

    texto = "\n\n".join(partes).strip()
    if not texto:
        raise PDFSemTexto("Nenhum texto extraído !! Talvez o PDF exija OCR")

    return texto