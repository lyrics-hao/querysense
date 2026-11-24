import json

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from langchain_huggingface import HuggingFaceEndpointEmbeddings


class QueryService:
    def __init__(self,
                 meta_mysql_repository: MetaMysqlRepository,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 dw_mysql_repository: DwMysqlRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 value_es_repository: ValueESRepository
                 ):
        self.meta_mysql_repository = meta_mysql_repository
        self.embedding_client: HuggingFaceEndpointEmbeddings = embedding_client
        self.dw_mysql_repository = dw_mysql_repository

        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository

    async def query(self, query: str):
        # 定义状态
        state = DataAgentState(query=query)
        # 上下文依赖
        context = DataAgentContext(column_qdrant_repository=self.column_qdrant_repository,
                                   embedding_client=self.embedding_client,
                                   metric_qdrant_repository=self.metric_qdrant_repository,
                                   value_es_repository=self.value_es_repository,
                                   meta_mysql_repository=self.meta_mysql_repository,
                                   dw_mysql_repository=self.dw_mysql_repository)
        # 流式调用
        try:
            async for chunk in graph.astream(state, context=context, stream_mode='custom'):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"  # 满足sse格式
        except Exception as e:
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"
