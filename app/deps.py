from collections.abc import AsyncGenerator
from typing import Annotated

import spacy
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
es = AsyncElasticsearch(settings.elasticsearch_url)
nlp = spacy.load(settings.spacy_model)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
