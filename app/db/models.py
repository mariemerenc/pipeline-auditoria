import uuid
from datetime import datetime
from enum import StrEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
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
    entidades: Mapped[dict | None] = mapped_column(JSONB)
    erro: Mapped[str | None]
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    documento_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documentos.id", ondelete="CASCADE"), index=True
    )
    ordem: Mapped[int]
    texto: Mapped[str]
    embedding: Mapped[list[float]] = mapped_column(Vector(384))
