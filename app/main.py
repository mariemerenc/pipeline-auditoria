from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.deps import engine, es
from app.routers import documentos


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await es.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(documentos.router)


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
