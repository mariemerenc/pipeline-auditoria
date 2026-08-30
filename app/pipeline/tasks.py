import asyncio
import uuid

from app.db.models import Documento, StatusDocumento
from app.deps import SessionLocal, nlp
from app.pipeline.anonymize import anonimizar
from app.pipeline.entities import extrair_entidades
from app.pipeline.extract import extrair_texto


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
        status_fim, erro = StatusDocumento.CONCLUIDO, None

    except Exception as e:
        texto, entidades = None, None
        status_fim, erro = StatusDocumento.ERRO, str(e)

    # salvando resultado
    async with SessionLocal() as session:
        doc = await session.get(Documento, doc_id)
        doc.status = status_fim
        doc.erro = erro
        doc.texto = texto
        doc.entidades = entidades
        await session.commit()
