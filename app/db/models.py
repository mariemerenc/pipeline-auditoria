import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class StatusDocumento(StrEnum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"


class Base(DeclarativeBase):
    pass


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome_arquivo: Mapped[str]
    caminho_arquivo: Mapped[str]
    status: Mapped[str] = mapped_column(default=StatusDocumento.PENDENTE)
    texto: Mapped[str | None]
    erro: Mapped[str | None]
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
