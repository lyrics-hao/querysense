from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class DwMysqlRepository():
    def __init__(self, session:AsyncSession):
        self.session = session

    async def get_column_types(self, table_name):
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        # 映射成字典
        result_dict = result.mappings().fetchall()

        # 列表推导式快捷键 compd 最终结果整理成 name : type
        return {row['Field']: row['Type'] for row in result_dict}

    async def get_column_values(self, table_name, column_name, limit = 10):
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        # 列表推导式 compl
        return [row[0] for row in result.fetchall()]

    async def get_db_info(self):
        sql = f"select version()"
        res = await self.session.execute(text(sql))
        version = res.scalar() #专门返回一行一列的单值  scarlars是一列的值返回list
        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate(self, sql: str):
        sql = f"explain {sql}"

        await self.session.execute(text(sql))

    async def run(self, sql) -> list[dict]:
        res = await self.session.execute(text(sql))

        return [dict(row) for row in res.mappings().fetchall()]

