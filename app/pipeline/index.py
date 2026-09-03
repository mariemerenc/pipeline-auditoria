from elasticsearch import AsyncElasticsearch

INDICE = "chunks"

MAPPING = {
    "properties": {
        "documento_id": {"type": "keyword"},
        "chunk_id": {"type": "keyword"},
        "ordem": {"type": "integer"},
        "texto": {"type": "text", "analyzer": "brazilian"},
    }
}


async def garantir_indice(es: AsyncElasticsearch) -> None:
    if not await es.indices.exists(index=INDICE):
        await es.indices.create(index=INDICE, mappings=MAPPING)



async def indexar(es: AsyncElasticsearch, documento_id, chunks) -> None:
    operacoes = []
    
    for c in chunks:
        operacoes.append({"index": {"_index": INDICE, "_id": str(c.id)}})
        operacoes.append(
            {
                "documento_id": str(documento_id),
                "chunk_id": str(c.id),
                "ordem": c.ordem,
                "texto": c.texto,
            }
        )
    if operacoes:
        await es.bulk(operations=operacoes, refresh=True)