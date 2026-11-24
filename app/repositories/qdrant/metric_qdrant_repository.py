from qdrant_client import  AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import PointStruct
from app.conf.app_config import app_config
from app.entities.metric_info import MetricInfo


class MetricQdrantRepository(object):
    collection_name = 'metric_info_collection'

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=app_config.qdrant.embedding_size, distance=Distance.COSINE)
            )

    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[dict], batch_size: int = 10):
        # type(zip()) tuple
        points: list[PointStruct] = [PointStruct(id=id, vector=vector, payload=payload) for id, vector, payload in
                                     zip(ids, embeddings, payloads)]
        # 防止gpu过载
        for i in range(0, len(points), batch_size):
            await self.client.upsert(collection_name=self.collection_name, points=points[i:i + batch_size])

    async def search(self, embedding: list[float], score_threshold: float = 0.6, limit: int = 10) -> list[MetricInfo]:
        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
        return [MetricInfo(**point.payload) for point in result.points]