import asyncio

from sqlalchemy import text
from app.conf.app_config import DBConfig, app_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession,async_sessionmaker

class MysqlClientManager:
    def __init__(self, config:DBConfig):
        self.engine: AsyncEngine | None = None # 啥时候用到sql啥时候创建session
        self.session_factory = None
        self.config:DBConfig = config

    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=10, # 默认是5
            pool_pre_ping=True, # 使用某个连接池前会ping一下 成功则可以使用
        )
        # autoflush 执行数据库查询操作前自动进行flush（把相关操作写入数据库）操作
        # expired_on_commit默认为True 异步操作不支持要设置False
        self.session_factory = async_sessionmaker(self.engine, autoflush=True, expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

# 访问元数据库时候
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)
# 访问模拟数仓的时候
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)

if __name__ == '__main__':
    dw_mysql_client_manager.init()
    engine = dw_mysql_client_manager.engine

    async def test():
        # async with AsyncSession(engine, autoflush=True, expire_on_commit=False) as session: 下面的写法是避免每次写很多参数
        # 实例() 相当于调用实例.__call__ 创建一个AsyncSession对象
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            res = await session.execute(text(sql))

            # mapping 可以通过字段名访问数据 dict
            rows = res.mappings().fetchall()

            print(type(rows))
            print(type(rows[0]))
            print(rows[0]['order_id'])
            print(rows)

    asyncio.run(test())
