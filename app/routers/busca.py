import asyncio
import uuid as _uuid

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.db.models import Chunk
from app.deps import SessionDep, es
from app.pipeline.embed import embutir_consulta
from app.pipeline.index import INDICE

router = APIRouter(tags=["busca"])

K_RRF = 60 
CANDIDATOS = 50


@router.get("/busca")
async def buscar(session: SessionDep, q: str = Query(min_length=2), limite: int = 10):
    #bm25 no elasticsearch
    resposta = await es.search(
        index=INDICE, query={"match": {"texto": q}}, size=CANDIDATOS
    )
    lexical = [h["_source"]["chunk_id"] for h in resposta["hits"]["hits"]]

    #knn no pgvector
    vetor = await asyncio.to_thread(embutir_consulta, q)
    stmt = (
        select(Chunk.id)
        .order_by(Chunk.embedding.cosine_distance(vetor))
        .limit(CANDIDATOS)
    )
    semantica = [str(cid) for cid in (await session.scalars(stmt)).all()]

    # rrf !
    scores: dict[str, float] = {}
    for lista in (lexical, semantica):
        for posicao, cid in enumerate(lista, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1 / (K_RRF + posicao)

    melhores = sorted(scores, key=lambda c: scores[c], reverse=True)[:limite]
    if not melhores:
        return {"consulta": q, "resultados": []}


    linhas = (
        await session.scalars(
            select(Chunk).where(Chunk.id.in_([_uuid.UUID(c) for c in melhores]))
        )
    ).all()
    por_id = {str(c.id): c for c in linhas}

    return {
        "consulta": q,
        "resultados": [
            {
                "chunk_id": cid,
                "documento_id": str(por_id[cid].documento_id),
                "ordem": por_id[cid].ordem,
                "score": round(scores[cid], 5),
                "texto": por_id[cid].texto,
            }
            for cid in melhores
            if cid in por_id
        ],
    }
