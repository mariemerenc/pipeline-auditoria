from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.deps import engine, es
from app.ml.model import detector
from app.pipeline.index import garantir_indice
from app.routers import anomalias, busca, documentos, perguntar


@asynccontextmanager
async def lifespan(app: FastAPI):
    await garantir_indice(es)
    metricas = detector.treinar(settings.historico_csv)
    print(f"detector de anomalias treinado: {metricas}")
    yield
    await es.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(documentos.router)
app.include_router(busca.router)
app.include_router(perguntar.router)
app.include_router(anomalias.router)


@app.get("/health")
async def get_health():
    """endpoint de health check"""

    status_report = {
        "postgres": {"status": "erro", "erro": ""},
        "elasticsearch": {"status": "erro", "erro": ""},
    }

    # teste postgres
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        status_report["postgres"]["status"] = "ok"

    except Exception as e:
        status_report["postgres"]["erro"] = str(e)

    # teste elasticsearch
    try:
        await es.info()
        status_report["elasticsearch"]["status"] = "ok"

    except Exception as e:
        status_report["elasticsearch"]["erro"] = str(e)

    tudo_ok = all(s["status"] == "ok" for s in status_report.values())
    return JSONResponse(status_code=200 if tudo_ok else 503, content=status_report)
