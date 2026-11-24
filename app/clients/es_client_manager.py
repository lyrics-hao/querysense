import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.client:AsyncElasticsearch | None = None
        self.config:ESConfig = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(
            hosts = [self._get_url()]
        )

    async def close(self):
        await self.client.close()

es_client_manager = ESClientManager(app_config.es)



if __name__ == '__main__':
    es_client_manager.init()
    client = es_client_manager.client

    async def test():
        # 创建索引
        await client.indices.create(
            index="test"
        )

        # 写入数据
        await client.index(
            index="test",
            document={
                "test": "test",
                "name": "zs",
                "age" : 18
            }
        )


        resp = await client.search(
            index="test",
        )
        print(resp)

        await es_client_manager.close()

    asyncio.run(test())

