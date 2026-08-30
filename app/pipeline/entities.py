import re

PADROES = {
    "LEGISLACAO": [
        re.compile(
            r"(?i)\b(?:lei|decreto|medida provisória|instrução normativa|portaria|resolução)"
            r"(?:\s+complementar)?\s+n?[º°.]?\s*\d[\d.]*(?:/\d{2,4})?"
        ),
        re.compile(
            r"(?i)\bart(?:igo)?\.?\s*\d+[º°]?"
            r"(?:\s*,\s*(?:caput|§\s*\d+|inciso\s+[IVXL]+|alínea\s+\w))?"
        ),
    ],
    "JURISPRUDENCIA": [
        re.compile(r"(?i)\bac[óo]rd[ãa]o\s+n?[º°]?\s*\d+/\d{4}(?:\s*-\s*TCU[\w-]*)?"),
        re.compile(r"(?i)\bs[úu]mula\s+(?:vinculante\s+)?n?[º°]?\s*\d+"),
    ],
    "VALOR": [re.compile(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}")],
}


def extrair_entidades(texto: str) -> dict[str, list[str]]:
    """Extrai entidades jurídicas e orçamentárias (sem anonimizar)"""
    encontrados: dict[str, list[str]] = {}
    for tipo, padroes in PADROES.items(): # p cada tipo
        vistos: list[str] = [] 
        for padrao in padroes: # p cada regex do tipo
            for m in padrao.finditer(texto): # p cada ocorrencia
                valor = " ".join(m.group().split())
                if valor not in vistos:
                    vistos.append(valor)
        if vistos:
            encontrados[tipo] = vistos
    return encontrados


def valor_p_float(valor: str) -> float:
    """'R$ 1.250.000,00' -> 1250000.0 """
    return float(valor.replace("R$", "").strip().replace(".", "").replace(",", "."))
