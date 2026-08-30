import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentoCriado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str


class DocumentoDetalhe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_arquivo: str
    status: str
    entidades: dict[str, list[str]] | None
    erro: str | None
    criado_em: datetime
