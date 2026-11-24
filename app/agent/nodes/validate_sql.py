# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime

from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.core.log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "检验sql"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        sql = state['sql']
        dw_mysql_repository: DwMysqlRepository = runtime.context['dw_mysql_repository']

        try:
            await dw_mysql_repository.validate(sql)
            writer(
                {
                    "type": "progress",
                    "step": step,
                    "status": "success"
                }
            )
            logger.info("SQL语法正确")
            return {"error": None}
        except Exception as e:
            writer(
                {
                    "type": "progress",
                    "step": step,
                    "status": "success"
                }
            )
            logger.error(f"SQL语法错误：{e}")
            return {"error": str(e)}
    except Exception as e:
        logger.error(f"{step}失败：{e}")
        writer(
            {
                "type": "progress",
                "step": step,
                "status": "error"
            }
        )
        raise
