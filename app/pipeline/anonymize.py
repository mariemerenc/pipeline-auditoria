import re
from dataclasses import dataclass

CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")


@dataclass(frozen=True)
class Ocorrencia:
    inicio: int
    fim: int
    tipo: str #cpf cnpj pessoa etc
    texto: str
    prioridade: int #0=regex, 1=ner


def cpf_valido(d: str) -> bool:
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(x) * (tamanho + 1 - i) for i, x in enumerate(d[:tamanho]))
        if (soma * 10) % 11 % 10 != int(d[tamanho]):
            return False
    return True


def cnpj_valido(d: str) -> bool:
    if len(d) != 14 or len(set(d)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, *pesos1]
    for pesos, pos in ((pesos1, 12), (pesos2, 13)):
        resto = sum(int(x) * p for x, p in zip(d[:pos], pesos)) % 11
        dv = 0 if resto < 2 else 11 - resto
        if dv != int(d[pos]):
            return False
    return True


def _parece_nome(texto: str) -> bool:
    partes = texto.split()
    return len(partes) >= 2 and partes[0].isalpha and partes[0][:1].isupper()


def _por_regex(texto: str) -> list[Ocorrencia]:
    achados: list[Ocorrencia] = []
    for padrao, tipo, valida in (
        (CNPJ_RE, "CNPJ", cnpj_valido),
        (CPF_RE, "CPF", cpf_valido),
    ):
        for m in padrao.finditer(texto):
            digitos = re.sub(r"\D", "", m.group())
            if valida(digitos):
                achados.append(Ocorrencia(m.start(), m.end(), tipo, m.group(), 0))
    return achados


def _por_ner(texto: str, nlp) -> list[Ocorrencia]:
    doc = nlp(texto)
    return [
        Ocorrencia(e.start_char, e.end_char, "PESSOA", e.text, prioridade=1)
        for e in doc.ents
        if e.label_ == "PER" and _parece_nome(e.text)
    ]


def _sem_sobreposicao(ocorrencias: list[Ocorrencia]) -> list[Ocorrencia]:
    aceitas: list[Ocorrencia] = []
    for oc in sorted(ocorrencias, key=lambda o: (o.prioridade, o.inicio)):
        if any(oc.inicio < a.fim and a.inicio < oc.fim for a in aceitas):
            continue
        aceitas.append(oc)
    return aceitas


def anonimizar(texto: str, nlp) -> tuple[str, dict[str, str]]:
    ocorrencias = _sem_sobreposicao([*_por_regex(texto), *_por_ner(texto, nlp)])
    mapa: dict[str, str] = {} 
    conts: dict[str, int] = {}

    #atribuiçao dos rotulos
    for oc in sorted(ocorrencias, key=lambda o: o.inicio):
        chave = f"{oc.tipo}:{oc.texto.lower().strip()}"
        if chave not in mapa:
            conts[oc.tipo] = conts.get(oc.tipo, 0)+1
            mapa[chave] = f"[{oc.tipo}_{conts[oc.tipo]}]"

    #substituicao
    for oc in sorted(ocorrencias, key=lambda o: o.inicio, reverse=True):
        rotulo = mapa[f"{oc.tipo}:{oc.texto.lower().strip()}"]
        texto = texto[: oc.inicio] + rotulo + texto[oc.fim :]


    return texto, mapa