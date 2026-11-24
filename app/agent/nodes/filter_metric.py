# state 读写修改的数据
# config 只读不变的一些参数
# runtime 处理运行时依赖 --- context静态上下文 数据库的客户端、数据库的连接; store 持久化; stream_writer：custom stream
import yaml

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.prompt.prompt_loader import load_prompt
from app.core.log import  logger


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    step = "过滤指标信息"
    writer(
        {
            "type": "progress",
            "step": step,
            "status": "running"
        }
    )

    try:
        query = state["query"]
        metric_infos = state["metric_infos"]

        prompt = PromptTemplate(template=load_prompt("filter_metric_info"), input_variables=['query', 'metric_infos'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        res = await chain.ainvoke({'query': query,
                                   'metric_infos': yaml.dump(metric_infos, allow_unicode=True, sort_keys=False)})

        filter_metric_infos = [metric_info for metric_info in metric_infos if metric_info['name'] in res]

        writer(
            {
                "type": "progress",
                "step": step,
                "status": "success"
            }
        )

        logger.info(f"过滤后的指标信息: {[filter_metric_info['name'] for filter_metric_info in filter_metric_infos]}")
        return {"metric_infos": filter_metric_infos}
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
