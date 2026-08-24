import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    UploadFile,
    status,
)

from app.config import settings
from app.db.models import Documento, StatusDocumento
from app.deps import SessionDep
from app.pipeline.tasks import processar_documento
from app.schemas import DocumentoCriado, DocumentoDetalhe

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=DocumentoCriado)
async def enviar_documento(
    arquivo: UploadFile, background_tasks: BackgroundTasks, session: SessionDep
):
    if arquivo.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="envie um arquivo pdf !!")

    doc_id = uuid.uuid4()
    caminho = settings.upload_dir / f"{doc_id}.pdf"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(await arquivo.read())

    doc = Documento(
        id=doc_id,
        nome_arquivo=arquivo.filename,
        caminho_arquivo=str(caminho),
        status=StatusDocumento.PENDENTE,
    )

    session.add(doc)
    await session.commit()

    background_tasks.add_task(processar_documento, doc_id)

    return doc


@router.get("/{doc_id}", response_model=DocumentoDetalhe)
async def obter_documento(
    doc_id: uuid.UUID,
    session: SessionDep,
):
    doc = await session.get(Documento, doc_id)

    if doc is None:
        raise HTTPException(status_code=404, detail="documento não encontrado")

    return doc
