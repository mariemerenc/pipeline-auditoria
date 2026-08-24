import asyncio
import uuid

from app.db.models import Documento, StatusDocumento
from app.deps import SessionLocal


async def processar_documento(doc_id: uuid.UUID) -> None:
    # processando (na teoria)
    async with SessionLocal() as session:
        doc = await session.get(Documento, doc_id)

        if doc is None:
            return
        doc.status = StatusDocumento.PROCESSANDO
        await session.commit()

    # processamento (na prática)
    try:
        await asyncio.sleep(2)
        status_fim, erro = StatusDocumento.CONCLUIDO, None

    except Exception as e:
        status_fim, erro = StatusDocumento.ERRO, str(e)

    # salvando resultado
    async with SessionLocal() as session:
        doc = await session.get(Documento, doc_id)
        doc.status = status_fim
        doc.erro = erro
        await session.commit()
