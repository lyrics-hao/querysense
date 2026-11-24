import asyncio

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config:QdrantConfig):
        self.client: AsyncQdrantClient | None = None
        self.config: QdrantConfig = config

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        await self.client.close()

qdrant_client_manager = QdrantClientManager(app_config.qdrant)


async def test():
    qdrant_client_manager.init()
    client = qdrant_client_manager.client
    # 创建集合
    await client.create_collection(
        collection_name="test_async",
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )

    # 写入数据
    await client.upsert(
        collection_name='test_async',
        wait=True,
        points=[
            PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={'city': 'Berlin'}),
            PointStruct(id=2, vector=[0.19, 0.81, 0.76, 0.74], payload={'city': 'china'}),
            PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={'city': 'USA'}),
            PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={'city': 'korea'}),
            PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={'city': 'Japan'}),
            PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={'city': 'Russia'})
        ]
    )

    search_res = await client.query_points(
        collection_name='test_async',
        query=[0.2, 0.1, 0.9, 0.7],
        with_payload=False,
        limit=3
    )

    print(search_res.points)

    await qdrant_client_manager.close()

if __name__ == '__main__':
    asyncio.run(test())