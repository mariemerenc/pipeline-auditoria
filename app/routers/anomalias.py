from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ml.model import detector

router = APIRouter(tags=["anomalias"])


class Contrato(BaseModel):
    fornecedor: str
    mes: int = Field(ge=1, le=12)
    valor: float = Field(gt=0)


@router.post("/anomalias/avaliar")
async def avaliar(contrato: Contrato):
    return detector.avaliar(contrato.fornecedor, contrato.mes, contrato.valor)


@router.get("/anomalias/metricas")
async def metricas():
    """precisão, recall e f1 medidos contra anomalias plantadas no histórico"""
    return detector.metricas
