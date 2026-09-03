import re


def _quebrar_longo(texto: str, tamanho: int, sobreposicao: int) -> list[str]:
    """PDF sem linha em branco vira um parágrafo gigante"""
    passo = tamanho - sobreposicao
    return [texto[i : i + tamanho] for i in range(0, len(texto), passo)]


def dividir(texto: str, tamanho: int = 800, sobreposicao: int = 100) -> list[str]:
    """divide o texto em pedaços que caibam na janela do modelo de embeddings. 
    corta por parágrafo, não por posição fixa!!!"""
    blocos: list[str] = []
    for paragrafo in re.split(r"\n\s*\n", texto):
        paragrafo = paragrafo.strip()
        if not paragrafo:
            continue
        if len(paragrafo) > tamanho:
            blocos.extend(_quebrar_longo(paragrafo, tamanho, sobreposicao))
        else:
            blocos.append(paragrafo)

    chunks: list[str] = []
    atual = ""
    for bloco in blocos:
        if atual and len(atual) + len(bloco) + 2 > tamanho:
            chunks.append(atual)
            atual = bloco
        else:
            atual = f"{atual}\n\n{bloco}" if atual else bloco
    if atual:
        chunks.append(atual)
    return chunks
