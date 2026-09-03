import asyncio
import uuid

from app.config import settings
from app.db.models import Chunk, Documento, StatusDocumento
from app.deps import SessionLocal, es, nlp
from app.pipeline.anonymize import anonimizar
from app.pipeline.chunk import dividir
from app.pipeline.embed import embutir_passagens
from app.pipeline.entities import extrair_entidades
from app.pipeline.extract import extrair_texto
from app.pipeline.index import indexar


async def processar_documento(doc_id: uuid.UUID) -> None:
    # processando (na teoria)
    async with SessionLocal() as session:
        doc = await session.get(Documento, doc_id)

        if doc is None:
            return
        caminho = doc.caminho_arquivo
        doc.status = StatusDocumento.PROCESSANDO
        await session.commit()

    # processamento (na prática)
    try:
        texto_bruto = await asyncio.to_thread(extrair_texto, caminho)
        entidades = extrair_entidades(texto_bruto)
        texto, _mapa = await asyncio.to_thread(anonimizar, texto_bruto, nlp)
        # os chunks guardam o texto já anonimizado
        pedacos = dividir(texto, settings.chunk_tam, settings.chunk_sobrepos)
        vetores = await asyncio.to_thread(embutir_passagens, pedacos)
        status_fim, erro = StatusDocumento.CONCLUIDO, None

    except Exception as e: 
        texto, entidades = None, None
        pedacos, vetores = [], []
        status_fim, erro = StatusDocumento.ERRO, str(e)

    # salvando resultado
    async with SessionLocal() as session:
        doc = await session.get(Documento, doc_id)
        doc.status = status_fim
        doc.erro = erro
        doc.texto = texto
        doc.entidades = entidades

        chunks = [
            Chunk(documento_id=doc_id, ordem=i, texto=t, embedding=v)
            for i, (t,v) in enumerate(zip(pedacos, vetores, strict=True))
        ]

        session.add_all(chunks)
        await session.commit()

    if chunks:
        await indexar(es, doc_id, chunks)
