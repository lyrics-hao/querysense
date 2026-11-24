# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
import yaml

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "过滤表格信息"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        table_infos: list[TableInfoState]= state["table_infos"]
        query = state["query"]


        prompt = PromptTemplate(template=load_prompt("filter_table_info"), input_variables=['query', 'table_infos'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        res = await chain.ainvoke({'query': query,
                                    'table_infos': yaml.dump(table_infos, allow_unicode=True, sort_keys=False)})
        # {
        #     "表名1" : ["字段1", "字段2"],
        #     "表名2" : ["字段1", "字段2"],
        # }

        filter_table_infos: list[TableInfoState]= []
        for table_info in table_infos:
            if table_info['name'] in res: # 进行表过滤
                # 对字段值进行过滤
                table_info['columns'] = [column_info for column_info in table_info['columns'] if column_info['name'] in res[table_info['name']]]
                filter_table_infos.append(table_info)

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"过滤后的表信息: {[filter_table_info['name'] for filter_table_info in filter_table_infos]}")
        return {"table_infos": filter_table_infos}
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
