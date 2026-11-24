# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
import yaml

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "生成sql"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        table_infos = state['table_infos']
        metric_infos = state['metric_infos']
        db_info = state['db_info']
        date_info = state['date_info']
        query = state['query']

        prompt = PromptTemplate(template=load_prompt("generate_sql"), input_variables=['table_infos', 'metric_infos', 'db_info', 'date_info', 'query'])
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        res = await chain.ainvoke({"table_infos" : yaml.dump(table_infos, allow_unicode = True, sort_keys = False),
                                    "metric_infos" : yaml.dump(metric_infos, allow_unicode = True, sort_keys = False),
                                    "db_info" : yaml.dump(db_info, allow_unicode = True, sort_keys = False),
                                    "date_info" : yaml.dump(date_info, allow_unicode = True, sort_keys = False),
                                    "query" : query})

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"生成的sql：{res}")
        return {"sql": res}
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
