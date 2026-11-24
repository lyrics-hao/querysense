from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository

from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.query_service import QueryService
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from fastapi import Depends


async def get_meta_Session():
    async with meta_mysql_client_manager.session_factory() as meta_session:
        yield meta_session

async def get_dw_Session():
    async with dw_mysql_client_manager.session_factory() as dw_session:
        yield dw_session


# 子依赖注入函数  init() 借用生命周期事件来实现 自定义上下文管理器函数
async def get_meta_mysql_repository(session: Annotated[AsyncSession, Depends(get_meta_Session)]) -> MetaMysqlRepository:
    return MetaMysqlRepository(session)

async def get_embedding_client() -> HuggingFaceEndpointEmbeddings:
    return embedding_client_manager.client

async def get_dw_mysql_repository(session: Annotated[AsyncSession, Depends(get_dw_Session)]) -> DwMysqlRepository:
    return DwMysqlRepository(session)

async def get_column_qdrant_repository() -> ColumnQdrantRepository:
    return ColumnQdrantRepository(qdrant_client_manager.client)

async def get_metric_qdrant_repository() -> MetricQdrantRepository:
    return MetricQdrantRepository(qdrant_client_manager.client)

async def get_value_es_repository() -> ValueESRepository:
    return ValueESRepository(es_client_manager.client)

# 依赖注入函数
async def get_query_service(
        meta_mysql_repository: Annotated[MetaMysqlRepository, Depends(get_meta_mysql_repository)],
        embedding_client: Annotated[HuggingFaceEndpointEmbeddings, Depends(get_embedding_client)],
        dw_mysql_repository: Annotated[DwMysqlRepository, Depends(get_dw_mysql_repository)],
        column_qdrant_repository: Annotated[ColumnQdrantRepository, Depends(get_column_qdrant_repository)],
        metric_qdrant_repository: Annotated[MetricQdrantRepository, Depends(get_metric_qdrant_repository)],
        value_es_repository: Annotated[ValueESRepository, Depends(get_value_es_repository)],
) ->QueryService:

    return QueryService(
        meta_mysql_repository=meta_mysql_repository,
        embedding_client=embedding_client,
        dw_mysql_repository=dw_mysql_repository,
        column_qdrant_repository=column_qdrant_repository,
        metric_qdrant_repository=metric_qdrant_repository,
        value_es_repository=value_es_repository
    )