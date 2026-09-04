import asyncio

from fastapi import APIRouter
from pydantic import BaseModel

from app.llm.client import perguntar

router = APIRouter(tags=["agente"])

class Pergunta(BaseModel):
    texto: str
    

@router.post("/perguntar")
async def responder(p: Pergunta):
    return await asyncio.to_thread(perguntar, p.texto)
