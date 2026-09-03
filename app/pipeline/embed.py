from sentence_transformers import SentenceTransformer

from app.config import settings

_modelo = SentenceTransformer(settings.embedding_model)

# a família e5 foi treinada com "passage: " no que é indexado e 
# "query: " no que é buscado. sem eles o modelo ainda devolve
# vetores (piores!) e por isso o prefixo fica encapsulado nestas duas funções.


def embutir_passagens(textos: list[str]) -> list[list[float]]:
    vetores = _modelo.encode(
        [f"passage: {t}" for t in textos], normalize_embeddings=True
    )
    return [v.tolist() for v in vetores]


def embutir_consulta(texto: str) -> list[float]:
    return _modelo.encode(f"query: {texto}", normalize_embeddings=True).tolist()
