# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
from datetime import date

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from langgraph.runtime import Runtime

from app.repositories.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.core.log import logger

async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "添加额外的上下文"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )
    try:
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month - 1) // 3 + 1}"
        date_info: DateInfoState = DateInfoState(date=date_str, weekday=weekday, quarter=quarter)

        dw_mysql_repository: DwMysqlRepository = runtime.context['dw_mysql_repository']

        db = await dw_mysql_repository.get_db_info()
        db_info: DBInfoState = DBInfoState(** db)

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success",
            }
        )

        logger.info(f"日期信息添加成功： {date_info}")
        logger.info(f"数据库信息添加成功： {db_info}")

        return {"date_info": date_info, "db_info": db_info}
    except Exception as e:
        logger.error(f"添加额外上下文失败： {e}")
        writer(
            {
                "type": "progress",
                "step": step,
                "status": "error"
            }
        )
        raise