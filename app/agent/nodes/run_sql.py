# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime

from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.core.log import logger

async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "运行sql"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        sql = state['sql']
        dw_mysql_repository: DwMysqlRepository = runtime.context["dw_mysql_repository"]

        res: list[dict] = await dw_mysql_repository.run(sql)

        logger.info(f"执行sql的结果: {res}")
        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )
        writer(
            {
                "type": "result",
                "data": res
            }
        )
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
